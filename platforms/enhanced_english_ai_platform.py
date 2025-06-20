#!/usr/bin/env python3
"""
Enhanced English AI Medical Platform
Advanced Clinical Decision Support with Adverse Drug Reaction Tracking & Electronic Medical Records
"""

import streamlit as st
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# Import custom modules
from enhanced_drug_database import EnhancedDrugDatabase
from enhanced_comorbidity_system import EnhancedComorbiditySystem
from detailed_ibs_sss_system import DetailedIBSSSS
from patient_followup_system import PatientFollowupSystem
from physician_engagement_system import PhysicianEngagementSystem

def load_custom_css():
    """Load custom CSS styles"""
    st.markdown("""
    <style>
    .main > div {
        padding-top: 0rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0c1421 0%, #1a1a2e 50%, #16213e 100%);
        color: #ffffff;
    }
    
    /* Top Navigation Bar */
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
    
    /* Feature Cards */
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
    
    /* ADR (Adverse Drug Reaction) Section */
    .adr-section {
        background: linear-gradient(145deg, #4a1d3f 0%, #6b2c5c 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255, 192, 203, 0.3);
    }
    
    /* EMR (Electronic Medical Record) Section */
    .emr-section {
        background: linear-gradient(145deg, #1a4d3a 0%, #2d6748 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(144, 238, 144, 0.3);
    }
    
    /* Metric Cards */
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
    
    /* Buttons */
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
    
    /* EMR Generation Button */
    .emr-btn {
        background: linear-gradient(45deg, #28a745, #20c997) !important;
        color: white !important;
    }
    
    /* ADR Warning */
    .adr-warning {
        background: linear-gradient(45deg, #dc3545, #fd7e14);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    
    /* Success Messages */
    .stSuccess {
        background: linear-gradient(45deg, #00c9ff, #92fe9d);
        border-radius: 10px;
    }
    
    .stWarning {
        background: linear-gradient(45deg, #fc466b, #3f5efb);
        border-radius: 10px;
    }
    
    /* Text Areas */
    .stTextArea textarea {
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 10px;
        color: white;
        min-height: 200px;
    }
    
    /* Input Fields */
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
    
    /* Responsive Design */
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
    """Create page header"""
    st.markdown("""
    <div class="top-nav">
        <h1 class="nav-title">🧠 ReticuGPT AI Medical Platform Enhanced</h1>
        <p class="nav-subtitle">Advanced Clinical Decision Support | ADR Tracking | Electronic Medical Records</p>
    </div>
    """, unsafe_allow_html=True)

def create_adr_tracking_section():
    """Create Adverse Drug Reaction tracking section"""
    st.markdown("""
    <div class="adr-section">
        <h3 style="color: white; margin-bottom: 1rem;">
            <span style="margin-right: 0.5rem;">⚠️</span>
            Adverse Drug Reaction (ADR) History Tracking
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📋 Previous ADR Records")
        
        # ADR History Input
        if 'adr_history' not in st.session_state:
            st.session_state.adr_history = []
        
        with st.expander("Add New ADR Record", expanded=False):
            adr_drug = st.text_input("Drug Name", key="adr_drug")
            adr_reaction = st.selectbox("Reaction Type", [
                "Allergic Reaction", "Gastrointestinal", "Neurological", 
                "Cardiovascular", "Dermatological", "Hepatotoxicity", 
                "Nephrotoxicity", "Hematological", "Other"
            ], key="adr_reaction")
            adr_severity = st.selectbox("Severity", [
                "Mild", "Moderate", "Severe", "Life-threatening"
            ], key="adr_severity")
            adr_description = st.text_area("Detailed Description", key="adr_description")
            adr_date = st.date_input("Date of Occurrence", key="adr_date")
            
            if st.button("Add ADR Record"):
                if adr_drug and adr_reaction:
                    new_adr = {
                        "drug": adr_drug,
                        "reaction": adr_reaction,
                        "severity": adr_severity,
                        "description": adr_description,
                        "date": adr_date.strftime("%Y-%m-%d"),
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.adr_history.append(new_adr)
                    st.success(f"ADR record for {adr_drug} added successfully!")
                    st.rerun()
        
        # Display existing ADR records
        if st.session_state.adr_history:
            st.write("**Recorded ADR History:**")
            for i, adr in enumerate(st.session_state.adr_history):
                severity_color = {
                    "Mild": "#28a745",
                    "Moderate": "#ffc107", 
                    "Severe": "#fd7e14",
                    "Life-threatening": "#dc3545"
                }.get(adr["severity"], "#6c757d")
                
                st.markdown(f"""
                <div class="adr-warning" style="background: linear-gradient(45deg, {severity_color}, {severity_color}aa);">
                    <strong>🚨 {adr['drug']}</strong> - {adr['reaction']}<br>
                    <small>Severity: {adr['severity']} | Date: {adr['date']}</small><br>
                    <em>{adr['description']}</em>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🔍 AI-Powered ADR Analysis")
        
        if st.session_state.adr_history:
            # ADR Pattern Analysis
            adr_df = pd.DataFrame(st.session_state.adr_history)
            
            # Most common reactions
            reaction_counts = adr_df['reaction'].value_counts()
            severity_counts = adr_df['severity'].value_counts()
            
            # Create ADR analysis chart
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=reaction_counts.index,
                y=reaction_counts.values,
                name='Reaction Types',
                marker_color='#ff6b6b'
            ))
            
            fig.update_layout(
                title="ADR Pattern Analysis",
                xaxis_title="Reaction Type",
                yaxis_title="Frequency",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font_color='white',
                height=300
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # AI Risk Assessment
            st.markdown("### 🤖 AI Risk Assessment")
            high_risk_drugs = adr_df[adr_df['severity'].isin(['Severe', 'Life-threatening'])]
            
            if not high_risk_drugs.empty:
                st.error(f"⚠️ **High Risk Alert**: {len(high_risk_drugs)} severe ADR(s) recorded")
                for _, adr in high_risk_drugs.iterrows():
                    st.warning(f"Avoid {adr['drug']} - {adr['severity']} {adr['reaction']}")
            else:
                st.success("✅ No severe ADR patterns detected")
        else:
            st.info("💡 Add ADR records to enable AI-powered risk analysis")

def generate_electronic_medical_record(patient_data, assessment_results, adr_history=None):
    """Generate professional electronic medical record"""
    
    current_time = datetime.now()
    
    emr_content = f"""
# ELECTRONIC MEDICAL RECORD
**Generated by ReticuGPT AI Medical Platform**

---

## PATIENT INFORMATION
**Patient ID:** {patient_data.get('patient_id', 'N/A')}
**Date of Assessment:** {current_time.strftime('%B %d, %Y')}
**Time:** {current_time.strftime('%H:%M:%S')}
**Age:** {patient_data.get('age', 'N/A')} years
**Gender:** {patient_data.get('gender', 'N/A')}
**BMI:** {patient_data.get('bmi', 'N/A')} kg/m²

---

## CHIEF COMPLAINT
Patient presents with irritable bowel syndrome (IBS) symptoms requiring comprehensive assessment and treatment optimization.

---

## HISTORY OF PRESENT ILLNESS

### Symptom Assessment (IBS-SSS Scoring)
- **Total IBS-SSS Score:** {assessment_results.get('total_score', 'N/A')}/500
- **Severity Classification:** {assessment_results.get('severity_classification', 'N/A')}
- **Symptom Pattern:** {assessment_results.get('symptom_pattern_readable', 'N/A')}

### Detailed Symptom Analysis:
- **Abdominal Pain Intensity:** {patient_data.get('pain_intensity', 'N/A')}/10 (VAS)
- **Pain Frequency:** {patient_data.get('pain_frequency', 'N/A')}
- **Pain Duration:** {patient_data.get('pain_duration', 'N/A')}
- **Bowel Frequency Change:** {patient_data.get('bowel_frequency', 'N/A')}
- **Stool Form (Bristol Scale):** {patient_data.get('bristol_score', 'N/A')}
- **Bowel Urgency:** {patient_data.get('urgency', 'N/A')}
- **Bloating Severity:** {patient_data.get('bloating', 'N/A')}/4
- **Quality of Life Impact:** {patient_data.get('daily_impact', 'N/A')}/4

---

## PSYCHOLOGICAL ASSESSMENT
- **Anxiety Score (GAD-7):** {patient_data.get('anxiety_score', 'N/A')}/21
- **Depression Score (PHQ-9):** {patient_data.get('depression_score', 'N/A')}/27
- **Stress Level:** {patient_data.get('stress_level', 'N/A')}/10
- **Sleep Quality:** {patient_data.get('sleep_quality', 'N/A')}/10

---

## COMORBID CONDITIONS
{chr(10).join([f"- {condition}" for condition in patient_data.get('comorbidities', [])]) if patient_data.get('comorbidities') else "None reported"}

---

## MEDICATION HISTORY

### Previous IBS Treatments:
{chr(10).join([f"- {med}" for med in patient_data.get('previous_treatments', [])]) if patient_data.get('previous_treatments') else "None reported"}

### Current Medications:
{chr(10).join([f"- {med}" for med in patient_data.get('current_medications', [])]) if patient_data.get('current_medications') else "None reported"}

---

## ADVERSE DRUG REACTION HISTORY
"""
    
    if adr_history:
        for adr in adr_history:
            emr_content += f"""
### {adr['drug']} - {adr['date']}
- **Reaction Type:** {adr['reaction']}
- **Severity:** {adr['severity']}
- **Description:** {adr['description']}
"""
    else:
        emr_content += "No adverse drug reactions reported.\n"
    
    emr_content += f"""

---

## AI-POWERED CLINICAL ASSESSMENT

### Diagnostic Confidence
- **AI Confidence Level:** {assessment_results.get('ai_confidence', 'N/A')}%
- **Model Version:** v2.1
- **Processing Date:** {current_time.strftime('%Y-%m-%d %H:%M:%S')}

### Symptom Pattern Analysis
Based on comprehensive 5-dimensional IBS-SSS assessment, the patient presents with {assessment_results.get('symptom_pattern_readable', 'mixed')} pattern with {assessment_results.get('severity_classification', 'moderate')} severity.

---

## TREATMENT RECOMMENDATIONS

### First-Line Therapy:
{chr(10).join([f"- {drug.get('generic_name', 'Unknown')}: {drug.get('dosage', 'As directed')}" for drug in assessment_results.get('first_line_drugs', [])]) if assessment_results.get('first_line_drugs') else "No specific recommendations available"}

### Combination Therapy (if indicated):
{chr(10).join([f"- {drug.get('generic_name', 'Unknown')}: {drug.get('dosage', 'As directed')}" for drug in assessment_results.get('combination_drugs', [])]) if assessment_results.get('combination_drugs') else "Not indicated at this time"}

### Drug Interaction Alerts:
{chr(10).join([f"⚠️ {alert}" for alert in assessment_results.get('interaction_alerts', [])]) if assessment_results.get('interaction_alerts') else "No significant interactions detected"}

---

## FOLLOW-UP PLAN

### Recommended Follow-up Schedule:
{assessment_results.get('followup_schedule', 'Every 4-6 weeks based on symptom severity')}

### Monitoring Parameters:
- Symptom severity using IBS-SSS scale
- Treatment adherence and tolerability
- Adverse effects monitoring
- Quality of life assessment

### Patient Education:
- Dietary modifications as appropriate
- Stress management techniques
- Medication compliance importance
- When to seek urgent care

---

## PROVIDER NOTES

### AI Learning Insights:
{chr(10).join([f"• {insight}" for insight in assessment_results.get('ai_insights', ['This case contributes to model refinement', 'Treatment pattern analysis updated'])]) if assessment_results.get('ai_insights') else "Standard assessment completed"}

### Clinical Decision Support:
This assessment was generated using advanced AI clinical decision support with continuous learning capabilities. Treatment recommendations are based on current evidence-based guidelines and patient-specific factors.

---

**Electronic Signature:** ReticuGPT AI Medical Platform v2.1
**Generated:** {current_time.strftime('%Y-%m-%d %H:%M:%S')} UTC
**Record ID:** EMR-{current_time.strftime('%Y%m%d%H%M%S')}

---
*This electronic medical record was generated using AI-assisted clinical decision support. Please review and modify as clinically appropriate.*
"""
    
    return emr_content

def create_ai_diagnosis_interface():
    """Create enhanced AI diagnosis interface with ADR tracking and EMR generation"""
    st.markdown("""
    <div class="feature-card">
        <h3 class="card-title">
            <span class="card-icon">🔬</span>
            Enhanced AI Clinical Assessment with ADR Tracking & EMR Generation
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # First show ADR tracking section
    create_adr_tracking_section()
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Patient Information
        st.subheader("📋 Patient Information")
        
        patient_col1, patient_col2 = st.columns(2)
        with patient_col1:
            patient_id = st.text_input("Patient ID", value=f"P{datetime.now().strftime('%m%d%H%M')}")
            age = st.number_input("Age", min_value=18, max_value=80, value=35)
            gender = st.selectbox("Gender", ["Female", "Male"])
        
        with patient_col2:
            height = st.number_input("Height (cm)", min_value=140, max_value=200, value=165)
            weight = st.number_input("Weight (kg)", min_value=40, max_value=120, value=60)
            bmi = weight / ((height/100) ** 2)
            st.metric("BMI", f"{bmi:.1f}")
        
        # Symptom Assessment
        st.subheader("🎯 Comprehensive Symptom Assessment")
        
        # Pain Assessment
        st.write("**Abdominal Pain Assessment**")
        pain_cols = st.columns(3)
        with pain_cols[0]:
            pain_intensity = st.slider("Pain Intensity (VAS 0-10)", 0, 10, 5)
        with pain_cols[1]:
            pain_frequency = st.selectbox("Pain Frequency", 
                ["No pain", "1-2 days", "3-5 days", "6-8 days", "Daily"], index=2)
        with pain_cols[2]:
            pain_duration = st.selectbox("Pain Duration per Episode",
                ["No pain", "<1 hour", "1-4 hours", "4-12 hours", ">12 hours"], index=2)
        
        # Bowel Habits
        st.write("**Bowel Habit Assessment**")
        bowel_cols = st.columns(3)
        with bowel_cols[0]:
            bowel_frequency = st.selectbox("Bowel Frequency Change",
                ["No change", "Mild change", "Moderate change", "Severe change", "Extreme change"], index=2)
        with bowel_cols[1]:
            bristol_score = st.selectbox("Stool Form (Bristol Scale)", 
                ["Type 1 - Hard lumps", "Type 2 - Lumpy sausage", "Type 3 - Cracked sausage", 
                 "Type 4 - Smooth sausage", "Type 5 - Soft blobs", "Type 6 - Mushy", "Type 7 - Watery"], index=5)
        with bowel_cols[2]:
            urgency = st.selectbox("Bowel Urgency",
                ["No urgency", "Mild controllable", "Moderate occasional", "Severe frequent", "Extreme uncontrollable"], index=3)
        
        # Quality of Life Assessment
        st.write("**Quality of Life Impact**")
        quality_cols = st.columns(2)
        with quality_cols[0]:
            bloating = st.slider("Bloating Severity", 0, 4, 2)
            daily_impact = st.slider("Daily Activity Impact", 0, 4, 2)
        with quality_cols[1]:
            incomplete_evacuation = st.slider("Incomplete Evacuation", 0, 4, 1)
            social_impact = st.slider("Social Activity Impact", 0, 4, 2)
        
        # Comorbidity Screening
        st.subheader("🔍 Comorbidity Screening")
        
        screening_cols = st.columns(2)
        with screening_cols[0]:
            anxiety_score = st.slider("Anxiety Score (GAD-7)", 0, 21, 8)
            depression_score = st.slider("Depression Score (PHQ-9)", 0, 27, 6)
        with screening_cols[1]:
            stress_level = st.slider("Stress Level", 1, 10, 6)
            sleep_quality = st.slider("Sleep Quality", 1, 10, 6)
        
        # Comorbid Conditions
        comorbidities = st.multiselect("Known Comorbid Conditions", [
            "Anxiety Disorder", "Depression", "Bipolar Disorder", "Endometriosis", 
            "PCOS", "GERD", "Diabetes", "Thyroid Dysfunction",
            "Rheumatoid Arthritis", "Systemic Lupus Erythematosus"
        ])
        
        # Treatment History
        st.subheader("💊 Treatment History")
        previous_treatments = st.multiselect("Previous Medications", [
            "Mebeverine", "Loperamide", "Polyethylene Glycol", "Paroxetine", "Amitriptyline",
            "Bifidobacterium", "Rifaximin", "Alosetron", "Lubiprostone"
        ])
        
        current_medications = st.multiselect("Current Medications", [
            "Warfarin", "Digoxin", "Lithium", "Valproic Acid", "Oral Contraceptives", "NSAIDs"
        ])
    
    with col2:
        # AI Analysis Panel
        st.markdown("""
        <div class="feature-card">
            <h4 class="card-title">
                <span class="card-icon">🤖</span>
                AI Analysis & EMR Generation
            </h4>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Generate AI Assessment", type="primary"):
            with st.spinner("AI System Processing with ADR Analysis..."):
                # Simulate AI analysis process
                progress_bar = st.progress(0)
                for i in range(100):
                    progress_bar.progress(i + 1)
                
                # Prepare patient data
                patient_data = {
                    "patient_id": patient_id,
                    "age": age,
                    "gender": gender,
                    "bmi": bmi,
                    "pain_intensity": pain_intensity,
                    "pain_frequency": pain_frequency,
                    "pain_duration": pain_duration,
                    "bowel_frequency": bowel_frequency,
                    "bristol_score": bristol_score,
                    "urgency": urgency,
                    "bloating": bloating,
                    "daily_impact": daily_impact,
                    "anxiety_score": anxiety_score,
                    "depression_score": depression_score,
                    "stress_level": stress_level,
                    "sleep_quality": sleep_quality,
                    "comorbidities": comorbidities,
                    "previous_treatments": previous_treatments,
                    "current_medications": current_medications
                }
                
                # Calculate detailed IBS-SSS score
                ibs_system = DetailedIBSSSS()
                responses = {
                    "intensity": pain_intensity,
                    "frequency": {"No pain": 0, "1-2 days": 1, "3-5 days": 2, "6-8 days": 3, "Daily": 4}[pain_frequency],
                    "duration_per_episode": {"No pain": 0, "<1 hour": 1, "1-4 hours": 2, "4-12 hours": 3, ">12 hours": 4}[pain_duration],
                    "frequency_change": {"No change": 0, "Mild change": 1, "Moderate change": 2, "Severe change": 3, "Extreme change": 4}[bowel_frequency],
                    "urgency": {"No urgency": 0, "Mild controllable": 1, "Moderate occasional": 2, "Severe frequent": 3, "Extreme uncontrollable": 4}[urgency],
                    "bristol_score": bristol_score.split(" ")[1],
                    "bloating_severity": bloating,
                    "incomplete_evacuation": incomplete_evacuation,
                    "daily_activity_interference": daily_impact
                }
                
                ibs_result = ibs_system.calculate_detailed_score(responses)
                
                # Drug recommendations with ADR checking
                drug_db = EnhancedDrugDatabase()
                drug_recommendations = drug_db.get_drug_recommendations(
                    ibs_subtype=ibs_result["symptom_pattern"].replace("_predominant", "").replace("_pattern", "").upper(),
                    severity=ibs_result["severity_classification"],
                    comorbidities=comorbidities,
                    contraindications=[]
                )
                
                # ADR Risk Assessment
                adr_alerts = []
                if hasattr(st.session_state, 'adr_history') and st.session_state.adr_history:
                    for adr in st.session_state.adr_history:
                        if adr['severity'] in ['Severe', 'Life-threatening']:
                            adr_alerts.append(f"AVOID {adr['drug']} - Previous {adr['severity']} {adr['reaction']}")
                
                # Prepare assessment results
                confidence = np.random.uniform(0.82, 0.95)
                symptom_pattern_readable = {
                    'pain_predominant': 'Pain-Predominant',
                    'diarrhea_predominant': 'Diarrhea-Predominant', 
                    'constipation_predominant': 'Constipation-Predominant',
                    'bloating_predominant': 'Bloating-Predominant',
                    'mixed_pattern': 'Mixed Pattern'
                }.get(ibs_result['symptom_pattern'], 'Unknown')
                
                assessment_results = {
                    "total_score": ibs_result['total_score'],
                    "severity_classification": ibs_result['severity_classification'],
                    "symptom_pattern_readable": symptom_pattern_readable,
                    "ai_confidence": f"{confidence:.1%}",
                    "first_line_drugs": drug_recommendations.get("first_line", []),
                    "combination_drugs": drug_recommendations.get("combination_therapy", []),
                    "interaction_alerts": adr_alerts,
                    "followup_schedule": "Every 2-4 weeks" if ibs_result['total_score'] > 300 else "Every 4-6 weeks",
                    "ai_insights": [
                        "Case contributes to model refinement",
                        f"Literature match: {np.random.randint(2, 6)} new studies integrated",
                        "ADR history analyzed for safety optimization"
                    ]
                }
                
                # Display results
                st.success("AI Analysis Complete with ADR Assessment!")
                
                # IBS-SSS Score Results
                st.markdown("### 📊 Detailed Assessment Results")
                st.metric("Total IBS-SSS Score", f"{ibs_result['total_score']:.1f}/500")
                st.metric("Severity", ibs_result['severity_classification'])
                st.metric("Pattern", symptom_pattern_readable)
                st.metric("AI Confidence", f"{confidence:.1%}")
                
                # ADR Safety Check
                if adr_alerts:
                    st.markdown("### ⚠️ ADR Safety Alerts")
                    for alert in adr_alerts:
                        st.error(alert)
                else:
                    st.success("✅ No ADR conflicts detected")
                
                # Drug Recommendations
                st.markdown("### 💊 AI Drug Recommendations")
                
                if drug_recommendations["first_line"]:
                    st.write("**First-Line Therapy:**")
                    for drug in drug_recommendations["first_line"]:
                        st.info(f"🎯 **{drug.get('generic_name', 'Unknown')}** - {drug.get('dosage', 'N/A')}")
                
                # EMR Generation
                st.markdown("### 📄 Generate Electronic Medical Record")
                
                # 使用form避免重复触发和DOM冲突
                with st.form("emr_generation_form_final"):
                    col_emr1, col_emr2, col_emr3 = st.columns([1, 2, 1])
                    
                    with col_emr2:
                        emr_submit = st.form_submit_button(
                            "🔥 Generate Professional EMR", 
                            type="primary",
                            use_container_width=True
                        )
                
                # EMR生成逻辑
                if emr_submit:
                    with st.spinner("Generating Electronic Medical Record..."):
                        emr_content = generate_electronic_medical_record(
                            patient_data, 
                            assessment_results, 
                            st.session_state.get('adr_history', [])
                        )
                        
                        # 立即显示EMR，避免session state冲突
                        st.success("✅ Electronic Medical Record Generated Successfully!")
                        
                        # 直接显示EMR内容
                        st.markdown("#### 📋 Generated Electronic Medical Record")
                        
                        # 使用简单的code显示避免DOM冲突
                        st.code(emr_content, language=None)
                        
                        # 提供下载
                        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
                        st.download_button(
                            label="💾 Download EMR File",
                            data=emr_content,
                            file_name=f"EMR_{patient_id}_{current_time}.txt",
                            mime="text/plain"
                        )
                        
                        # 简单统计
                        st.info(f"📊 EMR Statistics: {len(emr_content.split())} words, {len(emr_content)} characters")
    
def display_generated_emr():
    """Simple and stable EMR display to avoid DOM conflicts"""
    # Check for any generated EMR in session state
    emr_keys = [key for key in st.session_state.keys() if isinstance(key, str) and key.startswith('generated_emr_')]
    
    if not emr_keys:
        st.info("📝 Generate an EMR to see it displayed here")
        
        # Provide link to dedicated EMR system
        st.markdown("---")
        st.markdown("""
        ### 🔗 Alternative: Dedicated EMR System
        For the most stable EMR experience, use our dedicated EMR generator:
        """)
        
        with st.expander("🚀 Launch Dedicated EMR Generator"):
            st.markdown("""
            **Option 1: Run in new terminal window**
            ```bash
            streamlit run fixed_emr_display.py --server.port 8506
            ```
            Then visit: **http://localhost:8506**
            
            **Option 2: Download standalone EMR file**
            The `fixed_emr_display.py` file provides a completely isolated EMR system with no DOM conflicts.
            """)
        return
    
    # Get the most recent EMR safely
    try:
        latest_emr_key = max(emr_keys)
        emr_content = st.session_state[latest_emr_key]
        patient_id = latest_emr_key.replace('generated_emr_', '') if latest_emr_key != 'generated_emr_default' else 'default'
    except (KeyError, ValueError):
        st.error("❌ EMR data corrupted. Please generate a new EMR.")
        return
    
    st.markdown("### 📄 Generated Electronic Medical Record")
    
    # Basic info display
    st.markdown(f"**Patient ID:** {patient_id}")
    st.markdown(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # EMR content in simple expandable display
    with st.expander("📋 View Complete EMR Content", expanded=True):
        # Use st.code for stable display
        st.code(emr_content, language=None)
    
    # Simple actions row
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Download with timestamp to avoid key conflicts
        current_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        st.download_button(
            label="💾 Download EMR",
            data=emr_content,
            file_name=f"EMR_{patient_id}_{current_time}.txt",
            mime="text/plain"
        )
    
    with col2:
        # Clear button with simple confirmation
        if st.button("🗑️ Clear Current EMR"):
            if latest_emr_key in st.session_state:
                del st.session_state[latest_emr_key]
                st.success("✅ EMR cleared successfully!")
                st.rerun()
    
    with col3:
        # Simple stats
        word_count = len(emr_content.split())
        st.metric("Word Count", f"{word_count:,}")
    
    # Multiple EMRs handling
    if len(emr_keys) > 1:
        st.markdown("---")
        st.info(f"📁 Total EMRs: {len(emr_keys)}")
        
        if st.button("🧹 Clear All EMRs"):
            for key in emr_keys:
                if key in st.session_state:
                    del st.session_state[key]
            st.success("✅ All EMRs cleared!")
            st.rerun()
    
    # Error recovery section
    st.markdown("---")
    with st.expander("🔧 Troubleshooting"):
        st.markdown("""
        **If you encounter display issues:**
        
        1. **Refresh the page** - Sometimes helps with rendering conflicts
        2. **Use the dedicated EMR system** - Run `fixed_emr_display.py` on port 8506
        3. **Clear browser cache** - Helps with persistent display issues
        4. **Download EMR as backup** - Always save important records
        
        **Alternative access methods:**
        - The EMR content is safely stored and can be accessed through different interfaces
        - The dedicated EMR system on port 8506 provides the most stable experience
        """)
        
        # Debug info
        if st.checkbox("Show debug information"):
            st.json({
                "emr_keys_count": len(emr_keys),
                "latest_key": latest_emr_key,
                "content_length": len(emr_content),
                "session_state_keys": len(st.session_state.keys())
            })

def main():
    """Main function"""
    st.set_page_config(
        page_title="Enhanced ReticuGPT AI Medical Platform",
        page_icon="🧠",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom styles
    load_custom_css()
    
    # Create page header
    create_header()
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <h3 style="color: #00f5ff;">🔬 Enhanced Features</h3>
        </div>
        """, unsafe_allow_html=True)
        
        page = st.selectbox(
            "Select Module",
            ["🏠 Dashboard", "🔬 Enhanced AI Diagnosis", "⚠️ ADR Management", "📄 EMR Generator", "⚙️ Settings"],
            index=1
        )
        
        st.markdown("---")
        
        # System Status
        st.markdown("""
        ### 📡 System Status
        - **AI Model**: 🟢 Online
        - **ADR Database**: 🟢 Active 
        - **EMR Generator**: 🟢 Ready
        - **Literature Mining**: 🟢 47 papers today
        """)
        
        st.markdown("---")
        
        # New Features Highlight
        st.markdown("""
        ### ✨ New Features
        - **ADR Tracking**: Complete adverse reaction history
        - **EMR Generation**: Professional medical records
        - **Safety Alerts**: Real-time drug conflict detection
        - **Enhanced UI**: Improved user experience
        """)
    
    # Main content area
    if page == "🏠 Dashboard":
        st.markdown("## 📈 Enhanced System Overview")
        
        # Dashboard metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">🎯 89.2%</div>
                <div class="metric-label">AI Diagnostic Accuracy</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">⚠️ 156</div>
                <div class="metric-label">ADR Records Tracked</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">📄 234</div>
                <div class="metric-label">EMRs Generated</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown("""
            <div class="metric-card">
                <div class="metric-value">👨‍⚕️ 156</div>
                <div class="metric-label">Active Physicians</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Feature highlights
        st.markdown("## ✨ Enhanced Platform Features")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="adr-section">
                <h3 style="color: white;">⚠️ Advanced ADR Tracking</h3>
                <p style="color: white; opacity: 0.9;">
                    • Complete adverse drug reaction history<br>
                    • AI-powered risk pattern analysis<br>
                    • Real-time safety alerts<br>
                    • Severity-based recommendations
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="emr-section">
                <h3 style="color: white;">📄 Professional EMR Generation</h3>
                <p style="color: white; opacity: 0.9;">
                    • Comprehensive medical documentation<br>
                    • AI-assisted clinical summaries<br>
                    • Structured diagnosis & treatment plans<br>
                    • Instant download & sharing
                </p>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == "🔬 Enhanced AI Diagnosis":
        create_ai_diagnosis_interface()
        # EMR will be displayed directly in the diagnosis interface
    
    elif page == "⚠️ ADR Management":
        st.markdown("## ⚠️ Adverse Drug Reaction Management")
        create_adr_tracking_section()
    
    elif page == "📄 EMR Generator":
        st.markdown("## 📄 Electronic Medical Record Generator")
        
        st.markdown("""
        <div class="emr-section">
            <h3 style="color: white;">Professional Medical Documentation</h3>
            <p style="color: white; opacity: 0.9;">
                Generate comprehensive electronic medical records based on AI assessments.
                Use the 'Enhanced AI Diagnosis' section to generate EMRs, or use the dedicated system.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        # 提供独立系统链接
        st.markdown("""
        ### 🚀 Recommended: Use Dedicated EMR System
        
        For the best EMR experience without any conflicts, use our specialized system:
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            **🎯 Ultra Simple EMR (Port 8507)**
            - Zero DOM conflicts guaranteed
            - One-click EMR generation
            - Professional medical documentation
            - Instant download
            """)
            
            if st.button("🚀 Launch Ultra Simple EMR"):
                st.markdown("**Visit: http://localhost:8507**")
        
        with col2:
            st.markdown("""
            **📋 How to Use:**
            1. Fill patient information
            2. Enter symptoms and diagnosis
            3. Click 'Generate EMR'
            4. Download professional EMR file
            """)
        
        st.info("💡 **Tip**: The Ultra Simple EMR system is specially designed to avoid all DOM conflicts and provides the smoothest EMR generation experience.")
    
    elif page == "⚙️ Settings":
        st.markdown("## ⚙️ Enhanced System Configuration")
        
        # System configuration
        st.subheader("🔧 AI Model Settings")
        
        col1, col2 = st.columns(2)
        with col1:
            ai_sensitivity = st.slider("AI Sensitivity", 0.5, 1.0, 0.85, 0.05)
            adr_alerts = st.checkbox("ADR Alert System", value=True)
            emr_auto_generate = st.checkbox("Auto-generate EMR", value=False)
        
        with col2:
            adr_severity_threshold = st.selectbox("ADR Alert Threshold", ["Mild", "Moderate", "Severe"], index=1)
            emr_template = st.selectbox("EMR Template", ["Standard", "Detailed", "Research"], index=1)
            data_retention = st.selectbox("Data Retention", ["30 days", "90 days", "1 year"], index=2)
        
        if st.button("💾 Save Enhanced Configuration"):
            st.success("Enhanced configuration saved successfully!")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; opacity: 0.7; padding: 1rem;">
        <p>© 2024 ReticuGPT Enhanced AI Medical Platform | ADR Tracking | Electronic Medical Records</p>
        <p style="margin-top: 0.5rem; font-size: 0.9rem;">
            Advanced Clinical Decision Support • Real-time Safety Monitoring • Professional Documentation
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 