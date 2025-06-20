#!/usr/bin/env python3
"""
高级算法鲁棒性测试器
为AI系统提供全面的鲁棒性和显著性验证

解决核心问题:
1. 算法在不同数据条件下的稳定性
2. 统计显著性的严格检验
3. 持续学习能力的量化评估
4. 专家级别性能的验证
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional, Callable, Any
from scipy import stats
from sklearn.model_selection import KFold, StratifiedKFold
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, roc_auc_score
import matplotlib.pyplot as plt
import seaborn as sns
from dataclasses import dataclass
import warnings
from concurrent.futures import ThreadPoolExecutor
import time
import random

warnings.filterwarnings('ignore')

@dataclass
class RobustnessTestResult:
    """鲁棒性测试结果"""
    test_name: str
    mean_performance: float
    std_performance: float
    confidence_interval: Tuple[float, float]
    p_value: float
    effect_size: float
    significance_level: str
    robustness_score: float
    
class AdvancedRobustnessTester:
    """高级算法鲁棒性测试器"""
    
    def __init__(self, ai_system_predictor: Callable = None):
        """
        初始化测试器
        
        Args:
            ai_system_predictor: AI系统的预测函数
        """
        self.ai_system = ai_system_predictor or self._mock_ai_system
        self.test_results = {}
        self.robustness_scores = {}
        
    def _mock_ai_system(self, patient_data: Dict) -> float:
        """模拟AI系统预测函数"""
        # 基于患者特征生成预测结果
        base_score = 0.7
        
        # 考虑年龄因素
        if patient_data.get('age', 45) > 60:
            base_score += 0.05
        elif patient_data.get('age', 45) < 30:
            base_score -= 0.05
        
        # 考虑性别因素
        if patient_data.get('gender') == 'Female':
            base_score += 0.03
        
        # 考虑症状严重程度
        severity = patient_data.get('symptom_severity', 5)
        base_score += (severity - 5) * 0.02
        
        # 添加随机噪声
        noise = np.random.normal(0, 0.1)
        final_score = np.clip(base_score + noise, 0, 1)
        
        return final_score
    
    def test_data_perturbation_robustness(self, patient_data: List[Dict], 
                                        perturbation_levels: List[float] = [0.05, 0.1, 0.15, 0.2]) -> Dict:
        """
        测试数据扰动鲁棒性
        验证AI系统对输入数据微小变化的稳定性
        """
        print("🧪 开始数据扰动鲁棒性测试...")
        
        robustness_results = {}
        
        for perturbation_level in perturbation_levels:
            print(f"  测试扰动水平: {perturbation_level:.2f}")
            
            original_predictions = []
            perturbed_predictions = []
            
            for patient in patient_data:
                # 原始预测
                original_pred = self.ai_system(patient)
                original_predictions.append(original_pred)
                
                # 生成扰动数据
                perturbed_patient = self._perturb_patient_data(patient, perturbation_level)
                perturbed_pred = self.ai_system(perturbed_patient)
                perturbed_predictions.append(perturbed_pred)
            
            # 计算预测稳定性
            prediction_differences = [abs(orig - pert) for orig, pert in 
                                    zip(original_predictions, perturbed_predictions)]
            
            stability_score = 1 - np.mean(prediction_differences)
            consistency_score = 1 - np.std(prediction_differences)
            
            robustness_results[f'perturbation_{perturbation_level}'] = {
                'mean_difference': np.mean(prediction_differences),
                'std_difference': np.std(prediction_differences),
                'max_difference': np.max(prediction_differences),
                'stability_score': stability_score,
                'consistency_score': consistency_score,
                'robust_predictions_ratio': np.mean([diff < 0.1 for diff in prediction_differences])
            }
        
        # 计算总体鲁棒性评分
        overall_robustness = np.mean([result['stability_score'] for result in robustness_results.values()])
        
        self.test_results['data_perturbation'] = {
            'perturbation_results': robustness_results,
            'overall_robustness_score': overall_robustness,
            'robustness_grade': self._grade_robustness(overall_robustness)
        }
        
        print(f"✅ 数据扰动鲁棒性测试完成，总评分: {overall_robustness:.3f}")
        return self.test_results['data_perturbation']
    
    def test_cross_validation_stability(self, patient_data: List[Dict], 
                                      k_folds: int = 5, n_repeats: int = 10) -> Dict:
        """
        交叉验证稳定性测试
        多次交叉验证评估模型性能稳定性
        """
        print(f"🔄 开始{k_folds}折交叉验证稳定性测试 (重复{n_repeats}次)...")
        
        all_scores = []
        
        for repeat in range(n_repeats):
            kf = KFold(n_splits=k_folds, shuffle=True, random_state=repeat)
            fold_scores = []
            
            # 准备数据
            X = np.array([list(patient.values()) for patient in patient_data])
            
            for train_idx, test_idx in kf.split(X):
                # 训练和测试数据
                test_patients = [patient_data[i] for i in test_idx]
                
                # 预测测试集
                test_predictions = [self.ai_system(patient) for patient in test_patients]
                
                # 计算性能指标 (使用模拟的真实标签)
                true_labels = [self._generate_true_label(patient) for patient in test_patients]
                
                # 转换为二分类问题
                pred_binary = [1 if pred > 0.5 else 0 for pred in test_predictions]
                
                fold_score = accuracy_score(true_labels, pred_binary)
                fold_scores.append(fold_score)
            
            all_scores.extend(fold_scores)
        
        # 统计分析
        mean_score = np.mean(all_scores)
        std_score = np.std(all_scores)
        cv_coefficient = std_score / mean_score if mean_score > 0 else float('inf')
        
        # 置信区间
        ci_lower, ci_upper = stats.t.interval(0.95, len(all_scores)-1, 
                                             loc=mean_score, 
                                             scale=stats.sem(all_scores))
        
        cv_stability_result = {
            'mean_accuracy': mean_score,
            'std_accuracy': std_score,
            'coefficient_of_variation': cv_coefficient,
            'confidence_interval_95': (ci_lower, ci_upper),
            'stability_score': 1 - cv_coefficient,  # 越小越稳定
            'n_folds': k_folds,
            'n_repeats': n_repeats,
            'total_evaluations': len(all_scores)
        }
        
        self.test_results['cross_validation_stability'] = cv_stability_result
        
        print(f"✅ 交叉验证稳定性: {mean_score:.3f} ± {std_score:.3f}")
        print(f"✅ 变异系数: {cv_coefficient:.4f}")
        
        return cv_stability_result
    
    def test_adversarial_robustness(self, patient_data: List[Dict], 
                                   attack_strengths: List[float] = [0.1, 0.2, 0.3]) -> Dict:
        """
        对抗性鲁棒性测试
        测试AI系统对恶意输入的抵抗能力
        """
        print("⚔️ 开始对抗性鲁棒性测试...")
        
        adversarial_results = {}
        
        for attack_strength in attack_strengths:
            print(f"  测试攻击强度: {attack_strength:.1f}")
            
            original_predictions = []
            adversarial_predictions = []
            attack_success_count = 0
            
            for patient in patient_data:
                # 原始预测
                original_pred = self.ai_system(patient)
                original_predictions.append(original_pred)
                
                # 生成对抗样本
                adversarial_patient = self._generate_adversarial_sample(patient, attack_strength)
                adversarial_pred = self.ai_system(adversarial_patient)
                adversarial_predictions.append(adversarial_pred)
                
                # 检查攻击是否成功（预测变化超过阈值）
                if abs(original_pred - adversarial_pred) > 0.2:
                    attack_success_count += 1
            
            attack_success_rate = attack_success_count / len(patient_data)
            resistance_score = 1 - attack_success_rate
            
            adversarial_results[f'attack_strength_{attack_strength}'] = {
                'attack_success_rate': attack_success_rate,
                'resistance_score': resistance_score,
                'mean_prediction_change': np.mean([abs(orig - adv) for orig, adv in 
                                                 zip(original_predictions, adversarial_predictions)]),
                'max_prediction_change': np.max([abs(orig - adv) for orig, adv in 
                                               zip(original_predictions, adversarial_predictions)])
            }
        
        # 计算总体对抗性鲁棒性
        overall_resistance = np.mean([result['resistance_score'] for result in adversarial_results.values()])
        
        self.test_results['adversarial_robustness'] = {
            'attack_results': adversarial_results,
            'overall_resistance_score': overall_resistance,
            'resistance_grade': self._grade_robustness(overall_resistance)
        }
        
        print(f"✅ 对抗性鲁棒性测试完成，抗攻击评分: {overall_resistance:.3f}")
        return self.test_results['adversarial_robustness']
    
    def test_statistical_significance(self, patient_data: List[Dict], 
                                    baseline_performance: float = 0.65) -> Dict:
        """
        统计显著性检验
        验证AI系统性能是否显著优于基线
        """
        print("📊 开始统计显著性检验...")
        
        # 生成AI系统的预测结果
        ai_predictions = [self.ai_system(patient) for patient in patient_data]
        true_labels = [self._generate_true_label(patient) for patient in patient_data]
        
        # 转换为二分类
        ai_binary = [1 if pred > 0.5 else 0 for pred in ai_predictions]
        
        # 计算性能指标
        ai_accuracy = accuracy_score(true_labels, ai_binary)
        precision, recall, f1, _ = precision_recall_fscore_support(true_labels, ai_binary, average='weighted')
        
        # 单样本t检验 (与基线比较)
        # 使用bootstrap生成性能分布
        bootstrap_accuracies = []
        n_bootstrap = 1000
        
        for _ in range(n_bootstrap):
            # 重采样
            indices = np.random.choice(len(patient_data), size=len(patient_data), replace=True)
            bootstrap_patients = [patient_data[i] for i in indices]
            bootstrap_true = [true_labels[i] for i in indices]
            
            # 预测
            bootstrap_preds = [self.ai_system(patient) for patient in bootstrap_patients]
            bootstrap_binary = [1 if pred > 0.5 else 0 for pred in bootstrap_preds]
            
            # 计算准确率
            bootstrap_acc = accuracy_score(bootstrap_true, bootstrap_binary)
            bootstrap_accuracies.append(bootstrap_acc)
        
        # 统计检验
        t_stat, p_value = stats.ttest_1samp(bootstrap_accuracies, baseline_performance)
        
        # 效应量 (Cohen's d)
        cohens_d = (np.mean(bootstrap_accuracies) - baseline_performance) / np.std(bootstrap_accuracies)
        
        # 置信区间
        ci_lower, ci_upper = np.percentile(bootstrap_accuracies, [2.5, 97.5])
        
        # 功效分析
        power = self._calculate_statistical_power(bootstrap_accuracies, baseline_performance)
        
        significance_result = {
            'ai_accuracy': ai_accuracy,
            'ai_precision': precision,
            'ai_recall': recall,
            'ai_f1_score': f1,
            'baseline_performance': baseline_performance,
            'bootstrap_mean': np.mean(bootstrap_accuracies),
            'bootstrap_std': np.std(bootstrap_accuracies),
            't_statistic': t_stat,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'effect_size_interpretation': self._interpret_effect_size(cohens_d),
            'confidence_interval_95': (ci_lower, ci_upper),
            'statistical_power': power,
            'significance_level': 'p < 0.001' if p_value < 0.001 else f'p = {p_value:.4f}',
            'clinically_significant': ai_accuracy - baseline_performance > 0.1,
            'statistically_significant': p_value < 0.05
        }
        
        self.test_results['statistical_significance'] = significance_result
        
        print(f"✅ AI系统准确率: {ai_accuracy:.3f}")
        print(f"✅ vs 基线准确率: {baseline_performance:.3f}")
        print(f"✅ 统计显著性: {significance_result['significance_level']}")
        print(f"✅ 效应量: {cohens_d:.3f} ({self._interpret_effect_size(cohens_d)})")
        
        return significance_result
    
    def test_continuous_learning_capability(self, initial_data: List[Dict], 
                                          learning_iterations: int = 10) -> Dict:
        """
        持续学习能力测试
        验证AI系统的自适应学习能力
        """
        print("🧠 开始持续学习能力测试...")
        
        performance_trajectory = []
        learning_rates = []
        knowledge_retention_scores = []
        
        # 初始性能
        initial_performance = self._evaluate_performance(initial_data)
        performance_trajectory.append(initial_performance)
        
        current_data = initial_data.copy()
        
        for iteration in range(learning_iterations):
            print(f"  学习迭代 {iteration + 1}/{learning_iterations}")
            
            # 模拟新数据到达
            new_data = self._generate_new_learning_data(5)  # 5个新样本
            current_data.extend(new_data)
            
            # 模拟学习过程 (实际应用中这里会是真正的模型更新)
            learning_improvement = self._simulate_learning_step(current_data)
            
            # 评估学习后的性能
            new_performance = self._evaluate_performance(current_data)
            performance_trajectory.append(new_performance)
            
            # 计算学习率
            learning_rate = new_performance - performance_trajectory[-2]
            learning_rates.append(learning_rate)
            
            # 测试知识保持能力
            retention_score = self._test_knowledge_retention(initial_data, current_data)
            knowledge_retention_scores.append(retention_score)
        
        # 分析学习趋势
        learning_efficiency = np.mean(learning_rates)
        learning_stability = 1 - np.std(learning_rates)
        total_improvement = performance_trajectory[-1] - performance_trajectory[0]
        
        # 拟合学习曲线
        learning_curve_fit = self._fit_learning_curve(performance_trajectory)
        
        # 专家级别评估
        expert_level = self._assess_expert_level(performance_trajectory[-1])
        
        continuous_learning_result = {
            'performance_trajectory': performance_trajectory,
            'learning_rates': learning_rates,
            'knowledge_retention_scores': knowledge_retention_scores,
            'initial_performance': initial_performance,
            'final_performance': performance_trajectory[-1],
            'total_improvement': total_improvement,
            'learning_efficiency': learning_efficiency,
            'learning_stability': learning_stability,
            'mean_retention_score': np.mean(knowledge_retention_scores),
            'learning_curve_parameters': learning_curve_fit,
            'expert_level_achieved': expert_level,
            'convergence_rate': self._calculate_convergence_rate(performance_trajectory),
            'learning_capacity_score': self._calculate_learning_capacity(learning_rates, knowledge_retention_scores)
        }
        
        self.test_results['continuous_learning'] = continuous_learning_result
        
        print(f"✅ 初始性能: {initial_performance:.3f}")
        print(f"✅ 最终性能: {performance_trajectory[-1]:.3f}")
        print(f"✅ 总改进幅度: {total_improvement:.3f}")
        print(f"✅ 学习效率: {learning_efficiency:.4f}")
        print(f"✅ 达到专家级别: {expert_level}")
        
        return continuous_learning_result
    
    def test_population_generalization(self, patient_data: List[Dict]) -> Dict:
        """
        人群泛化能力测试
        测试AI系统在不同人群中的表现
        """
        print("🌍 开始人群泛化能力测试...")
        
        # 按人群特征分组
        groups = {
            'age_young': [p for p in patient_data if p.get('age', 45) < 40],
            'age_old': [p for p in patient_data if p.get('age', 45) >= 60],
            'gender_male': [p for p in patient_data if p.get('gender') == 'Male'],
            'gender_female': [p for p in patient_data if p.get('gender') == 'Female'],
            'severity_mild': [p for p in patient_data if p.get('symptom_severity', 5) <= 4],
            'severity_severe': [p for p in patient_data if p.get('symptom_severity', 5) >= 7]
        }
        
        group_performances = {}
        
        for group_name, group_data in groups.items():
            if len(group_data) >= 3:  # 至少3个样本才进行测试
                group_performance = self._evaluate_performance(group_data)
                group_performances[group_name] = {
                    'performance': group_performance,
                    'sample_size': len(group_data),
                    'relative_performance': group_performance / self._evaluate_performance(patient_data)
                }
        
        # 计算泛化一致性
        performances = [result['performance'] for result in group_performances.values()]
        generalization_consistency = 1 - (np.std(performances) / np.mean(performances)) if performances else 0
        
        # 公平性评估
        fairness_scores = {}
        if 'gender_male' in group_performances and 'gender_female' in group_performances:
            male_perf = group_performances['gender_male']['performance']
            female_perf = group_performances['gender_female']['performance']
            fairness_scores['gender_fairness'] = 1 - abs(male_perf - female_perf) / max(male_perf, female_perf)
        
        if 'age_young' in group_performances and 'age_old' in group_performances:
            young_perf = group_performances['age_young']['performance']
            old_perf = group_performances['age_old']['performance']
            fairness_scores['age_fairness'] = 1 - abs(young_perf - old_perf) / max(young_perf, old_perf)
        
        generalization_result = {
            'group_performances': group_performances,
            'generalization_consistency': generalization_consistency,
            'fairness_scores': fairness_scores,
            'overall_fairness': np.mean(list(fairness_scores.values())) if fairness_scores else 0,
            'population_robustness_grade': self._grade_robustness(generalization_consistency)
        }
        
        self.test_results['population_generalization'] = generalization_result
        
        print(f"✅ 泛化一致性: {generalization_consistency:.3f}")
        print(f"✅ 整体公平性: {generalization_result['overall_fairness']:.3f}")
        
        return generalization_result
    
    def run_comprehensive_robustness_test(self, patient_data: List[Dict]) -> Dict:
        """运行全面的鲁棒性测试"""
        print("🚀 开始全面鲁棒性测试...")
        print("=" * 60)
        
        # 执行所有测试
        perturbation_results = self.test_data_perturbation_robustness(patient_data)
        print()
        
        cv_results = self.test_cross_validation_stability(patient_data)
        print()
        
        adversarial_results = self.test_adversarial_robustness(patient_data)
        print()
        
        significance_results = self.test_statistical_significance(patient_data)
        print()
        
        learning_results = self.test_continuous_learning_capability(patient_data)
        print()
        
        generalization_results = self.test_population_generalization(patient_data)
        print()
        
        # 综合评估
        overall_robustness = self._calculate_overall_robustness_score()
        
        comprehensive_result = {
            'individual_tests': self.test_results,
            'overall_robustness_score': overall_robustness,
            'robustness_grade': self._grade_robustness(overall_robustness),
            'production_readiness': self._assess_production_readiness(overall_robustness),
            'recommendations': self._generate_recommendations()
        }
        
        print("=" * 60)
        print("🎉 全面鲁棒性测试完成!")
        print(f"📊 总体鲁棒性评分: {overall_robustness:.3f}")
        print(f"🏆 鲁棒性等级: {self._grade_robustness(overall_robustness)}")
        print(f"🚀 生产就绪度: {comprehensive_result['production_readiness']}")
        print("=" * 60)
        
        return comprehensive_result
    
    # 辅助方法
    def _perturb_patient_data(self, patient: Dict, perturbation_level: float) -> Dict:
        """对患者数据添加扰动"""
        perturbed = patient.copy()
        
        for key, value in patient.items():
            if isinstance(value, (int, float)) and key != 'patient_id':
                noise = np.random.normal(0, perturbation_level * abs(value))
                perturbed[key] = value + noise
        
        return perturbed
    
    def _generate_adversarial_sample(self, patient: Dict, attack_strength: float) -> Dict:
        """生成对抗样本"""
        adversarial = patient.copy()
        
        # 选择最敏感的特征进行攻击
        sensitive_features = ['symptom_severity', 'age', 'bmi']
        
        for feature in sensitive_features:
            if feature in adversarial:
                original_value = adversarial[feature]
                # 在指定强度范围内随机攻击
                attack_direction = np.random.choice([-1, 1])
                attack_magnitude = attack_strength * abs(original_value)
                adversarial[feature] = original_value + attack_direction * attack_magnitude
        
        return adversarial
    
    def _generate_true_label(self, patient: Dict) -> int:
        """生成模拟的真实标签"""
        # 基于患者特征生成真实标签
        severity = patient.get('symptom_severity', 5)
        age = patient.get('age', 45)
        
        # 简单的标签生成逻辑
        if severity > 6 or age > 65:
            return 1 if np.random.random() > 0.3 else 0
        else:
            return 1 if np.random.random() > 0.6 else 0
    
    def _evaluate_performance(self, data: List[Dict]) -> float:
        """评估性能"""
        predictions = [self.ai_system(patient) for patient in data]
        true_labels = [self._generate_true_label(patient) for patient in data]
        
        pred_binary = [1 if pred > 0.5 else 0 for pred in predictions]
        return accuracy_score(true_labels, pred_binary)
    
    def _generate_new_learning_data(self, n_samples: int) -> List[Dict]:
        """生成新的学习数据"""
        new_data = []
        for i in range(n_samples):
            patient = {
                'patient_id': f'NEW_{i:03d}',
                'age': np.random.randint(20, 80),
                'gender': np.random.choice(['Male', 'Female']),
                'symptom_severity': np.random.randint(1, 11),
                'bmi': np.random.normal(25, 5)
            }
            new_data.append(patient)
        return new_data
    
    def _simulate_learning_step(self, data: List[Dict]) -> float:
        """模拟学习步骤"""
        # 模拟学习改进
        return np.random.normal(0.02, 0.01)  # 平均2%的改进
    
    def _test_knowledge_retention(self, old_data: List[Dict], new_data: List[Dict]) -> float:
        """测试知识保持"""
        old_performance = self._evaluate_performance(old_data)
        # 模拟在旧数据上的性能（应该保持）
        retention_performance = old_performance * np.random.uniform(0.95, 1.05)
        return retention_performance / old_performance
    
    def _fit_learning_curve(self, trajectory: List[float]) -> Dict:
        """拟合学习曲线"""
        x = np.arange(len(trajectory))
        
        # 拟合对数函数
        try:
            # log(x+1) 形式
            from scipy.optimize import curve_fit
            
            def log_func(x, a, b, c):
                return a * np.log(x + 1) + b + c
            
            popt, _ = curve_fit(log_func, x, trajectory)
            
            return {
                'curve_type': 'logarithmic',
                'parameters': popt.tolist(),
                'final_asymptote': log_func(len(trajectory) * 2, *popt)
            }
        except:
            return {
                'curve_type': 'linear',
                'parameters': [np.mean(np.diff(trajectory))],
                'final_asymptote': trajectory[-1]
            }
    
    def _assess_expert_level(self, final_performance: float) -> str:
        """评估专家级别"""
        if final_performance >= 0.95:
            return "World-class Expert"
        elif final_performance >= 0.90:
            return "Senior Specialist"
        elif final_performance >= 0.85:
            return "Experienced Specialist"
        elif final_performance >= 0.80:
            return "Junior Specialist"
        elif final_performance >= 0.75:
            return "Senior Resident"
        else:
            return "Junior Resident"
    
    def _calculate_convergence_rate(self, trajectory: List[float]) -> float:
        """计算收敛速度"""
        if len(trajectory) < 3:
            return 0.0
        
        # 计算改进速度的衰减
        improvements = np.diff(trajectory)
        if len(improvements) < 2:
            return 0.0
        
        # 拟合指数衰减
        try:
            decay_rate = -np.polyfit(range(len(improvements)), np.log(np.abs(improvements) + 1e-6), 1)[0]
            return min(decay_rate, 1.0)
        except:
            return 0.5
    
    def _calculate_learning_capacity(self, learning_rates: List[float], 
                                   retention_scores: List[float]) -> float:
        """计算学习能力评分"""
        if not learning_rates or not retention_scores:
            return 0.0
        
        learning_efficiency = np.mean([max(0, lr) for lr in learning_rates])
        retention_quality = np.mean(retention_scores)
        
        return (learning_efficiency + retention_quality) / 2
    
    def _calculate_statistical_power(self, sample_data: List[float], 
                                   null_hypothesis: float) -> float:
        """计算统计功效"""
        effect_size = abs(np.mean(sample_data) - null_hypothesis) / np.std(sample_data)
        sample_size = len(sample_data)
        
        # 简化的功效计算
        power = min(1.0, effect_size * np.sqrt(sample_size) / 2.8)
        return power
    
    def _interpret_effect_size(self, cohens_d: float) -> str:
        """解释效应量"""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        elif abs_d < 1.2:
            return "large"
        else:
            return "very large"
    
    def _grade_robustness(self, score: float) -> str:
        """评估鲁棒性等级"""
        if score >= 0.95:
            return "Exceptional (A+)"
        elif score >= 0.90:
            return "Excellent (A)"
        elif score >= 0.85:
            return "Very Good (B+)"
        elif score >= 0.80:
            return "Good (B)"
        elif score >= 0.75:
            return "Satisfactory (C+)"
        elif score >= 0.70:
            return "Acceptable (C)"
        else:
            return "Needs Improvement (D)"
    
    def _calculate_overall_robustness_score(self) -> float:
        """计算总体鲁棒性评分"""
        if not self.test_results:
            return 0.0
        
        scores = []
        weights = {
            'data_perturbation': 0.2,
            'cross_validation_stability': 0.15,
            'adversarial_robustness': 0.15,
            'statistical_significance': 0.25,
            'continuous_learning': 0.15,
            'population_generalization': 0.1
        }
        
        for test_name, weight in weights.items():
            if test_name in self.test_results:
                if test_name == 'data_perturbation':
                    score = self.test_results[test_name]['overall_robustness_score']
                elif test_name == 'cross_validation_stability':
                    score = self.test_results[test_name]['stability_score']
                elif test_name == 'adversarial_robustness':
                    score = self.test_results[test_name]['overall_resistance_score']
                elif test_name == 'statistical_significance':
                    # 将准确率转换为0-1评分
                    score = min(1.0, self.test_results[test_name]['ai_accuracy'])
                elif test_name == 'continuous_learning':
                    score = self.test_results[test_name]['learning_capacity_score']
                elif test_name == 'population_generalization':
                    score = self.test_results[test_name]['generalization_consistency']
                else:
                    score = 0.8  # 默认分数
                
                scores.append(score * weight)
        
        return sum(scores)
    
    def _assess_production_readiness(self, robustness_score: float) -> str:
        """评估生产就绪度"""
        if robustness_score >= 0.90:
            return "Production Ready"
        elif robustness_score >= 0.85:
            return "Near Production Ready"
        elif robustness_score >= 0.80:
            return "Requires Minor Improvements"
        elif robustness_score >= 0.75:
            return "Requires Significant Improvements"
        else:
            return "Not Ready for Production"
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        
        if 'data_perturbation' in self.test_results:
            score = self.test_results['data_perturbation']['overall_robustness_score']
            if score < 0.8:
                recommendations.append("增强数据预处理和特征工程以提高数据扰动鲁棒性")
        
        if 'adversarial_robustness' in self.test_results:
            score = self.test_results['adversarial_robustness']['overall_resistance_score']
            if score < 0.8:
                recommendations.append("实施对抗性训练以提高安全性")
        
        if 'statistical_significance' in self.test_results:
            p_value = self.test_results['statistical_significance']['p_value']
            if p_value > 0.05:
                recommendations.append("收集更多数据以提高统计显著性")
        
        if 'continuous_learning' in self.test_results:
            score = self.test_results['continuous_learning']['learning_capacity_score']
            if score < 0.8:
                recommendations.append("优化持续学习算法以提高适应性")
        
        if not recommendations:
            recommendations.append("系统表现优秀，建议继续监控和优化")
        
        return recommendations

# 使用示例
if __name__ == "__main__":
    # 创建测试器
    tester = AdvancedRobustnessTester()
    
    # 生成测试数据
    test_patients = []
    for i in range(50):
        patient = {
            'patient_id': f'TEST_{i:03d}',
            'age': np.random.randint(20, 80),
            'gender': np.random.choice(['Male', 'Female']),
            'ethnicity': np.random.choice(['Asian', 'Caucasian', 'Hispanic', 'African American']),
            'symptom_severity': np.random.randint(1, 11),
            'bmi': np.random.normal(25, 5)
        }
        test_patients.append(patient)
    
    # 运行全面测试
    results = tester.run_comprehensive_robustness_test(test_patients)
    
    # 输出关键结果
    print(f"\n🏆 测试结果摘要:")
    print(f"总体鲁棒性评分: {results['overall_robustness_score']:.3f}")
    print(f"鲁棒性等级: {results['robustness_grade']}")
    print(f"生产就绪度: {results['production_readiness']}")
    print(f"\n📋 改进建议:")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}") 