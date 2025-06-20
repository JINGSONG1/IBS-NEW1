import json
from core.Reticulotype_Core import ReticulotypeCore

# 载入机制图谱和症状词表
with open("config/mechanism_graph.json", "r", encoding="utf-8") as f:
    mechanism_graph = json.load(f)
with open("config/symptom_vocab.json", "r", encoding="utf-8") as f:
    symptom_vocab = json.load(f)

# 初始化 Reticulotype 推荐核心系统
model = ReticulotypeCore(mechanism_graph, symptom_vocab)

# 真实状态输入示例（你可以替换为真实数据集循环调用）
patients = [
    {
        "id": "P001",
        "state_vector": [6, 5, 4, 2, 1],
        "target_symptoms": ["焦虑", "腹泻"]
    },
    {
        "id": "P002",
        "state_vector": [3, 2, 6, 5, 1],
        "target_symptoms": ["腹泻", "腹胀"]
    }
]

# 执行推荐并输出机制路径说明
for patient in patients:
    drug, decision, detail = model.recommend(
        patient["id"],
        patient["state_vector"],
        list(mechanism_graph.keys()),
        patient["target_symptoms"]
    )
    print("=" * 60)
    print(f"🧬 患者: {patient['id']}")
    print(f"📌 状态: {patient['state_vector']}")
    print(f"🎯 推荐药物: {drug}")
    print(f"✅ BuffGate 判定: {decision}")
    print(f"📊 机制解释细节: {detail}")
    print(f"📁 推荐路径图已保存为: fsm_path_{patient['id']}_{drug}.png")