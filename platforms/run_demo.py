"""
ReticulotypeToolkit Demo Script
Demonstrates the complete AI-powered IBS drug recommendation system
"""

import numpy as np
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def create_sample_patient():
    """Create a sample patient for demonstration"""
    return {
        'patient_id': 'demo_001',
        'age': 45,
        'questionnaire': {
            'anxiety': 7.5,
            'depression': 6.0,
            'stress': 8.0,
            'mood_swings': 5.5,
            'sleep_quality': 4.0,
            'diarrhea': 8.5,
            'constipation': 2.0,
            'bloating': 7.0,
            'abdominal_pain': 8.0,
            'gas': 6.5
        },
        'symptom_duration_months': 8,
        'previous_medications': 2,
        'comorbidities': ['anxiety', 'hypertension']
    }

def demo_state_encoding():
    """Demonstrate state encoding functionality"""
    print("🧠 === State Encoding Demo ===")
    
    try:
        from core.state_encoder import IBSStateEncoder
        
        # Initialize encoder
        encoder = IBSStateEncoder()
        
        # Create sample patient
        patient = create_sample_patient()
        questionnaire = patient['questionnaire']
        
        # Encode questionnaire
        state_vector = encoder.encode_questionnaire(questionnaire)
        severity = encoder.get_symptom_severity(state_vector)
        
        print(f"Patient ID: {patient['patient_id']}")
        print(f"Input questionnaire: {questionnaire}")
        print(f"Encoded state vector shape: {state_vector.shape}")
        print(f"Severity analysis: {severity}")
        
        return state_vector, patient
        
    except ImportError as e:
        print(f"⚠️ Could not import state encoder: {e}")
        print("Using mock state vector...")
        return np.random.randn(32), create_sample_patient()

def demo_fsm_paths():
    """Demonstrate FSM path loading and drug recommendation"""
    print("\n🧬 === FSM Path Loading Demo ===")
    
    try:
        from mechanism.fsm_path_loader import FSMPathLoader
        
        # Initialize FSM loader
        fsm_loader = FSMPathLoader()
        
        # Test drug path validation
        test_paths = [
            ["帕罗西汀", "抗焦虑", "焦虑"],
            ["洛哌丁胺", "止泻", "腹泻"],
            ["双歧杆菌", "调节肠道菌群", "腹胀"]
        ]
        
        print("Testing drug path validation:")
        for path in test_paths:
            is_valid = fsm_loader.validate_path(path)
            explanation = fsm_loader.get_path_explanation(path)
            print(f"  {' → '.join(path)}: {'✅ Valid' if is_valid else '❌ Invalid'}")
            print(f"    Confidence: {explanation.get('confidence', 0):.3f}")
        
        # Test symptom-based recommendations
        target_symptoms = ["焦虑", "腹泻"]
        drug_recommendations = fsm_loader.find_optimal_drug_for_symptoms(target_symptoms)
        
        print(f"\nTop drug recommendations for {target_symptoms}:")
        for drug, score in sorted(drug_recommendations.items(), key=lambda x: x[1], reverse=True)[:3]:
            print(f"  {drug}: {score:.3f}")
        
        return fsm_loader
        
    except ImportError as e:
        print(f"⚠️ Could not import FSM loader: {e}")
        print("Using mock FSM loader...")
        
        class MockFSMLoader:
            def validate_path(self, path):
                return len(path) == 3
            
            def find_optimal_drug_for_symptoms(self, symptoms):
                return {"帕罗西汀": 0.85, "双歧杆菌": 0.72, "阿米替林": 0.68}
        
        return MockFSMLoader()

def demo_keylock_matching():
    """Demonstrate KeyLock mechanism matching"""
    print("\n🔐 === KeyLock Matching Demo ===")
    
    try:
        from mechanism.mechanism_keylock_encoder import MechanismKeyLockEncoder
        
        # Initialize KeyLock encoder
        keylock_encoder = MechanismKeyLockEncoder()
        
        # Create sample state vector
        state_vector = np.random.randn(32)
        
        # Test mechanism compatibility
        test_mechanisms = ["抗焦虑", "改善腹泻", "抗抑郁"]
        compatibility = keylock_encoder.get_mechanism_compatibility(state_vector, test_mechanisms)
        
        print("Mechanism compatibility scores:")
        for mechanism, score in compatibility.items():
            print(f"  {mechanism}: {score:.3f}")
        
        # Find best mechanisms
        best_mechanisms = keylock_encoder.find_best_mechanisms(state_vector, top_k=3)
        print(f"\nTop 3 best matching mechanisms:")
        for mechanism, score in best_mechanisms:
            print(f"  {mechanism}: {score:.3f}")
        
        return keylock_encoder
        
    except ImportError as e:
        print(f"⚠️ Could not import KeyLock encoder: {e}")
        print("Using mock KeyLock encoder...")
        
        class MockKeyLockEncoder:
            def get_mechanism_compatibility(self, state_vector, mechanisms):
                return {mech: np.random.random() * 0.8 + 0.1 for mech in mechanisms}
        
        return MockKeyLockEncoder()

def demo_buffgate_validation():
    """Demonstrate BuffGate validation system"""
    print("\n🛡️ === BuffGate Validation Demo ===")
    
    # Create mock BuffGate for demo
    class MockBuffGate:
        def validate_recommendation(self, drug_path, state_vector, patient_profile):
            score = np.random.random() * 0.8 + 0.1
            return {
                "passed": score > 0.5,
                "overall_score": score,
                "recommendation_confidence": score,
                "gate_results": {
                    "fsm_validation": {"score": 1.0},
                    "keylock_matching": {"score": np.random.random()},
                    "extractability_assessment": {"score": np.random.random()}
                }
            }
    
    buffgate = MockBuffGate()
    
    # Test drug path
    drug_path = ["帕罗西汀", "抗焦虑", "焦虑"]
    state_vector = np.random.randn(32)
    patient_profile = {
        'age': 45,
        'symptom_duration_months': 8,
        'previous_medications': 2,
        'psychological_dependency_risk': 0.6
    }
    
    # Validate recommendation
    result = buffgate.validate_recommendation(drug_path, state_vector, patient_profile)
    
    print(f"Testing drug path: {' → '.join(drug_path)}")
    print(f"Validation result: {'✅ PASSED' if result['passed'] else '❌ REJECTED'}")
    print(f"Overall score: {result['overall_score']:.3f}")
    print(f"Confidence: {result['recommendation_confidence']:.3f}")
    
    # Show gate breakdown
    gate_results = result['gate_results']
    print(f"\nGate breakdown:")
    print(f"  FSM validation: {gate_results['fsm_validation']['score']:.3f}")
    print(f"  KeyLock matching: {gate_results['keylock_matching']['score']:.3f}")
    print(f"  Extractability: {gate_results['extractability_assessment']['score']:.3f}")
    
    return buffgate

def demo_complete_pipeline():
    """Demonstrate complete recommendation pipeline"""
    print("\n🔄 === Complete Pipeline Demo ===")
    
    # Create patient
    patient = create_sample_patient()
    print(f"Patient: {patient['patient_id']}, Age: {patient['age']}")
    
    # Step 1: Encode patient state
    state_vector, _ = demo_state_encoding()
    
    # Step 2: Get FSM recommendations
    fsm_loader = demo_fsm_paths()
    
    # Step 3: KeyLock matching
    keylock_encoder = demo_keylock_matching()
    
    # Step 4: BuffGate validation
    buffgate = demo_buffgate_validation()
    
    print("\n✅ Complete pipeline demonstration finished!")
    print("🎯 ReticulotypeToolkit successfully demonstrated all core components!")

def main():
    """Main demo function"""
    print("🧠 ReticulotypeToolkit Demo")
    print("=" * 50)
    print("Demonstrating AI-powered IBS drug recommendation system")
    print("=" * 50)
    
    try:
        # Run complete pipeline demo
        demo_complete_pipeline()
        
        print("\n🎉 Demo completed successfully!")
        print("💡 To run the web interface: streamlit run interface/streamlit_app.py")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Demo interrupted by user")
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        print("This is expected if dependencies are not fully installed")

if __name__ == "__main__":
    main()