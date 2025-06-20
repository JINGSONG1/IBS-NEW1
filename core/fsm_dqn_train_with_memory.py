"""
FSM-DQN Training Module with Memory Replay
Combines Finite State Machine path control with Deep Q-Network reinforcement learning
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
from collections import deque, namedtuple
import random
from typing import Dict, List, Tuple, Optional, Any
import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Experience tuple for memory replay
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])

class FSMDQNNetwork(nn.Module):
    """
    Deep Q-Network with FSM path awareness
    """
    
    def __init__(self, state_dim: int = 32, action_dim: int = 20, hidden_dim: int = 128):
        super(FSMDQNNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(hidden_dim, action_dim)
        )
        
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        return self.network(state)

class FSMReplayBuffer:
    """
    Experience replay buffer with FSM path awareness
    """
    
    def __init__(self, capacity: int = 10000):
        self.buffer = deque(maxlen=capacity)
        self.capacity = capacity
    
    def push(self, state: np.ndarray, action: int, reward: float, 
             next_state: np.ndarray, done: bool):
        """Add experience to buffer"""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """Sample batch of experiences"""
        return random.sample(self.buffer, batch_size)
    
    def __len__(self) -> int:
        return len(self.buffer)

class FSMDQNAgent:
    """
    FSM-aware DQN Agent for drug recommendation
    """
    
    def __init__(self, state_dim: int = 32, action_dim: int = 20, learning_rate: float = 0.001):
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.01
        
        # Networks
        self.q_network = FSMDQNNetwork(state_dim, action_dim)
        self.target_network = FSMDQNNetwork(state_dim, action_dim)
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=learning_rate)
        
        # Copy to target network
        self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Replay buffer
        self.replay_buffer = FSMReplayBuffer()
        
        # Drug path mappings
        self.action_to_path = self._create_action_mappings()
        
    def _create_action_mappings(self) -> Dict[int, List[str]]:
        """Create action to drug path mappings"""
        paths = [
            ["帕罗西汀", "抗焦虑", "焦虑"],
            ["帕罗西汀", "改善腹泻", "腹泻"],
            ["阿米替林", "抗抑郁", "抑郁"],
            ["洛哌丁胺", "止泻", "腹泻"],
            ["双歧杆菌", "调节肠道菌群", "腹胀"],
            ["奥沙西泮", "抗焦虑", "焦虑"],
            ["多潘立酮", "促胃肠动力", "腹胀"],
            ["匹维溴铵", "解痉", "腹痛"],
            ["曲美布汀", "促胃肠动力", "腹胀"],
            ["益生菌", "调节肠道菌群", "消化不良"]
        ]
        
        # Extend to action_dim
        action_mappings = {}
        for i in range(self.action_dim):
            action_mappings[i] = paths[i % len(paths)]
        
        return action_mappings
    
    def select_action(self, state: np.ndarray) -> int:
        """Select action using epsilon-greedy policy"""
        if random.random() < self.epsilon:
            return random.randint(0, self.action_dim - 1)
        
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            q_values = self.q_network(state_tensor)
            return q_values.argmax().item()
    
    def store_experience(self, state: np.ndarray, action: int, reward: float,
                        next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.replay_buffer.push(state, action, reward, next_state, done)
    
    def train_step(self, batch_size: int = 32):
        """Perform one training step"""
        if len(self.replay_buffer) < batch_size:
            return None
        
        # Sample batch
        experiences = self.replay_buffer.sample(batch_size)
        
        # Prepare tensors
        states = torch.FloatTensor([e.state for e in experiences])
        actions = torch.LongTensor([e.action for e in experiences])
        rewards = torch.FloatTensor([e.reward for e in experiences])
        next_states = torch.FloatTensor([e.next_state for e in experiences])
        dones = torch.BoolTensor([e.done for e in experiences])
        
        # Current Q values
        current_q_values = self.q_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)
        
        # Next Q values from target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1)[0]
            target_q_values = rewards + (0.99 * next_q_values * ~dones)
        
        # Compute loss
        loss = nn.MSELoss()(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        return loss.item()
    
    def update_target_network(self):
        """Update target network"""
        self.target_network.load_state_dict(self.q_network.state_dict())

class IBSEnvironment:
    """
    Simulated IBS treatment environment for training
    """
    
    def __init__(self):
        self.state_dim = 32
        self.current_state = None
        self.patient_profile = None
        
    def reset(self):
        """Reset environment with new patient"""
        self.patient_profile = self._generate_patient()
        self.current_state = self._profile_to_state(self.patient_profile)
        return self.current_state.copy()
    
    def _generate_patient(self):
        """Generate random patient profile"""
        return {
            'age': np.random.randint(18, 80),
            'anxiety': np.random.random(),
            'depression': np.random.random(),
            'diarrhea': np.random.random(),
            'pain': np.random.random(),
            'bloating': np.random.random()
        }
    
    def _profile_to_state(self, profile):
        """Convert profile to state vector"""
        state = np.zeros(self.state_dim)
        state[0] = profile['age'] / 80.0
        state[1] = profile['anxiety']
        state[2] = profile['depression']
        state[3] = profile['diarrhea']
        state[4] = profile['pain']
        state[5] = profile['bloating']
        state[6:] = np.random.randn(self.state_dim - 6) * 0.1
        return state
    
    def step(self, action: int, drug_path: List[str]):
        """Take action in environment"""
        reward = self._calculate_reward(drug_path)
        done = reward > 0.7 or np.random.random() < 0.1
        
        # Update state based on treatment
        if reward > 0.5:
            self.current_state[1:6] *= 0.9  # Improve symptoms
        
        return self.current_state.copy(), reward, done, {'drug_path': drug_path}
    
    def _calculate_reward(self, drug_path: List[str]) -> float:
        """Calculate reward for drug path"""
        if len(drug_path) != 3:
            return -1.0
        
        drug, mechanism, symptom = drug_path
        reward = 0.0
        
        # Match symptoms to patient profile
        if symptom == "焦虑" and self.patient_profile['anxiety'] > 0.6:
            reward += 0.4
        if symptom == "腹泻" and self.patient_profile['diarrhea'] > 0.6:
            reward += 0.4
        if symptom == "腹痛" and self.patient_profile['pain'] > 0.6:
            reward += 0.4
        if symptom == "腹胀" and self.patient_profile['bloating'] > 0.6:
            reward += 0.4
        
        # Add noise
        reward += np.random.normal(0, 0.1)
        return np.clip(reward, -1.0, 1.0)

def train_fsm_dqn_with_memory(episodes: int = 1000, batch_size: int = 32, 
                             learning_rate: float = 0.001, gamma: float = 0.99,
                             model_save_path: str = "model_fsm_dqn.pth"):
    """Train FSM-DQN agent with memory replay"""
    print("🚀 Starting FSM-DQN Training")
    
    env = IBSEnvironment()
    agent = FSMDQNAgent(learning_rate=learning_rate)
    
    episode_rewards = []
    
    for episode in range(episodes):
        state = env.reset()
        total_reward = 0
        
        for step in range(50):  # Max steps per episode
            action = agent.select_action(state)
            drug_path = agent.action_to_path[action]
            
            next_state, reward, done, info = env.step(action, drug_path)
            
            agent.store_experience(state, action, reward, next_state, done)
            
            if len(agent.replay_buffer) > batch_size:
                agent.train_step(batch_size)
            
            state = next_state
            total_reward += reward
            
            if done:
                break
        
        episode_rewards.append(total_reward)
        
        # Update target network periodically
        if episode % 100 == 0:
            agent.update_target_network()
            avg_reward = np.mean(episode_rewards[-100:])
            print(f"Episode {episode}: Avg Reward = {avg_reward:.3f}, Epsilon = {agent.epsilon:.3f}")
    
    # Save model
    torch.save({
        'q_network_state_dict': agent.q_network.state_dict(),
        'action_to_path': agent.action_to_path
    }, model_save_path)
    
    print(f"✅ Training completed! Model saved to {model_save_path}")
    return {'episode_rewards': episode_rewards, 'agent': agent}

if __name__ == "__main__":
    results = train_fsm_dqn_with_memory(episodes=500)
    print(f"Final average reward: {np.mean(results['episode_rewards'][-100:]):.3f}") 