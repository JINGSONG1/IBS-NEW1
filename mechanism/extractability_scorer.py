"""
Extractability Scorer Module
Detects if drug recommendation paths are extractable (can be withdrawn safely)
Prevents sticky/rebound drug dependencies
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json

class ExtractabilityScorer(nn.Module):
    """
    Extractability Scorer for drug recommendation paths
    Evaluates whether a drug path can be safely withdrawn without rebound effects
    """
    
    def __init__(self, 
                 path_dim: int = 64,
                 hidden_dim: int = 128,
                 dropout_rate: float = 0.3):
        super(ExtractabilityScorer, self).__init__()
        
        self.path_dim = path_dim
        self.hidden_dim = hidden_dim
        
        # Drug dependency risk database
        self.drug_dependency_risk = {
            "帕罗西汀": {"dependency_risk": 0.6, "withdrawal_difficulty": 0.7, "rebound_risk": 0.5},
            "阿米替林": {"dependency_risk": 0.4, "withdrawal_difficulty": 0.5, "rebound_risk": 0.4},
            "洛哌丁胺": {"dependency_risk": 0.8, "withdrawal_difficulty": 0.9, "rebound_risk": 0.8},
            "多潘立酮": {"dependency_risk": 0.2, "withdrawal_difficulty": 0.3, "rebound_risk": 0.2},
            "匹维溴铵": {"dependency_risk": 0.3, "withdrawal_difficulty": 0.4, "rebound_risk": 0.3},
            "双歧杆菌": {"dependency_risk": 0.1, "withdrawal_difficulty": 0.1, "rebound_risk": 0.1},
            "氟哌噻吨美利曲辛": {"dependency_risk": 0.5, "withdrawal_difficulty": 0.6, "rebound_risk": 0.5},
            "奥沙西泮": {"dependency_risk": 0.7, "withdrawal_difficulty": 0.8, "rebound_risk": 0.7},
            "曲美布汀": {"dependency_risk": 0.2, "withdrawal_difficulty": 0.3, "rebound_risk": 0.2},
            "益生菌": {"dependency_risk": 0.1, "withdrawal_difficulty": 0.1, "rebound_risk": 0.1}
        }
        
        # Mechanism extractability profiles
        self.mechanism_extractability = {
            "抗焦虑": {"base_extractability": 0.4, "time_factor": 0.8},
            "改善腹泻": {"base_extractability": 0.7, "time_factor": 0.9},
            "抗抑郁": {"base_extractability": 0.3, "time_factor": 0.7},
            "促胃肠动力": {"base_extractability": 0.8, "time_factor": 0.9},
            "解痉": {"base_extractability": 0.6, "time_factor": 0.8},
            "止泻": {"base_extractability": 0.2, "time_factor": 0.6},
            "调节肠道菌群": {"base_extractability": 0.9, "time_factor": 1.0},
            "镇静": {"base_extractability": 0.3, "time_factor": 0.7},
            "抗胆碱": {"base_extractability": 0.5, "time_factor": 0.8},
            "5-HT调节": {"base_extractability": 0.4, "time_factor": 0.7}
        }
        
        # Neural network for extractability prediction
        self.path_encoder = nn.Sequential(
            nn.Linear(path_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Dropout(dropout_rate)
        )
        
        self.extractability_predictor = nn.Sequential(
            nn.Linear(hidden_dim//2 + 10, hidden_dim//4),  # +10 for clinical features
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim//4, 1),
            nn.Sigmoid()  # Output extractability score [0,1]
        )
        
    def forward(self, path_embedding: torch.Tensor, 
                clinical_features: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for extractability scoring
        
        Args:
            path_embedding: Encoded drug path tensor (batch_size, path_dim)
            clinical_features: Clinical risk factors (batch_size, 10)
            
        Returns:
            extractability_scores: Extractability scores (batch_size, 1)
        """
        # Encode path
        path_encoded = self.path_encoder(path_embedding)
        
        # Combine with clinical features
        combined_features = torch.cat([path_encoded, clinical_features], dim=1)
        
        # Predict extractability
        extractability_scores = self.extractability_predictor(combined_features)
        
        return extractability_scores
    
    def encode_drug_path(self, drug_path: List[str]) -> np.ndarray:
        """
        Encode drug path to vector representation
        
        Args:
            drug_path: List of [drug, mechanism, symptom]
            
        Returns:
            path_vector: Encoded path vector
        """
        if len(drug_path) != 3:
            raise ValueError("Drug path must contain [drug, mechanism, symptom]")
        
        drug, mechanism, symptom = drug_path
        
        # Create path embedding (simplified)
        path_vector = np.zeros(64)
        
        # Drug features (first 20 dims)
        if drug in self.drug_dependency_risk:
            risk_profile = self.drug_dependency_risk[drug]
            path_vector[0] = risk_profile["dependency_risk"]
            path_vector[1] = risk_profile["withdrawal_difficulty"]
            path_vector[2] = risk_profile["rebound_risk"]
        
        # Mechanism features (next 20 dims)
        if mechanism in self.mechanism_extractability:
            mech_profile = self.mechanism_extractability[mechanism]
            path_vector[20] = mech_profile["base_extractability"]
            path_vector[21] = mech_profile["time_factor"]
        
        # Add some random features for demonstration
        path_vector[40:] = np.random.randn(24) * 0.1
        
        return path_vector
    
    def get_clinical_risk_features(self, patient_profile: Dict[str, Any]) -> np.ndarray:
        """
        Extract clinical risk features from patient profile
        
        Args:
            patient_profile: Patient clinical information
            
        Returns:
            risk_features: Clinical risk feature vector
        """
        risk_features = np.zeros(10)
        
        # Age factor (older patients have higher withdrawal risks)
        age = patient_profile.get('age', 40)
        risk_features[0] = min(age / 80.0, 1.0)
        
        # Duration of symptoms (longer duration = higher dependency risk)
        symptom_duration = patient_profile.get('symptom_duration_months', 6)
        risk_features[1] = min(symptom_duration / 24.0, 1.0)
        
        # Previous medication history
        previous_meds = patient_profile.get('previous_medications', 0)
        risk_features[2] = min(previous_meds / 5.0, 1.0)
        
        # Comorbidities
        comorbidities = patient_profile.get('comorbidities', [])
        risk_features[3] = min(len(comorbidities) / 3.0, 1.0)
        
        # Psychological dependency tendency
        psych_dependency = patient_profile.get('psychological_dependency_risk', 0.5)
        risk_features[4] = psych_dependency
        
        # Severity of symptoms
        symptom_severity = patient_profile.get('symptom_severity', 5) / 10.0
        risk_features[5] = symptom_severity
        
        # Social support (higher support = better extractability)
        social_support = patient_profile.get('social_support_score', 5) / 10.0
        risk_features[6] = 1.0 - social_support  # Invert for risk
        
        # Treatment compliance history
        compliance = patient_profile.get('treatment_compliance', 0.8)
        risk_features[7] = 1.0 - compliance  # Invert for risk
        
        # Economic factors
        economic_stress = patient_profile.get('economic_stress', 0.3)
        risk_features[8] = economic_stress
        
        # Random factor for model complexity
        risk_features[9] = np.random.random() * 0.2
        
        return risk_features
    
    def calculate_extractability_score(self, drug_path: List[str], 
                                     patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate extractability score for a drug path and patient
        
        Args:
            drug_path: [drug, mechanism, symptom]
            patient_profile: Patient clinical information
            
        Returns:
            extractability_result: Dictionary with extractability analysis
        """
        drug, mechanism, symptom = drug_path
        
        # Get base extractability from clinical knowledge
        drug_risk = self.drug_dependency_risk.get(drug, {
            "dependency_risk": 0.5, "withdrawal_difficulty": 0.5, "rebound_risk": 0.5
        })
        
        mechanism_extract = self.mechanism_extractability.get(mechanism, {
            "base_extractability": 0.5, "time_factor": 0.8
        })
        
        # Calculate base extractability score
        base_extractability = mechanism_extract["base_extractability"]
        drug_penalty = (drug_risk["dependency_risk"] + drug_risk["withdrawal_difficulty"]) / 2
        
        # Adjust for patient factors
        age_factor = min(patient_profile.get('age', 40) / 80.0, 1.0)
        duration_factor = min(patient_profile.get('symptom_duration_months', 6) / 24.0, 1.0)
        
        # Final extractability score
        extractability_score = base_extractability * (1 - drug_penalty) * (1 - age_factor * 0.3) * (1 - duration_factor * 0.2)
        extractability_score = max(0.0, min(1.0, extractability_score))
        
        # Determine extractability level
        if extractability_score >= 0.7:
            level = "容易撤药"
            recommendation = "可以安全停药，建议逐步减量"
        elif extractability_score >= 0.5:
            level = "中等难度"
            recommendation = "需要缓慢减量，监测症状反弹"
        elif extractability_score >= 0.3:
            level = "撤药困难"
            recommendation = "需要专业指导下逐步撤药"
        else:
            level = "高依赖风险"
            recommendation = "不建议突然停药，需要长期管理"
        
        return {
            "drug_path": drug_path,
            "extractability_score": extractability_score,
            "extractability_level": level,
            "recommendation": recommendation,
            "risk_factors": {
                "drug_dependency_risk": drug_risk["dependency_risk"],
                "withdrawal_difficulty": drug_risk["withdrawal_difficulty"],
                "rebound_risk": drug_risk["rebound_risk"],
                "patient_age_factor": age_factor,
                "symptom_duration_factor": duration_factor
            },
            "safe_to_recommend": extractability_score >= 0.4
        }
    
    def compare_path_extractability(self, drug_paths: List[List[str]], 
                                  patient_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Compare extractability scores for multiple drug paths
        
        Args:
            drug_paths: List of drug paths to compare
            patient_profile: Patient clinical information
            
        Returns:
            comparison_results: List of extractability results sorted by score
        """
        results = []
        
        for path in drug_paths:
            result = self.calculate_extractability_score(path, patient_profile)
            results.append(result)
        
        # Sort by extractability score (descending)
        results.sort(key=lambda x: x["extractability_score"], reverse=True)
        
        return results
    
    def get_withdrawal_plan(self, drug_path: List[str], 
                          patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate withdrawal plan for a drug path
        
        Args:
            drug_path: [drug, mechanism, symptom]
            patient_profile: Patient clinical information
            
        Returns:
            withdrawal_plan: Detailed withdrawal strategy
        """
        extractability_result = self.calculate_extractability_score(drug_path, patient_profile)
        drug, mechanism, symptom = drug_path
        
        # Determine withdrawal timeline based on extractability score
        score = extractability_result["extractability_score"]
        
        if score >= 0.7:
            timeline = "2-4周"
            strategy = "直接减量法"
            monitoring = "每周评估"
        elif score >= 0.5:
            timeline = "4-8周"
            strategy = "分阶段减量法"
            monitoring = "每3天评估"
        elif score >= 0.3:
            timeline = "8-16周"
            strategy = "超缓慢减量法"
            monitoring = "每日评估"
        else:
            timeline = "16周以上"
            strategy = "替代治疗法"
            monitoring = "密切监测"
        
        return {
            "drug": drug,
            "extractability_score": score,
            "withdrawal_timeline": timeline,
            "withdrawal_strategy": strategy,
            "monitoring_frequency": monitoring,
            "risk_mitigation": [
                "逐步减量，避免突然停药",
                "监测反弹症状",
                "必要时使用替代治疗",
                "心理支持和教育"
            ],
            "warning_signs": [
                "症状明显反弹",
                "新出现的不适症状",
                "焦虑或抑郁加重",
                "睡眠质量下降"
            ]
        }
    
    def is_path_extractable(self, drug_path: List[str], 
                          patient_profile: Dict[str, Any],
                          threshold: float = 0.4) -> bool:
        """
        Check if a drug path is extractable above threshold
        
        Args:
            drug_path: [drug, mechanism, symptom]
            patient_profile: Patient clinical information
            threshold: Minimum extractability threshold
            
        Returns:
            is_extractable: Boolean indicating if path is extractable
        """
        result = self.calculate_extractability_score(drug_path, patient_profile)
        return result["extractability_score"] >= threshold

def create_sample_patient_profile() -> Dict[str, Any]:
    """Create sample patient profile for testing"""
    return {
        'age': 45,
        'symptom_duration_months': 8,
        'previous_medications': 2,
        'comorbidities': ['anxiety', 'hypertension'],
        'psychological_dependency_risk': 0.6,
        'symptom_severity': 7,
        'social_support_score': 6,
        'treatment_compliance': 0.8,
        'economic_stress': 0.4
    }

if __name__ == "__main__":
    # Test the extractability scorer
    scorer = ExtractabilityScorer()
    
    print("🔓 Extractability Scorer Test")
    
    # Sample patient profile
    patient_profile = create_sample_patient_profile()
    
    # Test drug paths
    test_paths = [
        ["帕罗西汀", "抗焦虑", "焦虑"],
        ["洛哌丁胺", "止泻", "腹泻"],
        ["双歧杆菌", "调节肠道菌群", "腹胀"],
        ["奥沙西泮", "抗焦虑", "失眠"]
    ]
    
    print(f"\n患者档案: {patient_profile}")
    
    # Compare extractability for different paths
    comparison_results = scorer.compare_path_extractability(test_paths, patient_profile)
    
    print(f"\n药物路径可拔出性比较:")
    for i, result in enumerate(comparison_results, 1):
        path = result["drug_path"]
        score = result["extractability_score"]
        level = result["extractability_level"]
        print(f"  {i}. {' → '.join(path)}")
        print(f"     可拔出性评分: {score:.3f} ({level})")
        print(f"     建议: {result['recommendation']}")
        print()
    
    # Generate withdrawal plan for best path
    best_path = comparison_results[0]["drug_path"]
    withdrawal_plan = scorer.get_withdrawal_plan(best_path, patient_profile)
    
    print(f"最佳路径撤药计划:")
    print(f"  药物: {withdrawal_plan['drug']}")
    print(f"  撤药时间: {withdrawal_plan['withdrawal_timeline']}")
    print(f"  撤药策略: {withdrawal_plan['withdrawal_strategy']}")
    print(f"  监测频率: {withdrawal_plan['monitoring_frequency']}")
    print(f"  风险缓解措施: {withdrawal_plan['risk_mitigation']}")
    print(f"  警告信号: {withdrawal_plan['warning_signs']}") 