import argparse
from core.fsm_dqn_train_with_memory import train_fsm_dqn_with_memory

def main():
    parser = argparse.ArgumentParser(description="Train FSM-Gated DQN model")
    parser.add_argument("--episodes", type=int, default=1000, help="Number of training episodes")
    parser.add_argument("--batch_size", type=int, default=32, help="Batch size")
    parser.add_argument("--lr", type=float, default=0.001, help="Learning rate")
    parser.add_argument("--gamma", type=float, default=0.99, help="Discount factor")
    parser.add_argument("--save_path", type=str, default="model_fsm_dqn.pth", help="Model save path")

    args = parser.parse_args()

    print("📦 Training FSM-DQN with memory replay and BuffGate")
    train_fsm_dqn_with_memory(
        episodes=args.episodes,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        gamma=args.gamma,
        model_save_path=args.save_path
    )

if __name__ == "__main__":
    main()