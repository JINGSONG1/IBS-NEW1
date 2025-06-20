#!/usr/bin/env python3
"""
Ultra Simple EMR Generator - Zero DOM Conflicts
医生填完数据直接生成EMR，绝对无冲突
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import uuid
import time

# 页面配置
st.set_page_config(
    page_title="Ultra Simple EMR Generator",
    page_icon="📋",
    layout="wide"
)

# 自定义CSS
st.markdown("""
<style>
.main-header {
    background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
    padding: 2rem;
    border-radius: 10px;
    text-align: center;
    color: white;
    margin-bottom: 2rem;
}
.success-msg {
    background: #d4edda;
    border: 1px solid #c3e6cb;
    color: #155724;
    padding: 1rem;
    border-radius: 5px;
    margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)

# 页面标题
st.markdown("""
<div class="main-header">
    <h1>📋 Ultra Simple EMR Generator</h1>
    <p>医生填完数据 → 一键生成EMR → 零冲突 → 立即下载</p>
</div>
""", unsafe_allow_html=True)

# 第一步：患者基本信息
st.markdown("## 📝 第一步：患者基本信息")

col1, col2, col3 = st.columns(3)

with col1:
    patient_name = st.text_input("患者姓名", value="张某某")
    patient_age = st.number_input("年龄", min_value=1, max_value=120, value=35)

with col2:
    patient_gender = st.selectbox("性别", ["男", "女"])
    patient_id = st.text_input("病历号", value=f"EMR{datetime.now().strftime('%Y%m%d%H%M')}")

with col3:
    height = st.number_input("身高(cm)", min_value=100, max_value=250, value=170)
    weight = st.number_input("体重(kg)", min_value=30, max_value=200, value=65)

# 第二步：症状评估
st.markdown("## 🎯 第二步：症状评估")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**疼痛评估**")
    pain_score = st.slider("疼痛评分 (0-10)", 0, 10, 5)
    pain_location = st.text_input("疼痛部位", value="腹部")
    
    st.markdown("**消化症状**")
    bowel_habit = st.selectbox("排便习惯", ["正常", "腹泻型", "便秘型", "混合型"])
    bloating = st.selectbox("腹胀程度", ["无", "轻度", "中度", "重度"])

with col2:
    st.markdown("**心理状态**")
    anxiety_level = st.slider("焦虑水平 (1-10)", 1, 10, 5)
    depression_level = st.slider("抑郁水平 (1-10)", 1, 10, 3)
    
    st.markdown("**生活影响**")
    life_quality = st.selectbox("生活质量影响", ["无影响", "轻度影响", "中度影响", "严重影响"])
    work_impact = st.selectbox("工作影响", ["无影响", "偶尔影响", "经常影响", "无法工作"])

# 第三步：诊断和治疗
st.markdown("## 💊 第三步：诊断和治疗")

col1, col2 = st.columns(2)

with col1:
    primary_diagnosis = st.text_input("主要诊断", value="肠易激综合征")
    secondary_diagnosis = st.text_area("次要诊断", value="", height=100)
    
with col2:
    current_medications = st.text_area("当前用药", value="", height=100)
    treatment_plan = st.text_area("治疗计划", value="", height=100)

# 第四步：生成EMR
st.markdown("## 🚀 第四步：生成EMR")

# 使用form来避免重复触发
with st.form("emr_generation_form"):
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        generate_button = st.form_submit_button(
            "🔥 立即生成EMR", 
            type="primary",
            use_container_width=True
        )

# EMR生成逻辑
if generate_button:
    # 显示进度
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for i in range(100):
        progress_bar.progress(i + 1)
        if i < 30:
            status_text.text("正在收集患者信息...")
        elif i < 60:
            status_text.text("正在分析症状数据...")
        elif i < 90:
            status_text.text("正在生成专业EMR...")
        else:
            status_text.text("EMR生成完成!")
        time.sleep(0.01)
    
    # 清除进度显示
    progress_bar.empty()
    status_text.empty()
    
    # 生成EMR内容
    current_time = datetime.now()
    bmi = round(weight / ((height/100) ** 2), 1)
    
    emr_content = f"""电子病历 (EMR)
========================================

基本信息
----------------------------------------
患者姓名：{patient_name}
病历号：{patient_id}
性别：{patient_gender}
年龄：{patient_age}岁
身高：{height}cm
体重：{weight}kg
BMI：{bmi}

就诊信息
----------------------------------------
就诊日期：{current_time.strftime('%Y年%m月%d日')}
就诊时间：{current_time.strftime('%H:%M:%S')}
生成时间：{current_time.strftime('%Y-%m-%d %H:%M:%S')}

症状评估
----------------------------------------
疼痛评分：{pain_score}/10分
疼痛部位：{pain_location}
排便习惯：{bowel_habit}
腹胀程度：{bloating}
焦虑水平：{anxiety_level}/10分
抑郁水平：{depression_level}/10分
生活质量影响：{life_quality}
工作影响：{work_impact}

诊断结果
----------------------------------------
主要诊断：{primary_diagnosis}
次要诊断：{secondary_diagnosis if secondary_diagnosis else '无'}

治疗信息
----------------------------------------
当前用药：{current_medications if current_medications else '无'}
治疗计划：{treatment_plan if treatment_plan else '待制定'}

医生建议
----------------------------------------
1. 定期随访，监测症状变化
2. 注意饮食调理，避免刺激性食物
3. 保持心理健康，必要时心理咨询
4. 按时服药，注意药物副作用

下次随访时间：{(current_time + timedelta(days=30)).strftime('%Y年%m月%d日')}

========================================
电子病历系统生成
生成ID：{uuid.uuid4().hex[:8].upper()}
========================================"""
    
    # 显示成功消息
    st.markdown("""
    <div class="success-msg">
        <h4>✅ EMR生成成功！</h4>
        <p>电子病历已完成生成，您可以查看、复制或下载。</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 显示EMR内容
    st.markdown("### 📋 生成的电子病历")
    
    # 使用简单的code显示，避免任何DOM冲突
    st.code(emr_content, language=None)
    
    # 下载按钮
    st.download_button(
        label="💾 下载EMR文件",
        data=emr_content,
        file_name=f"EMR_{patient_name}_{patient_id}_{current_time.strftime('%Y%m%d_%H%M%S')}.txt",
        mime="text/plain"
    )
    
    # 统计信息
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("字符数", f"{len(emr_content):,}")
    
    with col2:
        st.metric("单词数", f"{len(emr_content.split()):,}")
    
    with col3:
        st.metric("行数", f"{emr_content.count(chr(10)):,}")
    
    with col4:
        st.metric("文件大小", f"{len(emr_content.encode('utf-8'))} bytes")

# 页面底部
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <p>© 2024 Ultra Simple EMR Generator | 零冲突 | 一键生成 | 专业可靠</p>
    <p style="font-size: 0.9rem;">本系统采用最简化设计，确保绝对无DOM冲突</p>
</div>
""", unsafe_allow_html=True) 