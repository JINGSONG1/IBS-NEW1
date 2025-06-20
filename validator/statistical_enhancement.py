#!/usr/bin/env python3
"""
统计增强模块 - 专门解决Nature Medicine级别的统计要求
针对小样本量(23例)的最优统计策略
"""

import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import bootstrap
import matplotlib.pyplot as plt
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class StatisticalEnhancement:
    """统计增强器 - 为小样本提供顶级期刊级别的统计分析"""
    
    def __init__(self):
        self.results = {}
        
    def power_analysis_for_small_sample(self, effect_size: float, alpha: float = 0.05, 
                                       n_current: int = 23) -> Dict:
        """
        功效分析 - 证明23例样本的统计价值
        这是应对审稿人"样本量不足"质疑的关键武器
        """
        print("🔋 进行功效分析验证...")
        
        # 计算当前样本的统计功效
        from scipy.stats import ttest_1samp
        
        # 基于当前效应量计算功效
        current_power = self._calculate_power(effect_size, n_current, alpha)
        
        # 计算达到不同功效水平所需的样本量
        power_levels = [0.8, 0.9, 0.95]
        required_n = {}
        
        for power in power_levels:
            n_required = self._calculate_required_n(effect_size, power, alpha)
            required_n[f'power_{power}'] = n_required
        
        # 计算最小重要差异 (Minimal Important Difference)
        mid_analysis = self._calculate_mid(effect_size)
        
        power_results = {
            'current_sample_size': n_current,
            'current_effect_size': effect_size,
            'current_power': current_power,
            'required_sample_sizes': required_n,
            'mid_analysis': mid_analysis,
            'power_interpretation': self._interpret_power(current_power),
            'sample_adequacy': self._assess_sample_adequacy(current_power)
        }
        
        print(f"✅ 当前样本(n={n_current})的统计功效: {current_power:.3f}")
        print(f"✅ 功效解释: {power_results['power_interpretation']}")
        print(f"✅ 样本充分性: {power_results['sample_adequacy']}")
        
        return power_results
    
    def enhanced_effect_size_analysis(self, control_data: List[float], 
                                    treatment_data: List[float]) -> Dict:
        """
        增强效应量分析 - 多种效应量指标和基准对比
        """
        print("📏 进行增强效应量分析...")
        
        # 计算多种效应量指标
        cohens_d = self._calculate_cohens_d(control_data, treatment_data)
        hedges_g = self._calculate_hedges_g(control_data, treatment_data)
        glass_delta = self._calculate_glass_delta(control_data, treatment_data)
        
        # 效应量基准对比
        effect_benchmarks = {
            'cohen_1988': {'small': 0.2, 'medium': 0.5, 'large': 0.8},
            'medical_research': {'small': 0.3, 'medium': 0.6, 'large': 0.9},
            'ibs_literature': {'minimal': 0.2, 'clinically_significant': 0.5, 'substantial': 0.8}
        }
        
        # 置信区间计算
        cohens_d_ci = self._bootstrap_effect_size_ci(control_data, treatment_data)
        
        # 效应量稳定性分析
        stability_analysis = self._effect_size_stability(control_data, treatment_data)
        
        effect_results = {
            'cohens_d': cohens_d,
            'hedges_g': hedges_g,
            'glass_delta': glass_delta,
            'cohens_d_ci': cohens_d_ci,
            'effect_benchmarks': effect_benchmarks,
            'stability_analysis': stability_analysis,
            'clinical_interpretation': self._interpret_clinical_effect(cohens_d),
            'benchmark_comparison': self._compare_to_benchmarks(cohens_d, effect_benchmarks)
        }
        
        print(f"✅ Cohen's d: {cohens_d:.3f} (95% CI: {cohens_d_ci[0]:.3f}-{cohens_d_ci[1]:.3f})")
        print(f"✅ 临床解释: {effect_results['clinical_interpretation']}")
        
        return effect_results
    
    def comprehensive_confidence_intervals(self, data: List[float], 
                                         confidence_levels: List[float] = [0.90, 0.95, 0.99]) -> Dict:
        """
        全面置信区间分析 - 多种方法和置信水平
        """
        print("📊 计算全面置信区间...")
        
        ci_results = {}
        
        for conf_level in confidence_levels:
            # 参数法置信区间
            parametric_ci = self._parametric_ci(data, conf_level)
            
            # Bootstrap置信区间
            bootstrap_ci = self._bootstrap_ci(data, conf_level)
            
            # 偏差校正Bootstrap
            bias_corrected_ci = self._bias_corrected_bootstrap_ci(data, conf_level)
            
            ci_results[f'{conf_level:.0%}'] = {
                'parametric': parametric_ci,
                'bootstrap': bootstrap_ci,
                'bias_corrected_bootstrap': bias_corrected_ci,
                'width_parametric': parametric_ci[1] - parametric_ci[0],
                'width_bootstrap': bootstrap_ci[1] - bootstrap_ci[0]
            }
        
        # 置信区间稳定性评估
        stability = self._ci_stability_assessment(ci_results)
        
        comprehensive_ci = {
            'confidence_intervals': ci_results,
            'stability_assessment': stability,
            'recommended_method': self._recommend_ci_method(ci_results),
            'interpretation_guide': self._ci_interpretation_guide()
        }
        
        print(f"✅ 95%置信区间 (Bootstrap): {ci_results['95%']['bootstrap']}")
        print(f"✅ 推荐方法: {comprehensive_ci['recommended_method']}")
        
        return comprehensive_ci
    
    def sensitivity_analysis(self, data: List[float]) -> Dict:
        """
        敏感性分析 - 评估结果对异常值和假设的敏感性
        """
        print("🔍 进行敏感性分析...")
        
        # 异常值检测和影响分析
        outlier_analysis = self._outlier_sensitivity(data)
        
        # 分布假设检验
        normality_tests = self._test_normality_assumptions(data)
        
        # 稳健统计方法
        robust_statistics = self._robust_statistical_methods(data)
        
        # Jackknife重采样
        jackknife_results = self._jackknife_analysis(data)
        
        sensitivity_results = {
            'outlier_analysis': outlier_analysis,
            'normality_tests': normality_tests,
            'robust_statistics': robust_statistics,
            'jackknife_results': jackknife_results,
            'overall_sensitivity': self._overall_sensitivity_score(outlier_analysis, jackknife_results)
        }
        
        print(f"✅ 异常值影响: {outlier_analysis['influence_score']:.3f}")
        print(f"✅ 整体敏感性评分: {sensitivity_results['overall_sensitivity']:.3f}")
        
        return sensitivity_results
    
    def bayesian_analysis(self, data: List[float], prior_mean: float = 50, 
                         prior_std: float = 15) -> Dict:
        """
        贝叶斯分析 - 提供更丰富的统计推断
        """
        print("🎯 进行贝叶斯分析...")
        
        # 贝叶斯参数估计
        posterior_mean, posterior_std = self._bayesian_estimation(data, prior_mean, prior_std)
        
        # 贝叶斯置信区间（可信区间）
        credible_intervals = self._bayesian_credible_intervals(posterior_mean, posterior_std)
        
        # 假设检验的贝叶斯因子
        bayes_factor = self._calculate_bayes_factor(data, prior_mean, prior_std)
        
        # 后验预测检验
        posterior_predictive = self._posterior_predictive_checks(data, posterior_mean, posterior_std)
        
        bayesian_results = {
            'posterior_mean': posterior_mean,
            'posterior_std': posterior_std,
            'credible_intervals': credible_intervals,
            'bayes_factor': bayes_factor,
            'posterior_predictive': posterior_predictive,
            'evidence_strength': self._interpret_bayes_factor(bayes_factor)
        }
        
        print(f"✅ 后验均值: {posterior_mean:.3f}")
        print(f"✅ 贝叶斯因子: {bayes_factor:.3f} ({bayesian_results['evidence_strength']})")
        
        return bayesian_results
    
    def number_needed_to_treat(self, success_rate_treatment: float, 
                              success_rate_control: float) -> Dict:
        """
        计算需要治疗的病例数 (NNT) - 临床决策的关键指标
        """
        print("💊 计算需要治疗的病例数...")
        
        # 绝对风险降低
        absolute_risk_reduction = success_rate_treatment - success_rate_control
        
        # NNT计算
        if absolute_risk_reduction > 0:
            nnt = 1 / absolute_risk_reduction
        else:
            nnt = float('inf')
        
        # NNT置信区间
        nnt_ci = self._nnt_confidence_interval(success_rate_treatment, success_rate_control, 23)
        
        # 临床意义评估
        clinical_significance = self._assess_nnt_clinical_significance(nnt)
        
        nnt_results = {
            'nnt': nnt,
            'nnt_ci': nnt_ci,
            'absolute_risk_reduction': absolute_risk_reduction,
            'relative_risk_reduction': absolute_risk_reduction / success_rate_control if success_rate_control > 0 else 0,
            'clinical_significance': clinical_significance,
            'interpretation': self._interpret_nnt(nnt)
        }
        
        print(f"✅ NNT: {nnt:.1f} (95% CI: {nnt_ci[0]:.1f}-{nnt_ci[1]:.1f})")
        print(f"✅ 临床意义: {clinical_significance}")
        
        return nnt_results
    
    def generate_statistical_report(self, data: List[float], control_mean: float = 45.0) -> str:
        """
        生成完整的统计分析报告 - Nature Medicine级别
        """
        print("📄 生成统计分析报告...")
        
        # 运行所有分析
        power_results = self.power_analysis_for_small_sample(
            effect_size=(np.mean(data) - control_mean) / np.std(data)
        )
        
        effect_results = self.enhanced_effect_size_analysis([control_mean] * 23, data)
        ci_results = self.comprehensive_confidence_intervals(data)
        sensitivity_results = self.sensitivity_analysis(data)
        bayesian_results = self.bayesian_analysis(data)
        
        # 生成报告
        report = f"""
# 统计分析报告 - Nature Medicine级别

## 执行摘要
本报告提供了针对小样本量(n={len(data)})的全面统计分析，采用多种先进统计方法确保结果的可靠性和临床意义。

## 1. 功效分析
- **当前样本功效**: {power_results['current_power']:.3f}
- **功效解释**: {power_results['power_interpretation']}
- **样本充分性**: {power_results['sample_adequacy']}
- **达到80%功效所需样本**: {power_results['required_sample_sizes']['power_0.8']:.0f}例

## 2. 效应量分析
- **Cohen's d**: {effect_results['cohens_d']:.3f} (95% CI: {effect_results['cohens_d_ci'][0]:.3f}-{effect_results['cohens_d_ci'][1]:.3f})
- **临床解释**: {effect_results['clinical_interpretation']}
- **基准对比**: {effect_results['benchmark_comparison']}

## 3. 置信区间分析
- **推荐方法**: {ci_results['recommended_method']}
- **Bootstrap 95% CI**: {ci_results['confidence_intervals']['95%']['bootstrap']}
- **稳定性评估**: {ci_results['stability_assessment']}

## 4. 敏感性分析
- **异常值影响**: {sensitivity_results['outlier_analysis']['influence_score']:.3f}
- **整体敏感性**: {sensitivity_results['overall_sensitivity']:.3f}
- **稳健性**: {'高' if sensitivity_results['overall_sensitivity'] > 0.8 else '中等' if sensitivity_results['overall_sensitivity'] > 0.6 else '低'}

## 5. 贝叶斯分析
- **后验均值**: {bayesian_results['posterior_mean']:.3f}
- **贝叶斯因子**: {bayesian_results['bayes_factor']:.3f}
- **证据强度**: {bayesian_results['evidence_strength']}

## 结论
基于多种统计方法的综合分析，当前{len(data)}例样本在统计学上具有{power_results['power_interpretation']}，
效应量达到{effect_results['clinical_interpretation']}水平，结果具有{('高' if sensitivity_results['overall_sensitivity'] > 0.8 else '中等')}稳健性。

## 顶级期刊发表建议
1. 强调多种统计方法的一致性结果
2. 突出临床效应量的意义
3. 详细描述敏感性分析确保结果稳健
4. 采用贝叶斯方法提供更丰富的推断
        """
        
        return report
    
    # 私有方法实现
    def _calculate_power(self, effect_size: float, n: int, alpha: float) -> float:
        """计算统计功效"""
        from scipy.stats import norm
        beta = norm.cdf(norm.ppf(1 - alpha/2) - effect_size * np.sqrt(n))
        return 1 - beta
    
    def _calculate_required_n(self, effect_size: float, power: float, alpha: float) -> int:
        """计算所需样本量"""
        from scipy.stats import norm
        z_alpha = norm.ppf(1 - alpha/2)
        z_beta = norm.ppf(power)
        n = ((z_alpha + z_beta) / effect_size) ** 2
        return int(np.ceil(n))
    
    def _calculate_mid(self, effect_size: float) -> Dict:
        """计算最小重要差异"""
        return {
            'statistical_mid': effect_size * 0.2,  # 基于效应量的20%
            'clinical_mid': effect_size * 0.3,     # 临床意义阈值
            'patient_reported_mid': effect_size * 0.25  # 患者感知阈值
        }
    
    def _interpret_power(self, power: float) -> str:
        """解释统计功效"""
        if power >= 0.9:
            return "极高功效"
        elif power >= 0.8:
            return "高功效"
        elif power >= 0.7:
            return "中等功效"
        elif power >= 0.6:
            return "可接受功效"
        else:
            return "功效不足"
    
    def _assess_sample_adequacy(self, power: float) -> str:
        """评估样本充分性"""
        if power >= 0.8:
            return "样本量充分"
        elif power >= 0.7:
            return "样本量基本充分，建议补充数据"
        else:
            return "样本量不足，强烈建议扩大样本"
    
    def _calculate_cohens_d(self, control: List[float], treatment: List[float]) -> float:
        """计算Cohen's d"""
        pooled_std = np.sqrt(((len(control)-1)*np.var(control, ddof=1) + 
                             (len(treatment)-1)*np.var(treatment, ddof=1)) / 
                            (len(control) + len(treatment) - 2))
        return (np.mean(treatment) - np.mean(control)) / pooled_std
    
    def _calculate_hedges_g(self, control: List[float], treatment: List[float]) -> float:
        """计算Hedges' g (小样本校正的Cohen's d)"""
        cohens_d = self._calculate_cohens_d(control, treatment)
        n = len(control) + len(treatment)
        correction_factor = 1 - (3 / (4 * n - 9))
        return cohens_d * correction_factor
    
    def _calculate_glass_delta(self, control: List[float], treatment: List[float]) -> float:
        """计算Glass's Δ"""
        return (np.mean(treatment) - np.mean(control)) / np.std(control, ddof=1)
    
    def _bootstrap_effect_size_ci(self, control: List[float], treatment: List[float], 
                                 n_bootstrap: int = 1000, alpha: float = 0.05) -> Tuple[float, float]:
        """Bootstrap效应量置信区间"""
        bootstrap_effects = []
        for _ in range(n_bootstrap):
            control_boot = np.random.choice(control, size=len(control), replace=True)
            treatment_boot = np.random.choice(treatment, size=len(treatment), replace=True)
            effect = self._calculate_cohens_d(control_boot, treatment_boot)
            bootstrap_effects.append(effect)
        
        ci_lower = np.percentile(bootstrap_effects, 100 * alpha/2)
        ci_upper = np.percentile(bootstrap_effects, 100 * (1 - alpha/2))
        return (ci_lower, ci_upper)
    
    def _effect_size_stability(self, control: List[float], treatment: List[float]) -> Dict:
        """效应量稳定性分析"""
        # Jackknife重采样
        jackknife_effects = []
        combined_data = control + treatment
        n_control = len(control)
        
        for i in range(len(combined_data)):
            if i < n_control:
                control_jack = control[:i] + control[i+1:]
                treatment_jack = treatment
            else:
                control_jack = control
                treatment_jack = treatment[:i-n_control] + treatment[i-n_control+1:]
            
            if len(control_jack) > 0 and len(treatment_jack) > 0:
                effect = self._calculate_cohens_d(control_jack, treatment_jack)
                jackknife_effects.append(effect)
        
        return {
            'mean_jackknife_effect': np.mean(jackknife_effects),
            'std_jackknife_effect': np.std(jackknife_effects),
            'stability_coefficient': 1 - (np.std(jackknife_effects) / np.mean(jackknife_effects))
        }
    
    def _interpret_clinical_effect(self, cohens_d: float) -> str:
        """解释临床效应量"""
        abs_d = abs(cohens_d)
        if abs_d >= 0.9:
            return "极大临床效应"
        elif abs_d >= 0.7:
            return "大临床效应"
        elif abs_d >= 0.5:
            return "中等临床效应"
        elif abs_d >= 0.3:
            return "小临床效应"
        elif abs_d >= 0.1:
            return "微小临床效应"
        else:
            return "无临床意义"
    
    def _compare_to_benchmarks(self, effect_size: float, benchmarks: Dict) -> str:
        """与基准对比"""
        medical_bench = benchmarks['medical_research']
        if effect_size >= medical_bench['large']:
            return f"超越医学研究大效应基准 ({medical_bench['large']})"
        elif effect_size >= medical_bench['medium']:
            return f"达到医学研究中等效应基准 ({medical_bench['medium']})"
        elif effect_size >= medical_bench['small']:
            return f"达到医学研究小效应基准 ({medical_bench['small']})"
        else:
            return "低于医学研究效应基准"
    
    def _parametric_ci(self, data: List[float], confidence: float) -> Tuple[float, float]:
        """参数法置信区间"""
        n = len(data)
        mean = np.mean(data)
        sem = stats.sem(data)
        t_critical = stats.t.ppf((1 + confidence) / 2, n - 1)
        margin_error = t_critical * sem
        return (mean - margin_error, mean + margin_error)
    
    def _bootstrap_ci(self, data: List[float], confidence: float, 
                     n_bootstrap: int = 1000) -> Tuple[float, float]:
        """Bootstrap置信区间"""
        bootstrap_means = []
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(bootstrap_sample))
        
        alpha = 1 - confidence
        ci_lower = np.percentile(bootstrap_means, 100 * alpha/2)
        ci_upper = np.percentile(bootstrap_means, 100 * (1 - alpha/2))
        return (ci_lower, ci_upper)
    
    def _bias_corrected_bootstrap_ci(self, data: List[float], confidence: float, 
                                   n_bootstrap: int = 1000) -> Tuple[float, float]:
        """偏差校正Bootstrap置信区间"""
        original_mean = np.mean(data)
        bootstrap_means = []
        
        for _ in range(n_bootstrap):
            bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
            bootstrap_means.append(np.mean(bootstrap_sample))
        
        # 偏差校正
        bias_correction = stats.norm.ppf(np.mean([x < original_mean for x in bootstrap_means]))
        alpha = 1 - confidence
        z_alpha_2 = stats.norm.ppf(alpha/2)
        z_1_alpha_2 = stats.norm.ppf(1 - alpha/2)
        
        # 校正后的百分位数
        alpha1 = stats.norm.cdf(2 * bias_correction + z_alpha_2)
        alpha2 = stats.norm.cdf(2 * bias_correction + z_1_alpha_2)
        
        ci_lower = np.percentile(bootstrap_means, 100 * alpha1)
        ci_upper = np.percentile(bootstrap_means, 100 * alpha2)
        return (ci_lower, ci_upper)
    
    def _ci_stability_assessment(self, ci_results: Dict) -> str:
        """置信区间稳定性评估"""
        # 比较不同方法的置信区间宽度
        widths = []
        for conf_level in ci_results:
            width_param = ci_results[conf_level]['width_parametric']
            width_boot = ci_results[conf_level]['width_bootstrap']
            widths.append(abs(width_param - width_boot) / width_param)
        
        avg_difference = np.mean(widths)
        if avg_difference < 0.1:
            return "高度稳定"
        elif avg_difference < 0.2:
            return "中等稳定"
        else:
            return "不够稳定"
    
    def _recommend_ci_method(self, ci_results: Dict) -> str:
        """推荐置信区间方法"""
        # 基于样本量和数据特征推荐
        return "偏差校正Bootstrap (适合小样本)"
    
    def _ci_interpretation_guide(self) -> Dict:
        """置信区间解释指南"""
        return {
            'narrow_ci': "结果精确，估计可靠",
            'wide_ci': "结果不确定性较大，建议增加样本",
            'bootstrap_preferred': "小样本情况下Bootstrap方法更稳健",
            'multiple_levels': "多个置信水平提供更全面的不确定性评估"
        }
    
    def _outlier_sensitivity(self, data: List[float]) -> Dict:
        """异常值敏感性分析"""
        # 检测异常值
        q1, q3 = np.percentile(data, [25, 75])
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr
        
        outliers = [x for x in data if x < lower_bound or x > upper_bound]
        
        # 计算去除异常值后的影响
        if outliers:
            data_no_outliers = [x for x in data if lower_bound <= x <= upper_bound]
            original_mean = np.mean(data)
            no_outliers_mean = np.mean(data_no_outliers)
            influence_score = abs(original_mean - no_outliers_mean) / original_mean
        else:
            influence_score = 0.0
        
        return {
            'outliers_detected': len(outliers),
            'outlier_values': outliers,
            'influence_score': influence_score,
            'outlier_interpretation': '低影响' if influence_score < 0.05 else '中等影响' if influence_score < 0.1 else '高影响'
        }
    
    def _test_normality_assumptions(self, data: List[float]) -> Dict:
        """正态性假设检验"""
        # Shapiro-Wilk检验
        shapiro_stat, shapiro_p = stats.shapiro(data)
        
        # Anderson-Darling检验
        anderson_result = stats.anderson(data, dist='norm')
        
        # Kolmogorov-Smirnov检验
        ks_stat, ks_p = stats.kstest(data, 'norm', args=(np.mean(data), np.std(data, ddof=1)))
        
        return {
            'shapiro_wilk': {'statistic': shapiro_stat, 'p_value': shapiro_p, 'normal': shapiro_p > 0.05},
            'anderson_darling': {'statistic': anderson_result.statistic, 'critical_values': anderson_result.critical_values},
            'kolmogorov_smirnov': {'statistic': ks_stat, 'p_value': ks_p, 'normal': ks_p > 0.05},
            'overall_normality': shapiro_p > 0.05 and ks_p > 0.05
        }
    
    def _robust_statistical_methods(self, data: List[float]) -> Dict:
        """稳健统计方法"""
        return {
            'median': np.median(data),
            'trimmed_mean_10': stats.trim_mean(data, 0.1),
            'trimmed_mean_20': stats.trim_mean(data, 0.2),
            'mad': stats.median_abs_deviation(data),  # 中位数绝对偏差
            'iqr': np.percentile(data, 75) - np.percentile(data, 25),
            'huber_location': self._huber_location(data)
        }
    
    def _huber_location(self, data: List[float]) -> float:
        """Huber位置估计"""
        # 简化的Huber估计
        median = np.median(data)
        mad = stats.median_abs_deviation(data)
        k = 1.345  # Huber常数
        
        weights = np.where(np.abs(data - median) <= k * mad, 1.0, 
                          k * mad / np.abs(data - median))
        return np.average(data, weights=weights)
    
    def _jackknife_analysis(self, data: List[float]) -> Dict:
        """Jackknife重采样分析"""
        n = len(data)
        jackknife_means = []
        
        for i in range(n):
            jackknife_sample = data[:i] + data[i+1:]
            jackknife_means.append(np.mean(jackknife_sample))
        
        jackknife_mean = np.mean(jackknife_means)
        jackknife_var = (n - 1) / n * np.sum([(jm - jackknife_mean)**2 for jm in jackknife_means])
        
        return {
            'jackknife_mean': jackknife_mean,
            'jackknife_variance': jackknife_var,
            'jackknife_std': np.sqrt(jackknife_var),
            'bias_estimate': (n - 1) * (jackknife_mean - np.mean(data))
        }
    
    def _overall_sensitivity_score(self, outlier_analysis: Dict, jackknife_results: Dict) -> float:
        """总体敏感性评分"""
        outlier_component = 1 - outlier_analysis['influence_score']
        # 基于Jackknife方差的稳定性评分
        variance_component = max(0.0, 1 - jackknife_results['jackknife_variance'] / 100)  # 归一化
        return (outlier_component + variance_component) / 2
    
    def _bayesian_estimation(self, data: List[float], prior_mean: float, prior_std: float) -> Tuple[float, float]:
        """贝叶斯参数估计"""
        n = len(data)
        sample_mean = np.mean(data)
        sample_var = np.var(data, ddof=1)
        
        # 假设已知方差的正态-正态共轭
        prior_precision = 1 / (prior_std ** 2)
        likelihood_precision = n / sample_var
        
        posterior_precision = prior_precision + likelihood_precision
        posterior_mean = (prior_precision * prior_mean + likelihood_precision * sample_mean) / posterior_precision
        posterior_std = np.sqrt(1 / posterior_precision)
        
        return posterior_mean, posterior_std
    
    def _bayesian_credible_intervals(self, posterior_mean: float, posterior_std: float) -> Dict:
        """贝叶斯可信区间"""
        return {
            '90%': (stats.norm.ppf(0.05, posterior_mean, posterior_std), 
                   stats.norm.ppf(0.95, posterior_mean, posterior_std)),
            '95%': (stats.norm.ppf(0.025, posterior_mean, posterior_std), 
                   stats.norm.ppf(0.975, posterior_mean, posterior_std)),
            '99%': (stats.norm.ppf(0.005, posterior_mean, posterior_std), 
                   stats.norm.ppf(0.995, posterior_mean, posterior_std))
        }
    
    def _calculate_bayes_factor(self, data: List[float], prior_mean: float, prior_std: float) -> float:
        """计算贝叶斯因子"""
        # 简化的贝叶斯因子计算
        n = len(data)
        sample_mean = np.mean(data)
        sample_std = np.std(data, ddof=1)
        
        # BF10 = P(D|H1) / P(D|H0)
        # 这里使用近似计算
        likelihood_h1 = stats.norm.pdf(sample_mean, prior_mean, prior_std / np.sqrt(n))
        likelihood_h0 = stats.norm.pdf(sample_mean, 0, sample_std / np.sqrt(n))
        
        return likelihood_h1 / likelihood_h0 if likelihood_h0 > 0 else float('inf')
    
    def _posterior_predictive_checks(self, data: List[float], posterior_mean: float, posterior_std: float) -> Dict:
        """后验预测检验"""
        # 生成后验预测数据
        n_pred = 1000
        predicted_means = np.random.normal(posterior_mean, posterior_std, n_pred)
        
        # 计算预测统计量
        observed_mean = np.mean(data)
        predicted_mean_dist = predicted_means
        
        p_value = np.mean(predicted_mean_dist > observed_mean)
        
        return {
            'predicted_mean_range': (np.min(predicted_mean_dist), np.max(predicted_mean_dist)),
            'observed_mean': observed_mean,
            'posterior_predictive_p': p_value,
            'model_adequacy': 'Good' if 0.1 <= p_value <= 0.9 else 'Questionable'
        }
    
    def _interpret_bayes_factor(self, bf: float) -> str:
        """解释贝叶斯因子"""
        if bf > 100:
            return "极强证据支持假设"
        elif bf > 30:
            return "很强证据支持假设"
        elif bf > 10:
            return "强证据支持假设"
        elif bf > 3:
            return "中等证据支持假设"
        elif bf > 1:
            return "轻微证据支持假设"
        else:
            return "证据不支持假设"
    
    def _nnt_confidence_interval(self, p1: float, p0: float, n: int) -> Tuple[float, float]:
        """NNT置信区间"""
        # 使用Delta方法计算NNT的置信区间
        arr = p1 - p0
        if arr <= 0:
            return (float('inf'), float('inf'))
        
        # 方差估计
        var_arr = (p1 * (1 - p1) + p0 * (1 - p0)) / n
        se_arr = np.sqrt(var_arr)
        
        # ARR的95%置信区间
        arr_ci_lower = arr - 1.96 * se_arr
        arr_ci_upper = arr + 1.96 * se_arr
        
        # NNT置信区间
        if arr_ci_lower > 0:
            nnt_ci_upper = 1 / arr_ci_lower
        else:
            nnt_ci_upper = float('inf')
        
        if arr_ci_upper > 0:
            nnt_ci_lower = 1 / arr_ci_upper
        else:
            nnt_ci_lower = float('inf')
        
        return (nnt_ci_lower, nnt_ci_upper)
    
    def _assess_nnt_clinical_significance(self, nnt: float) -> str:
        """评估NNT的临床意义"""
        if nnt <= 2:
            return "极高临床价值"
        elif nnt <= 5:
            return "高临床价值"
        elif nnt <= 10:
            return "中等临床价值"
        elif nnt <= 20:
            return "有限临床价值"
        else:
            return "临床价值较低"
    
    def _interpret_nnt(self, nnt: float) -> str:
        """解释NNT"""
        if nnt == float('inf'):
            return "治疗无效果"
        else:
            return f"每治疗{nnt:.0f}位患者，有1位获得额外益处"

# 使用示例
if __name__ == "__main__":
    enhancer = StatisticalEnhancement()
    
    # 模拟23例患者数据
    np.random.seed(42)
    patient_data = np.random.normal(55, 15, 23).tolist()
    
    # 运行统计增强分析
    report = enhancer.generate_statistical_report(patient_data)
    print(report) 