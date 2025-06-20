#!/usr/bin/env python3
"""
🧠 Super Strategy Inductor - 超强策略归纳器
AI Agent学习"什么机制路径更好"的规则归纳系统
FSM + ReplayBuffer + Transformer归纳器 + 策略融合
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
from plotly.subplots import make_subplots
import json
import pickle
from datetime import datetime, timedelta
from collections import defaultdict, deque
import random
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="🧠 Super Strategy Inductor",
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
.metrics-box {
    background: linear-gradient(45deg, #f093fb 0%, #f5576c 100%);
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
.path-score {
    background: linear-gradient(90deg, #ffecd2 0%, #fcb69f 100%);
    padding: 0.8rem;
    border-radius: 8px;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

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
            self.context.get('年龄', 35) / 100,  # 归一化
            self.context.get('性别', 0),  # 0=女, 1=男
            self.context.get('病程', 12) / 120,  # 归一化月数
            self.context.get('严重程度', 5) / 10,  # 归一化
            self.context.get('既往史', 0)  # 0=无, 1=有
        ]
        vector.extend(context_vector)
        
        return np.array(vector, dtype=np.float32)

class FSMPath:
    """FSM路径表示"""
    def __init__(self, path_id: str, mechanisms: List[str], outcome: Dict):
        self.path_id = path_id
        self.mechanisms = mechanisms  # ['心理调节', '抗炎', '肠道菌群']
        self.outcome = outcome  # {'效果': 0.85, '副作用': 0.1, '满意度': 0.9}
        
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

# ==================== Transformer规则引擎 ====================

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
        """编码路径类型"""
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
            encoded = encoded.unsqueeze(1)  # 添加序列维度
        
        transformed = self.transformer(encoded)
        pooled = transformed.mean(dim=1)  # 池化
        
        # 预测
        path_scores, effect_scores = self.path_predictor(pooled)
        effect_scores = self.effect_predictor(pooled)
        
        return path_scores, effect_scores
    
    def extract_rules(self, state_batch) -> Dict:
        """提取可解释规则"""
        self.eval()
        with torch.no_grad():
            path_scores, effect_scores = self.forward(state_batch)
            
            # 分析注意力权重 (简化版)
            rules = {}
            
            # 基于路径评分的规则
            path_prefs = F.softmax(path_scores, dim=1).mean(dim=0)
            path_types = ['心理路径', '抗炎路径', '菌群路径', '动力路径', '综合路径']
            
            for i, (path_type, score) in enumerate(zip(path_types, path_prefs)):
                rules[f'偏好_{path_type}'] = float(score)
            
            # 基于效果预测的规则
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
        # 基于学习到的规则和患者状态
        if patient_state.get('焦虑', 0) > 7:
            return '心理路径'
        elif patient_state.get('炎症标志物', 0) > 5:
            return '抗炎路径'
        elif patient_state.get('肠道菌群失调', 0) > 6:
            return '菌群路径'
        else:
            # 使用学习到的偏好
            best_path = max(self.path_preferences.items(), 
                          key=lambda x: x[1], default=('综合路径', 0))
            return best_path[0]
    
    def _select_backup_paths(self, patient_state: Dict) -> List[str]:
        """选择备用路径"""
        all_paths = ['心理路径', '抗炎路径', '菌群路径', '动力路径', '综合路径']
        primary = self._select_primary_path(patient_state)
        
        backup = [p for p in all_paths if p != primary]
        
        # 根据偏好排序
        backup.sort(key=lambda p: self.path_preferences.get(p, 0), reverse=True)
        
        return backup[:2]  # 返回top 2备用路径
    
    def _calculate_confidence(self, patient_state: Dict) -> float:
        """计算策略信心度"""
        base_confidence = 0.7
        
        # 基于规则匹配度调整
        if self.learned_rules.get('预期效果', 0) > 0.8:
            base_confidence += 0.2
        
        return min(base_confidence, 0.95)

# ==================== 主应用 ====================

def main():
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Super Strategy Inductor</h1>
        <p>AI Agent超强策略归纳器 - 学习最优机制路径规则</p>
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
        ["📊 数据收集", "🧠 规则学习", "🎯 策略应用", "📈 性能分析"]
    )
    
    if mode == "📊 数据收集":
        data_collection_interface()
    elif mode == "🧠 规则学习":
        rule_learning_interface()
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
        
        # 症状输入
        symptoms = {}
        st.markdown("**症状评分 (0-10分)**")
        
        symptom_cols = st.columns(2)
        with symptom_cols[0]:
            symptoms['腹痛'] = st.slider("腹痛", 0, 10, 5)
            symptoms['腹泻'] = st.slider("腹泻", 0, 10, 3)
            symptoms['便秘'] = st.slider("便秘", 0, 10, 2)
            symptoms['腹胀'] = st.slider("腹胀", 0, 10, 6)
            symptoms['焦虑'] = st.slider("焦虑", 0, 10, 7)
        
        with symptom_cols[1]:
            symptoms['抑郁'] = st.slider("抑郁", 0, 10, 4)
            symptoms['疲劳'] = st.slider("疲劳", 0, 10, 6)
            symptoms['失眠'] = st.slider("失眠", 0, 10, 5)
            symptoms['恶心'] = st.slider("恶心", 0, 10, 3)
            symptoms['食欲不振'] = st.slider("食欲不振", 0, 10, 4)
        
        # 上下文输入
        st.markdown("**患者背景**")
        context = {}
        context['年龄'] = st.number_input("年龄", 18, 80, 35)
        context['性别'] = st.selectbox("性别", ["女", "男"])
        context['性别'] = 0 if context['性别'] == "女" else 1
        context['病程'] = st.number_input("病程(月)", 1, 120, 12)
        context['严重程度'] = st.slider("严重程度", 1, 10, 5)
        context['既往史'] = st.selectbox("既往史", ["无", "有"])
        context['既往史'] = 0 if context['既往史'] == "无" else 1
    
    with col2:
        st.markdown("### 路径选择与结果")
        
        # 路径输入
        st.markdown("**机制路径**")
        mechanisms = st.multiselect(
            "选择应用的机制",
            ['心理调节', '抗炎', '肠道菌群', '胃肠动力', '抗焦虑', '免疫调节', '益生菌'],
            default=['心理调节', '抗炎']
        )
        
        # 结果输入
        st.markdown("**治疗结果**")
        outcome = {}
        outcome['效果'] = st.slider("治疗效果", 0.0, 1.0, 0.8, 0.05)
        outcome['副作用'] = st.slider("副作用程度", 0.0, 1.0, 0.2, 0.05)
        outcome['满意度'] = st.slider("患者满意度", 0.0, 1.0, 0.85, 0.05)
        
        if st.button("💾 添加到经验库", type="primary"):
            # 创建状态和路径
            state = FSMState(symptoms, context, datetime.now().timestamp())
            path = FSMPath(f"path_{len(st.session_state.replay_buffer.buffer)}", 
                          mechanisms, outcome)
            
            # 计算奖励
            reward = path.get_effectiveness_score()
            
            # 添加到经验库
            st.session_state.replay_buffer.add_experience(state, path, reward)
            
            st.success(f"✅ 成功添加经验！奖励评分: {reward:.3f}")
    
    # 显示当前经验库状态
    st.markdown("### 📈 经验库状态")
    
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metrics-box">
            <h3>{buffer_size}</h3>
            <p>总经验数</p>
        </div>
        """, unsafe_allow_html=True)
    
    if buffer_size > 0:
        stats = st.session_state.replay_buffer.get_path_statistics()
        
        with col2:
            best_mechanism = max(stats.items(), key=lambda x: x[1]['mean_reward'], 
                               default=('无', {'mean_reward': 0}))
            st.markdown(f"""
            <div class="metrics-box">
                <h3>{best_mechanism[0]}</h3>
                <p>最佳机制类型</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            avg_reward = np.mean([exp['reward'] for exp in st.session_state.replay_buffer.buffer])
            st.markdown(f"""
            <div class="metrics-box">
                <h3>{avg_reward:.3f}</h3>
                <p>平均奖励</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            success_count = sum(1 for exp in st.session_state.replay_buffer.buffer 
                              if exp['reward'] > 0.7)
            success_rate = success_count / buffer_size
            st.markdown(f"""
            <div class="metrics-box">
                <h3>{success_rate:.1%}</h3>
                <p>成功率</p>
            </div>
            """, unsafe_allow_html=True)

def rule_learning_interface():
    """规则学习界面"""
    st.markdown("## 🧠 策略规则学习")
    
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    if buffer_size < 10:
        st.warning(f"⚠️ 经验数据不足！当前: {buffer_size}, 需要至少: 10")
        return
    
    # 显示学习统计
    stats = st.session_state.replay_buffer.get_path_statistics()
    
    st.markdown("### 📊 机制路径效果分析")
    
    if stats:
        mechanisms = list(stats.keys())
        mean_rewards = [stats[m]['mean_reward'] for m in mechanisms]
        success_rates = [stats[m]['success_rate'] for m in mechanisms]
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 平均效果对比
            fig = go.Figure(go.Bar(
                x=mechanisms,
                y=mean_rewards,
                text=[f'{r:.3f}' for r in mean_rewards],
                textposition='auto',
                marker_color='lightblue'
            ))
            fig.update_layout(
                title="各机制平均效果",
                yaxis_title="平均奖励",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # 成功率对比
            fig = go.Figure(go.Bar(
                x=mechanisms,
                y=success_rates,
                text=[f'{r:.1%}' for r in success_rates],
                textposition='auto',
                marker_color='lightcoral'
            ))
            fig.update_layout(
                title="各机制成功率",
                yaxis_title="成功率",
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # 归纳规则
    st.markdown("### 🎯 归纳出的策略规则")
    
    if stats:
        # 自动归纳规则
        rules = generate_strategy_rules(stats, st.session_state.replay_buffer.buffer)
        
        for rule_type, rule_content in rules.items():
            st.markdown(f"""
            <div class="rule-box">
                <h4>{rule_type}</h4>
                <p>{rule_content}</p>
            </div>
            """, unsafe_allow_html=True)

def strategy_application_interface():
    """策略应用界面"""
    st.markdown("## 🎯 智能策略应用")
    
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    if buffer_size < 5:
        st.warning("⚠️ 数据不足，无法生成策略建议")
        return
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 👤 新患者状态")
        
        # 新患者输入
        patient_state = {}
        
        st.markdown("**症状评分**")
        patient_state['腹痛'] = st.slider("腹痛程度", 0, 10, 6)
        patient_state['腹泻'] = st.slider("腹泻频率", 0, 10, 7)
        patient_state['焦虑'] = st.slider("焦虑水平", 0, 10, 8)
        patient_state['抑郁'] = st.slider("抑郁程度", 0, 10, 5)
        
        if st.button("🎯 生成智能策略", type="primary"):
            # 生成策略建议
            strategy = generate_patient_strategy(patient_state, st.session_state.replay_buffer.buffer)
            st.session_state.current_strategy = strategy
    
    with col2:
        st.markdown("### 🧠 AI推荐策略")
        
        if 'current_strategy' in st.session_state:
            strategy = st.session_state.current_strategy
            
            # 主要路径
            st.markdown(f"""
            <div class="path-score">
                <h4>🎯 主推荐路径</h4>
                <h3>{strategy['primary_path']}</h3>
                <p>预期效果: {strategy['expected_effect']:.1%}</p>
                <p>信心度: {strategy['confidence']:.1%}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # 理由说明
            st.markdown("**💡 推荐理由**")
            for reason in strategy['reasons']:
                st.info(reason)
            
            # 备选方案
            if strategy.get('alternatives'):
                st.markdown("**🔄 备选方案**")
                for alt in strategy['alternatives']:
                    st.markdown(f"• {alt}")

def performance_analysis_interface():
    """性能分析界面"""
    st.markdown("## 📈 系统性能分析")
    
    buffer_size = len(st.session_state.replay_buffer.buffer)
    
    if buffer_size < 5:
        st.warning("⚠️ 数据不足，无法进行性能分析")
        return
    
    # 总体性能指标
    st.markdown("### 🎯 总体性能指标")
    
    all_rewards = [exp['reward'] for exp in st.session_state.replay_buffer.buffer]
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_reward = np.mean(all_rewards)
        st.markdown(f"""
        <div class="metrics-box">
            <h3>{avg_reward:.3f}</h3>
            <p>平均效果</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        success_rate = sum(1 for r in all_rewards if r > 0.7) / len(all_rewards)
        st.markdown(f"""
        <div class="metrics-box">
            <h3>{success_rate:.1%}</h3>
            <p>成功率</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        std_reward = np.std(all_rewards)
        st.markdown(f"""
        <div class="metrics-box">
            <h3>{std_reward:.3f}</h3>
            <p>效果稳定性</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        max_reward = max(all_rewards)
        st.markdown(f"""
        <div class="metrics-box">
            <h3>{max_reward:.3f}</h3>
            <p>最佳效果</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 时间趋势分析
    st.markdown("### 📈 效果趋势分析")
    
    # 按时间排序的奖励
    sorted_exp = sorted(st.session_state.replay_buffer.buffer, 
                       key=lambda x: x['timestamp'])
    
    rewards_over_time = [exp['reward'] for exp in sorted_exp]
    
    # 计算移动平均
    window_size = min(10, len(rewards_over_time) // 2)
    if window_size > 1:
        moving_avg = []
        for i in range(len(rewards_over_time)):
            start_idx = max(0, i - window_size + 1)
            moving_avg.append(np.mean(rewards_over_time[start_idx:i+1]))
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            y=rewards_over_time,
            mode='markers',
            name='实际效果',
            opacity=0.6
        ))
        fig.add_trace(go.Scatter(
            y=moving_avg,
            mode='lines',
            name=f'移动平均({window_size})',
            line=dict(color='red', width=2)
        ))
        
        fig.update_layout(
            title="治疗效果时间趋势",
            xaxis_title="经验序号",
            yaxis_title="治疗效果",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)

def generate_strategy_rules(stats: Dict, buffer: List) -> Dict:
    """生成策略规则"""
    rules = {}
    
    # 最佳机制识别
    if stats:
        best_mechanism = max(stats.items(), key=lambda x: x[1]['mean_reward'])
        rules["🏆 最优机制路径"] = f"{best_mechanism[0]}表现最佳，平均效果{best_mechanism[1]['mean_reward']:.3f}"
        
        # 高成功率机制
        high_success = [k for k, v in stats.items() if v['success_rate'] > 0.8]
        if high_success:
            rules["✅ 高成功率机制"] = f"{', '.join(high_success)}具有高成功率(>80%)"
        
        # 稳定性分析
        stable_mechanisms = [k for k, v in stats.items() if v['std_reward'] < 0.2]
        if stable_mechanisms:
            rules["🎯 稳定性机制"] = f"{', '.join(stable_mechanisms)}表现稳定，效果波动小"
    
    # 症状特异性规则
    symptom_rules = analyze_symptom_patterns(buffer)
    rules.update(symptom_rules)
    
    return rules

def analyze_symptom_patterns(buffer: List) -> Dict:
    """分析症状模式"""
    rules = {}
    
    # 按症状分组分析
    anxiety_high = [exp for exp in buffer if exp['state'].symptoms.get('焦虑', 0) > 7]
    inflammation_high = [exp for exp in buffer if exp['state'].symptoms.get('腹痛', 0) > 7]
    
    if anxiety_high:
        anxiety_rewards = [exp['reward'] for exp in anxiety_high]
        anxiety_paths = [exp['path'].get_mechanism_type() for exp in anxiety_high]
        
        if anxiety_paths:
            best_for_anxiety = max(set(anxiety_paths), key=anxiety_paths.count)
            rules["🧠 高焦虑患者"] = f"焦虑症状重的患者，{best_for_anxiety}路径效果更好"
    
    if inflammation_high:
        inflam_rewards = [exp['reward'] for exp in inflammation_high]
        inflam_paths = [exp['path'].get_mechanism_type() for exp in inflammation_high]
        
        if inflam_paths:
            best_for_inflam = max(set(inflam_paths), key=inflam_paths.count)
            rules["🔥 高炎症患者"] = f"炎症症状重的患者，{best_for_inflam}路径效果更好"
    
    return rules

def generate_patient_strategy(patient_state: Dict, buffer: List) -> Dict:
    """为新患者生成策略"""
    strategy = {
        'primary_path': '综合路径',
        'expected_effect': 0.7,
        'confidence': 0.8,
        'reasons': [],
        'alternatives': []
    }
    
    # 基于症状的路径选择
    if patient_state.get('焦虑', 0) > 7:
        strategy['primary_path'] = '心理调节路径'
        strategy['reasons'].append("患者焦虑水平较高，心理干预是首选")
    elif patient_state.get('腹痛', 0) > 7:
        strategy['primary_path'] = '抗炎路径'
        strategy['reasons'].append("腹痛症状突出，抗炎治疗可能有效")
    elif patient_state.get('腹泻', 0) > 7:
        strategy['primary_path'] = '肠道菌群路径'
        strategy['reasons'].append("腹泻频繁，肠道菌群调节是关键")
    
    # 基于历史数据调整预期效果
    if buffer:
        similar_cases = find_similar_cases(patient_state, buffer)
        if similar_cases:
            avg_reward = np.mean([case['reward'] for case in similar_cases])
            strategy['expected_effect'] = avg_reward
            strategy['confidence'] = min(0.9, 0.6 + len(similar_cases) * 0.1)
            
            if len(similar_cases) > 3:
                strategy['reasons'].append(f"基于{len(similar_cases)}个相似病例的经验")
    
    # 生成备选方案
    all_paths = ['心理调节路径', '抗炎路径', '肠道菌群路径', '胃肠动力路径']
    strategy['alternatives'] = [p for p in all_paths if p != strategy['primary_path']][:2]
    
    return strategy

def find_similar_cases(patient_state: Dict, buffer: List, threshold: float = 3.0) -> List:
    """找到相似病例"""
    similar_cases = []
    
    for exp in buffer:
        # 计算症状相似度
        distance = 0
        for symptom in ['腹痛', '腹泻', '焦虑', '抑郁']:
            patient_score = patient_state.get(symptom, 0)
            case_score = exp['state'].symptoms.get(symptom, 0)
            distance += abs(patient_score - case_score)
        
        if distance <= threshold:
            similar_cases.append(exp)
    
    return similar_cases

if __name__ == "__main__":
    main() 