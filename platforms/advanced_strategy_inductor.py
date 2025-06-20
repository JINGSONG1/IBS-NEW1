#!/usr/bin/env python3
"""
🧠 Advanced Strategy Inductor - 完整Transformer策略归纳器
包含完整的FSM + ReplayBuffer + Transformer + 策略融合功能
"""

import streamlit as st
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader, Dataset
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="🧠 Advanced Strategy Inductor",
    page_icon="🧠",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}
.transformer-box {
    background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 8px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.rule-box {
    background: #e8f5e8;
    border-left: 4px solid #4CAF50;
    padding: 1rem;
    margin: 1rem 0;
    border-radius: 5px;
}
.attention-box {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 1rem;
    border-radius: 5px;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ==================== Transformer组件 ====================

class PathDataset(Dataset):
    """路径数据集"""
    def __init__(self, experiences: List[Dict]):
        self.experiences = experiences
        
    def __len__(self):
        return len(self.experiences)
    
    def __getitem__(self, idx):
        exp = self.experiences[idx]
        state_vector = exp['state'].to_vector()
        path_type = self._encode_path_type(exp['path'].get_mechanism_type())
        reward = exp['reward']
        
        return {
            'state': torch.FloatTensor(state_vector),
            'path_type': torch.LongTensor([path_type]),
            'reward': torch.FloatTensor([reward])
        }
    
    def _encode_path_type(self, mechanism_type: str) -> int:
        mapping = {
            'psychological': 0,
            'anti_inflammatory': 1,
            'microbiome': 2,
            'motility': 3,
            'combined': 4
        }
        return mapping.get(mechanism_type, 4)

class TransformerRuleEngine(nn.Module):
    """Transformer规则引擎"""
    def __init__(self, state_dim: int = 15, hidden_dim: int = 128, num_heads: int = 4):
        super().__init__()
        self.state_dim = state_dim
        self.hidden_dim = hidden_dim
        
        # 状态编码器
        self.state_encoder = nn.Linear(state_dim, hidden_dim)
        
        # Transformer层
        self.transformer = nn.TransformerEncoder(
            nn.TransformerEncoderLayer(
                d_model=hidden_dim,
                nhead=num_heads,
                dim_feedforward=hidden_dim * 2,
                dropout=0.1,
                batch_first=True
            ),
            num_layers=2
        )
        
        # 路径偏好预测器
        self.path_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(hidden_dim // 2, 5)  # 5种路径类型
        )
        
        # 效果预测器
        self.effect_predictor = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1),
            nn.Sigmoid()
        )
    
    def forward(self, state_batch):
        # 编码状态
        encoded = self.state_encoder(state_batch)
        
        # Transformer处理
        if len(encoded.shape) == 2:
            encoded = encoded.unsqueeze(1)
        
        transformed = self.transformer(encoded)
        pooled = transformed.mean(dim=1)
        
        # 预测
        path_scores = self.path_predictor(pooled)
        effect_scores = self.effect_predictor(pooled)
        
        return path_scores, effect_scores
    
    def extract_rules(self, state_batch) -> Dict:
        """提取可解释规则"""
        self.eval()
        with torch.no_grad():
            path_scores, effect_scores = self.forward(state_batch)
            
            # 分析路径偏好
            path_prefs = F.softmax(path_scores, dim=1).mean(dim=0)
            path_types = ['心理路径', '抗炎路径', '菌群路径', '动力路径', '综合路径']
            
            rules = {}
            for i, (path_type, score) in enumerate(zip(path_types, path_prefs)):
                rules[f'偏好_{path_type}'] = float(score)
            
            rules['预期效果'] = float(effect_scores.mean())
            
            return rules

class StrategicPolicyInitializer:
    """策略初始化器"""
    def __init__(self):
        self.learned_rules = {}
        self.path_preferences = {}
        
    def update_from_rules(self, rules: Dict):
        """从学习到的规则更新策略"""
        self.learned_rules.update(rules)
        
        # 更新路径偏好
        path_prefs = {}
        for key, value in rules.items():
            if key.startswith('偏好_'):
                path_type = key.replace('偏好_', '')
                path_prefs[path_type] = value
        
        self.path_preferences = path_prefs
    
    def get_initial_strategy(self, patient_state: Dict) -> Dict:
        """获取初始策略"""
        strategy = {
            'primary_path': self._select_primary_path(patient_state),
            'backup_paths': self._select_backup_paths(patient_state),
            'confidence': self._calculate_confidence(patient_state)
        }
        
        return strategy
    
    def _select_primary_path(self, patient_state: Dict) -> str:
        """选择主要路径"""
        if patient_state.get('焦虑', 0) > 7:
            return '心理路径'
        elif patient_state.get('炎症', 0) > 5:
            return '抗炎路径'
        elif patient_state.get('菌群失调', 0) > 6:
            return '菌群路径'
        else:
            best_path = max(self.path_preferences.items(), 
                          key=lambda x: x[1], default=('综合路径', 0))
            return best_path[0]
    
    def _select_backup_paths(self, patient_state: Dict) -> List[str]:
        """选择备用路径"""
        all_paths = ['心理路径', '抗炎路径', '菌群路径', '动力路径', '综合路径']
        primary = self._select_primary_path(patient_state)
        
        backup = [p for p in all_paths if p != primary]
        backup.sort(key=lambda p: self.path_preferences.get(p, 0), reverse=True)
        
        return backup[:2]
    
    def _calculate_confidence(self, patient_state: Dict) -> float:
        """计算策略信心度"""
        base_confidence = 0.7
        
        if self.learned_rules.get('预期效果', 0) > 0.8:
            base_confidence += 0.2
        
        return min(base_confidence, 0.95)

# ==================== 核心数据结构 ====================

class FSMState:
    """FSM状态表示"""
    def __init__(self, symptoms: Dict, context: Dict, timestamp: float):
        self.symptoms = symptoms
        self.context = context
        self.timestamp = timestamp
        
    def to_vector(self) -> np.ndarray:
        """转换为向量表示"""
        vector = []
        
        # 症状向量 (10维)
        symptom_vector = [
            self.symptoms.get('腹痛', 0),
            self.symptoms.get('腹泻', 0), 
            self.symptoms.get('便秘', 0),
            self.symptoms.get('腹胀', 0),
            self.symptoms.get('焦虑', 0),
            self.symptoms.get('抑郁', 0),
            self.symptoms.get('疲劳', 0),
            self.symptoms.get('失眠', 0),
            self.symptoms.get('恶心', 0),
            self.symptoms.get('食欲不振', 0)
        ]
        vector.extend(symptom_vector)
        
        # 上下文向量 (5维)
        context_vector = [
            self.context.get('年龄', 35) / 100,
            self.context.get('性别', 0),
            self.context.get('病程', 12) / 120,
            self.context.get('严重程度', 5) / 10,
            self.context.get('既往史', 0)
        ]
        vector.extend(context_vector)
        
        return np.array(vector, dtype=np.float32)

class FSMPath:
    """FSM路径表示"""
    def __init__(self, path_id: str, mechanisms: List[str], outcome: Dict):
        self.path_id = path_id
        self.mechanisms = mechanisms
        self.outcome = outcome
        
    def get_mechanism_type(self) -> str:
        """获取主要机制类型"""
        if '心理调节' in self.mechanisms or '抗焦虑' in self.mechanisms:
            return 'psychological'
        elif '抗炎' in self.mechanisms or '免疫调节' in self.mechanisms:
            return 'anti_inflammatory'
        elif '肠道菌群' in self.mechanisms or '益生菌' in self.mechanisms:
            return 'microbiome'
        elif '胃肠动力' in self.mechanisms:
            return 'motility'
        else:
            return 'combined'
    
    def get_effectiveness_score(self) -> float:
        """计算综合有效性评分"""
        return (
            self.outcome.get('效果', 0) * 0.4 +
            (1 - self.outcome.get('副作用', 0)) * 0.3 +
            self.outcome.get('满意度', 0) * 0.3
        )

class FSMReplayBuffer:
    """FSM路径经验缓冲器"""
    def __init__(self, max_size: int = 10000):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
        
    def add_experience(self, state: FSMState, path: FSMPath, reward: float):
        """添加经验"""
        experience = {
            'state': state,
            'path': path,
            'reward': reward,
            'timestamp': datetime.now()
        }
        self.buffer.append(experience)
    
    def sample_batch(self, batch_size: int = 32) -> List[Dict]:
        """采样批次"""
        return random.sample(list(self.buffer), min(batch_size, len(self.buffer)))
    
    def get_path_statistics(self) -> Dict:
        """获取路径统计信息"""
        stats = defaultdict(list)
        
        for exp in self.buffer:
            mechanism_type = exp['path'].get_mechanism_type()
            reward = exp['reward']
            stats[mechanism_type].append(reward)
        
        result = {}
        for mech_type, rewards in stats.items():
            result[mech_type] = {
                'count': len(rewards),
                'mean_reward': np.mean(rewards),
                'std_reward': np.std(rewards),
                'success_rate': sum(r > 0.7 for r in rewards) / len(rewards)
            }
        
        return result

# ==================== 主应用 ====================

def main():
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Advanced Strategy Inductor</h1>
        <p>完整Transformer策略归纳器</p>
        <p>FSM + ReplayBuffer + Transformer + 策略融合</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 初始化session state
    if 'replay_buffer' not in st.session_state:
        st.session_state.replay_buffer = FSMReplayBuffer()
        st.session_state.rule_engine = TransformerRuleEngine()
        st.session_state.policy_initializer = StrategicPolicyInitializer()
        st.session_state.training_history = []
    
    # 侧边栏控制
    st.sidebar.markdown("## 🎛️ 系统控制")
    
    mode = st.sidebar.selectbox(
        "选择模式",
        ["📊 数据收集", "🧠 Transformer训练", "🎯 策略应用", "📈 性能分析"]
    )
    
    if mode == "📊 数据收集":
        data_collection_interface()
    elif mode == "🧠 Transformer训练":
        transformer_training_interface()
    elif mode == "🎯 策略应用":
        strategy_application_interface()
    else:
        performance_analysis_interface()

def data_collection_interface():
    """数据收集界面"""
    st.markdown("## 📊 FSM路径数据收集")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 患者状态输入")
        
        symptoms = {}
        st.markdown("**症状评分 (0-10分)**")
        
        symptoms['腹痛'] = st.slider("腹痛", 0, 10, 5)
        symptoms['腹泻'] = st.slider("腹泻", 0, 10, 3)
        symptoms['便秘'] = st.slider("便秘", 0, 10, 2)
        symptoms['腹胀'] = st.slider("腹胀", 0, 10, 6)
        symptoms['焦虑'] = st.slider("焦虑", 0, 10, 7)
        symptoms['抑郁'] = st.slider("抑郁", 0, 10, 4)
        
        context = {}
        context['年龄'] = st.number_input("年龄", 18, 80, 35)
        context['性别'] = 0 if st.selectbox("性别", ["女", "男"]) == "女" else 1
        context['病程'] = st.number_input("病程(月)", 1, 120, 12)
        context['严重程度'] = st.slider("严重程度", 1, 10, 5)
        context['既往史'] = 0 if st.selectbox("既往史", ["无", "有"]) == "无" else 1
    
    with col2:
        st.markdown("### 路径选择与结果")
        
        mechanisms = st.multiselect(
            "选择应用的机制",
            ['心理调节', '抗炎', '肠道菌群', '胃肠动力', '抗焦虑', '免疫调节', '益生菌'],
            default=['心理调节', '抗炎']
        )
        
        outcome = {}
        outcome['效果'] = st.slider("治疗效果", 0.0, 1.0, 0.8, 0.05)
        outcome['副作用'] = st.slider("副作用程度", 0.0, 1.0, 0.2, 0.05)
        outcome['满意度'] = st.slider("患者满意度", 0.0, 1.0, 0.85, 0.05)
        
        if st.button("💾 添加到经验库", type="primary"):
            state = FSMState(symptoms, context, datetime.now().timestamp())
            path = FSMPath(f"path_{len(st.session_state.replay_buffer.buffer)}", 
                          mechanisms, outcome)
            reward = path.get_effectiveness_score()
            
            st.session_state.replay_buffer.add_experience(state, path, reward)
            st.success(f"✅ 成功添加经验！奖励评分: {reward:.3f}")
    
    # 显示经验库状态
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="transformer-box">
            <h3>{buffer_size}</h3>
            <p>总经验数</p>
        </div>
        """, unsafe_allow_html=True)
    
    if buffer_size > 0:
        stats = st.session_state.replay_buffer.get_path_statistics()
        avg_reward = np.mean([exp['reward'] for exp in st.session_state.replay_buffer.buffer])
        
        with col2:
            best_mechanism = max(stats.items(), key=lambda x: x[1]['mean_reward'], 
                               default=('无', {'mean_reward': 0}))
            st.markdown(f"""
            <div class="transformer-box">
                <h4>{best_mechanism[0]}</h4>
                <p>最佳机制</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="transformer-box">
                <h3>{avg_reward:.3f}</h3>
                <p>平均奖励</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            success_count = sum(1 for exp in st.session_state.replay_buffer.buffer 
                              if exp['reward'] > 0.7)
            success_rate = success_count / buffer_size
            st.markdown(f"""
            <div class="transformer-box">
                <h3>{success_rate:.1%}</h3>
                <p>成功率</p>
            </div>
            """, unsafe_allow_html=True)

def transformer_training_interface():
    """Transformer训练界面"""
    st.markdown("## 🧠 Transformer规则学习")
    
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    if buffer_size < 10:
        st.warning(f"⚠️ 经验数据不足！当前: {buffer_size}, 需要至少: 10")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎛️ 训练参数")
        
        epochs = st.slider("训练轮数", 5, 100, 20)
        batch_size = st.slider("批次大小", 8, 64, 16)
        learning_rate = st.selectbox("学习率", [0.001, 0.0005, 0.0001], index=1)
        
        if st.button("🚀 开始Transformer训练", type="primary"):
            # 准备数据
            experiences = list(st.session_state.replay_buffer.buffer)
            dataset = PathDataset(experiences)
            dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
            
            # 训练模型
            model = st.session_state.rule_engine
            optimizer = torch.optim.Adam(model.parameters(), lr=learning_rate)
            
            # 训练进度
            progress_bar = st.progress(0)
            loss_history = []
            
            model.train()
            for epoch in range(epochs):
                epoch_losses = []
                
                for batch in dataloader:
                    state_batch = batch['state']
                    path_batch = batch['path_type'].flatten()
                    reward_batch = batch['reward'].flatten()
                    
                    # 前向传播
                    path_scores, effect_scores = model(state_batch)
                    
                    # 损失计算
                    path_loss = F.cross_entropy(path_scores, path_batch)
                    effect_loss = F.mse_loss(effect_scores.flatten(), reward_batch)
                    total_loss = path_loss + effect_loss
                    
                    # 反向传播
                    optimizer.zero_grad()
                    total_loss.backward()
                    optimizer.step()
                    
                    epoch_losses.append(total_loss.item())
                
                avg_loss = np.mean(epoch_losses)
                loss_history.append(avg_loss)
                progress_bar.progress((epoch + 1) / epochs)
            
            st.session_state.training_history.extend(loss_history)
            st.success("✅ Transformer训练完成！")
    
    with col2:
        st.markdown("### 📊 训练状态")
        
        if st.session_state.training_history:
            # 损失曲线
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                y=st.session_state.training_history,
                mode='lines',
                name='训练损失',
                line=dict(color='#FF6B6B')
            ))
            fig.update_layout(
                title="Transformer训练损失曲线",
                xaxis_title="训练步数",
                yaxis_title="损失值",
                height=300
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 提取和显示规则
    if buffer_size >= 10:
        st.markdown("### 🎯 学习到的策略规则")
        
        # 创建示例状态进行规则提取
        sample_states = []
        for exp in random.sample(list(st.session_state.replay_buffer.buffer), 
                                min(10, buffer_size)):
            sample_states.append(exp['state'].to_vector())
        
        if sample_states:
            state_tensor = torch.FloatTensor(np.array(sample_states))
            rules = st.session_state.rule_engine.extract_rules(state_tensor)
            
            # 更新策略初始化器
            st.session_state.policy_initializer.update_from_rules(rules)
            
            # 显示规则
            rule_cols = st.columns(2)
            
            with rule_cols[0]:
                st.markdown("**路径偏好规则**")
                for key, value in rules.items():
                    if key.startswith('偏好_'):
                        path_name = key.replace('偏好_', '')
                        confidence = "高" if value > 0.3 else "中" if value > 0.15 else "低"
                        st.markdown(f"""
                        <div class="rule-box">
                            <strong>{path_name}</strong><br>
                            偏好度: {value:.3f} ({confidence})
                        </div>
                        """, unsafe_allow_html=True)
            
            with rule_cols[1]:
                st.markdown("**效果预测规则**")
                expected_effect = rules.get('预期效果', 0)
                effect_level = "优秀" if expected_effect > 0.8 else "良好" if expected_effect > 0.6 else "一般"
                
                st.markdown(f"""
                <div class="rule-box">
                    <strong>整体预期效果</strong><br>
                    评分: {expected_effect:.3f} ({effect_level})
                </div>
                """, unsafe_allow_html=True)

def strategy_application_interface():
    """策略应用界面"""
    st.markdown("## 🎯 智能策略应用")
    
    if not hasattr(st.session_state.policy_initializer, 'path_preferences') or \
       not st.session_state.policy_initializer.path_preferences:
        st.warning("⚠️ 请先进行Transformer训练以获得策略知识！")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 👤 新患者状态")
        
        patient_state = {}
        patient_state['腹痛'] = st.slider("腹痛程度", 0, 10, 6)
        patient_state['腹泻'] = st.slider("腹泻频率", 0, 10, 7)
        patient_state['焦虑'] = st.slider("焦虑水平", 0, 10, 8)
        patient_state['炎症'] = st.slider("炎症标志物", 0, 10, 4)
        patient_state['菌群失调'] = st.slider("菌群失调", 0, 10, 6)
        
        if st.button("🎯 生成AI策略", type="primary"):
            strategy = st.session_state.policy_initializer.get_initial_strategy(patient_state)
            st.session_state.current_strategy = strategy
            st.session_state.current_patient = patient_state
    
    with col2:
        st.markdown("### 🧠 AI推荐策略")
        
        if 'current_strategy' in st.session_state:
            strategy = st.session_state.current_strategy
            
            st.markdown(f"""
            <div class="attention-box">
                <h4>🎯 主推荐路径</h4>
                <h3>{strategy['primary_path']}</h3>
                <p>策略信心度: {strategy['confidence']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("**🔄 备用路径**")
            for i, backup_path in enumerate(strategy['backup_paths'], 1):
                st.markdown(f"• 备选 {i}: {backup_path}")
            
            # 路径偏好分析
            preferences = st.session_state.policy_initializer.path_preferences
            
            if preferences:
                paths = list(preferences.keys())
                scores = list(preferences.values())
                
                fig = go.Figure(go.Bar(
                    x=paths,
                    y=scores,
                    text=[f'{s:.3f}' for s in scores],
                    textposition='auto',
                    marker_color='lightblue'
                ))
                
                fig.update_layout(
                    title="Transformer学习的路径偏好",
                    xaxis_title="机制路径",
                    yaxis_title="偏好评分",
                    height=400
                )
                
                st.plotly_chart(fig, use_container_width=True)

def performance_analysis_interface():
    """性能分析界面"""
    st.markdown("## 📈 Transformer性能分析")
    
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    if buffer_size < 5:
        st.warning("⚠️ 数据不足，无法进行性能分析")
        return
    
    # 总体性能指标
    all_rewards = [exp['reward'] for exp in st.session_state.replay_buffer.buffer]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_reward = np.mean(all_rewards)
        st.markdown(f"""
        <div class="transformer-box">
            <h3>{avg_reward:.3f}</h3>
            <p>平均效果</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        success_rate = sum(1 for r in all_rewards if r > 0.7) / len(all_rewards)
        st.markdown(f"""
        <div class="transformer-box">
            <h3>{success_rate:.1%}</h3>
            <p>成功率</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.session_state.training_history:
            last_loss = st.session_state.training_history[-1]
            st.markdown(f"""
            <div class="transformer-box">
                <h3>{last_loss:.4f}</h3>
                <p>最终损失</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col4:
        model_params = sum(p.numel() for p in st.session_state.rule_engine.parameters())
        st.markdown(f"""
        <div class="transformer-box">
            <h3>{model_params:,}</h3>
            <p>模型参数数</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 训练历史可视化
    if st.session_state.training_history:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=st.session_state.training_history,
            mode='lines+markers',
            name='训练损失',
            line=dict(color='purple', width=2)
        ))
        
        fig.update_layout(
            title="Transformer学习曲线",
            xaxis_title="训练轮次",
            yaxis_title="损失值",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main() 