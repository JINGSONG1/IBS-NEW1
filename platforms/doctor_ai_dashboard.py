#!/usr/bin/env python3
"""
👨‍⚕️ Doctor-AI Learning Dashboard - 医生-AI双向学习仪表盘
医生打分滑条 + 模型随时间自改进曲线
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

# 页面配置
st.set_page_config(
    page_title="👨‍⚕️ Doctor-AI Dashboard",
    page_icon="👨‍⚕️",
    layout="wide"
)

def main():
    st.markdown("# 👨‍⚕️ Doctor-AI Learning Dashboard")
    st.markdown("医生-AI双向学习仪表盘")
    
    # 初始化数据
    if 'feedback_data' not in st.session_state:
        st.session_state.feedback_data = []
        st.session_state.model_performance = generate_model_performance_data()
    
    tab1, tab2, tab3 = st.tabs(["💬 医生反馈", "📈 AI改进曲线", "🎯 综合分析"])
    
    with tab1:
        st.markdown("### 💬 医生诊疗反馈系统")
        
        # 病例信息输入
        col1, col2 = st.columns(2)
        
        with col1:
            case_id = st.text_input("病例ID", value=f"CASE_{len(st.session_state.feedback_data)+1:04d}")
            ai_diagnosis = st.selectbox("AI诊断", ["IBS-D", "IBS-C", "IBS-M", "IBS-U"])
            ai_treatment = st.selectbox("AI推荐治疗", ["心理调节", "抗炎治疗", "肠道菌群", "胃肠动力", "综合治疗"])
        
        with col2:
            patient_age = st.number_input("患者年龄", 18, 80, 35)
            patient_gender = st.selectbox("患者性别", ["女", "男"])
            severity = st.slider("症状严重度", 1, 10, 5)
        
        # 医生评分区域
        st.markdown("#### 🏥 医生专业评分")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            efficacy_score = st.slider(
                "🎯 疗效评分 (治疗效果如何?)",
                0.0, 10.0, 7.0, 0.1,
                help="根据患者实际改善情况评分，10分为完全缓解"
            )
        
        with col2:
            interpretability_score = st.slider(
                "🔍 可解释度 (推理逻辑清晰吗?)",
                0.0, 10.0, 8.0, 0.1,
                help="AI的诊断推理过程是否容易理解，10分为完全透明"
            )
        
        with col3:
            confidence_score = st.slider(
                "🎖️ 可信度 (您信任这个诊断吗?)",
                0.0, 10.0, 7.5, 0.1,
                help="基于您的临床经验，对AI诊断的信任程度"
            )
        
        # 自由文本反馈
        doctor_comments = st.text_area(
            "📝 详细反馈意见",
            placeholder="请输入您对此次AI诊断的具体意见、建议或补充..."
        )
        
        # 提交反馈
        if st.button("📤 提交反馈", type="primary"):
            feedback_entry = {
                'timestamp': datetime.now().isoformat(),
                'case_id': case_id,
                'ai_diagnosis': ai_diagnosis,
                'ai_treatment': ai_treatment,
                'patient_age': patient_age,
                'patient_gender': patient_gender,
                'severity': severity,
                'efficacy_score': efficacy_score,
                'interpretability_score': interpretability_score,
                'confidence_score': confidence_score,
                'doctor_comments': doctor_comments
            }
            
            st.session_state.feedback_data.append(feedback_entry)
            
            st.success(f"✅ 反馈已提交！案例 {case_id} 记录完成")
            
            # 显示提交的反馈摘要
            st.info(f"""
            **反馈摘要**:
            - 疗效评分: {efficacy_score:.1f}/10
            - 可解释度: {interpretability_score:.1f}/10  
            - 可信度: {confidence_score:.1f}/10
            - 综合评分: {(efficacy_score + interpretability_score + confidence_score)/3:.1f}/10
            """)
    
    with tab2:
        st.markdown("### 📈 AI模型自改进曲线")
        
        if len(st.session_state.feedback_data) >= 3:
            # 基于医生反馈更新模型性能
            update_model_performance_from_feedback()
        
        performance_data = st.session_state.model_performance
        
        # 性能趋势图
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=performance_data['date'],
            y=performance_data['accuracy'],
            mode='lines+markers',
            name='诊断准确率',
            line=dict(color='blue', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=performance_data['date'],
            y=performance_data['doctor_satisfaction'],
            mode='lines+markers', 
            name='医生满意度',
            line=dict(color='green', width=3)
        ))
        
        fig.add_trace(go.Scatter(
            x=performance_data['date'],
            y=performance_data['interpretability'],
            mode='lines+markers',
            name='可解释性',
            line=dict(color='orange', width=3)
        ))
        
        fig.update_layout(
            title="AI模型性能随时间改进趋势",
            xaxis_title="时间",
            yaxis_title="评分 (%)",
            hovermode='x unified',
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # 关键改进里程碑
        st.markdown("#### 🎯 关键改进里程碑")
        
        milestones = [
            {"date": "2024-01-15", "event": "基础模型部署", "improvement": "+5% 准确率"},
            {"date": "2024-02-01", "event": "医生反馈整合", "improvement": "+8% 满意度"},
            {"date": "2024-02-15", "event": "解释性增强", "improvement": "+12% 可解释性"},
            {"date": "2024-03-01", "event": "个性化适配", "improvement": "+6% 准确率"},
        ]
        
        for milestone in milestones:
            st.success(f"**{milestone['date']}** - {milestone['event']}: {milestone['improvement']}")
    
    with tab3:
        st.markdown("### 🎯 医生-AI协作综合分析")
        
        if st.session_state.feedback_data:
            df = pd.DataFrame(st.session_state.feedback_data)
            
            # 总体统计
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("反馈总数", len(df))
            with col2:
                avg_efficacy = df['efficacy_score'].mean()
                st.metric("平均疗效", f"{avg_efficacy:.1f}/10")
            with col3:
                avg_interpret = df['interpretability_score'].mean()
                st.metric("平均可解释度", f"{avg_interpret:.1f}/10")
            with col4:
                avg_confidence = df['confidence_score'].mean()
                st.metric("平均可信度", f"{avg_confidence:.1f}/10")
            
            # 评分分布
            fig = go.Figure()
            
            fig.add_trace(go.Histogram(
                x=df['efficacy_score'],
                name='疗效评分',
                opacity=0.7,
                nbinsx=20
            ))
            
            fig.add_trace(go.Histogram(
                x=df['interpretability_score'], 
                name='可解释度',
                opacity=0.7,
                nbinsx=20
            ))
            
            fig.add_trace(go.Histogram(
                x=df['confidence_score'],
                name='可信度',
                opacity=0.7,
                nbinsx=20
            ))
            
            fig.update_layout(
                title="医生评分分布",
                xaxis_title="评分",
                yaxis_title="频次",
                barmode='overlay'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # AI诊断类型效果分析
            st.markdown("#### 📊 不同诊断类型的医生认可度")
            
            diagnosis_stats = df.groupby('ai_diagnosis')[['efficacy_score', 'interpretability_score', 'confidence_score']].mean()
            
            fig = go.Figure()
            
            diagnoses = diagnosis_stats.index
            fig.add_trace(go.Bar(
                x=diagnoses,
                y=diagnosis_stats['efficacy_score'],
                name='疗效评分',
                marker_color='lightblue'
            ))
            
            fig.update_layout(
                title="各IBS亚型AI诊断的医生评分",
                xaxis_title="IBS诊断类型",
                yaxis_title="平均评分"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # 改进建议
            st.markdown("#### 💡 基于反馈的改进建议")
            
            if avg_efficacy < 7:
                st.warning("🎯 疗效评分偏低，建议优化治疗推荐算法")
            if avg_interpret < 7:
                st.warning("🔍 可解释性有待提高，建议增强诊断逻辑展示")
            if avg_confidence < 7:
                st.warning("🎖️ 可信度需要改善，建议加强临床证据支持")
            
            if avg_efficacy >= 8 and avg_interpret >= 8 and avg_confidence >= 8:
                st.success("🎉 AI系统表现优秀，医生满意度很高！")
        
        else:
            st.info("📭 暂无医生反馈数据，请先在'医生反馈'选项卡提交反馈")

def generate_model_performance_data():
    """生成模型性能数据"""
    dates = pd.date_range(start='2024-01-01', end='2024-03-15', freq='D')
    
    # 模拟AI性能随时间改进
    base_accuracy = 75
    base_satisfaction = 70
    base_interpretability = 65
    
    performance_data = {
        'date': [],
        'accuracy': [],
        'doctor_satisfaction': [],
        'interpretability': []
    }
    
    for i, date in enumerate(dates):
        # 添加趋势和随机波动
        trend_factor = i / len(dates) * 15  # 15%的整体改进
        noise = np.random.normal(0, 2)  # 随机波动
        
        accuracy = base_accuracy + trend_factor + noise
        satisfaction = base_satisfaction + trend_factor * 0.8 + noise
        interpretability = base_interpretability + trend_factor * 1.2 + noise
        
        performance_data['date'].append(date)
        performance_data['accuracy'].append(max(0, min(100, accuracy)))
        performance_data['doctor_satisfaction'].append(max(0, min(100, satisfaction)))
        performance_data['interpretability'].append(max(0, min(100, interpretability)))
    
    return performance_data

def update_model_performance_from_feedback():
    """基于医生反馈更新模型性能"""
    feedback_data = st.session_state.feedback_data
    
    if len(feedback_data) >= 3:
        # 计算最近反馈的平均分
        recent_feedback = feedback_data[-3:]
        
        avg_efficacy = np.mean([f['efficacy_score'] for f in recent_feedback])
        avg_interpret = np.mean([f['interpretability_score'] for f in recent_feedback])
        avg_confidence = np.mean([f['confidence_score'] for f in recent_feedback])
        
        # 更新最新的性能数据
        performance_data = st.session_state.model_performance
        
        # 添加基于反馈的新数据点
        latest_date = datetime.now()
        
        performance_data['date'].append(latest_date)
        performance_data['accuracy'].append(avg_efficacy * 10)  # 转换为百分比
        performance_data['doctor_satisfaction'].append(avg_confidence * 10)
        performance_data['interpretability'].append(avg_interpret * 10)
        
        st.session_state.model_performance = performance_data

if __name__ == "__main__":
    main() 