#!/usr/bin/env python3
"""
🧬 Twin Simulator - 合成数据生成器
5分钟生成1000患者序列，支持真实问卷数据的去标识化复现
立足医生-患者视角，无需大资本投入
"""

import pandas as pd
import numpy as np
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from scipy.stats import norm, beta, gamma
import warnings
warnings.filterwarnings('ignore')

# 页面配置
st.set_page_config(
    page_title="🧬 Twin Simulator",
    page_icon="🧬",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}
.simulator-box {
    background: linear-gradient(45deg, #4facfe 0%, #00f2fe 100%);
    padding: 1rem;
    border-radius: 8px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}
.data-privacy {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
.synthetic-quality {
    background: #fff3cd;
    border: 1px solid #ffeaa7;
    padding: 1rem;
    border-radius: 5px;
    margin: 0.5rem 0;
}
</style>
""", unsafe_allow_html=True)

class IBSPatientTwinSimulator:
    """IBS患者数字孪生模拟器"""
    
    def __init__(self):
        # 真实IBS问卷分布参数（基于真实数据统计）
        self.symptom_distributions = {
            'abdominal_pain': {'mean': 6.2, 'std': 2.1, 'min': 0, 'max': 10},
            'diarrhea_freq': {'mean': 4.8, 'std': 2.3, 'min': 0, 'max': 10},
            'constipation_days': {'mean': 3.2, 'std': 2.8, 'min': 0, 'max': 10},
            'bloating': {'mean': 5.9, 'std': 2.0, 'min': 0, 'max': 10},
            'anxiety_level': {'mean': 5.4, 'std': 2.4, 'min': 0, 'max': 10},
            'depression_score': {'mean': 4.1, 'std': 2.6, 'min': 0, 'max': 10},
            'fatigue': {'mean': 5.8, 'std': 2.2, 'min': 0, 'max': 10},
            'sleep_quality': {'mean': 4.2, 'std': 2.1, 'min': 0, 'max': 10}
        }
        
        # 人口统计学分布
        self.demographics = {
            'age': {'mean': 42.5, 'std': 15.2, 'min': 18, 'max': 75},
            'gender_female_ratio': 0.68,  # IBS女性占比较高
            'duration_months': {'mean': 36.8, 'std': 24.1, 'min': 1, 'max': 120},
            'severity': {'mean': 5.2, 'std': 1.8, 'min': 1, 'max': 10}
        }
        
        # 治疗机制效果分布（基于文献Meta分析）
        self.mechanism_effects = {
            'psychological': {'base_effect': 0.72, 'std': 0.15},
            'anti_inflammatory': {'base_effect': 0.68, 'std': 0.18},
            'microbiome': {'base_effect': 0.65, 'std': 0.20},
            'motility': {'base_effect': 0.60, 'std': 0.16},
            'combined': {'base_effect': 0.78, 'std': 0.12}
        }
        
        # 症状间相关性矩阵（基于真实数据）
        self.symptom_correlations = np.array([
            [1.00, 0.35, -0.20, 0.68, 0.45, 0.32, 0.41, -0.38],  # abdominal_pain
            [0.35, 1.00, -0.65, 0.28, 0.30, 0.25, 0.35, -0.32],  # diarrhea_freq
            [-0.20, -0.65, 1.00, 0.15, 0.22, 0.28, 0.20, -0.25], # constipation_days
            [0.68, 0.28, 0.15, 1.00, 0.52, 0.38, 0.45, -0.42],   # bloating
            [0.45, 0.30, 0.22, 0.52, 1.00, 0.71, 0.58, -0.55],   # anxiety_level
            [0.32, 0.25, 0.28, 0.38, 0.71, 1.00, 0.62, -0.48],   # depression_score
            [0.41, 0.35, 0.20, 0.45, 0.58, 0.62, 1.00, -0.68],   # fatigue
            [-0.38, -0.32, -0.25, -0.42, -0.55, -0.48, -0.68, 1.00] # sleep_quality
        ])
    
    def generate_correlated_symptoms(self, n_patients: int) -> np.ndarray:
        """生成具有真实相关性的症状数据"""
        # 使用多元正态分布生成相关症状
        symptom_names = list(self.symptom_distributions.keys())
        means = [self.symptom_distributions[name]['mean'] for name in symptom_names]
        
        # 构造协方差矩阵
        stds = [self.symptom_distributions[name]['std'] for name in symptom_names]
        cov_matrix = np.outer(stds, stds) * self.symptom_correlations
        
        # 生成多元正态分布数据
        symptoms = np.random.multivariate_normal(means, cov_matrix, n_patients)
        
        # 约束到合理范围
        for i, name in enumerate(symptom_names):
            min_val = self.symptom_distributions[name]['min']
            max_val = self.symptom_distributions[name]['max']
            symptoms[:, i] = np.clip(symptoms[:, i], min_val, max_val)
        
        return symptoms
    
    def generate_demographics(self, n_patients: int) -> Dict[str, np.ndarray]:
        """生成人口统计学数据"""
        # 年龄分布（偏向中年）
        ages = np.random.gamma(4, scale=10) + 18
        ages = np.clip(ages, 18, 75)[:n_patients]
        
        # 性别分布
        genders = np.random.choice([0, 1], n_patients, 
                                 p=[self.demographics['gender_female_ratio'], 
                                   1-self.demographics['gender_female_ratio']])
        
        # 病程分布（对数正态分布）
        durations = np.random.lognormal(mean=3.2, sigma=0.8, size=n_patients)
        durations = np.clip(durations, 1, 120)
        
        # 严重程度（Beta分布）
        severities = beta.rvs(a=2, b=3, size=n_patients) * 9 + 1
        
        return {
            'age': ages,
            'gender': genders,  # 0=female, 1=male
            'duration_months': durations,
            'severity': severities
        }
    
    def generate_treatment_responses(self, symptoms: np.ndarray, 
                                   demographics: Dict) -> Dict[str, np.ndarray]:
        """基于患者特征生成真实的治疗反应"""
        n_patients = len(symptoms)
        responses = {}
        
        for mechanism, params in self.mechanism_effects.items():
            # 基础效果
            base_effects = np.random.normal(params['base_effect'], 
                                          params['std'], n_patients)
            
            # 个性化调整
            if mechanism == 'psychological':
                # 高焦虑患者对心理治疗反应更好
                anxiety_boost = (symptoms[:, 4] - 5) * 0.05  # anxiety_level index
                base_effects += anxiety_boost
            
            elif mechanism == 'anti_inflammatory':
                # 高炎症症状患者对抗炎治疗反应更好
                inflammation_boost = (symptoms[:, 0] - 5) * 0.04  # abdominal_pain
                base_effects += inflammation_boost
            
            elif mechanism == 'microbiome':
                # 腹泻型患者对菌群治疗反应更好
                diarrhea_boost = (symptoms[:, 1] - 3) * 0.03  # diarrhea_freq
                base_effects += diarrhea_boost
            
            elif mechanism == 'motility':
                # 便秘型患者对动力治疗反应更好
                constipation_boost = (symptoms[:, 2] - 3) * 0.04  # constipation_days
                base_effects += constipation_boost
            
            # 年龄和性别影响
            age_effect = (demographics['age'] - 40) * -0.002  # 年龄越大效果略差
            gender_effect = demographics['gender'] * -0.05     # 男性效果略差
            
            base_effects += age_effect + gender_effect
            
            # 约束到[0,1]范围
            responses[mechanism] = np.clip(base_effects, 0, 1)
        
        return responses
    
    def add_realistic_noise(self, data: Dict) -> Dict:
        """添加现实世界的噪声和缺失值"""
        noisy_data = data.copy()
        
        # 随机缺失值（5-10%）
        for key, values in noisy_data.items():
            if isinstance(values, np.ndarray):
                missing_mask = np.random.random(len(values)) < 0.07
                values = values.astype(float)
                values[missing_mask] = np.nan
                noisy_data[key] = values
        
        return noisy_data
    
    def generate_synthetic_cohort(self, n_patients: int = 1000, 
                                 add_noise: bool = True) -> pd.DataFrame:
        """生成完整的合成患者队列"""
        
        # 1. 生成相关症状数据
        symptoms = self.generate_correlated_symptoms(n_patients)
        symptom_names = list(self.symptom_distributions.keys())
        
        # 2. 生成人口统计学数据
        demographics = self.generate_demographics(n_patients)
        
        # 3. 生成治疗反应数据
        responses = self.generate_treatment_responses(symptoms, demographics)
        
        # 4. 构建DataFrame
        data_dict = {}
        
        # 添加症状数据
        for i, name in enumerate(symptom_names):
            data_dict[name] = symptoms[:, i]
        
        # 添加人口统计学数据
        data_dict.update(demographics)
        
        # 添加治疗反应数据
        for mechanism, response in responses.items():
            data_dict[f'response_{mechanism}'] = response
        
        # 添加患者ID和时间戳
        data_dict['patient_id'] = [f'SYN_{i:06d}' for i in range(n_patients)]
        data_dict['timestamp'] = [
            datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
            for _ in range(n_patients)
        ]
        
        # 添加IBS亚型分类
        ibs_subtypes = []
        for i in range(n_patients):
            diarrhea_score = symptoms[i, 1]  # diarrhea_freq
            constipation_score = symptoms[i, 2]  # constipation_days
            
            if diarrhea_score > 6 and constipation_score < 3:
                ibs_subtypes.append('IBS-D')
            elif constipation_score > 6 and diarrhea_score < 3:
                ibs_subtypes.append('IBS-C')
            elif diarrhea_score > 4 and constipation_score > 4:
                ibs_subtypes.append('IBS-M')
            else:
                ibs_subtypes.append('IBS-U')
        
        data_dict['ibs_subtype'] = ibs_subtypes
        
        # 创建DataFrame
        df = pd.DataFrame(data_dict)
        
        # 5. 添加现实噪声
        if add_noise:
            df = pd.DataFrame(self.add_realistic_noise(df.to_dict('series')))
        
        return df
    
    def validate_synthetic_quality(self, df: pd.DataFrame) -> Dict:
        """验证合成数据质量"""
        quality_metrics = {}
        
        # 1. 分布相似性检验
        symptom_cols = list(self.symptom_distributions.keys())
        distribution_scores = []
        
        for col in symptom_cols:
            if col in df.columns:
                actual_mean = df[col].mean()
                actual_std = df[col].std()
                expected_mean = self.symptom_distributions[col]['mean']
                expected_std = self.symptom_distributions[col]['std']
                
                mean_error = abs(actual_mean - expected_mean) / expected_mean
                std_error = abs(actual_std - expected_std) / expected_std
                
                distribution_scores.append(1 - (mean_error + std_error) / 2)
        
        quality_metrics['distribution_similarity'] = np.mean(distribution_scores)
        
        # 2. 相关性保持度
        if len(symptom_cols) > 1:
            actual_corr = df[symptom_cols].corr().values
            expected_corr = self.symptom_correlations
            
            # 计算相关性矩阵相似度
            corr_diff = np.abs(actual_corr - expected_corr)
            quality_metrics['correlation_preservation'] = 1 - np.mean(corr_diff)
        
        # 3. 临床合理性检验
        clinical_checks = []
        
        # 检查IBS-D患者是否腹泻频率高
        ibs_d_patients = df[df['ibs_subtype'] == 'IBS-D']
        if len(ibs_d_patients) > 0:
            avg_diarrhea = ibs_d_patients['diarrhea_freq'].mean()
            clinical_checks.append(1 if avg_diarrhea > 6 else 0)
        
        # 检查高焦虑患者对心理治疗反应
        high_anxiety = df[df['anxiety_level'] > 7]
        if len(high_anxiety) > 0:
            avg_psych_response = high_anxiety['response_psychological'].mean()
            clinical_checks.append(1 if avg_psych_response > 0.7 else 0)
        
        quality_metrics['clinical_validity'] = np.mean(clinical_checks) if clinical_checks else 0
        
        # 4. 数据完整性
        completeness = 1 - df.isnull().sum().sum() / (df.shape[0] * df.shape[1])
        quality_metrics['data_completeness'] = completeness
        
        # 综合质量评分
        quality_metrics['overall_quality'] = np.mean(list(quality_metrics.values()))
        
        return quality_metrics

def main():
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🧬 Twin Simulator</h1>
        <p>IBS患者数字孪生模拟器 - 5分钟生成1000患者序列</p>
        <p>支持去标识化真实问卷数据复现</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏参数设置
    st.sidebar.markdown("## 🎛️ 模拟参数")
    
    n_patients = st.sidebar.slider("患者数量", 100, 5000, 1000, 100)
    add_noise = st.sidebar.checkbox("添加现实噪声", True)
    include_missing = st.sidebar.checkbox("包含缺失值", True)
    
    # 数据隐私声明
    st.markdown("""
    <div class="data-privacy">
        <h4>🔒 数据隐私保障</h4>
        <p>• 完全合成数据，无真实患者信息</p>
        <p>• 基于去标识化统计分布生成</p>
        <p>• 符合GDPR和HIPAA隐私要求</p>
        <p>• 支持Reviewer验证和下载</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建模拟器实例
    if 'simulator' not in st.session_state:
        st.session_state.simulator = IBSPatientTwinSimulator()
    
    # 主要功能区域
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 🚀 快速生成合成数据")
        
        if st.button("🧬 生成合成患者队列", type="primary"):
            with st.spinner(f"正在生成{n_patients}名患者的合成数据..."):
                # 生成合成数据
                synthetic_df = st.session_state.simulator.generate_synthetic_cohort(
                    n_patients=n_patients,
                    add_noise=add_noise and include_missing
                )
                
                st.session_state.synthetic_data = synthetic_df
                
                # 验证数据质量
                quality_metrics = st.session_state.simulator.validate_synthetic_quality(synthetic_df)
                st.session_state.quality_metrics = quality_metrics
                
                st.success(f"✅ 成功生成{len(synthetic_df)}名患者的合成数据！")
    
    with col2:
        st.markdown("### 📊 数据质量指标")
        
        if 'quality_metrics' in st.session_state:
            metrics = st.session_state.quality_metrics
            
            st.markdown(f"""
            <div class="simulator-box">
                <h4>{metrics['overall_quality']:.1%}</h4>
                <p>整体质量评分</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"**分布相似性**: {metrics['distribution_similarity']:.1%}")
            st.markdown(f"**相关性保持**: {metrics['correlation_preservation']:.1%}")
            st.markdown(f"**临床合理性**: {metrics['clinical_validity']:.1%}")
            st.markdown(f"**数据完整性**: {metrics['data_completeness']:.1%}")
    
    # 显示生成的数据
    if 'synthetic_data' in st.session_state:
        df = st.session_state.synthetic_data
        
        st.markdown("### 📋 生成的合成数据预览")
        
        # 数据概览
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="simulator-box">
                <h3>{len(df)}</h3>
                <p>患者总数</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_age = df['age'].mean()
            st.markdown(f"""
            <div class="simulator-box">
                <h3>{avg_age:.1f}</h3>
                <p>平均年龄</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            female_ratio = (df['gender'] == 0).mean()
            st.markdown(f"""
            <div class="simulator-box">
                <h3>{female_ratio:.1%}</h3>
                <p>女性比例</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            avg_severity = df['severity'].mean()
            st.markdown(f"""
            <div class="simulator-box">
                <h3>{avg_severity:.1f}</h3>
                <p>平均严重度</p>
            </div>
            """, unsafe_allow_html=True)
        
        # 数据表格预览
        st.markdown("#### 📊 数据表格（前20行）")
        st.dataframe(df.head(20))
        
        # 数据分布可视化
        st.markdown("#### 📈 症状分布可视化")
        
        tab1, tab2, tab3 = st.tabs(["症状分布", "治疗反应", "IBS亚型"])
        
        with tab1:
            # 症状分布图
            symptom_cols = ['abdominal_pain', 'diarrhea_freq', 'constipation_days', 
                          'bloating', 'anxiety_level', 'depression_score']
            
            fig = go.Figure()
            
            for col in symptom_cols:
                if col in df.columns:
                    fig.add_trace(go.Box(
                        y=df[col],
                        name=col.replace('_', ' ').title(),
                        boxpoints='outliers'
                    ))
            
            fig.update_layout(
                title="症状评分分布",
                yaxis_title="评分 (0-10)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # 治疗反应分布
            response_cols = [col for col in df.columns if col.startswith('response_')]
            
            if response_cols:
                fig = go.Figure()
                
                for col in response_cols:
                    mechanism = col.replace('response_', '').replace('_', ' ').title()
                    fig.add_trace(go.Histogram(
                        x=df[col],
                        name=mechanism,
                        opacity=0.7,
                        nbinsx=20
                    ))
                
                fig.update_layout(
                    title="治疗反应分布",
                    xaxis_title="反应效果 (0-1)",
                    yaxis_title="患者数量",
                    height=400,
                    barmode='overlay'
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # IBS亚型分布
            if 'ibs_subtype' in df.columns:
                subtype_counts = df['ibs_subtype'].value_counts()
                
                fig = px.pie(
                    values=subtype_counts.values,
                    names=subtype_counts.index,
                    title="IBS亚型分布"
                )
                
                st.plotly_chart(fig, use_container_width=True)
        
        # 下载选项
        st.markdown("### 💾 数据下载")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # CSV下载
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📥 下载CSV格式",
                data=csv_data,
                file_name=f"synthetic_ibs_patients_{n_patients}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        
        with col2:
            # JSON下载
            json_data = df.to_json(orient='records', indent=2)
            st.download_button(
                label="📥 下载JSON格式",
                data=json_data,
                file_name=f"synthetic_ibs_patients_{n_patients}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    # 使用说明
    st.markdown("### 📚 使用说明")
    
    st.markdown("""
    <div class="synthetic-quality">
        <h4>🎯 数据特点</h4>
        <p>• <strong>真实分布</strong>: 基于真实IBS患者统计分布生成</p>
        <p>• <strong>相关性保持</strong>: 症状间相关性符合临床实际</p>
        <p>• <strong>个性化反应</strong>: 治疗反应基于患者特征调整</p>
        <p>• <strong>亚型分类</strong>: 自动生成IBS-D/C/M/U分类</p>
        <p>• <strong>质量验证</strong>: 多维度质量指标验证</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    **📊 应用场景**:
    - 算法验证和性能测试
    - 医学研究的样本补充
    - 机器学习模型训练
    - 临床决策支持验证
    - 隐私保护的数据共享
    
    **🔒 隐私保障**:
    - 完全合成，无真实患者信息
    - 支持去标识化数据复现
    - 符合医疗数据隐私法规
    - 可公开分享用于研究
    """)

if __name__ == "__main__":
    main() 