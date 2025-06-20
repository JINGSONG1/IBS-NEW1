"""
PPO Training Main Script with Meta-Learning Support
支持 MAML/Reptile 元学习算法和 LOCO 交叉验证的 PPO 训练主程序
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import argparse
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
import logging
from dataclasses import dataclass
from collections import defaultdict

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class MetaLearningConfig:
    """元学习配置"""
    algorithm: str = "MAML"  # MAML, Reptile, 或 None
    inner_lr: float = 0.01
    outer_lr: float = 0.001
    inner_steps: int = 5
    meta_batch_size: int = 4
    adaptation_steps: int = 5
    first_order: bool = False  # MAML的一阶近似

@dataclass
class TrainingConfig:
    """训练配置"""
    num_epochs: int = 100
    batch_size: int = 32
    learning_rate: float = 3e-4
    gamma: float = 0.99
    gae_lambda: float = 0.95
    clip_epsilon: float = 0.2
    entropy_coef: float = 0.01
    value_loss_coef: float = 0.5
    max_grad_norm: float = 0.5
    
class PPONetwork(nn.Module):
    """PPO 策略和价值网络"""
    
    def __init__(self, state_dim: int = 48, action_dim: int = 20, hidden_dim: int = 128):
        super(PPONetwork, self).__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # 共享特征提取层
        self.feature_extractor = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # 策略头（Actor）
        self.policy_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, action_dim),
            nn.Softmax(dim=-1)
        )
        
        # 价值头（Critic）
        self.value_head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim // 2),
            nn.ReLU(),
            nn.Linear(hidden_dim // 2, 1)
        )
    
    def forward(self, state: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        前向传播
        
        Args:
            state: 状态张量 (batch_size, state_dim)
            
        Returns:
            policy: 动作概率分布 (batch_size, action_dim)
            value: 状态价值 (batch_size, 1)
        """
        features = self.feature_extractor(state)
        policy = self.policy_head(features)
        value = self.value_head(features)
        return policy, value
    
    def get_action(self, state: torch.Tensor, deterministic: bool = False) -> Tuple[torch.Tensor, torch.Tensor]:
        """
        获取动作
        
        Args:
            state: 状态张量
            deterministic: 是否确定性选择动作
            
        Returns:
            action: 选择的动作
            log_prob: 动作的对数概率
        """
        policy, value = self.forward(state)
        
        if deterministic:
            action = torch.argmax(policy, dim=-1)
            log_prob = torch.log(policy.gather(1, action.unsqueeze(-1)))
        else:
            dist = torch.distributions.Categorical(policy)
            action = dist.sample()
            log_prob = dist.log_prob(action)
        
        return action, log_prob

class MAMLTrainer:
    """MAML 元学习训练器"""
    
    def __init__(self, model: PPONetwork, config: MetaLearningConfig):
        self.model = model
        self.config = config
        self.meta_optimizer = optim.Adam(self.model.parameters(), lr=config.outer_lr)
    
    def adapt(self, support_data: List[Tuple], task_lr: float = None) -> PPONetwork:
        """
        在支持集上适应模型
        
        Args:
            support_data: 支持集数据
            task_lr: 任务特定学习率
            
        Returns:
            adapted_model: 适应后的模型
        """
        if task_lr is None:
            task_lr = self.config.inner_lr
        
        # 创建模型副本
        adapted_model = PPONetwork(self.model.state_dim, self.model.action_dim)
        adapted_model.load_state_dict(self.model.state_dict())
        
        # 内循环优化
        inner_optimizer = optim.SGD(adapted_model.parameters(), lr=task_lr)
        
        for _ in range(self.config.inner_steps):
            inner_optimizer.zero_grad()
            
            total_loss = 0
            for state, action, reward, next_state in support_data:
                policy, value = adapted_model(state)
                
                # 简化的策略损失
                action_prob = policy.gather(1, action.unsqueeze(-1))
                policy_loss = -torch.log(action_prob) * reward
                value_loss = nn.MSELoss()(value, reward.unsqueeze(-1))
                
                loss = policy_loss.mean() + 0.5 * value_loss
                total_loss += loss
            
            total_loss.backward()
            inner_optimizer.step()
        
        return adapted_model
    
    def meta_update(self, tasks: List[List[Tuple]]) -> float:
        """
        元更新
        
        Args:
            tasks: 任务列表，每个任务包含支持集和查询集
            
        Returns:
            meta_loss: 元损失
        """
        self.meta_optimizer.zero_grad()
        
        meta_loss = 0
        for task_data in tasks:
            # 分割支持集和查询集
            split_idx = len(task_data) // 2
            support_data = task_data[:split_idx]
            query_data = task_data[split_idx:]
            
            # 在支持集上适应
            adapted_model = self.adapt(support_data)
            
            # 在查询集上计算损失
            task_loss = 0
            for state, action, reward, next_state in query_data:
                policy, value = adapted_model(state)
                
                action_prob = policy.gather(1, action.unsqueeze(-1))
                policy_loss = -torch.log(action_prob) * reward
                value_loss = nn.MSELoss()(value, reward.unsqueeze(-1))
                
                loss = policy_loss.mean() + 0.5 * value_loss
                task_loss += loss
            
            meta_loss += task_loss / len(query_data)
        
        meta_loss = meta_loss / len(tasks)
        meta_loss.backward()
        self.meta_optimizer.step()
        
        return meta_loss.item()

class ReptileTrainer:
    """Reptile 元学习训练器"""
    
    def __init__(self, model: PPONetwork, config: MetaLearningConfig):
        self.model = model
        self.config = config
        self.meta_optimizer = optim.Adam(self.model.parameters(), lr=config.outer_lr)
    
    def train_on_task(self, task_data: List[Tuple]) -> Dict[str, torch.Tensor]:
        """
        在单个任务上训练
        
        Args:
            task_data: 任务数据
            
        Returns:
            task_weights: 任务训练后的权重
        """
        # 保存初始权重
        initial_weights = {name: param.clone() for name, param in self.model.named_parameters()}
        
        # 任务优化器
        task_optimizer = optim.SGD(self.model.parameters(), lr=self.config.inner_lr)
        
        # 在任务上训练
        for _ in range(self.config.inner_steps):
            task_optimizer.zero_grad()
            
            total_loss = 0
            for state, action, reward, next_state in task_data:
                policy, value = self.model(state)
                
                action_prob = policy.gather(1, action.unsqueeze(-1))
                policy_loss = -torch.log(action_prob) * reward
                value_loss = nn.MSELoss()(value, reward.unsqueeze(-1))
                
                loss = policy_loss.mean() + 0.5 * value_loss
                total_loss += loss
            
            total_loss.backward()
            task_optimizer.step()
        
        # 返回更新后的权重
        updated_weights = {name: param.clone() for name, param in self.model.named_parameters()}
        
        # 恢复初始权重
        for name, param in self.model.named_parameters():
            param.data = initial_weights[name]
        
        return updated_weights
    
    def meta_update(self, tasks: List[List[Tuple]]) -> float:
        """Reptile 元更新"""
        initial_weights = {name: param.clone() for name, param in self.model.named_parameters()}
        
        # 收集所有任务的权重更新
        all_weight_updates = defaultdict(list)
        
        for task_data in tasks:
            task_weights = self.train_on_task(task_data)
            
            for name, updated_param in task_weights.items():
                weight_update = updated_param - initial_weights[name]
                all_weight_updates[name].append(weight_update)
        
        # 计算平均权重更新
        self.meta_optimizer.zero_grad()
        
        for name, param in self.model.named_parameters():
            if name in all_weight_updates:
                avg_update = torch.stack(all_weight_updates[name]).mean(dim=0)
                param.grad = -avg_update  # 负号因为我们想要朝着更新方向移动
        
        self.meta_optimizer.step()
        
        # 计算平均损失（用于监控）
        total_loss = 0
        for task_data in tasks:
            for state, action, reward, next_state in task_data:
                policy, value = self.model(state)
                action_prob = policy.gather(1, action.unsqueeze(-1))
                policy_loss = -torch.log(action_prob) * reward
                value_loss = nn.MSELoss()(value, reward.unsqueeze(-1))
                loss = policy_loss.mean() + 0.5 * value_loss
                total_loss += loss.item()
        
        return total_loss / (len(tasks) * len(tasks[0]))

class LOCOValidator:
    """Leave-One-Center-Out (LOCO) 交叉验证器"""
    
    def __init__(self, centers: List[str]):
        self.centers = centers
        self.validation_results = {}
    
    def split_data_by_center(self, data: List[Tuple], center_labels: List[str]) -> Dict[str, List[Tuple]]:
        """按中心分割数据"""
        center_data = defaultdict(list)
        
        for sample, center in zip(data, center_labels):
            center_data[center].append(sample)
        
        return dict(center_data)
    
    def loco_validate(self, 
                     model_class: type, 
                     data: List[Tuple], 
                     center_labels: List[str],
                     config: TrainingConfig) -> Dict[str, Any]:
        """
        执行 LOCO 交叉验证
        
        Args:
            model_class: 模型类
            data: 训练数据
            center_labels: 中心标签
            config: 训练配置
            
        Returns:
            validation_results: 验证结果
        """
        center_data = self.split_data_by_center(data, center_labels)
        results = {}
        
        for held_out_center in self.centers:
            logger.info(f"LOCO validation: holding out center {held_out_center}")
            
            # 分割训练和测试数据
            train_data = []
            test_data = center_data.get(held_out_center, [])
            
            for center, center_samples in center_data.items():
                if center != held_out_center:
                    train_data.extend(center_samples)
            
            # 训练模型
            model = model_class()
            # 这里应该实现具体的训练逻辑
            # train_model(model, train_data, config)
            
            # 评估模型
            # test_score = evaluate_model(model, test_data)
            test_score = np.random.random()  # 模拟评估分数
            
            results[held_out_center] = {
                'test_score': test_score,
                'train_size': len(train_data),
                'test_size': len(test_data)
            }
        
        # 计算总体统计
        all_scores = [r['test_score'] for r in results.values()]
        results['overall'] = {
            'mean_score': np.mean(all_scores),
            'std_score': np.std(all_scores),
            'min_score': np.min(all_scores),
            'max_score': np.max(all_scores)
        }
        
        return results

def create_mock_data(num_samples: int = 1000, num_centers: int = 5) -> Tuple[List[Tuple], List[str]]:
    """创建模拟数据"""
    data = []
    center_labels = []
    
    centers = [f"Center_{i+1}" for i in range(num_centers)]
    
    for i in range(num_samples):
        state = torch.randn(48)
        action = torch.randint(0, 20, (1,))
        reward = torch.randn(1)
        next_state = torch.randn(48)
        
        data.append((state, action, reward, next_state))
        center_labels.append(centers[i % num_centers])
    
    return data, center_labels

def main():
    """主训练函数"""
    parser = argparse.ArgumentParser(description='PPO Training with Meta-Learning')
    parser.add_argument('--meta', choices=['MAML', 'Reptile', 'None'], default='None',
                       help='Meta-learning algorithm to use')
    parser.add_argument('--loco', action='store_true', help='Use LOCO cross-validation')
    parser.add_argument('--epochs', type=int, default=100, help='Number of training epochs')
    parser.add_argument('--output_dir', type=str, default='training_results', 
                       help='Output directory for results')
    
    args = parser.parse_args()
    
    # 创建输出目录
    os.makedirs(args.output_dir, exist_ok=True)
    
    # 配置
    meta_config = MetaLearningConfig(algorithm=args.meta)
    train_config = TrainingConfig(num_epochs=args.epochs)
    
    # 创建模型
    model = PPONetwork()
    
    # 创建模拟数据
    data, center_labels = create_mock_data()
    
    logger.info(f"开始训练 - 元学习算法: {args.meta}, LOCO验证: {args.loco}")
    
    if args.loco:
        # LOCO 交叉验证
        centers = list(set(center_labels))
        loco_validator = LOCOValidator(centers)
        
        loco_results = loco_validator.loco_validate(
            PPONetwork, data, center_labels, train_config
        )
        
        logger.info(f"LOCO验证结果: {loco_results['overall']}")
        
        # 保存 LOCO 结果
        with open(os.path.join(args.output_dir, 'loco_results.json'), 'w') as f:
            json.dump(loco_results, f, indent=2, default=str)
    
    if args.meta != 'None':
        # 元学习训练
        if args.meta == 'MAML':
            trainer = MAMLTrainer(model, meta_config)
        elif args.meta == 'Reptile':
            trainer = ReptileTrainer(model, meta_config)
        
        # 将数据分组为任务
        task_size = 50
        tasks = []
        for i in range(0, len(data), task_size):
            task_data = data[i:i+task_size]
            if len(task_data) >= task_size:
                tasks.append(task_data)
        
        # 元训练循环
        for epoch in range(train_config.num_epochs):
            # 随机选择任务批次
            batch_tasks = np.random.choice(tasks, meta_config.meta_batch_size, replace=False).tolist()
            
            # 元更新
            meta_loss = trainer.meta_update(batch_tasks)
            
            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}, Meta Loss: {meta_loss:.4f}")
        
        # 保存训练好的模型
        model_path = os.path.join(args.output_dir, f'ppo_model_{args.meta}.pth')
        torch.save(model.state_dict(), model_path)
        logger.info(f"模型已保存: {model_path}")
    
    # 保存训练配置
    config_dict = {
        'meta_learning': meta_config.__dict__,
        'training': train_config.__dict__,
        'args': vars(args),
        'timestamp': datetime.now().isoformat()
    }
    
    with open(os.path.join(args.output_dir, 'training_config.json'), 'w') as f:
        json.dump(config_dict, f, indent=2)
    
    logger.info("训练完成!")

if __name__ == "__main__":
    main() 