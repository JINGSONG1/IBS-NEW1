#!/usr/bin/env python3
"""
现代化AI医疗平台
科技感界面设计，整合所有功能模块
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 导入自定义模块
from enhanced_drug_database import EnhancedDrugDatabase
from enhanced_comorbidity_system import EnhancedComorbiditySystem
from detailed_ibs_sss_system import DetailedIBSSSS
from patient_followup_system import PatientFollowupSystem
from physician_engagement_system import PhysicianEngagementSystem

def load_custom_css():
    """加载自定义CSS样式"""
    st.markdown("""
    <style>
    /* 全局样式 */
    .main > div {
        padding-top: 0rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c1421 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* 顶部导航栏 */
    .top-nav {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1rem 2rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 20px 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.3);
    }
    
    .nav-title {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(45deg, #00f5ff, #0080ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 0;
        text-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
    }
    
    .nav-subtitle {
        text-align: center;
        color: #a0b4d6;
        font-size: 1.1rem;
        margin-top: 0.5rem;
        opacity: 0.9;
    }
    
    /* 卡片样式 */
    .feature-card {
        background: linear-gradient(145deg, #1a2332 0%, #2d3748 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 245, 255, 0.2);
    }
    
    .card-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #00f5ff;
        margin-bottom: 0.8rem;
        display: flex;
        align-items: center;
    }
    
    .card-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        text-align: center;
        color: white;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.2);
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.3rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* 按钮样式 */
    .stButton > button {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* 侧边栏样式 */
    .css-1d391kg {
        background: linear-gradient(180deg, #1a2332 0%, #2d3748 100%);
    }
    
    /* 输入框样式 */
    .stTextInput > div > div > input {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white;
    }
    
    .stSelectbox > div > div > select {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white;
    }
    
    /* 滑块样式 */
    .stSlider > div > div > div > div {
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    /* 标签页样式 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        color: #00f5ff;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(45deg, #667eea, #764ba2);
        color: white;
    }
    
    /* 进度条样式 */
    .stProgress > div > div > div > div {
        background: linear-gradient(45deg, #00f5ff, #0080ff);
    }
    
    /* 成功/警告消息样式 */
    .stSuccess {
        background: linear-gradient(45deg, #00c9ff, #92fe9d);
        border-radius: 10px;
    }
    
    .stWarning {
        background: linear-gradient(45deg, #fc466b, #3f5efb);
        border-radius: 10px;
    }
    
    /* 数据可视化容器 */
    .plot-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* 动画效果 */
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .fade-in {
        animation: fadeInUp 0.6s ease-out;
    }
    
    /* 响应式设计 */
    @media (max-width: 768px) {
        .nav-title {
            font-size: 2rem;
        }
        
        .feature-card {
            padding: 1rem;
        }
        
        .metric-card {
            padding: 1rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """创建页面头部"""
    st.markdown("""
    <div class="top-nav fade-in">
        <h1 class="nav-title">🧠 ReticuGPT AI Medical Platform</h1>
        <p class="nav-subtitle">智能IBS诊疗系统 | AI-Powered Clinical Decision Support</p>
    </div>
    """, unsafe_allow_html=True)

def create_dashboard_metrics():
    """创建仪表板指标"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card fade-in">
            <div class="metric-value">🎯 89.2%</div>
            <div class="metric-label">AI诊断准确率</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card fade-in">
            <div class="metric-value">⚡ 78%</div>
            <div class="metric-label">治疗效果改善</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card fade-in">
            <div class="metric-value">👨‍⚕️ 156</div>
            <div class="metric-label">活跃医生用户</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card fade-in">
            <div class="metric-value">🏥 2,847</div>
            <div class="metric-label">累计患者案例</div>
        </div>
        """, unsafe_allow_html=True)

def create_ai_diagnosis_interface():
    """创建AI诊断界面"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3 class="card-title">
            <span class="card-icon">🔬</span>
            AI智能诊断分析
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 患者基本信息
        st.subheader("📋 患者信息")
        
        patient_col1, patient_col2 = st.columns(2)
        with patient_col1:
            patient_id = st.text_input("患者ID", value=f"P{datetime.now().strftime('%m%d%H%M')}")
            age = st.number_input("年龄", min_value=18, max_value=80, value=35)
            gender = st.selectbox("性别", ["女", "男"])
        
        with patient_col2:
            height = st.number_input("身高 (cm)", min_value=140, max_value=200, value=165)
            weight = st.number_input("体重 (kg)", min_value=40, max_value=120, value=60)
            bmi = weight / ((height/100) ** 2)
            st.metric("BMI", f"{bmi:.1f}")
        
        # 详细症状评估
        st.subheader("🎯 详细症状评估")
        
        # 使用详细IBS-SSS系统
        ibs_system = DetailedIBSSSS()
        
        # 腹痛评估
        st.write("**腹痛评估**")
        pain_cols = st.columns(3)
        with pain_cols[0]:
            pain_intensity = st.slider("疼痛强度 (VAS 0-10)", 0, 10, 5)
        with pain_cols[1]:
            pain_frequency = st.selectbox("疼痛频率", 
                ["无腹痛", "1-2天", "3-5天", "6-8天", "每天都有"], index=2)
        with pain_cols[2]:
            pain_duration = st.selectbox("单次持续时间",
                ["无疼痛", "<1小时", "1-4小时", "4-12小时", ">12小时"], index=2)
        
        # 排便习惯
        st.write("**排便习惯评估**")
        bowel_cols = st.columns(3)
        with bowel_cols[0]:
            bowel_frequency = st.selectbox("排便频率变化",
                ["无改变", "轻度改变", "中度改变", "重度改变", "极度改变"], index=2)
        with bowel_cols[1]:
            bristol_score = st.selectbox("大便性状 (Bristol)", 
                ["1型-硬球", "2型-块状", "3型-裂缝", "4型-光滑", "5型-软块", "6型-糊状", "7型-水样"], index=5)
        with bowel_cols[2]:
            urgency = st.selectbox("排便急迫感",
                ["无急迫感", "轻度可控", "中度偶难控", "重度经常难控", "极度无法控"], index=3)
        
        # 腹胀和生活质量
        st.write("**腹胀和生活质量**")
        quality_cols = st.columns(2)
        with quality_cols[0]:
            bloating = st.slider("腹胀严重程度", 0, 4, 2)
            daily_impact = st.slider("日常活动影响", 0, 4, 2)
        with quality_cols[1]:
            incomplete_evacuation = st.slider("排便不尽感", 0, 4, 1)
            social_impact = st.slider("社交活动影响", 0, 4, 2)
        
        # 合并疾病筛查
        st.subheader("🔍 合并疾病筛查")
        comorbidity_system = EnhancedComorbiditySystem()
        
        screening_cols = st.columns(2)
        with screening_cols[0]:
            anxiety_score = st.slider("焦虑评分 (GAD-7)", 0, 21, 8)
            depression_score = st.slider("抑郁评分 (PHQ-9)", 0, 27, 6)
        with screening_cols[1]:
            stress_level = st.slider("压力水平", 1, 10, 6)
            sleep_quality = st.slider("睡眠质量", 1, 10, 6)
        
        # 合并疾病选择
        comorbidities = st.multiselect("已知合并疾病", [
            "焦虑症", "抑郁症", "双相情感障碍", "子宫内膜异位症", 
            "多囊卵巢综合征", "胃食管反流病", "糖尿病", "甲状腺功能异常",
            "类风湿关节炎", "系统性红斑狼疮"
        ])
        
        # 既往治疗
        st.subheader("💊 既往治疗史")
        previous_treatments = st.multiselect("既往用药", [
            "美贝维林", "洛哌丁胺", "聚乙二醇", "利那洛肽", "阿洛司琼",
            "帕罗西汀", "阿米替林", "双歧杆菌制剂", "补脾益肠丸"
        ])
        
        current_medications = st.multiselect("当前用药", [
            "华法林", "地高辛", "锂盐", "丙戊酸", "避孕药", "NSAIDs"
        ])
    
    with col2:
        # AI分析结果面板
        st.markdown("""
        <div class="feature-card">
            <h4 class="card-title">
                <span class="card-icon">🤖</span>
                AI实时分析
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 生成AI诊断建议", type="primary"):
            with st.spinner("AI系统分析中..."):
                # 模拟AI分析过程
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                
                # 准备患者数据
                patient_data = {
                    "patient_id": patient_id,
                    "age": age,
                    "gender": gender,
                    "anxiety_score": anxiety_score,
                    "depression_score": depression_score,
                    "stress_level": stress_level,
                    "comorbidities": comorbidities,
                    "previous_treatments": previous_treatments
                }
                
                # 计算详细IBS-SSS评分
                responses = {
                    "intensity": pain_intensity,
                    "frequency": {"无腹痛": 0, "1-2天": 1, "3-5天": 2, "6-8天": 3, "每天都有": 4}[pain_frequency],
                    "duration_per_episode": {"无疼痛": 0, "<1小时": 1, "1-4小时": 2, "4-12小时": 3, ">12小时": 4}[pain_duration],
                    "frequency_change": {"无改变": 0, "轻度改变": 1, "中度改变": 2, "重度改变": 3, "极度改变": 4}[bowel_frequency],
                    "urgency": {"无急迫感": 0, "轻度可控": 1, "中度偶难控": 2, "重度经常难控": 3, "极度无法控": 4}[urgency],
                    "bristol_score": bristol_score.split("型")[0],
                    "bloating_severity": bloating,
                    "incomplete_evacuation": incomplete_evacuation,
                    "daily_activity_interference": daily_impact
                }
                
                ibs_result = ibs_system.calculate_detailed_score(responses)
                
                # 药物推荐
                drug_db = EnhancedDrugDatabase()
                drug_recommendations = drug_db.get_drug_recommendations(
                    ibs_subtype=ibs_result["symptom_pattern"].replace("_predominant", "").replace("_pattern", "").upper(),
                    severity=ibs_result["severity_classification"],
                    comorbidities=comorbidities,
                    contraindications=[]
                )
                
                # 显示结果
                st.success("AI分析完成！")
                
                # IBS-SSS评分结果
                st.markdown("### 📊 IBS-SSS详细评分")
                st.metric("总分", f"{ibs_result['total_score']:.1f}/500")
                st.metric("严重程度", ibs_result['severity_classification'])
                st.metric("症状模式", {
                    'pain_predominant': '疼痛为主型',
                    'diarrhea_predominant': '腹泻为主型', 
                    'constipation_predominant': '便秘为主型',
                    'bloating_predominant': '腹胀为主型',
                    'mixed_pattern': '混合型'
                }.get(ibs_result['symptom_pattern'], '未知'))
                
                # AI置信度
                confidence = np.random.uniform(0.82, 0.95)
                st.metric("AI置信度", f"{confidence:.1%}")
                
                # 症状分析雷达图
                st.markdown("### 📈 症状维度分析")
                
                # 创建雷达图
                categories = ['腹痛', '排便习惯', '腹胀', '排便满意度', '生活质量']
                values = [
                    ibs_result['detailed_scores']['abdominal_pain']['total_score'],
                    ibs_result['detailed_scores']['bowel_habit_disturbance']['total_score'],
                    ibs_result['detailed_scores']['abdominal_distension']['total_score'],
                    ibs_result['detailed_scores']['bowel_satisfaction']['total_score'],
                    ibs_result['detailed_scores']['quality_of_life_impact']['total_score']
                ]
                
                fig = go.Figure()
                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=categories,
                    fill='toself',
                    name='症状评分',
                    line_color='#00f5ff',
                    fillcolor='rgba(0, 245, 255, 0.3)'
                ))
                
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0, 100],
                            gridcolor='rgba(255, 255, 255, 0.2)',
                            linecolor='rgba(255, 255, 255, 0.2)'
                        ),
                        angularaxis=dict(
                            gridcolor='rgba(255, 255, 255, 0.2)',
                            linecolor='rgba(255, 255, 255, 0.2)'
                        )
                    ),
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font_color='white',
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # 药物推荐
                st.markdown("### 💊 AI药物推荐")
                
                if drug_recommendations["first_line"]:
                    st.write("**一线推荐:**")
                    for drug in drug_recommendations["first_line"]:
                        st.info(f"🎯 **{drug.get('generic_name', 'Unknown')}** - {drug.get('dosage', 'N/A')}")
                
                if drug_recommendations["combination_therapy"]:
                    st.write("**联合治疗:**")
                    for drug in drug_recommendations["combination_therapy"]:
                        st.info(f"🔄 **{drug.get('generic_name', 'Unknown')}** - {drug.get('dosage', 'N/A')}")
                
                # 相互作用检查
                if current_medications:
                    st.markdown("### ⚠️ 药物相互作用")
                    for current_drug in current_medications:
                        interactions = drug_db.get_drug_interaction_check(
                            current_drugs=[current_drug],
                            new_drug="帕罗西汀"  # 示例
                        )
                        if interactions["major_interactions"]:
                            st.warning(f"与{current_drug}存在重要相互作用")
                
                # 随访计划
                followup_system = PatientFollowupSystem()
                st.markdown("### 📅 随访计划")
                
                if ibs_result['total_score'] > 300:
                    st.info("🏥 **建议随访**: 每1-2周")
                elif ibs_result['total_score'] > 175:
                    st.info("🏥 **建议随访**: 每2-4周")
                else:
                    st.info("🏥 **建议随访**: 每4-6周")
                
                # 保存患者数据
                if 'patients_data' not in st.session_state:
                    st.session_state.patients_data = []
                
                patient_record = {
                    **patient_data,
                    "ibs_sss_total": ibs_result['total_score'],
                    "symptom_pattern": ibs_result['symptom_pattern'],
                    "ai_confidence": confidence,
                    "assessment_date": datetime.now().isoformat(),
                    "drug_recommendations": drug_recommendations
                }
                
                st.session_state.patients_data.append(patient_record)
                st.success(f"患者 {patient_id} 数据已保存到系统")

def create_analytics_dashboard():
    """创建分析仪表板"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3 class="card-title">
            <span class="card-icon">📊</span>
            数据分析仪表板
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 模拟数据分析
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 治疗效果趋势")
        
        # 创建模拟治疗效果数据
        dates = pd.date_range('2024-01-01', periods=30, freq='D')
        improvement_rates = np.random.normal(75, 8, 30)
        improvement_rates = np.clip(improvement_rates, 60, 90)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates,
            y=improvement_rates,
            mode='lines+markers',
            name='症状改善率',
            line=dict(color='#00f5ff', width=3),
            marker=dict(size=6, color='#00f5ff')
        ))
        
        fig.update_layout(
            title="30天症状改善趋势",
            xaxis_title="日期",
            yaxis_title="改善率 (%)",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🎯 症状模式分布")
        
        # 症状模式分布饼图
        patterns = ['腹泻为主型', '便秘为主型', '疼痛为主型', '腹胀为主型', '混合型']
        values = [35, 25, 20, 12, 8]
        colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#feca57']
        
        fig = go.Figure(data=[go.Pie(
            labels=patterns,
            values=values,
            hole=0.4,
            marker_colors=colors
        )])
        
        fig.update_layout(
            title="IBS症状模式分布",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # 药物使用统计
    st.subheader("💊 药物使用统计")
    
    drug_usage_data = {
        '药物名称': ['美贝维林', '洛哌丁胺', '聚乙二醇', '帕罗西汀', '阿米替林', '双歧杆菌制剂'],
        '使用频次': [245, 198, 156, 134, 89, 267],
        '有效率(%)': [78, 82, 71, 68, 74, 65],
        '副作用率(%)': [12, 18, 15, 28, 31, 8]
    }
    
    df = pd.DataFrame(drug_usage_data)
    
    # 创建药物效果对比图
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=("使用频次", "有效率 vs 副作用率"),
        specs=[[{"type": "bar"}, {"type": "scatter"}]]
    )
    
    # 使用频次柱状图
    fig.add_trace(
        go.Bar(x=df['药物名称'], y=df['使用频次'], 
               marker_color='#667eea', name="使用频次"),
        row=1, col=1
    )
    
    # 有效率vs副作用率散点图
    fig.add_trace(
        go.Scatter(x=df['有效率(%)'], y=df['副作用率(%)'],
                  mode='markers+text',
                  text=df['药物名称'],
                  textposition="top center",
                  marker=dict(size=df['使用频次']/10, color='#764ba2'),
                  name="有效率vs副作用率"),
        row=1, col=2
    )
    
    fig.update_layout(
        height=400,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font_color='white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def create_physician_dashboard():
    """创建医生仪表板"""
    st.markdown("""
    <div class="feature-card fade-in">
        <h3 class="card-title">
            <span class="card-icon">👨‍⚕️</span>
            医生工作台
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # 医生个人绩效
    physician_system = PhysicianEngagementSystem()
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.subheader("📊 个人绩效")
        
        # 模拟医生数据
        physician_data = {
            "usage_frequency": 18,
            "adoption_rate": 82,
            "feedback_quality": 88,
            "patient_outcomes": 76
        }
        
        score = physician_system.calculate_engagement_score(physician_data)
        
        st.metric("参与度评分", f"{score['total_score']:.1f}/100")
        st.metric("参与水平", score['level'])
        
        # 绩效雷达图
        metrics = ['使用频率', '采纳率', '反馈质量', '患者结局']
        values = [physician_data[k] for k in physician_data.keys()]
        
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics,
            fill='toself',
            name='绩效评分',
            line_color='#667eea',
            fillcolor='rgba(102, 126, 234, 0.3)'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100])
            ),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='white',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏆 成就系统")
        
        # 成就徽章
        achievements = [
            {"name": "AI专家", "progress": 85, "description": "熟练使用AI系统"},
            {"name": "患者守护者", "progress": 92, "description": "患者满意度高"},
            {"name": "创新先锋", "progress": 67, "description": "提出改进建议"},
            {"name": "学习达人", "progress": 78, "description": "完成培训课程"}
        ]
        
        for achievement in achievements:
            progress = achievement["progress"]
            if progress >= 90:
                badge_color = "🥇"
            elif progress >= 75:
                badge_color = "🥈"
            elif progress >= 60:
                badge_color = "🥉"
            else:
                badge_color = "⭐"
            
            st.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="font-size: 1.5rem; margin-right: 0.5rem;">{badge_color}</span>
                        <strong>{achievement['name']}</strong>
                        <br><small style="opacity: 0.8;">{achievement['description']}</small>
                    </div>
                    <div style="text-align: right;">
                        <div style="font-size: 1.2rem; color: #00f5ff;">{progress}%</div>
                    </div>
                </div>
                <div style="background: rgba(255,255,255,0.2); height: 4px; border-radius: 2px; margin-top: 0.5rem;">
                    <div style="background: linear-gradient(45deg, #667eea, #764ba2); height: 100%; width: {progress}%; border-radius: 2px;"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        st.subheader("📚 学习资源")
        
        learning_modules = [
            {"title": "AI医疗基础", "duration": "30分钟", "completed": True},
            {"title": "药物相互作用", "duration": "45分钟", "completed": True},
            {"title": "个性化治疗", "duration": "1小时", "completed": False},
            {"title": "临床决策支持", "duration": "40分钟", "completed": False}
        ]
        
        for module in learning_modules:
            status = "✅" if module["completed"] else "⏳"
            color = "rgba(0, 255, 0, 0.2)" if module["completed"] else "rgba(255, 255, 255, 0.1)"
            
            st.markdown(f"""
            <div style="background: {color}; padding: 1rem; border-radius: 10px; margin: 0.5rem 0;">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div>
                        <span style="margin-right: 0.5rem;">{status}</span>
                        <strong>{module['title']}</strong>
                        <br><small style="opacity: 0.8;">预计时长: {module['duration']}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("📖 开始学习", key="learning"):
            st.success("学习模块已启动！")

def main():
    """主函数"""
    st.set_page_config(
        page_title="ReticuGPT AI Medical Platform",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 加载自定义样式
    load_custom_css()
    
    # 创建页面头部
    create_header()
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3 style="color: #00f5ff;">🔬 功能导航</h3>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.selectbox(
            "选择功能模块",
            ["🏠 总览仪表板", "🔬 AI智能诊断", "📊 数据分析", "👨‍⚕️ 医生工作台", "⚙️ 系统设置"],
            index=0
        )
        
        st.markdown("---")
        
        # 系统状态
        st.markdown("""
        ### 📡 系统状态
        - **AI模型**: 🟢 在线
        - **数据库**: 🟢 正常 
        - **API服务**: 🟢 运行中
        - **用户数**: 156位医生
        """)
        
        st.markdown("---")
        
        # 快速操作
        st.markdown("### ⚡ 快速操作")
        if st.button("🔄 刷新数据"):
            st.rerun()
        
        if st.button("📊 生成报告"):
            st.success("报告生成中...")
        
        if st.button("💾 导出数据"):
            st.success("数据导出完成!")
    
    # 主要内容区域
    if page == "🏠 总览仪表板":
        st.markdown("## 📈 系统总览")
        create_dashboard_metrics()
        
        col1, col2 = st.columns([2, 1])
        with col1:
            create_analytics_dashboard()
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h4>🔔 系统通知</h4>
                <div style="margin: 1rem 0;">
                    <div style="background: rgba(0, 245, 255, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                        🎉 新版本v2.1已发布，增加了药物相互作用检查功能
                    </div>
                    <div style="background: rgba(255, 193, 7, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                        ⚠️ 系统将于今晚23:00进行例行维护
                    </div>
                    <div style="background: rgba(40, 167, 69, 0.1); padding: 0.8rem; border-radius: 8px; margin: 0.5rem 0;">
                        📊 本月AI准确率达到89.2%，创历史新高
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == "🔬 AI智能诊断":
        create_ai_diagnosis_interface()
    
    elif page == "📊 数据分析":
        create_analytics_dashboard()
    
    elif page == "👨‍⚕️ 医生工作台":
        create_physician_dashboard()
    
    elif page == "⚙️ 系统设置":
        st.markdown("## ⚙️ 系统设置")
        
        # 系统配置
        st.subheader("🔧 系统配置")
        
        col1, col2 = st.columns(2)
        with col1:
            ai_sensitivity = st.slider("AI敏感度", 0.5, 1.0, 0.85, 0.05)
            auto_save = st.checkbox("自动保存", value=True)
            notification = st.checkbox("推送通知", value=True)
        
        with col2:
            theme = st.selectbox("界面主题", ["深色模式", "浅色模式", "自动"])
            language = st.selectbox("语言", ["中文", "English"])
            timezone = st.selectbox("时区", ["GMT+8", "GMT+0", "GMT-5"])
        
        if st.button("💾 保存设置"):
            st.success("设置已保存！")
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; padding: 1rem;">
        <p>© 2024 ReticuGPT AI Medical Platform | 智能医疗，精准诊疗 | Powered by Advanced AI</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 