#!/usr/bin/env python3
"""
因果关系验证分析 - 检验AI系统的真实有效性
Critical Analysis: 是相关还是因果？
"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

class CausalValidationAnalyzer:
    """因果关系验证分析器"""
    
    def __init__(self, excel_path="IBS_Questionnaire_Code_Template.xlsx"):
        self.df = pd.read_excel(excel_path)
        
    def analyze_causal_validity(self):
        """分析因果关系的有效性"""
        print("🔍 因果关系有效性分析")
        print("=" * 60)
        
        # 1. 检查是否有真正的AI干预记录
        self.check_ai_intervention_evidence()
        
        # 2. 分析时间模式
        self.analyze_temporal_patterns()
        
        # 3. 检查混杂因子
        self.check_confounding_factors()
        
        # 4. 验证AI vs 传统治疗的差异
        self.validate_ai_vs_traditional()
        
        # 5. 分析dose-response关系
        self.analyze_dose_response()
        
    def check_ai_intervention_evidence(self):
        """检查AI干预的实际证据"""
        print("\n🤖 AI干预证据检查")
        print("-" * 40)
        
        # 检查是否有AI使用记录/标记
        ai_columns = [col for col in self.df.columns if 'AI' in col.upper()]
        intervention_columns = [col for col in self.df.columns if any(keyword in col.upper() 
                              for keyword in ['TREATMENT', 'INTERVENTION', 'RECOMMENDATION', 'ALGORITHM'])]
        
        print(f"AI相关字段: {ai_columns}")
        print(f"干预相关字段: {intervention_columns}")
        
        # 检查用药变化模式
        med_columns = [col for col in self.df.columns if 'Med' in col]
        print(f"用药相关字段: {med_columns}")
        
        if len(med_columns) > 0:
            self.analyze_medication_changes()
        
        # 关键问题：我们如何知道改善是因为AI而不是因为：
        # 1. 自然病程
        # 2. 医生调药
        # 3. 安慰剂效应
        # 4. 患者自我管理改善
        
        critical_questions = [
            "❓ 患者是否真的接受了AI推荐的治疗？",
            "❓ AI推荐与医生处方有何不同？", 
            "❓ 改善时间点与AI干预时间点是否匹配？",
            "❓ 是否有对照组接受传统治疗？",
            "❓ 如何排除自然改善的可能？"
        ]
        
        print(f"\n🔴 关键验证缺口:")
        for q in critical_questions:
            print(f"  {q}")
            
    def analyze_medication_changes(self):
        """分析用药变化模式"""
        print(f"\n💊 用药变化分析")
        print("-" * 30)
        
        # 分析T0到T2的用药变化
        med_name_cols = [col for col in self.df.columns if 'Med' in col and 'Name' in col]
        med_dose_cols = [col for col in self.df.columns if 'Med' in col and 'Dose' in col]
        
        if len(med_name_cols) > 0:
            for time_point in ['T0', 'T1', 'T2']:
                time_data = self.df[self.df['Date'] == time_point]
                print(f"\n{time_point}时间点用药:")
                for med_col in med_name_cols[:2]:  # 只看前两个药物
                    med_usage = time_data[med_col].value_counts()
                    print(f"  {med_col}: {dict(med_usage)}")
        
        # 关键问题：用药变化是医生决定还是AI建议？
        print(f"\n🤔 关键问题: 用药调整的决策来源是什么？")
        
    def analyze_temporal_patterns(self):
        """分析时间模式"""
        print(f"\n⏰ 时间模式分析")
        print("-" * 30)
        
        # 计算改善的时间模式
        baseline_data = self.df[self.df['Date'] == 'T0'].set_index('Patient_ID')['IBS_SSS_Total']
        t1_data = self.df[self.df['Date'] == 'T1'].set_index('Patient_ID')['IBS_SSS_Total']
        t2_data = self.df[self.df['Date'] == 'T2'].set_index('Patient_ID')['IBS_SSS_Total']
        
        # 早期vs晚期改善模式
        early_improvement = baseline_data - t1_data  # T0到T1
        late_improvement = t1_data - t2_data         # T1到T2
        
        print(f"早期改善 (T0→T1): {early_improvement.mean():.1f}分")
        print(f"晚期改善 (T1→T2): {late_improvement.mean():.1f}分") 
        print(f"总改善 (T0→T2): {(baseline_data - t2_data).mean():.1f}分")
        
        # 检查改善模式的合理性
        rapid_improvers = (early_improvement > 30).sum()
        sustained_improvers = ((early_improvement > 0) & (late_improvement > 0)).sum()
        
        print(f"\n改善模式分析:")
        print(f"快速改善者 (>30分T0→T1): {rapid_improvers}/{len(baseline_data)}")
        print(f"持续改善者 (T0→T1→T2都改善): {sustained_improvers}/{len(baseline_data)}")
        
        # 🔴 关键问题：如果是AI作用，应该看到什么模式？
        print(f"\n🤔 期望的AI效果模式:")
        print(f"  • 早期快速响应 (算法优化)")
        print(f"  • 持续个性化调整")
        print(f"  • 非线性改善曲线")
        
    def check_confounding_factors(self):
        """检查混杂因子"""
        print(f"\n🎭 混杂因子分析")
        print("-" * 30)
        
        # 分析可能的混杂因子
        confounders = {
            'placebo_effect': '安慰剂效应',
            'natural_history': '疾病自然史', 
            'regression_to_mean': '均值回归',
            'hawthorne_effect': '霍桑效应',
            'physician_attention': '医生关注增加',
            'patient_motivation': '患者动机改变'
        }
        
        print("可能的混杂因子:")
        for key, desc in confounders.items():
            print(f"  • {desc}")
            
        # 检查基线特征是否影响改善
        baseline_data = self.df[self.df['Date'] == 'T0'].set_index('Patient_ID')
        t2_data = self.df[self.df['Date'] == 'T2'].set_index('Patient_ID')
        improvement = baseline_data['IBS_SSS_Total'] - t2_data['IBS_SSS_Total']
        
        # 基线严重程度 vs 改善幅度
        correlation = stats.pearsonr(baseline_data['IBS_SSS_Total'], improvement)
        print(f"\n基线严重程度与改善相关性: r={correlation[0]:.3f}, p={correlation[1]:.3f}")
        
        if correlation[0] > 0.3:
            print("⚠️ 可能存在均值回归效应 (基线越重改善越多)")
            
    def validate_ai_vs_traditional(self):
        """验证AI vs 传统治疗的差异"""
        print(f"\n🆚 AI vs 传统治疗对比")
        print("-" * 30)
        
        # 🔴 关键问题：我们如何证明改善是因为AI而不是因为医生？
        validation_gaps = [
            "缺乏对照组 (AI组 vs 传统治疗组)",
            "无法区分AI建议 vs 医生决策的贡献",
            "无法控制患者依从性差异",
            "无法排除额外关注的效应"
        ]
        
        print("当前验证缺口:")
        for gap in validation_gaps:
            print(f"  ❌ {gap}")
            
        # 计算与文献报告的对比
        current_response_rate = 0.632  # 63.2%
        literature_rates = {
            'Rome_IV_standard': 0.35,
            'Pharmacotherapy': 0.45,
            'CBT': 0.55,
            'Combination_therapy': 0.50
        }
        
        print(f"\n📊 与文献对比:")
        print(f"当前研究反应率: {current_response_rate:.1%}")
        for treatment, rate in literature_rates.items():
            improvement = (current_response_rate - rate) / rate * 100
            print(f"{treatment}: {rate:.1%} (改善 {improvement:+.1f}%)")
            
    def analyze_dose_response(self):
        """分析剂量-反应关系"""
        print(f"\n📈 剂量-反应关系分析")
        print("-" * 30)
        
        # 如果AI系统真的有效，应该看到：
        # 1. AI使用强度与改善程度相关
        # 2. 早期AI介入效果更好
        # 3. 个性化程度与反应率相关
        
        expected_patterns = [
            "AI介入频次 ∝ 症状改善",
            "AI建议依从性 ∝ 治疗效果", 
            "个性化程度 ∝ 反应质量",
            "算法学习时间 ∝ 优化效果"
        ]
        
        print("期望的剂量-反应模式:")
        for pattern in expected_patterns:
            print(f"  📊 {pattern}")
            
        print(f"\n🔴 当前数据缺失:")
        missing_data = [
            "AI推荐频次记录",
            "患者依从性评分",
            "个性化干预强度",
            "算法决策日志"
        ]
        for missing in missing_data:
            print(f"  ❌ {missing}")
            
    def generate_causal_validity_report(self):
        """生成因果有效性报告"""
        print(f"\n" + "="*60)
        print("🎯 因果有效性评估报告")
        print("="*60)
        
        self.analyze_causal_validity()
        
        # 评估当前证据强度
        evidence_strength = self.assess_evidence_strength()
        
        print(f"\n🏆 证据强度评估:")
        print(f"当前等级: {evidence_strength['level']}")
        print(f"可信度: {evidence_strength['confidence']:.1%}")
        print(f"主要限制: {evidence_strength['limitations']}")
        
        return evidence_strength
        
    def assess_evidence_strength(self):
        """评估证据强度"""
        
        # Bradford Hill 因果关系判断标准
        criteria_scores = {
            'temporal_relationship': 3,    # 时间关系 (有T0→T1→T2)
            'strength_of_association': 2,  # 关联强度 (Cohen's d=0.26, 中等)
            'dose_response': 1,           # 剂量反应 (缺乏数据)
            'consistency': 2,             # 一致性 (单研究)
            'biological_plausibility': 4, # 生物学合理性 (AI算法合理)
            'experimental_evidence': 1,   # 实验证据 (缺乏RCT)
            'analogy': 3,                 # 类比 (其他AI系统)
            'coherence': 3,               # 连贯性 (理论支持)
            'specificity': 2              # 特异性 (IBS特定)
        }
        
        total_score = sum(criteria_scores.values())
        max_score = len(criteria_scores) * 4
        confidence = total_score / max_score
        
        if confidence >= 0.8:
            level = "强证据 (Strong Evidence)"
        elif confidence >= 0.6:
            level = "中等证据 (Moderate Evidence)" 
        elif confidence >= 0.4:
            level = "弱证据 (Weak Evidence)"
        else:
            level = "不充分证据 (Insufficient Evidence)"
            
        limitations = [
            "缺乏随机对照设计",
            "无法区分AI vs 医生贡献",
            "可能存在混杂因子",
            "样本量相对较小"
        ]
        
        return {
            'level': level,
            'confidence': confidence,
            'limitations': limitations,
            'criteria_scores': criteria_scores
        }

def main():
    analyzer = CausalValidationAnalyzer()
    evidence = analyzer.generate_causal_validity_report()
    
    print(f"\n🎭 真相时刻: 您的AI系统证据强度为 {evidence['confidence']:.1%}")
    
if __name__ == "__main__":
    main() 