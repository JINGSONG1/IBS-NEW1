"""
FSM-MCP BuffGate Module
Multi-layer validation gate to prevent incorrect drug recommendations
Implements FSM + KeyLock + Extractability triple verification
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional, Any, Union
import json
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

class FSMMCPBuffGate:
    """
    Multi-layer BuffGate for drug recommendation validation
    Combines FSM path validation, KeyLock matching, and Extractability scoring
    """
    
    def __init__(self, 
                 config_path: str = "config/buffgate_config.json"):
        
        # Initialize components (will be loaded lazily)
        self.fsm_loader = None
        self.keylock_encoder = None
        self.extractability_scorer = None
        
        # BuffGate configuration
        self.config_path = config_path
        self.gate_config = self._load_gate_config()
        
        # Validation thresholds
        self.fsm_threshold = self.gate_config.get("fsm_threshold", 1.0)  # Must be valid FSM path
        self.keylock_threshold = self.gate_config.get("keylock_threshold", 0.5)
        self.extractability_threshold = self.gate_config.get("extractability_threshold", 0.4)
        self.overall_threshold = self.gate_config.get("overall_threshold", 0.6)
        
        # Gate weights
        self.gate_weights = self.gate_config.get("gate_weights", {
            "fsm_weight": 0.4,
            "keylock_weight": 0.3,
            "extractability_weight": 0.3
        })
        
        # Recommendation history for learning
        self.recommendation_history = []
        
        # Initialize components
        self._initialize_components()
        
    def _initialize_components(self):
        """Initialize the component modules"""
        try:
            from .fsm_path_loader import FSMPathLoader
            from .mechanism_keylock_encoder import MechanismKeyLockEncoder
            from .extractability_scorer import ExtractabilityScorer
            
            self.fsm_loader = FSMPathLoader()
            self.keylock_encoder = MechanismKeyLockEncoder()
            self.extractability_scorer = ExtractabilityScorer()
            
            print("✅ BuffGate components initialized successfully")
            
        except ImportError as e:
            print(f"⚠️ Failed to import components: {e}")
            print("Using mock components for testing")
            self._initialize_mock_components()
    
    def _initialize_mock_components(self):
        """Initialize mock components for testing"""
        class MockFSMLoader:
            def validate_path(self, path):
                return len(path) == 3 and path[0] != "无效药物"
            
            def get_path_explanation(self, path):
                return {"confidence": 0.8}
            
            def get_symptom_paths(self, symptom):
                return [
                    ["帕罗西汀", "抗焦虑", symptom],
                    ["双歧杆菌", "调节肠道菌群", symptom]
                ]
        
        class MockKeyLockEncoder:
            def get_mechanism_compatibility(self, state_vector, mechanisms):
                return {mech: np.random.random() * 0.8 + 0.1 for mech in mechanisms}
            
            def get_keylock_explanation(self, state_vector, mechanism):
                score = np.random.random() * 0.8 + 0.1
                return {
                    "confidence": score,
                    "suitability": "较为适合" if score > 0.5 else "可能适合"
                }
        
        class MockExtractabilityScorer:
            def calculate_extractability_score(self, path, profile):
                score = np.random.random() * 0.8 + 0.1
                return {
                    "extractability_score": score,
                    "extractability_level": "中等难度",
                    "safe_to_recommend": score > 0.4
                }
        
        self.fsm_loader = MockFSMLoader()
        self.keylock_encoder = MockKeyLockEncoder()
        self.extractability_scorer = MockExtractabilityScorer()
        
    def _load_gate_config(self) -> Dict[str, Any]:
        """Load BuffGate configuration"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            print(f"✅ Loaded BuffGate config from {self.config_path}")
            return config
        except FileNotFoundError:
            print(f"⚠️ BuffGate config not found, using defaults")
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict[str, Any]:
        """Create default BuffGate configuration"""
        default_config = {
            "fsm_threshold": 1.0,
            "keylock_threshold": 0.5,
            "extractability_threshold": 0.4,
            "overall_threshold": 0.6,
            "gate_weights": {
                "fsm_weight": 0.4,
                "keylock_weight": 0.3,
                "extractability_weight": 0.3
            },
            "safety_rules": {
                "max_dependency_risk": 0.8,
                "min_extractability": 0.3,
                "require_mechanism_match": True,
                "allow_off_label": False
            },
            "escalation_rules": {
                "high_risk_threshold": 0.7,
                "require_doctor_approval": True,
                "max_auto_recommendations": 3
            }
        }
        
        # Save default config
        Path(self.config_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, ensure_ascii=False, indent=2)
        
        return default_config
    
    def validate_recommendation(self, 
                              drug_path: List[str],
                              state_vector: np.ndarray,
                              patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Comprehensive validation of drug recommendation through BuffGate
        
        Args:
            drug_path: [drug, mechanism, symptom]
            state_vector: Patient state vector
            patient_profile: Patient clinical information
            
        Returns:
            validation_result: Comprehensive validation results
        """
        if len(drug_path) != 3:
            return {
                "passed": False,
                "overall_score": 0.0,
                "reason": "Invalid drug path format",
                "gate_results": {}
            }
        
        drug, mechanism, symptom = drug_path
        
        # Gate 1: FSM Path Validation
        fsm_result = self._validate_fsm_path(drug_path)
        
        # Gate 2: KeyLock Mechanism Matching
        keylock_result = self._validate_keylock_matching(drug_path, state_vector)
        
        # Gate 3: Extractability Assessment
        extractability_result = self._validate_extractability(drug_path, patient_profile)
        
        # Combine results
        overall_score = self._calculate_overall_score(fsm_result, keylock_result, extractability_result)
        
        # Final decision
        passed = self._make_final_decision(fsm_result, keylock_result, extractability_result, overall_score)
        
        # Generate explanation
        explanation = self._generate_explanation(fsm_result, keylock_result, extractability_result, passed)
        
        validation_result = {
            "drug_path": drug_path,
            "passed": passed,
            "overall_score": overall_score,
            "explanation": explanation,
            "gate_results": {
                "fsm_validation": fsm_result,
                "keylock_matching": keylock_result,
                "extractability_assessment": extractability_result
            },
            "safety_flags": self._check_safety_flags(drug_path, patient_profile),
            "recommendation_confidence": min(overall_score * 1.2, 1.0)
        }
        
        # Log recommendation for learning
        self._log_recommendation(validation_result)
        
        return validation_result
    
    def _validate_fsm_path(self, drug_path: List[str]) -> Dict[str, Any]:
        """Validate drug path through FSM"""
        is_valid = self.fsm_loader.validate_path(drug_path)
        
        if is_valid:
            path_explanation = self.fsm_loader.get_path_explanation(drug_path)
            confidence = path_explanation.get("confidence", 0.8)
        else:
            confidence = 0.0
        
        return {
            "valid": is_valid,
            "score": 1.0 if is_valid else 0.0,
            "confidence": confidence,
            "threshold_passed": is_valid,
            "details": f"FSM路径验证: {'通过' if is_valid else '失败'}"
        }
    
    def _validate_keylock_matching(self, drug_path: List[str], state_vector: np.ndarray) -> Dict[str, Any]:
        """Validate mechanism matching through KeyLock"""
        drug, mechanism, symptom = drug_path
        
        # Get mechanism compatibility
        compatibility = self.keylock_encoder.get_mechanism_compatibility(state_vector, [mechanism])
        score = compatibility[mechanism]
        
        # Check if passes threshold
        threshold_passed = score >= self.keylock_threshold
        
        # Get detailed explanation
        explanation = self.keylock_encoder.get_keylock_explanation(state_vector, mechanism)
        
        return {
            "valid": threshold_passed,
            "score": score,
            "confidence": explanation.get("confidence", 0.5),
            "threshold_passed": threshold_passed,
            "details": f"KeyLock匹配: {explanation.get('suitability', '未知')} (评分: {score:.3f})"
        }
    
    def _validate_extractability(self, drug_path: List[str], patient_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Validate extractability through Extractability Scorer"""
        extractability_result = self.extractability_scorer.calculate_extractability_score(drug_path, patient_profile)
        
        score = extractability_result["extractability_score"]
        threshold_passed = score >= self.extractability_threshold
        safe_to_recommend = extractability_result["safe_to_recommend"]
        
        return {
            "valid": safe_to_recommend,
            "score": score,
            "confidence": min(score * 1.5, 1.0),
            "threshold_passed": threshold_passed,
            "details": f"可拔出性评估: {extractability_result['extractability_level']} (评分: {score:.3f})"
        }
    
    def _calculate_overall_score(self, fsm_result: Dict, keylock_result: Dict, extractability_result: Dict) -> float:
        """Calculate weighted overall score"""
        weights = self.gate_weights
        
        overall_score = (
            fsm_result["score"] * weights["fsm_weight"] +
            keylock_result["score"] * weights["keylock_weight"] +
            extractability_result["score"] * weights["extractability_weight"]
        )
        
        return overall_score
    
    def _make_final_decision(self, fsm_result: Dict, keylock_result: Dict, 
                           extractability_result: Dict, overall_score: float) -> bool:
        """Make final recommendation decision"""
        # Hard requirements
        if not fsm_result["valid"]:
            return False  # Must be valid FSM path
        
        # Soft requirements with overall score
        if overall_score < self.overall_threshold:
            return False
        
        # Additional safety checks
        safety_rules = self.gate_config.get("safety_rules", {})
        
        if safety_rules.get("require_mechanism_match", True):
            if not keylock_result["threshold_passed"]:
                return False
        
        if extractability_result["score"] < safety_rules.get("min_extractability", 0.3):
            return False
        
        return True
    
    def _generate_explanation(self, fsm_result: Dict, keylock_result: Dict, 
                            extractability_result: Dict, passed: bool) -> str:
        """Generate human-readable explanation"""
        explanations = []
        
        # FSM explanation
        explanations.append(fsm_result["details"])
        
        # KeyLock explanation
        explanations.append(keylock_result["details"])
        
        # Extractability explanation
        explanations.append(extractability_result["details"])
        
        # Final decision
        decision = "✅ 推荐通过" if passed else "❌ 推荐被拒绝"
        
        return f"{decision}\n" + "\n".join(f"• {exp}" for exp in explanations)
    
    def _check_safety_flags(self, drug_path: List[str], patient_profile: Dict[str, Any]) -> List[str]:
        """Check for safety flags"""
        flags = []
        
        drug, mechanism, symptom = drug_path
        
        # Check age-related flags
        age = patient_profile.get('age', 40)
        if age > 65:
            flags.append("老年患者用药需谨慎")
        if age < 18:
            flags.append("未成年患者用药需特别注意")
        
        # Check drug-specific flags
        if drug in ["奥沙西泮", "洛哌丁胺"]:
            flags.append("高依赖风险药物")
        
        # Check duration flags
        duration = patient_profile.get('symptom_duration_months', 6)
        if duration > 12:
            flags.append("长期症状，需考虑根本原因")
        
        # Check comorbidity flags
        comorbidities = patient_profile.get('comorbidities', [])
        if 'liver_disease' in comorbidities:
            flags.append("肝功能异常，需调整剂量")
        if 'kidney_disease' in comorbidities:
            flags.append("肾功能异常，需调整剂量")
        
        return flags
    
    def _log_recommendation(self, validation_result: Dict[str, Any]):
        """Log recommendation for learning and analysis"""
        import datetime
        
        self.recommendation_history.append({
            "timestamp": datetime.datetime.now().isoformat(),
            "drug_path": validation_result["drug_path"],
            "passed": validation_result["passed"],
            "overall_score": validation_result["overall_score"],
            "gate_scores": {
                "fsm": validation_result["gate_results"]["fsm_validation"]["score"],
                "keylock": validation_result["gate_results"]["keylock_matching"]["score"],
                "extractability": validation_result["gate_results"]["extractability_assessment"]["score"]
            }
        })
        
        # Keep only recent history
        if len(self.recommendation_history) > 1000:
            self.recommendation_history = self.recommendation_history[-500:]
    
    def batch_validate_recommendations(self, 
                                     recommendations: List[Tuple[List[str], np.ndarray, Dict[str, Any]]]) -> List[Dict[str, Any]]:
        """Batch validate multiple recommendations"""
        results = []
        
        for drug_path, state_vector, patient_profile in recommendations:
            result = self.validate_recommendation(drug_path, state_vector, patient_profile)
            results.append(result)
        
        return results
    
    def get_alternative_recommendations(self, 
                                      failed_path: List[str],
                                      state_vector: np.ndarray,
                                      patient_profile: Dict[str, Any],
                                      max_alternatives: int = 3) -> List[Dict[str, Any]]:
        """Get alternative recommendations when original fails"""
        drug, mechanism, symptom = failed_path
        
        # Get alternative paths for the same symptom
        alternative_paths = self.fsm_loader.get_symptom_paths(symptom)
        
        # Filter out the failed path
        alternative_paths = [path for path in alternative_paths if path != failed_path]
        
        # Validate alternatives
        validated_alternatives = []
        for alt_path in alternative_paths[:max_alternatives * 2]:  # Check more than needed
            result = self.validate_recommendation(alt_path, state_vector, patient_profile)
            if result["passed"]:
                validated_alternatives.append(result)
                if len(validated_alternatives) >= max_alternatives:
                    break
        
        # Sort by overall score
        validated_alternatives.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return validated_alternatives[:max_alternatives]
    
    def update_gate_thresholds(self, feedback_data: List[Dict[str, Any]]):
        """Update gate thresholds based on feedback"""
        # Simple threshold adjustment based on feedback
        # In practice, this would use more sophisticated ML techniques
        
        successful_recommendations = [f for f in feedback_data if f.get("success", False)]
        failed_recommendations = [f for f in feedback_data if not f.get("success", False)]
        
        if len(successful_recommendations) > 0 and len(failed_recommendations) > 0:
            # Calculate average scores for successful vs failed
            success_scores = [f["overall_score"] for f in successful_recommendations]
            fail_scores = [f["overall_score"] for f in failed_recommendations]
            
            success_avg = np.mean(success_scores)
            fail_avg = np.mean(fail_scores)
            
            # Adjust threshold to be between fail_avg and success_avg
            new_threshold = (fail_avg + success_avg) / 2
            
            # Update with momentum
            momentum = 0.1
            self.overall_threshold = (1 - momentum) * self.overall_threshold + momentum * new_threshold
            
            print(f"📊 Updated BuffGate threshold: {self.overall_threshold:.3f}")
    
    def get_gate_statistics(self) -> Dict[str, Any]:
        """Get BuffGate performance statistics"""
        if not self.recommendation_history:
            return {"message": "No recommendation history available"}
        
        total_recommendations = len(self.recommendation_history)
        passed_recommendations = sum(1 for r in self.recommendation_history if r["passed"])
        
        # Calculate average scores
        avg_overall = np.mean([r["overall_score"] for r in self.recommendation_history])
        avg_fsm = np.mean([r["gate_scores"]["fsm"] for r in self.recommendation_history])
        avg_keylock = np.mean([r["gate_scores"]["keylock"] for r in self.recommendation_history])
        avg_extractability = np.mean([r["gate_scores"]["extractability"] for r in self.recommendation_history])
        
        return {
            "total_recommendations": total_recommendations,
            "passed_recommendations": passed_recommendations,
            "pass_rate": passed_recommendations / total_recommendations,
            "average_scores": {
                "overall": avg_overall,
                "fsm": avg_fsm,
                "keylock": avg_keylock,
                "extractability": avg_extractability
            },
            "current_thresholds": {
                "fsm": self.fsm_threshold,
                "keylock": self.keylock_threshold,
                "extractability": self.extractability_threshold,
                "overall": self.overall_threshold
            }
        }

if __name__ == "__main__":
    # Test the BuffGate system
    buffgate = FSMMCPBuffGate()
    
    print("🛡️ BuffGate Validation System Test")
    
    # Sample test data
    test_recommendations = [
        (["帕罗西汀", "抗焦虑", "焦虑"], np.random.randn(32), {"age": 45, "symptom_duration_months": 8}),
        (["洛哌丁胺", "止泻", "腹泻"], np.random.randn(32), {"age": 30, "symptom_duration_months": 3}),
        (["双歧杆菌", "调节肠道菌群", "腹胀"], np.random.randn(32), {"age": 50, "symptom_duration_months": 12}),
        (["无效药物", "无效机制", "无效症状"], np.random.randn(32), {"age": 25, "symptom_duration_months": 1})
    ]
    
    print("\n🔍 批量验证推荐:")
    for i, (drug_path, state_vector, patient_profile) in enumerate(test_recommendations, 1):
        result = buffgate.validate_recommendation(drug_path, state_vector, patient_profile)
        
        print(f"\n{i}. 药物路径: {' → '.join(drug_path)}")
        print(f"   验证结果: {'✅ 通过' if result['passed'] else '❌ 拒绝'}")
        print(f"   综合评分: {result['overall_score']:.3f}")
        print(f"   说明: {result['explanation'].replace(chr(10), ' ')}")
        
        if result["safety_flags"]:
            print(f"   安全提醒: {', '.join(result['safety_flags'])}")
    
    # Test alternative recommendations
    print(f"\n🔄 获取替代推荐:")
    failed_path = ["无效药物", "无效机制", "无效症状"]
    alternatives = buffgate.get_alternative_recommendations(
        failed_path, np.random.randn(32), {"age": 35, "symptom_duration_months": 6}
    )
    
    for i, alt in enumerate(alternatives, 1):
        print(f"  {i}. {' → '.join(alt['drug_path'])} (评分: {alt['overall_score']:.3f})")
    
    # Show statistics
    print(f"\n📊 BuffGate统计:")
    stats = buffgate.get_gate_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}") 