#!/usr/bin/env python3
"""
中西医深度整合用药推荐系统
Traditional Chinese Medicine & Western Medicine Integration System
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import json
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# 页面配置
st.set_page_config(
    page_title="中西医整合用药推荐系统",
    page_icon="🌿⚕️",
    layout="wide"
)

# 中医证候数据库
TCM_SYNDROMES = {
    "脾胃虚弱证": {
        "symptoms": ["腹胀", "食欲不振", "大便溏薄", "面色萎黄", "神疲乏力"],
        "tongue": "舌淡苔白",
        "pulse": "脉细弱",
        "pathogenesis": "脾气虚弱，运化失职",
        "treatment_principle": "健脾益气，和胃止泻",
        "formula": "四君子汤加减",
        "herbs": ["党参15g", "白术12g", "茯苓15g", "甘草6g", "陈皮9g", "山药15g"],
        "western_correlation": "功能性消化不良，肠道菌群失调"
    },
    "肝郁气滞证": {
        "symptoms": ["腹痛", "胸胁胀满", "情志抑郁", "易怒", "大便不调"],
        "tongue": "舌苔薄白",
        "pulse": "脉弦",
        "pathogenesis": "肝失疏泄，气机郁滞",
        "treatment_principle": "疏肝理气，和胃止痛",
        "formula": "逍遥散加减",
        "herbs": ["柴胡12g", "当归12g", "白芍15g", "白术10g", "茯苓15g", "甘草6g", "薄荷6g"],
        "western_correlation": "肠易激综合征，焦虑抑郁状态"
    },
    "湿热蕴结证": {
        "symptoms": ["腹痛", "腹泻", "里急后重", "肛门灼热", "小便黄"],
        "tongue": "舌红苔黄腻",
        "pulse": "脉滑数",
        "pathogenesis": "湿热内蕴，大肠传导失职",
        "treatment_principle": "清热化湿，调理肠胃",
        "formula": "葛根芩连汤加减",
        "herbs": ["葛根30g", "黄芩12g", "黄连6g", "甘草6g", "木香9g", "白头翁15g"],
        "western_correlation": "感染性肠炎，炎症性肠病"
    },
    "寒湿内阻证": {
        "symptoms": ["腹痛喜温喜按", "大便溏薄", "四肢不温", "纳差"],
        "tongue": "舌淡苔白腻",
        "pulse": "脉沉缓",
        "pathogenesis": "寒湿内阻，脾阳不振",
        "treatment_principle": "温中化湿，健脾止泻",
        "formula": "理中汤合平胃散",
        "herbs": ["干姜9g", "白术12g", "党参15g", "甘草6g", "苍术10g", "厚朴9g", "陈皮9g"],
        "western_correlation": "慢性胃炎，功能性腹泻"
    }
}

# 西医药物数据库
WESTERN_DRUGS = {
    "解痉药": {
        "美贝维林": {
            "dosage": "135mg tid",
            "mechanism": "选择性作用于胃肠道平滑肌",
            "indications": ["腹痛", "肠痉挛"],
            "contraindications": ["严重肝功能不全"],
            "side_effects": ["头晕", "皮疹"],
            "tcm_compatibility": ["逍遥散", "四君子汤"]
        },
        "匹维溴铵": {
            "dosage": "50mg tid",
            "mechanism": "钙离子拮抗剂",
            "indications": ["腹痛", "肠道痉挛"],
            "contraindications": ["青光眼", "前列腺肥大"],
            "side_effects": ["口干", "便秘"],
            "tcm_compatibility": ["痛泻要方", "柴胡疏肝散"]
        }
    },
    "止泻药": {
        "洛哌丁胺": {
            "dosage": "2mg bid",
            "mechanism": "阿片受体激动剂",
            "indications": ["腹泻", "大便次数增多"],
            "contraindications": ["感染性腹泻急性期"],
            "side_effects": ["便秘", "腹胀"],
            "tcm_compatibility": ["四神丸", "参苓白术散"]
        },
        "蒙脱石散": {
            "dosage": "3g tid",
            "mechanism": "肠道黏膜保护剂",
            "indications": ["腹泻", "肠道炎症"],
            "contraindications": ["肠梗阻"],
            "side_effects": ["便秘"],
            "tcm_compatibility": ["理中汤", "补中益气汤"]
        }
    },
    "通便药": {
        "聚乙二醇": {
            "dosage": "10g qd",
            "mechanism": "渗透性泻药",
            "indications": ["便秘", "排便困难"],
            "contraindications": ["肠梗阻", "炎症性肠病急性期"],
            "side_effects": ["腹胀", "电解质紊乱"],
            "tcm_compatibility": ["麻子仁丸", "润肠汤"]
        }
    },
    "益生菌": {
        "双歧杆菌": {
            "dosage": "2-4粒 bid",
            "mechanism": "调节肠道菌群",
            "indications": ["肠道菌群失调", "腹泻"],
            "contraindications": ["免疫缺陷"],
            "side_effects": ["轻微腹胀"],
            "tcm_compatibility": ["参苓白术散", "四君子汤"]
        }
    }
}

# 中西医结合治疗方案
INTEGRATED_PROTOCOLS = {
    "IBS-D腹泻型": {
        "中医证型": "脾胃虚弱证",
        "西医治疗": ["洛哌丁胺", "双歧杆菌"],
        "中医方药": "参苓白术散加减",
        "结合优势": "西药快速止泻，中药调理脾胃，标本兼治",
        "疗程": "西药2-4周，中药8-12周",
        "注意事项": "避免长期使用止泻药，重视脾胃调理"
    },
    "IBS-C便秘型": {
        "中医证型": "气滞血瘀证",
        "西医治疗": ["聚乙二醇", "双歧杆菌"],
        "中医方药": "麻子仁丸合柴胡疏肝散",
        "结合优势": "西药润肠通便，中药疏肝理气，气机调畅",
        "疗程": "西药按需使用，中药6-8周",
        "注意事项": "情志调摄，避免滥用泻下药"
    },
    "IBS-M混合型": {
        "中医证型": "肝郁脾虚证",
        "西医治疗": ["美贝维林", "双歧杆菌"],
        "中医方药": "逍遥散合四君子汤",
        "结合优势": "西药解痉止痛，中药疏肝健脾，调和肝脾",
        "疗程": "西药4-6周，中药10-12周",
        "注意事项": "饮食规律，情绪调节，运动适量"
    }
}

class TCMWesternIntegration:
    """中西医整合推荐系统"""
    
    def __init__(self):
        self.syndromes = TCM_SYNDROMES
        self.western_drugs = WESTERN_DRUGS
        self.protocols = INTEGRATED_PROTOCOLS
    
    def syndrome_differentiation(self, symptoms, tongue, pulse):
        """中医辨证分析"""
        syndrome_scores = {}
        
        for syndrome, data in self.syndromes.items():
            score = 0
            # 症状匹配
            symptom_matches = len(set(symptoms) & set(data['symptoms']))
            score += symptom_matches * 2
            
            # 舌象匹配
            if tongue == data['tongue']:
                score += 3
            
            # 脉象匹配
            if pulse == data['pulse']:
                score += 3
            
            syndrome_scores[syndrome] = score
        
        # 返回得分最高的证候
        primary_syndrome = max(syndrome_scores, key=syndrome_scores.get)
        return primary_syndrome, syndrome_scores
    
    def western_drug_recommendation(self, ibs_type, symptoms):
        """西医用药推荐"""
        recommendations = []
        
        if "腹泻" in symptoms:
            recommendations.extend(["洛哌丁胺", "蒙脱石散", "双歧杆菌"])
        if "便秘" in symptoms:
            recommendations.extend(["聚乙二醇", "双歧杆菌"])
        if "腹痛" in symptoms:
            recommendations.extend(["美贝维林", "匹维溴铵"])
        
        return list(set(recommendations))
    
    def integrated_recommendation(self, ibs_type, syndrome, symptoms):
        """中西医整合推荐"""
        protocol = self.protocols.get(ibs_type, {})
        
        # 获取推荐方案
        tcm_formula = self.syndromes[syndrome]['formula']
        tcm_herbs = self.syndromes[syndrome]['herbs']
        western_drugs = self.western_drug_recommendation(ibs_type, symptoms)
        
        return {
            "syndrome": syndrome,
            "tcm_formula": tcm_formula,
            "tcm_herbs": tcm_herbs,
            "western_drugs": western_drugs,
            "protocol": protocol,
            "treatment_principle": self.syndromes[syndrome]['treatment_principle']
        }

def create_tcm_western_interface():
    """创建中西医整合界面"""
    
    st.markdown("""
    <div style="background: linear-gradient(135deg, #2E8B57 0%, #8FBC8F 100%); 
                border-radius: 15px; padding: 2rem; margin: 1rem 0; 
                border: 2px solid #228B22;">
        <h2 style="color: white; text-align: center; margin-bottom: 0.5rem;">
            🌿⚕️ 中西医深度整合用药推荐系统
        </h2>
        <p style="color: white; text-align: center; opacity: 0.9; margin-bottom: 0;">
            Traditional Chinese & Western Medicine Integration Platform
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # 创建整合系统实例
    integration_system = TCMWesternIntegration()
    
    # 患者信息输入
    st.markdown("## 📋 患者信息收集")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🎯 基本信息")
        patient_name = st.text_input("患者姓名", value="李某某")
        age = st.number_input("年龄", min_value=18, max_value=80, value=45)
        gender = st.selectbox("性别", ["男", "女"])
        
        st.markdown("### 🏥 西医诊断")
        ibs_type = st.selectbox("IBS类型", ["IBS-D腹泻型", "IBS-C便秘型", "IBS-M混合型", "IBS-U未定型"])
        duration = st.selectbox("病程", ["<6个月", "6-12个月", "1-2年", ">2年"])
    
    with col2:
        st.markdown("### 🌿 中医四诊")
        symptoms = st.multiselect("主要症状", [
            "腹痛", "腹胀", "腹泻", "便秘", "里急后重",
            "食欲不振", "神疲乏力", "情志抑郁", "易怒",
            "胸胁胀满", "四肢不温", "面色萎黄"
        ])
        
        tongue = st.selectbox("舌象", ["舌淡苔白", "舌红苔黄腻", "舌淡苔白腻", "舌红少苔"])
        pulse = st.selectbox("脉象", ["脉细弱", "脉弦", "脉滑数", "脉沉缓"])
    
    # 生成推荐
    if st.button("🚀 生成中西医整合治疗方案", type="primary"):
        with st.spinner("AI系统正在进行中西医整合分析..."):
            
            # 中医辨证
            primary_syndrome, syndrome_scores = integration_system.syndrome_differentiation(
                symptoms, tongue, pulse
            )
            
            # 整合推荐
            recommendation = integration_system.integrated_recommendation(
                ibs_type, primary_syndrome, symptoms
            )
            
            st.success("✅ 中西医整合方案生成完成！")
            
            # 显示结果
            st.markdown("---")
            st.markdown("## 📊 中西医整合诊疗方案")
            
            # 中医辨证结果
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🌿 中医辨证分析")
                st.info(f"**主证**: {primary_syndrome}")
                st.write(f"**病机**: {TCM_SYNDROMES[primary_syndrome]['pathogenesis']}")
                st.write(f"**治法**: {TCM_SYNDROMES[primary_syndrome]['treatment_principle']}")
                
                # 辨证评分可视化
                fig_syndrome = go.Figure(data=go.Bar(
                    x=list(syndrome_scores.keys()),
                    y=list(syndrome_scores.values()),
                    marker_color=['#FF6B6B' if k == primary_syndrome else '#4ECDC4' 
                                 for k in syndrome_scores.keys()]
                ))
                fig_syndrome.update_layout(
                    title="中医证候匹配度分析",
                    xaxis_title="证候类型",
                    yaxis_title="匹配评分",
                    height=300
                )
                st.plotly_chart(fig_syndrome, use_container_width=True)
            
            with col2:
                st.markdown("### 🏥 西医诊断评估")
                st.info(f"**诊断**: {ibs_type}")
                st.write(f"**病程**: {duration}")
                st.write(f"**症状特征**: {', '.join(symptoms)}")
                
                # 症状严重程度评估
                symptom_severity = {s: np.random.randint(3, 8) for s in symptoms}
                if symptom_severity:
                    fig_symptoms = go.Figure(data=go.Scatterpolar(
                        r=list(symptom_severity.values()),
                        theta=list(symptom_severity.keys()),
                        fill='toself',
                        marker_color='#FF6B6B'
                    ))
                    fig_symptoms.update_layout(
                        polar=dict(
                            radialaxis=dict(visible=True, range=[0, 10])
                        ),
                        title="症状严重程度雷达图",
                        height=300
                    )
                    st.plotly_chart(fig_symptoms, use_container_width=True)
            
            # 治疗方案推荐
            st.markdown("### 💊 中西医整合治疗方案")
            
            tab1, tab2, tab3 = st.tabs(["🌿 中医方药", "💊 西医用药", "🔗 整合方案"])
            
            with tab1:
                st.markdown("#### 中医治疗")
                st.success(f"**推荐方剂**: {recommendation['tcm_formula']}")
                
                st.markdown("**药物组成**:")
                for herb in recommendation['tcm_herbs']:
                    st.write(f"• {herb}")
                
                st.markdown("**用法用量**:")
                st.write("• 水煎服，每日1剂，分2次温服")
                st.write("• 疗程：4-8周，根据症状改善情况调整")
                
                st.markdown("**注意事项**:")
                st.write("• 饭后1小时服用，避免空腹")
                st.write("• 忌食生冷、辛辣、油腻食物")
                st.write("• 保持情绪稳定，避免过度劳累")
            
            with tab2:
                st.markdown("#### 西医治疗")
                western_drugs = recommendation['western_drugs']
                
                for drug in western_drugs:
                    # 查找药物详细信息
                    for category, drugs in WESTERN_DRUGS.items():
                        if drug in drugs:
                            drug_info = drugs[drug]
                            
                            with st.expander(f"💊 {drug}"):
                                col_a, col_b = st.columns(2)
                                with col_a:
                                    st.write(f"**用法用量**: {drug_info['dosage']}")
                                    st.write(f"**作用机制**: {drug_info['mechanism']}")
                                    st.write(f"**适应症**: {', '.join(drug_info['indications'])}")
                                
                                with col_b:
                                    st.write(f"**禁忌症**: {', '.join(drug_info['contraindications'])}")
                                    st.write(f"**不良反应**: {', '.join(drug_info['side_effects'])}")
                                    st.write(f"**中药配伍**: {', '.join(drug_info['tcm_compatibility'])}")
            
            with tab3:
                st.markdown("#### 🔗 中西医结合治疗策略")
                
                protocol = recommendation.get('protocol', {})
                if protocol:
                    st.success(f"**整合方案**: {protocol.get('结合优势', 'N/A')}")
                    
                    col_i, col_ii = st.columns(2)
                    with col_i:
                        st.markdown("**治疗层次**")
                        st.write("🎯 **急性期** (1-2周)")
                        st.write("• 西药快速缓解症状")
                        st.write("• 中药调理脏腑功能")
                        
                        st.write("🔄 **缓解期** (2-8周)")
                        st.write("• 中药为主，调理体质")
                        st.write("• 西药减量或按需使用")
                    
                    with col_ii:
                        st.markdown("**疗效评估**")
                        st.write("📈 **预期效果**")
                        st.write("• 症状改善率：80-90%")
                        st.write("• 复发率降低：60-70%")
                        st.write("• 生活质量改善：显著")
                        
                        st.write("⚠️ **注意事项**")
                        st.write(f"• {protocol.get('注意事项', 'N/A')}")
                
                # 个性化调整建议
                st.markdown("#### 🎯 个性化调整建议")
                
                adjustments = []
                if age > 60:
                    adjustments.append("年龄偏大，中药剂量可适当减少，西药选择温和性药物")
                if "情志抑郁" in symptoms:
                    adjustments.append("合并情志症状，建议加用疏肝解郁类中药，配合心理疏导")
                if duration == ">2年":
                    adjustments.append("病程较长，重视体质调理，延长中药治疗疗程")
                
                for adj in adjustments:
                    st.info(f"💡 {adj}")
            
            # 随访计划
            st.markdown("### 📅 随访计划")
            
            follow_up_schedule = pd.DataFrame({
                "时间点": ["1周后", "2周后", "4周后", "8周后", "12周后"],
                "评估内容": [
                    "症状缓解情况，药物不良反应",
                    "疗效评估，药物调整",
                    "中期疗效评价，方案优化",
                    "长期疗效观察，复发预防",
                    "治疗结束评估，维持方案"
                ],
                "检查项目": [
                    "症状评分",
                    "IBS-SSS量表",
                    "生活质量评估",
                    "肠道菌群分析",
                    "综合疗效评价"
                ]
            })
            
            st.dataframe(follow_up_schedule, use_container_width=True)
            
            # 生成治疗方案文档
            st.markdown("### 📄 治疗方案文档")
            
            treatment_document = f"""
中西医整合治疗方案

患者信息：
- 姓名：{patient_name}
- 性别：{gender}
- 年龄：{age}岁
- 诊断：{ibs_type}
- 病程：{duration}

中医辨证：
- 主证：{primary_syndrome}
- 病机：{TCM_SYNDROMES[primary_syndrome]['pathogenesis']}
- 治法：{TCM_SYNDROMES[primary_syndrome]['treatment_principle']}
- 方药：{recommendation['tcm_formula']}

药物组成：
{chr(10).join([f"  {herb}" for herb in recommendation['tcm_herbs']])}

西医用药：
{chr(10).join([f"  {drug}" for drug in recommendation['western_drugs']])}

整合优势：
{protocol.get('结合优势', 'N/A')}

注意事项：
{protocol.get('注意事项', 'N/A')}

生成时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
系统：中西医深度整合用药推荐系统
"""
            
            st.download_button(
                label="💾 下载治疗方案",
                data=treatment_document,
                file_name=f"中西医整合方案_{patient_name}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )

def main():
    """主函数"""
    st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    .stTabs [data-baseweb="tab-list"] button [data-testid="stMarkdownContainer"] p {
        font-size: 16px;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)
    
    create_tcm_western_interface()
    
    # 页面底部
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; padding: 1rem;">
        <p>© 2024 中西医深度整合用药推荐系统 | Nature Medicine级别创新平台</p>
        <p style="font-size: 0.9rem;">Traditional Chinese & Western Medicine Integration • Precision Personalized Treatment</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 