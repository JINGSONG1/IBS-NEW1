Reticulotype Toolkit — IBS Digital Twin Reinforcement Engine
（FSM‑driven, doctor‑in‑the‑loop recommendation system for Irritable Bowel Syndrome）
Project scope
1.Personalised therapy planner for IBS‑D/C/M based on questionnaire + wearable streams.

2.Finite‑state causal graph (FSM) guarantees mechanism‑consistent decisions.

3.PPO + Memory Replay + Auto‑Critic learns optimal multi‑step drug / lifestyle paths.

4.Doctor–AI co‑supervision (SIP) provides real‑time explanation & veto.

5.Edge‑CPU ≤0.5 s / patient → suitable for primary‑care deployment.

This repository reproduces all figures, tables and supplementary analyses in our Nature Medicine manuscript “Graph‑constrained reinforcement learning enables clinically‑explainable digital twins for IBS”.

🔧 Installation
# clone
$ git clone https://github.com/reticulotype/IBS-Twin.git && cd IBS-Twin
# build env (Python ≥3.9)
$ pip install -r requirements.txt
# optional: edge benchmark extras
$ pip install -r requirements-edge.txt

Quick‑start demo (5 min, CPU‑only)
# 1. download demo data (19×3‑week questionnaire)
$ bash scripts/get_demo_data.sh
# 2. train 1 k steps & log explanations
$ python core/ppo_train_main.py \
        --config configs/demo.yaml \
        --data  data/demo_questionnaire.csv
# 3. open explanation dashboard
$ streamlit run scripts/explanation_dashboard.py
Expected: output/ contains the trained model, mcp_log.csv, and <0.5 s per inference on an Intel i5‑8265U.

🗄️ Data preparation

Internal cohort (N = 19, 57 sequences)
Place de‑identified CSV into data/.

Ethics & compliance

IRB #CU‑GI‑2025‑041 approved by Columbia Univ. IRB.
All raw IDs hashed (SHA‑256) and dates shifted ± 3 days.
See docs/ethics_statement.md for GDPR & Chinese DSL assessment.

