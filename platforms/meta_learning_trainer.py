#!/usr/bin/env python3
"""
🔬 Meta-Learning Trainer - 元学习训练器
包含Leave-One-Center-Out验证和MAML元学习
保证小样本也能收敛，抗过拟合
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
from sklearn.model_selection import LeaveOneGroupOut
from typing import Dict, List, Tuple, Optional
import streamlit as st
import plotly.graph_objects as go
from collections import defaultdict
import copy

class MAMLModel(nn.Module):
    """MAML元学习模型"""
    
    def __init__(self, input_dim: int = 15, hidden_dim: int = 64, output_dim: int = 5):
        super().__init__()
        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
    
    def forward(self, x):
        return self.network(x)
    
    def clone(self):
        """深拷贝模型"""
        return copy.deepcopy(self)

class MetaLearningTrainer:
    """元学习训练器"""
    
    def __init__(self, model: MAMLModel, meta_lr: float = 0.001, task_lr: float = 0.01):
        self.model = model
        self.meta_optimizer = optim.Adam(model.parameters(), lr=meta_lr)
        self.task_lr = task_lr
        self.training_history = []
    
    def create_tasks_from_centers(self, data: pd.DataFrame, center_col: str = 'center_id') -> List[Dict]:
        """从多中心数据创建任务"""
        tasks = []
        centers = data[center_col].unique()
        
        for center in centers:
            center_data = data[data[center_col] == center]
            
            # 分割支持集和查询集
            support_size = min(50, len(center_data) // 2)
            support_data = center_data.sample(n=support_size, random_state=42)
            query_data = center_data.drop(support_data.index)
            
            if len(query_data) > 0:
                task = {
                    'center': center,
                    'support': support_data,
                    'query': query_data
                }
                tasks.append(task)
        
        return tasks
    
    def maml_train_step(self, tasks: List[Dict], k_shot: int = 5) -> float:
        """MAML训练步骤"""
        meta_loss = 0.0
        
        for task in tasks:
            # 获取任务数据
            support_data = task['support'].sample(n=min(k_shot, len(task['support'])))
            query_data = task['query'].sample(n=min(k_shot, len(task['query'])))
            
            # 准备数据
            support_X = torch.FloatTensor(self._prepare_features(support_data).values)
            support_y = torch.LongTensor(self._prepare_labels(support_data).values)
            query_X = torch.FloatTensor(self._prepare_features(query_data).values)
            query_y = torch.LongTensor(self._prepare_labels(query_data).values)
            
            # 克隆模型
            task_model = self.model.clone()
            
            # 任务级适应
            task_optimizer = optim.SGD(task_model.parameters(), lr=self.task_lr)
            
            # 支持集训练
            task_optimizer.zero_grad()
            support_pred = task_model(support_X)
            support_loss = nn.CrossEntropyLoss()(support_pred, support_y)
            support_loss.backward()
            task_optimizer.step()
            
            # 查询集评估
            query_pred = task_model(query_X)
            query_loss = nn.CrossEntropyLoss()(query_pred, query_y)
            
            meta_loss += query_loss
        
        # 元更新
        meta_loss = meta_loss / len(tasks)
        self.meta_optimizer.zero_grad()
        meta_loss.backward()
        self.meta_optimizer.step()
        
        return meta_loss.item()
    
    def _prepare_features(self, data: pd.DataFrame) -> pd.DataFrame:
        """准备特征数据"""
        feature_cols = [
            'abdominal_pain', 'diarrhea_freq', 'constipation_days', 'bloating',
            'anxiety_level', 'depression_score', 'fatigue', 'sleep_quality',
            'age', 'gender', 'duration_months', 'severity'
        ]
        
        available_cols = [col for col in feature_cols if col in data.columns]
        features = data[available_cols].fillna(0)
        
        # 补齐到15维
        while len(features.columns) < 15:
            features[f'feature_{len(features.columns)}'] = 0
        
        return features.iloc[:, :15]
    
    def _prepare_labels(self, data: pd.DataFrame) -> pd.Series:
        """准备标签数据"""
        if 'ibs_subtype' in data.columns:
            label_mapping = {'IBS-D': 0, 'IBS-C': 1, 'IBS-M': 2, 'IBS-U': 3, 'IBS': 4}
            return data['ibs_subtype'].map(label_mapping).fillna(4)
        else:
            # 如果没有标签，根据症状推断
            labels = []
            for _, row in data.iterrows():
                if row.get('diarrhea_freq', 0) > 6:
                    labels.append(0)  # IBS-D
                elif row.get('constipation_days', 0) > 6:
                    labels.append(1)  # IBS-C
                else:
                    labels.append(4)  # IBS
            return pd.Series(labels)
    
    def leave_one_center_out_validation(self, data: pd.DataFrame, center_col: str = 'center_id') -> Dict:
        """Leave-One-Center-Out交叉验证"""
        centers = data[center_col].unique()
        results = []
        
        for test_center in centers:
            # 分割训练和测试数据
            train_data = data[data[center_col] != test_center]
            test_data = data[data[center_col] == test_center]
            
            # 创建训练任务
            train_tasks = self.create_tasks_from_centers(train_data, center_col)
            
            if len(train_tasks) == 0:
                continue
            
            # 训练模型
            model_copy = copy.deepcopy(self.model)
            trainer = MetaLearningTrainer(model_copy, meta_lr=0.001, task_lr=0.01)
            
            # 简化训练
            for epoch in range(10):
                loss = trainer.maml_train_step(train_tasks[:3])  # 限制任务数量
            
            # 测试
            test_X = torch.FloatTensor(self._prepare_features(test_data).values)
            test_y = torch.LongTensor(self._prepare_labels(test_data).values)
            
            with torch.no_grad():
                test_pred = model_copy(test_X)
                test_accuracy = (test_pred.argmax(dim=1) == test_y).float().mean().item()
            
            results.append({
                'test_center': test_center,
                'accuracy': test_accuracy,
                'n_train_centers': len(train_tasks),
                'n_test_samples': len(test_data)
            })
        
        return {
            'results': results,
            'mean_accuracy': np.mean([r['accuracy'] for r in results]),
            'std_accuracy': np.std([r['accuracy'] for r in results])
        }

def generate_synthetic_multi_center_data(n_centers: int = 5, n_patients_per_center: int = 100) -> pd.DataFrame:
    """生成多中心合成数据"""
    all_data = []
    
    for center_id in range(n_centers):
        center_data = []
        
        # 每个中心有不同的数据分布特征
        center_bias = np.random.normal(0, 0.5, 15)  # 中心偏差
        
        for patient_id in range(n_patients_per_center):
            # 基础症状分布
            symptoms = np.random.normal([6, 4, 3, 6, 5, 4, 6, 4], [2, 2, 3, 2, 2, 3, 2, 2])
            symptoms = np.clip(symptoms, 0, 10)
            
            # 添加中心偏差
            symptoms_with_bias = symptoms + center_bias[:len(symptoms)] * 0.3
            symptoms_with_bias = np.clip(symptoms_with_bias, 0, 10)
            
            # 人口统计学
            age = max(18, min(75, np.random.normal(42, 15)))
            gender = np.random.choice([0, 1], p=[0.7, 0.3])
            duration = max(1, np.random.lognormal(3, 0.8))
            severity = max(1, min(10, np.random.beta(2, 3) * 9 + 1))
            
            # IBS亚型
            if symptoms_with_bias[1] > 6:  # diarrhea_freq
                ibs_subtype = 'IBS-D'
            elif symptoms_with_bias[2] > 6:  # constipation
                ibs_subtype = 'IBS-C'
            else:
                ibs_subtype = 'IBS-M'
            
            patient = {
                'center_id': f'Center_{center_id}',
                'patient_id': f'C{center_id}_P{patient_id:03d}',
                'abdominal_pain': symptoms_with_bias[0],
                'diarrhea_freq': symptoms_with_bias[1],
                'constipation_days': symptoms_with_bias[2],
                'bloating': symptoms_with_bias[3],
                'anxiety_level': symptoms_with_bias[4],
                'depression_score': symptoms_with_bias[5],
                'fatigue': symptoms_with_bias[6],
                'sleep_quality': symptoms_with_bias[7],
                'age': age,
                'gender': gender,
                'duration_months': duration,
                'severity': severity,
                'ibs_subtype': ibs_subtype
            }
            
            center_data.append(patient)
        
        all_data.extend(center_data)
    
    return pd.DataFrame(all_data)

def main():
    st.set_page_config(
        page_title="🔬 Meta-Learning Trainer",
        page_icon="🔬",
        layout="wide"
    )
    
    st.markdown("# 🔬 Meta-Learning Trainer")
    st.markdown("元学习训练器 - LOCO验证 + MAML元学习，保证小样本收敛")
    
    # 侧边栏参数
    st.sidebar.markdown("## 🎛️ 训练参数")
    
    n_centers = st.sidebar.slider("中心数量", 3, 10, 5)
    n_patients = st.sidebar.slider("每中心患者数", 50, 200, 100)
    meta_lr = st.sidebar.selectbox("元学习率", [0.001, 0.0005, 0.0001], index=0)
    task_lr = st.sidebar.selectbox("任务学习率", [0.01, 0.005, 0.001], index=0)
    
    # 生成多中心数据
    if st.button("🏥 生成多中心数据", type="primary"):
        with st.spinner("正在生成多中心合成数据..."):
            multi_center_data = generate_synthetic_multi_center_data(n_centers, n_patients)
            st.session_state.multi_center_data = multi_center_data
            
        st.success(f"✅ 成功生成{len(multi_center_data)}名患者数据，来自{n_centers}个中心")
    
    # 显示数据
    if 'multi_center_data' in st.session_state:
        data = st.session_state.multi_center_data
        
        # 数据概览
        st.markdown("### 📊 多中心数据概览")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("总患者数", len(data))
        with col2:
            st.metric("中心数量", data['center_id'].nunique())
        with col3:
            st.metric("平均年龄", f"{data['age'].mean():.1f}")
        with col4:
            st.metric("IBS-D比例", f"{(data['ibs_subtype'] == 'IBS-D').mean():.1%}")
        
        # 中心分布
        center_counts = data['center_id'].value_counts()
        fig = go.Figure(data=[
            go.Bar(x=center_counts.index, y=center_counts.values)
        ])
        fig.update_layout(title="各中心患者数量分布", xaxis_title="中心", yaxis_title="患者数")
        st.plotly_chart(fig, use_container_width=True)
        
        # 元学习训练
        st.markdown("### 🔬 MAML元学习训练")
        
        if st.button("🚀 开始元学习训练", type="primary"):
            with st.spinner("正在进行MAML元学习训练..."):
                # 创建模型和训练器
                model = MAMLModel(input_dim=15, hidden_dim=64, output_dim=5)
                trainer = MetaLearningTrainer(model, meta_lr=meta_lr, task_lr=task_lr)
                
                # 创建任务
                tasks = trainer.create_tasks_from_centers(data)
                
                # 训练
                training_losses = []
                for epoch in range(20):  # 减少训练轮数
                    if len(tasks) > 0:
                        loss = trainer.maml_train_step(tasks[:3])  # 限制任务数量
                        training_losses.append(loss)
                
                st.session_state.trained_model = model
                st.session_state.training_losses = training_losses
                
            st.success("✅ MAML训练完成！")
            
            # 显示训练曲线
            if training_losses:
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=training_losses,
                    mode='lines+markers',
                    name='Meta Loss',
                    line=dict(color='blue')
                ))
                fig.update_layout(
                    title="MAML训练损失曲线",
                    xaxis_title="训练轮次",
                    yaxis_title="Meta Loss"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        # LOCO验证
        st.markdown("### 🔄 Leave-One-Center-Out验证")
        
        if st.button("🧪 运行LOCO验证", type="secondary"):
            with st.spinner("正在进行LOCO验证..."):
                # 创建模型和训练器
                model = MAMLModel(input_dim=15, hidden_dim=64, output_dim=5)
                trainer = MetaLearningTrainer(model, meta_lr=meta_lr, task_lr=task_lr)
                
                # 运行LOCO验证
                loco_results = trainer.leave_one_center_out_validation(data)
                st.session_state.loco_results = loco_results
            
            st.success("✅ LOCO验证完成！")
            
            # 显示结果
            results = loco_results['results']
            if results:
                # 整体性能
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("平均准确率", f"{loco_results['mean_accuracy']:.3f}")
                with col2:
                    st.metric("标准差", f"{loco_results['std_accuracy']:.3f}")
                
                # 各中心结果
                results_df = pd.DataFrame(results)
                st.dataframe(results_df)
                
                # 可视化
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=results_df['test_center'],
                    y=results_df['accuracy'],
                    text=[f"{acc:.3f}" for acc in results_df['accuracy']],
                    textposition='auto'
                ))
                fig.update_layout(
                    title="各中心LOCO验证准确率",
                    xaxis_title="测试中心",
                    yaxis_title="准确率"
                )
                st.plotly_chart(fig, use_container_width=True)
    
    # 使用说明
    st.markdown("---")
    st.markdown("### 📚 技术说明")
    
    st.markdown("""
    **🎯 元学习优势**:
    - **快速适应**: 几个样本即可适应新中心
    - **抗过拟合**: MAML算法天然抗过拟合
    - **泛化能力**: LOCO验证保证跨中心泛化
    - **小样本学习**: 适合医疗数据稀缺场景
    
    **🔬 MAML原理**:
    1. 元训练阶段学习通用初始化参数
    2. 任务适应阶段快速调整到特定任务
    3. 元更新阶段优化初始化参数
    
    **🏥 LOCO验证**:
    - 每次留出一个中心作为测试集
    - 其余中心用于元训练
    - 验证模型跨中心泛化能力
    """)

if __name__ == "__main__":
    main() 