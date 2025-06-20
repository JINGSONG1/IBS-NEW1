#!/usr/bin/env python3
"""
🏆 IBS-RL Mini-Challenge - IBS强化学习挑战赛
社群飞轮驱动，提供baseline + 数据生成器
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import random

# 页面配置
st.set_page_config(
    page_title="🏆 IBS-RL Challenge",
    page_icon="🏆",
    layout="wide"
)

class IBSRLChallenge:
    """IBS强化学习挑战赛管理器"""
    
    def __init__(self):
        self.challenge_tracks = {
            "track1": {
                "name": "IBS亚型分类挑战",
                "description": "基于症状数据准确分类IBS-D/C/M/U",
                "metric": "准确率",
                "baseline_score": 0.72,
                "data_size": 1000
            },
            "track2": {
                "name": "治疗效果预测挑战", 
                "description": "预测不同治疗方案对患者的效果",
                "metric": "MAE",
                "baseline_score": 0.15,
                "data_size": 800
            },
            "track3": {
                "name": "个性化推荐挑战",
                "description": "为患者推荐最适合的治疗路径",
                "metric": "NDCG@5",
                "baseline_score": 0.68,
                "data_size": 600
            }
        }
        
        self.leaderboard = self._generate_leaderboard()
    
    def _generate_leaderboard(self):
        """生成排行榜数据"""
        teams = [
            "MedAI_Team", "DeepDoc", "HealthRL", "SmartCare", "AIPhysician",
            "MedTech_Pro", "ClinicalAI", "DigitalMD", "BioIntelligence", "CareBot"
        ]
        
        leaderboard_data = []
        
        for track_id, track_info in self.challenge_tracks.items():
            for i, team in enumerate(teams):
                # 模拟不同团队的表现
                if track_info["metric"] in ["准确率", "NDCG@5"]:
                    # 越高越好的指标
                    base_score = track_info["baseline_score"]
                    variation = np.random.normal(0, 0.05)
                    score = max(0, min(1, base_score + variation + (len(teams)-i)*0.01))
                else:
                    # 越低越好的指标（如MAE）
                    base_score = track_info["baseline_score"]
                    variation = np.random.normal(0, 0.02)
                    score = max(0.01, base_score - variation - (len(teams)-i)*0.005)
                
                leaderboard_data.append({
                    'track': track_id,
                    'team': team,
                    'score': score,
                    'rank': i + 1,
                    'submission_time': datetime.now() - timedelta(days=random.randint(1, 30)),
                    'method': random.choice(['Transformer', 'LSTM+DQN', 'Graph Neural Network', 
                                           'Ensemble', 'Meta-Learning', 'Multi-Task Learning'])
                })
        
        return pd.DataFrame(leaderboard_data)
    
    def generate_baseline_model_code(self, track_id: str) -> str:
        """生成baseline模型代码"""
        
        if track_id == "track1":
            return """
# IBS亚型分类 Baseline Model
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

class IBSClassificationBaseline:
    def __init__(self):
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.feature_names = [
            'abdominal_pain', 'diarrhea_freq', 'constipation_days', 
            'bloating', 'anxiety_level', 'depression_score'
        ]
    
    def preprocess_data(self, X):
        # 标准化特征
        X_norm = (X - X.mean()) / X.std()
        return X_norm.fillna(0)
    
    def train(self, X_train, y_train):
        X_processed = self.preprocess_data(X_train)
        self.model.fit(X_processed, y_train)
    
    def predict(self, X_test):
        X_processed = self.preprocess_data(X_test)
        return self.model.predict(X_processed)
    
    def predict_proba(self, X_test):
        X_processed = self.preprocess_data(X_test)
        return self.model.predict_proba(X_processed)

# 使用示例
# baseline = IBSClassificationBaseline()
# baseline.train(X_train, y_train)
# predictions = baseline.predict(X_test)
# accuracy = accuracy_score(y_test, predictions)
"""
        
        elif track_id == "track2":
            return """
# 治疗效果预测 Baseline Model
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

class TreatmentEffectBaseline:
    def __init__(self):
        self.model = LinearRegression()
        self.feature_names = [
            'abdominal_pain', 'anxiety_level', 'severity',
            'treatment_psychological', 'treatment_antiinflammatory',
            'treatment_microbiome', 'age', 'gender'
        ]
    
    def create_features(self, symptoms, treatments, demographics):
        # 组合特征工程
        features = []
        
        # 基础症状特征
        features.extend(symptoms)
        
        # 治疗特征
        features.extend(treatments)
        
        # 人口统计学特征
        features.extend(demographics)
        
        # 交互特征：症状 × 治疗
        for i, symptom in enumerate(symptoms):
            for j, treatment in enumerate(treatments):
                features.append(symptom * treatment)
        
        return np.array(features)
    
    def train(self, X_train, y_train):
        self.model.fit(X_train, y_train)
    
    def predict(self, X_test):
        predictions = self.model.predict(X_test)
        return np.clip(predictions, 0, 1)  # 限制在[0,1]范围

# 使用示例
# baseline = TreatmentEffectBaseline()
# baseline.train(X_train, y_train)
# predictions = baseline.predict(X_test)
# mae = mean_absolute_error(y_test, predictions)
"""
        
        else:  # track3
            return """
# 个性化推荐 Baseline Model
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

class PersonalizedRecommendationBaseline:
    def __init__(self):
        self.patient_profiles = None
        self.treatment_effects = None
        self.similarity_threshold = 0.7
    
    def fit(self, patient_data, treatment_outcomes):
        self.patient_profiles = patient_data
        self.treatment_effects = treatment_outcomes
    
    def find_similar_patients(self, target_patient, top_k=5):
        # 计算相似度
        similarities = cosine_similarity(
            target_patient.reshape(1, -1),
            self.patient_profiles
        )[0]
        
        # 找到最相似的患者
        similar_indices = np.argsort(similarities)[::-1][:top_k]
        return similar_indices, similarities[similar_indices]
    
    def recommend_treatments(self, target_patient, top_k=5):
        similar_indices, similarities = self.find_similar_patients(target_patient)
        
        # 基于相似患者的治疗效果进行推荐
        treatment_scores = {}
        
        for idx, sim in zip(similar_indices, similarities):
            patient_outcomes = self.treatment_effects[idx]
            for treatment, effect in patient_outcomes.items():
                if treatment not in treatment_scores:
                    treatment_scores[treatment] = 0
                treatment_scores[treatment] += effect * sim
        
        # 排序推荐
        sorted_treatments = sorted(treatment_scores.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        return sorted_treatments[:top_k]

# 使用示例
# baseline = PersonalizedRecommendationBaseline()
# baseline.fit(patient_profiles, treatment_outcomes)
# recommendations = baseline.recommend_treatments(new_patient)
"""
    
    def generate_challenge_data(self, track_id: str, n_samples: int = 1000):
        """生成挑战赛数据"""
        np.random.seed(42)
        
        # 基础患者特征
        data = {
            'patient_id': [f'P_{i:05d}' for i in range(n_samples)],
            'abdominal_pain': np.clip(np.random.normal(6, 2, n_samples), 0, 10),
            'diarrhea_freq': np.clip(np.random.normal(4, 2.5, n_samples), 0, 10),
            'constipation_days': np.clip(np.random.normal(3, 2.8, n_samples), 0, 10),
            'bloating': np.clip(np.random.normal(6, 2, n_samples), 0, 10),
            'anxiety_level': np.clip(np.random.normal(5, 2.5, n_samples), 0, 10),
            'depression_score': np.clip(np.random.normal(4, 2.8, n_samples), 0, 10),
            'age': np.clip(np.random.normal(42, 15, n_samples), 18, 80),
            'gender': np.random.choice([0, 1], n_samples, p=[0.7, 0.3]),
            'severity': np.clip(np.random.beta(2, 3, n_samples) * 9 + 1, 1, 10)
        }
        
        df = pd.DataFrame(data)
        
        if track_id == "track1":
            # 添加IBS亚型标签
            labels = []
            for _, row in df.iterrows():
                if row['diarrhea_freq'] > 6 and row['constipation_days'] < 3:
                    labels.append('IBS-D')
                elif row['constipation_days'] > 6 and row['diarrhea_freq'] < 3:
                    labels.append('IBS-C')
                elif row['diarrhea_freq'] > 4 and row['constipation_days'] > 4:
                    labels.append('IBS-M')
                else:
                    labels.append('IBS-U')
            df['ibs_subtype'] = labels
            
        elif track_id == "track2":
            # 添加治疗效果数据
            treatments = ['psychological', 'antiinflammatory', 'microbiome', 'motility']
            for treatment in treatments:
                base_effect = 0.6 + np.random.normal(0, 0.1, n_samples)
                
                # 基于患者特征调整效果
                if treatment == 'psychological':
                    effect_boost = (df['anxiety_level'] - 5) * 0.05
                elif treatment == 'antiinflammatory':
                    effect_boost = (df['abdominal_pain'] - 5) * 0.04
                elif treatment == 'microbiome':
                    effect_boost = (df['diarrhea_freq'] - 3) * 0.03
                else:
                    effect_boost = (df['constipation_days'] - 3) * 0.04
                
                df[f'effect_{treatment}'] = np.clip(base_effect + effect_boost, 0, 1)
                
        elif track_id == "track3":
            # 添加推荐相关数据
            treatments = ['psychological', 'antiinflammatory', 'microbiome', 'motility', 'combined']
            for treatment in treatments:
                # 生成推荐评分
                relevance = np.random.beta(2, 3, n_samples)
                df[f'relevance_{treatment}'] = relevance
        
        return df

def main():
    st.markdown("# 🏆 IBS-RL Mini-Challenge")
    st.markdown("IBS强化学习挑战赛 - 社群驱动的医疗AI竞赛平台")
    
    # 创建挑战赛实例
    if 'challenge' not in st.session_state:
        st.session_state.challenge = IBSRLChallenge()
    
    challenge = st.session_state.challenge
    
    # 主导航
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏁 挑战赛概览", "📊 排行榜", "💻 Baseline代码", "📁 数据下载", "🤝 社群交流"])
    
    with tab1:
        st.markdown("### 🏁 挑战赛概览")
        
        # 挑战赛统计
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("参赛团队", "127", delta="+23")
        with col2:
            st.metric("提交次数", "1,845", delta="+156")
        with col3:
            st.metric("数据下载", "3,247", delta="+89")
        with col4:
            st.metric("社群成员", "892", delta="+45")
        
        # 赛道介绍
        st.markdown("### 🎯 挑战赛道")
        
        for track_id, track_info in challenge.challenge_tracks.items():
            with st.expander(f"🏆 {track_info['name']}", expanded=True):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**描述**: {track_info['description']}")
                    st.markdown(f"**评估指标**: {track_info['metric']}")
                    st.markdown(f"**数据规模**: {track_info['data_size']} 样本")
                
                with col2:
                    st.markdown(f"**Baseline成绩**")
                    st.metric(track_info['metric'], f"{track_info['baseline_score']:.3f}")
        
        # 时间轴
        st.markdown("### 📅 赛程安排")
        
        timeline_events = [
            {"date": "2024-03-01", "event": "挑战赛启动", "status": "completed"},
            {"date": "2024-03-15", "event": "数据发布", "status": "completed"},
            {"date": "2024-04-01", "event": "Baseline发布", "status": "current"},
            {"date": "2024-05-01", "event": "中期评估", "status": "upcoming"},
            {"date": "2024-06-01", "event": "最终截止", "status": "upcoming"},
            {"date": "2024-06-15", "event": "结果公布", "status": "upcoming"}
        ]
        
        for event in timeline_events:
            if event["status"] == "completed":
                st.success(f"✅ {event['date']}: {event['event']}")
            elif event["status"] == "current":
                st.info(f"🔄 {event['date']}: {event['event']} (进行中)")
            else:
                st.write(f"📅 {event['date']}: {event['event']}")
    
    with tab2:
        st.markdown("### 📊 实时排行榜")
        
        # 赛道选择
        selected_track = st.selectbox(
            "选择赛道",
            options=list(challenge.challenge_tracks.keys()),
            format_func=lambda x: challenge.challenge_tracks[x]['name']
        )
        
        # 获取该赛道的排行榜数据
        track_leaderboard = challenge.leaderboard[
            challenge.leaderboard['track'] == selected_track
        ].sort_values('score', ascending=False)
        
        # 显示排行榜
        st.markdown(f"#### 🏆 {challenge.challenge_tracks[selected_track]['name']} 排行榜")
        
        display_df = track_leaderboard[['rank', 'team', 'score', 'method', 'submission_time']].copy()
        display_df['submission_time'] = display_df['submission_time'].dt.strftime('%Y-%m-%d %H:%M')
        display_df.columns = ['排名', '团队名称', '得分', '方法', '提交时间']
        
        # 高亮前三名
        def highlight_top3(row):
            if row.name < 3:
                return ['background-color: #FFD700' if row.name == 0 else 
                       'background-color: #C0C0C0' if row.name == 1 else
                       'background-color: #CD7F32'] * len(row)
            return [''] * len(row)
        
        st.dataframe(display_df.style.apply(highlight_top3, axis=1), use_container_width=True)
        
        # 成绩分布图
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=track_leaderboard['score'],
            nbinsx=20,
            name='成绩分布',
            marker_color='lightblue'
        ))
        
        fig.update_layout(
            title=f"{challenge.challenge_tracks[selected_track]['name']} 成绩分布",
            xaxis_title=challenge.challenge_tracks[selected_track]['metric'],
            yaxis_title="团队数量"
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.markdown("### 💻 Baseline代码下载")
        
        # 赛道选择
        baseline_track = st.selectbox(
            "选择赛道获取Baseline",
            options=list(challenge.challenge_tracks.keys()),
            format_func=lambda x: challenge.challenge_tracks[x]['name'],
            key="baseline_track"
        )
        
        track_info = challenge.challenge_tracks[baseline_track]
        
        st.markdown(f"#### 🎯 {track_info['name']} Baseline")
        st.markdown(f"**当前Baseline成绩**: {track_info['baseline_score']:.3f} ({track_info['metric']})")
        
        # 生成并显示代码
        baseline_code = challenge.generate_baseline_model_code(baseline_track)
        
        st.markdown("#### 📝 Baseline代码")
        st.code(baseline_code, language='python')
        
        # 下载按钮
        st.download_button(
            label="📥 下载Baseline代码",
            data=baseline_code,
            file_name=f"baseline_{baseline_track}.py",
            mime="text/plain"
        )
        
        # 使用说明
        st.markdown("#### 📚 使用说明")
        st.info("""
        **快速开始**:
        1. 下载Baseline代码
        2. 下载对应赛道的训练数据
        3. 运行代码获得基础结果
        4. 在此基础上改进模型
        5. 提交改进后的结果
        
        **改进建议**:
        - 特征工程：创建更有意义的特征
        - 模型选择：尝试深度学习、集成学习
        - 数据增强：合成数据、数据平衡
        - 超参数优化：网格搜索、贝叶斯优化
        """)
    
    with tab4:
        st.markdown("### 📁 挑战赛数据下载")
        
        # 数据统计
        st.markdown("#### 📊 数据集概览")
        
        for track_id, track_info in challenge.challenge_tracks.items():
            with st.expander(f"📁 {track_info['name']} 数据集"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown(f"**样本数量**: {track_info['data_size']}")
                    st.markdown(f"**特征维度**: 10-15维")
                    st.markdown(f"**数据格式**: CSV")
                
                with col2:
                    if st.button(f"🔄 生成{track_info['name']}数据", key=f"gen_{track_id}"):
                        with st.spinner("正在生成数据..."):
                            data = challenge.generate_challenge_data(track_id, track_info['data_size'])
                            st.session_state[f'data_{track_id}'] = data
                        st.success("✅ 数据生成完成！")
                
                # 显示生成的数据
                if f'data_{track_id}' in st.session_state:
                    data = st.session_state[f'data_{track_id}']
                    
                    st.markdown("**数据预览**:")
                    st.dataframe(data.head(10))
                    
                    # 下载按钮
                    csv_data = data.to_csv(index=False)
                    st.download_button(
                        label=f"📥 下载{track_info['name']}数据",
                        data=csv_data,
                        file_name=f"challenge_{track_id}_data.csv",
                        mime="text/csv",
                        key=f"download_{track_id}"
                    )
        
        # 数据使用协议
        st.markdown("#### 📜 数据使用协议")
        st.warning("""
        **重要提醒**:
        - 数据仅限挑战赛使用
        - 不得用于商业目的
        - 不得二次分发
        - 比赛结束后请删除数据
        - 遵守数据隐私保护规定
        """)
    
    with tab5:
        st.markdown("### 🤝 社群交流")
        
        # 社群统计
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("论坛帖子", "234", delta="+12")
        with col2:
            st.metric("技术问答", "89", delta="+5")
        with col3:
            st.metric("代码分享", "67", delta="+8")
        
        # 最新动态
        st.markdown("#### 📢 最新动态")
        
        recent_posts = [
            {"time": "2小时前", "user": "DeepDoc", "content": "分享一个特征工程的小技巧，症状交互特征很有效！", "likes": 23},
            {"time": "5小时前", "user": "HealthRL", "content": "有人尝试过Transformer架构吗？我在Track1上有不错效果", "likes": 18},
            {"time": "1天前", "user": "MedAI_Team", "content": "发布了改进的Baseline代码，欢迎大家试用", "likes": 45},
            {"time": "2天前", "user": "SmartCare", "content": "关于数据不平衡问题的解决方案讨论", "likes": 31},
            {"time": "3天前", "user": "ClinicalAI", "content": "Meta-Learning在小样本学习中的应用心得", "likes": 28}
        ]
        
        for post in recent_posts:
            st.markdown(f"""
            <div style="border-left: 3px solid #4CAF50; padding: 10px; margin: 10px 0; background-color: #f9f9f9;">
                <strong>{post['user']}</strong> · {post['time']}<br>
                {post['content']}<br>
                <small>👍 {post['likes']} 点赞</small>
            </div>
            """, unsafe_allow_html=True)
        
        # 加入社群
        st.markdown("#### 🔗 加入我们")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            **微信群**  
            扫码加入技术交流群  
            🔗 [二维码]
            """)
        
        with col2:
            st.markdown("""
            **论坛**  
            深度技术讨论  
            🔗 forum.ibsrl.org
            """)
        
        with col3:
            st.markdown("""
            **GitHub**  
            代码共享仓库  
            🔗 github.com/ibsrl-challenge
            """)
    
    # 页脚信息
    st.markdown("---")
    st.markdown("""
    ### 🎖️ 挑战赛奖励
    
    **🥇 冠军奖**: ¥50,000 + Nature Medicine推荐发表机会  
    **🥈 亚军奖**: ¥30,000 + 顶会论文推荐  
    **🥉 季军奖**: ¥20,000 + 实习/工作推荐  
    **🏆 优秀奖**: 纪念品 + 证书 + 社群荣誉
    
    **主办方**: IBS-RL研究联盟 | **技术支持**: AI医疗开源社区
    """)

if __name__ == "__main__":
    main() 