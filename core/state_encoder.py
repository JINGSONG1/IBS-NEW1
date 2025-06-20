"""
State Encoder Module for IBS Symptom Questionnaire with Hidden Causal Mechanisms
Converts psychological, physical symptoms and hidden causal factors to state vectors
"""

import numpy as np
import torch
import torch.nn as nn
from typing import Dict, Any

class IBSStateEncoder(nn.Module):
    """
    Enhanced Encodes IBS symptoms from questionnaire data into state vectors
    Handles psychological, physical symptoms and hidden causal mechanisms
    New: Type-D personality, SSAI, Vitamin D deficiency, etc.
    """
    
    def __init__(self, 
                 symptom_dim: int = 10,
                 psychological_dim: int = 5, 
                 physical_dim: int = 5,
                 hidden_causal_dim: int = 8,  # NEW: Hidden causal mechanisms
                 hidden_dim: int = 96,  # Increased for multi-channel
                 output_dim: int = 48):  # Increased output dimension
        super(IBSStateEncoder, self).__init__()
        
        self.symptom_dim = symptom_dim
        self.psychological_dim = psychological_dim
        self.physical_dim = physical_dim
        self.hidden_causal_dim = hidden_causal_dim
        self.hidden_dim = hidden_dim
        self.output_dim = output_dim
        
        # Enhanced symptom categories mapping
        self.psychological_symptoms = ['anxiety', 'depression', 'stress', 'mood_swings', 'sleep_quality']
        self.physical_symptoms = ['diarrhea', 'constipation', 'bloating', 'abdominal_pain', 'gas']
        
        # NEW: Hidden causal mechanism factors
        self.hidden_causal_factors = [
            'type_d_negative_affectivity',  # Type-D personality: negative affectivity
            'type_d_social_inhibition',     # Type-D personality: social inhibition
            'ssai_state_anxiety',           # SSAI: State anxiety
            'ssai_trait_anxiety',           # SSAI: Trait anxiety
            'vitamin_d_deficiency',         # Vitamin D deficiency level
            'cortisol_dysregulation',       # Cortisol level dysregulation
            'inflammatory_markers',         # Inflammatory marker levels (IL-6, TNF-α)
            'gut_microbiome_diversity'      # Gut microbiome diversity index
        ]
        
        # Multi-channel encoders
        self.psychological_encoder = nn.Sequential(
            nn.Linear(self.psychological_dim, hidden_dim//3),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim//3, hidden_dim//6),
            nn.ReLU(),
            nn.Dropout(0.15)
        )
        
        self.physical_encoder = nn.Sequential(
            nn.Linear(self.physical_dim, hidden_dim//3),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim//3, hidden_dim//6),
            nn.ReLU(),
            nn.Dropout(0.15)
        )
        
        # NEW: Hidden causal mechanism encoder
        self.hidden_causal_encoder = nn.Sequential(
            nn.Linear(self.hidden_causal_dim, hidden_dim//3),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(hidden_dim//3, hidden_dim//6),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        
        # Enhanced fusion layer with attention mechanism
        self.attention_layer = nn.MultiheadAttention(
            embed_dim=hidden_dim//6,
            num_heads=2,
            dropout=0.2,
            batch_first=True
        )
        
        self.fusion_layer = nn.Sequential(
            nn.Linear(hidden_dim//2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Dropout(0.25),
            nn.Linear(hidden_dim//2, output_dim),
            nn.Tanh()  # Normalize output to [-1, 1]
        )
        
    def forward(self, questionnaire_data: torch.Tensor) -> torch.Tensor:
        """
        Enhanced forward pass to encode questionnaire data with hidden causal mechanisms
        
        Args:
            questionnaire_data: Tensor of shape (batch_size, total_dim)
                               First 5 dims: psychological symptoms
                               Next 5 dims: physical symptoms  
                               Last 8 dims: hidden causal mechanisms
        
        Returns:
            state_vector: Enhanced encoded state tensor (batch_size, output_dim)
        """
        batch_size = questionnaire_data.shape[0]
        
        # Split into three channels
        psychological_data = questionnaire_data[:, :self.psychological_dim]
        physical_data = questionnaire_data[:, self.psychological_dim:self.psychological_dim + self.physical_dim]
        hidden_causal_data = questionnaire_data[:, -self.hidden_causal_dim:]
        
        # Encode each channel
        psychological_encoded = self.psychological_encoder(psychological_data)
        physical_encoded = self.physical_encoder(physical_data)
        hidden_causal_encoded = self.hidden_causal_encoder(hidden_causal_data)
        
        # Multi-channel attention mechanism
        channels = torch.stack([psychological_encoded, physical_encoded, hidden_causal_encoded], dim=1)
        attended_channels, _ = self.attention_layer(channels, channels, channels)
        
        # Fusion
        combined = attended_channels.view(batch_size, -1)
        state_vector = self.fusion_layer(combined)
        
        return state_vector
    
    def encode_questionnaire(self, questionnaire_dict: Dict[str, float]) -> np.ndarray:
        """
        Enhanced encode questionnaire dictionary to state vector with hidden causal mechanisms
        
        Args:
            questionnaire_dict: Dictionary with symptom scores and causal factors (0-10 scale)
        
        Returns:
            state_vector: Numpy array of enhanced encoded state
        """
        # Initialize enhanced symptom vector
        total_dim = self.psychological_dim + self.physical_dim + self.hidden_causal_dim
        symptom_vector = np.zeros(total_dim)
        
        # Fill psychological symptoms
        for i, symptom in enumerate(self.psychological_symptoms):
            if symptom in questionnaire_dict:
                symptom_vector[i] = questionnaire_dict[symptom] / 10.0  # Normalize to [0,1]
        
        # Fill physical symptoms  
        for i, symptom in enumerate(self.physical_symptoms):
            if symptom in questionnaire_dict:
                symptom_vector[self.psychological_dim + i] = questionnaire_dict[symptom] / 10.0
        
        # NEW: Fill hidden causal mechanisms
        for i, factor in enumerate(self.hidden_causal_factors):
            if factor in questionnaire_dict:
                symptom_vector[self.psychological_dim + self.physical_dim + i] = questionnaire_dict[factor] / 10.0
        
        # Convert to tensor and encode
        with torch.no_grad():
            symptom_tensor = torch.FloatTensor(symptom_vector).unsqueeze(0)
            state_vector = self.forward(symptom_tensor)
            
        return state_vector.squeeze(0).numpy()
    
    def get_enhanced_symptom_analysis(self, state_vector: torch.Tensor) -> Dict[str, Any]:
        """
        Enhanced interpretation of state vector including hidden causal mechanisms
        
        Args:
            state_vector: Enhanced encoded state tensor
            
        Returns:
            analysis_dict: Dictionary with comprehensive analysis
        """
        # Enhanced interpretation based on state vector magnitudes
        analysis_dict = {}
        
        # Traditional symptom analysis
        psychological_severity = torch.mean(torch.abs(state_vector[:16]))  # First 16 dims
        physical_severity = torch.mean(torch.abs(state_vector[16:32]))     # Next 16 dims
        hidden_causal_severity = torch.mean(torch.abs(state_vector[32:]))  # Last dims
        
        def severity_level(score):
            if score < 0.3:
                return "Mild"
            elif score < 0.7:
                return "Moderate" 
            else:
                return "Severe"
        
        analysis_dict['psychological_severity'] = severity_level(psychological_severity)
        analysis_dict['physical_severity'] = severity_level(physical_severity)
        analysis_dict['hidden_causal_severity'] = severity_level(hidden_causal_severity)
        analysis_dict['overall_severity'] = severity_level((psychological_severity + physical_severity + hidden_causal_severity) / 3)
        
        # NEW: Hidden causal mechanism analysis
        analysis_dict['type_d_personality_risk'] = "High" if hidden_causal_severity > 0.6 else "Low"
        analysis_dict['vitamin_d_deficiency_risk'] = "Present" if torch.mean(torch.abs(state_vector[36:40])) > 0.5 else "Absent"
        analysis_dict['inflammatory_risk'] = "Elevated" if torch.mean(torch.abs(state_vector[40:44])) > 0.5 else "Normal"
        analysis_dict['microbiome_dysbiosis_risk'] = "Present" if torch.mean(torch.abs(state_vector[44:])) > 0.5 else "Absent"
        
        return analysis_dict
    
    # Compatibility method for existing code
    def get_symptom_severity(self, state_vector: torch.Tensor) -> Dict[str, str]:
        """Legacy method for backward compatibility"""
        enhanced_analysis = self.get_enhanced_symptom_analysis(state_vector)
        return {
            'psychological_severity': enhanced_analysis['psychological_severity'],
            'physical_severity': enhanced_analysis['physical_severity'],
            'overall_severity': enhanced_analysis['overall_severity']
        }

def create_enhanced_sample_questionnaire() -> Dict[str, float]:
    """Create an enhanced sample questionnaire with hidden causal mechanisms"""
    return {
        # Traditional symptoms
        'anxiety': 7.5,
        'depression': 6.0,
        'stress': 8.0,
        'mood_swings': 5.5,
        'sleep_quality': 4.0,
        'diarrhea': 8.5,
        'constipation': 2.0,
        'bloating': 7.0,
        'abdominal_pain': 8.0,
        'gas': 6.5,
        
        # NEW: Hidden causal mechanisms
        'type_d_negative_affectivity': 7.0,
        'type_d_social_inhibition': 6.5,
        'ssai_state_anxiety': 8.0,
        'ssai_trait_anxiety': 7.5,
        'vitamin_d_deficiency': 8.5,
        'cortisol_dysregulation': 6.0,
        'inflammatory_markers': 7.0,
        'gut_microbiome_diversity': 3.0  # Lower is worse
    }

# Compatibility function for existing code
def create_sample_questionnaire() -> Dict[str, float]:
    """Create a sample questionnaire for backward compatibility"""
    enhanced_sample = create_enhanced_sample_questionnaire()
    # Return only traditional symptoms for backward compatibility
    return {k: v for k, v in enhanced_sample.items() if k in [
        'anxiety', 'depression', 'stress', 'mood_swings', 'sleep_quality',
        'diarrhea', 'constipation', 'bloating', 'abdominal_pain', 'gas'
    ]}

if __name__ == "__main__":
    # Test the enhanced state encoder
    encoder = IBSStateEncoder()
    
    # Test with enhanced sample data
    enhanced_questionnaire = create_enhanced_sample_questionnaire()
    state_vector = encoder.encode_questionnaire(enhanced_questionnaire)
    
    print("📊 Enhanced IBS State Encoder Test")
    print(f"Input questionnaire: {enhanced_questionnaire}")
    print(f"Encoded state vector shape: {state_vector.shape}")
    print(f"State vector: {state_vector}")
    
    # Test enhanced analysis
    enhanced_analysis = encoder.get_enhanced_symptom_analysis(torch.FloatTensor(state_vector))
    print(f"Enhanced analysis: {enhanced_analysis}")
    
    # Test backward compatibility
    traditional_analysis = encoder.get_symptom_severity(torch.FloatTensor(state_vector))
    print(f"Traditional analysis (backward compatibility): {traditional_analysis}") 