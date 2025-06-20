"""
Mechanism KeyLock Encoder Module
Implements state vector to mechanism path matching using KeyLock paradigm
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import json

class MechanismKeyLockEncoder(nn.Module):
    """
    KeyLock Encoder for matching patient state vectors to mechanism paths
    Uses neural network to determine if patient state (Key) matches mechanism path (Lock)
    """
    
    def __init__(self, 
                 state_dim: int = 32,
                 mechanism_dim: int = 16,
                 hidden_dim: int = 64,
                 num_mechanisms: int = 10,
                 dropout_rate: float = 0.3):
        super(MechanismKeyLockEncoder, self).__init__()
        
        self.state_dim = state_dim
        self.mechanism_dim = mechanism_dim
        self.hidden_dim = hidden_dim
        self.num_mechanisms = num_mechanisms
        
        # Mechanism embeddings (Locks)
        self.mechanism_embeddings = nn.Embedding(num_mechanisms, mechanism_dim)
        
        # State encoder (Key processor)
        self.state_encoder = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim//2, mechanism_dim)
        )
        
        # KeyLock matching network
        self.keylock_matcher = nn.Sequential(
            nn.Linear(mechanism_dim * 2, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim, hidden_dim//2),
            nn.ReLU(),
            nn.Dropout(dropout_rate),
            nn.Linear(hidden_dim//2, 1),
            nn.Sigmoid()  # Output matching probability
        )
        
        # Mechanism name mapping
        self.mechanism_names = [
            "抗焦虑", "改善腹泻", "抗抑郁", "促胃肠动力", "解痉",
            "止泻", "调节肠道菌群", "镇静", "抗胆碱", "5-HT调节"
        ]
        
        self.name_to_id = {name: i for i, name in enumerate(self.mechanism_names)}
        
    def forward(self, state_vector: torch.Tensor, mechanism_ids: torch.Tensor) -> torch.Tensor:
        """
        Forward pass for KeyLock matching
        
        Args:
            state_vector: Patient state tensor (batch_size, state_dim)
            mechanism_ids: Mechanism ID tensor (batch_size, num_mechanisms)
            
        Returns:
            match_scores: Matching probability scores (batch_size, num_mechanisms)
        """
        batch_size = state_vector.shape[0]
        
        # Encode state vector (Key)
        state_key = self.state_encoder(state_vector)  # (batch_size, mechanism_dim)
        
        # Get mechanism embeddings (Locks)
        mechanism_locks = self.mechanism_embeddings(mechanism_ids)  # (batch_size, num_mechanisms, mechanism_dim)
        
        # Expand state key for broadcasting
        state_key_expanded = state_key.unsqueeze(1).expand(-1, mechanism_ids.shape[1], -1)
        
        # Concatenate key and lock for matching
        keylock_input = torch.cat([state_key_expanded, mechanism_locks], dim=-1)
        
        # Compute matching scores
        match_scores = self.keylock_matcher(keylock_input).squeeze(-1)
        
        return match_scores
    
    def get_mechanism_compatibility(self, state_vector: np.ndarray, 
                                  mechanism_names: List[str]) -> Dict[str, float]:
        """
        Get compatibility scores between state vector and mechanism names
        
        Args:
            state_vector: Patient state vector
            mechanism_names: List of mechanism names to evaluate
            
        Returns:
            compatibility_scores: Dictionary mapping mechanism names to scores
        """
        with torch.no_grad():
            # Convert to tensor
            state_tensor = torch.FloatTensor(state_vector).unsqueeze(0)
            
            # Get mechanism IDs
            mechanism_ids = []
            for name in mechanism_names:
                if name in self.name_to_id:
                    mechanism_ids.append(self.name_to_id[name])
                else:
                    mechanism_ids.append(0)  # Default to first mechanism
            
            mechanism_tensor = torch.LongTensor(mechanism_ids).unsqueeze(0)
            
            # Compute compatibility scores
            scores = self.forward(state_tensor, mechanism_tensor)
            scores_np = scores.squeeze(0).numpy()
            
            # Create result dictionary
            compatibility_scores = {}
            for i, name in enumerate(mechanism_names):
                compatibility_scores[name] = float(scores_np[i])
            
            return compatibility_scores
    
    def find_best_mechanisms(self, state_vector: np.ndarray, 
                           top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Find top-k best matching mechanisms for given state vector
        
        Args:
            state_vector: Patient state vector
            top_k: Number of top mechanisms to return
            
        Returns:
            best_mechanisms: List of (mechanism_name, score) tuples
        """
        # Get compatibility with all mechanisms
        compatibility_scores = self.get_mechanism_compatibility(state_vector, self.mechanism_names)
        
        # Sort by score and return top-k
        sorted_mechanisms = sorted(compatibility_scores.items(), 
                                 key=lambda x: x[1], reverse=True)
        
        return sorted_mechanisms[:top_k]
    
    def is_mechanism_suitable(self, state_vector: np.ndarray, 
                            mechanism_name: str, threshold: float = 0.5) -> bool:
        """
        Check if a mechanism is suitable for given state vector
        
        Args:
            state_vector: Patient state vector
            mechanism_name: Mechanism name to check
            threshold: Minimum compatibility threshold
            
        Returns:
            is_suitable: Boolean indicating suitability
        """
        compatibility = self.get_mechanism_compatibility(state_vector, [mechanism_name])
        return compatibility[mechanism_name] >= threshold
    
    def get_keylock_explanation(self, state_vector: np.ndarray, 
                              mechanism_name: str) -> Dict[str, Any]:
        """
        Get explanation for KeyLock matching decision
        
        Args:
            state_vector: Patient state vector
            mechanism_name: Mechanism name
            
        Returns:
            explanation: Dictionary with explanation details
        """
        compatibility = self.get_mechanism_compatibility(state_vector, [mechanism_name])
        score = compatibility[mechanism_name]
        
        # Determine suitability level
        if score >= 0.8:
            suitability = "高度适合"
            reason = "患者状态与机制高度匹配"
        elif score >= 0.6:
            suitability = "较为适合"
            reason = "患者状态与机制较好匹配"
        elif score >= 0.4:
            suitability = "可能适合"
            reason = "患者状态与机制部分匹配"
        else:
            suitability = "不太适合"
            reason = "患者状态与机制匹配度较低"
        
        return {
            "mechanism": mechanism_name,
            "compatibility_score": score,
            "suitability": suitability,
            "reason": reason,
            "threshold_passed": score >= 0.5,
            "confidence": min(score * 1.2, 1.0)  # Adjusted confidence
        }
    
    def train_keylock_matching(self, training_data: List[Dict], 
                             epochs: int = 100, lr: float = 0.001):
        """
        Train the KeyLock matching network
        
        Args:
            training_data: List of training examples with state vectors and mechanism labels
            epochs: Number of training epochs
            lr: Learning rate
        """
        optimizer = torch.optim.Adam(self.parameters(), lr=lr)
        criterion = nn.BCELoss()
        
        for epoch in range(epochs):
            total_loss = 0.0
            
            for batch in training_data:
                state_vector = torch.FloatTensor(batch['state_vector']).unsqueeze(0)
                mechanism_ids = torch.LongTensor(batch['mechanism_ids']).unsqueeze(0)
                target_scores = torch.FloatTensor(batch['target_scores']).unsqueeze(0)
                
                # Forward pass
                predicted_scores = self.forward(state_vector, mechanism_ids)
                
                # Compute loss
                loss = criterion(predicted_scores, target_scores)
                
                # Backward pass
                optimizer.zero_grad()
                loss.backward()
                optimizer.step()
                
                total_loss += loss.item()
            
            if epoch % 20 == 0:
                print(f"Epoch {epoch}, Loss: {total_loss/len(training_data):.4f}")
    
    def save_model(self, filepath: str):
        """Save the trained model"""
        torch.save({
            'model_state_dict': self.state_dict(),
            'mechanism_names': self.mechanism_names,
            'name_to_id': self.name_to_id,
            'config': {
                'state_dim': self.state_dim,
                'mechanism_dim': self.mechanism_dim,
                'hidden_dim': self.hidden_dim,
                'num_mechanisms': self.num_mechanisms
            }
        }, filepath)
        print(f"✅ KeyLock model saved to {filepath}")
    
    def load_model(self, filepath: str):
        """Load a trained model"""
        checkpoint = torch.load(filepath, map_location='cpu')
        self.load_state_dict(checkpoint['model_state_dict'])
        self.mechanism_names = checkpoint['mechanism_names']
        self.name_to_id = checkpoint['name_to_id']
        print(f"✅ KeyLock model loaded from {filepath}")

def create_sample_training_data(num_samples: int = 100) -> List[Dict]:
    """Create sample training data for KeyLock matching"""
    training_data = []
    
    for _ in range(num_samples):
        # Random state vector
        state_vector = np.random.randn(32)
        
        # Random mechanism selection
        num_mechanisms = 10
        mechanism_ids = list(range(num_mechanisms))
        
        # Create target scores based on some heuristic
        target_scores = []
        for i in range(num_mechanisms):
            # Simple heuristic: higher scores for mechanisms that match state patterns
            if i < 3:  # First 3 mechanisms more likely for anxiety/depression states
                score = max(0.0, min(1.0, 0.7 + 0.3 * np.random.randn()))
            else:
                score = max(0.0, min(1.0, 0.3 + 0.4 * np.random.randn()))
            target_scores.append(score)
        
        training_data.append({
            'state_vector': state_vector,
            'mechanism_ids': mechanism_ids,
            'target_scores': target_scores
        })
    
    return training_data

if __name__ == "__main__":
    # Test the KeyLock encoder
    keylock_encoder = MechanismKeyLockEncoder()
    
    print("🔐 KeyLock Encoder Test")
    
    # Create sample state vector
    sample_state = np.random.randn(32)
    
    # Test mechanism compatibility
    test_mechanisms = ["抗焦虑", "改善腹泻", "抗抑郁"]
    compatibility = keylock_encoder.get_mechanism_compatibility(sample_state, test_mechanisms)
    
    print(f"\n状态向量与机制的兼容性:")
    for mechanism, score in compatibility.items():
        print(f"  {mechanism}: {score:.3f}")
    
    # Test best mechanism finding
    best_mechanisms = keylock_encoder.find_best_mechanisms(sample_state, top_k=3)
    print(f"\n最佳匹配机制:")
    for mechanism, score in best_mechanisms:
        print(f"  {mechanism}: {score:.3f}")
    
    # Test explanation
    explanation = keylock_encoder.get_keylock_explanation(sample_state, "抗焦虑")
    print(f"\n机制匹配解释:")
    for key, value in explanation.items():
        print(f"  {key}: {value}")
    
    # Test training with sample data
    print(f"\n🎯 训练KeyLock匹配网络...")
    training_data = create_sample_training_data(50)
    keylock_encoder.train_keylock_matching(training_data, epochs=20, lr=0.01) 