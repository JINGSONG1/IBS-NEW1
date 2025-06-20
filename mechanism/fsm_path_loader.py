"""
FSM Path Loader Module
Implements Drug → Mechanism → Symptom finite state machine paths
"""

import json
import networkx as nx
import numpy as np
from typing import Dict, List, Tuple, Optional, Set, Any, Union
from pathlib import Path

class FSMPathLoader:
    """
    Finite State Machine Path Loader for drug recommendation
    Manages the Drug → Mechanism → Symptom pathways
    """
    
    def __init__(self, mechanism_graph_path: Optional[str] = None):
        self.mechanism_graph_path = mechanism_graph_path or "config/mechanism_graph.json"
        self.fsm_graph = nx.DiGraph()
        self.drug_mechanisms = {}
        self.mechanism_symptoms = {}
        self.valid_paths = []
        self.state_transitions = {}
        
        self._load_mechanism_graph()
        self._build_fsm_graph()
        self._generate_valid_paths()
    
    def _load_mechanism_graph(self):
        """Load mechanism graph from JSON configuration"""
        try:
            with open(self.mechanism_graph_path, 'r', encoding='utf-8') as f:
                raw_data = json.load(f)
            
            # Parse the mechanism graph structure
            for drug, mechanisms in raw_data.items():
                self.drug_mechanisms[drug] = mechanisms
                
            # Define mechanism to symptom mappings (clinical knowledge base)
            self.mechanism_symptoms = {
                "抗焦虑": ["焦虑", "紧张", "心悸", "失眠"],
                "改善腹泻": ["腹泻", "大便次数增多", "大便不成形", "腹痛"],
                "抗抑郁": ["抑郁", "情绪低落", "兴趣缺乏", "疲劳"],
                "促胃肠动力": ["腹胀", "恶心", "食欲不振", "胃排空延迟"],
                "解痉": ["腹痛", "肠痉挛", "腹部不适"],
                "止泻": ["腹泻", "大便频繁", "水样便"],
                "调节肠道菌群": ["腹胀", "消化不良", "肠道不适"],
                "镇静": ["失眠", "烦躁", "紧张不安"],
                "抗胆碱": ["腹痛", "肠痉挛", "胃酸分泌过多"],
                "5-HT调节": ["情绪波动", "肠道敏感", "内脏过敏"]
            }
            
            print(f"✅ Loaded mechanism graph with {len(self.drug_mechanisms)} drugs")
            
        except FileNotFoundError:
            print(f"⚠️ Mechanism graph file not found: {self.mechanism_graph_path}")
            self._create_default_mechanism_graph()
    
    def _create_default_mechanism_graph(self):
        """Create default mechanism graph if file doesn't exist"""
        default_graph = {
            "帕罗西汀": ["抗焦虑", "改善腹泻", "抗抑郁"],
            "阿米替林": ["抗抑郁", "镇静", "抗胆碱"],
            "洛哌丁胺": ["止泻", "解痉"],
            "多潘立酮": ["促胃肠动力", "抗恶心"],
            "匹维溴铵": ["解痉", "抗胆碱"],
            "双歧杆菌": ["调节肠道菌群", "改善腹泻"],
            "氟哌噻吨美利曲辛": ["抗焦虑", "抗抑郁", "解痉"],
            "奥沙西泮": ["抗焦虑", "镇静"],
            "曲美布汀": ["促胃肠动力", "解痉", "5-HT调节"],
            "益生菌": ["调节肠道菌群", "改善消化"]
        }
        
        self.drug_mechanisms = default_graph
        
        # Save default graph
        Path(self.mechanism_graph_path).parent.mkdir(parents=True, exist_ok=True)
        with open(self.mechanism_graph_path, 'w', encoding='utf-8') as f:
            json.dump(default_graph, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Created default mechanism graph with {len(default_graph)} drugs")
    
    def _build_fsm_graph(self):
        """Build the FSM graph structure"""
        # Add nodes for each layer
        drugs = list(self.drug_mechanisms.keys())
        mechanisms = set()
        symptoms = set()
        
        for drug, drug_mechanisms in self.drug_mechanisms.items():
            mechanisms.update(drug_mechanisms)
            for mechanism in drug_mechanisms:
                if mechanism in self.mechanism_symptoms:
                    symptoms.update(self.mechanism_symptoms[mechanism])
        
        # Add nodes with attributes
        for drug in drugs:
            self.fsm_graph.add_node(drug, layer='drug', type='drug')
        
        for mechanism in mechanisms:
            self.fsm_graph.add_node(mechanism, layer='mechanism', type='mechanism')
        
        for symptom in symptoms:
            self.fsm_graph.add_node(symptom, layer='symptom', type='symptom')
        
        # Add edges: Drug → Mechanism
        for drug, drug_mechanisms in self.drug_mechanisms.items():
            for mechanism in drug_mechanisms:
                self.fsm_graph.add_edge(drug, mechanism, 
                                      edge_type='drug_to_mechanism',
                                      weight=1.0)
        
        # Add edges: Mechanism → Symptom
        for mechanism, mechanism_symptoms in self.mechanism_symptoms.items():
            for symptom in mechanism_symptoms:
                if mechanism in self.fsm_graph.nodes():
                    self.fsm_graph.add_edge(mechanism, symptom,
                                          edge_type='mechanism_to_symptom', 
                                          weight=1.0)
        
        print(f"✅ Built FSM graph: {len(drugs)} drugs, {len(mechanisms)} mechanisms, {len(symptoms)} symptoms")
    
    def _generate_valid_paths(self):
        """Generate all valid Drug → Mechanism → Symptom paths"""
        self.valid_paths = []
        
        for drug in self.drug_mechanisms.keys():
            for mechanism in self.drug_mechanisms[drug]:
                if mechanism in self.mechanism_symptoms:
                    for symptom in self.mechanism_symptoms[mechanism]:
                        path = [drug, mechanism, symptom]
                        self.valid_paths.append(path)
        
        print(f"✅ Generated {len(self.valid_paths)} valid FSM paths")
    
    def get_drug_paths(self, drug: str) -> List[List[str]]:
        """Get all valid paths for a specific drug"""
        return [path for path in self.valid_paths if path[0] == drug]
    
    def get_symptom_paths(self, symptom: str) -> List[List[str]]:
        """Get all paths that can treat a specific symptom"""
        return [path for path in self.valid_paths if path[2] == symptom]
    
    def get_mechanism_paths(self, mechanism: str) -> List[List[str]]:
        """Get all paths involving a specific mechanism"""
        return [path for path in self.valid_paths if path[1] == mechanism]
    
    def find_optimal_drug_for_symptoms(self, target_symptoms: List[str]) -> Dict[str, float]:
        """
        Find optimal drugs for treating given symptoms
        
        Args:
            target_symptoms: List of symptoms to treat
            
        Returns:
            drug_scores: Dictionary of drug names and their relevance scores
        """
        drug_scores = {}
        
        for symptom in target_symptoms:
            symptom_paths = self.get_symptom_paths(symptom)
            
            for path in symptom_paths:
                drug = path[0]
                if drug not in drug_scores:
                    drug_scores[drug] = 0
                drug_scores[drug] += 1.0 / len(target_symptoms)  # Normalized score
        
        # Sort by score
        return dict(sorted(drug_scores.items(), key=lambda x: x[1], reverse=True))
    
    def get_path_explanation(self, path: List[str]) -> Dict[str, Any]:
        """Get explanation for a specific path"""
        if len(path) != 3:
            return {"error": "Invalid path format"}
        
        drug, mechanism, symptom = path
        
        return {
            "drug": drug,
            "mechanism": mechanism, 
            "symptom": symptom,
            "explanation": f"{drug}通过{mechanism}机制来改善{symptom}症状",
            "path_type": "Drug → Mechanism → Symptom",
            "confidence": self._calculate_path_confidence(path)
        }
    
    def _calculate_path_confidence(self, path: List[str]) -> float:
        """Calculate confidence score for a path based on clinical evidence"""
        # Simple heuristic - in practice this would be based on clinical studies
        drug, mechanism, symptom = path
        
        # Base confidence
        confidence = 0.7
        
        # Adjust based on drug-mechanism strength
        if len(self.drug_mechanisms.get(drug, [])) <= 2:
            confidence += 0.1  # Specialized drugs get higher confidence
        
        # Adjust based on mechanism-symptom specificity
        if len(self.mechanism_symptoms.get(mechanism, [])) <= 3:
            confidence += 0.1  # Specific mechanisms get higher confidence
        
        return min(confidence, 1.0)
    
    def validate_path(self, path: List[str]) -> bool:
        """Validate if a path is feasible in the FSM"""
        if len(path) != 3:
            return False
        
        drug, mechanism, symptom = path
        
        # Check if drug can use this mechanism
        if mechanism not in self.drug_mechanisms.get(drug, []):
            return False
        
        # Check if mechanism can treat this symptom
        if symptom not in self.mechanism_symptoms.get(mechanism, []):
            return False
        
        return True
    
    def get_fsm_state_space(self) -> Dict[str, List[str]]:
        """Get the complete FSM state space"""
        return {
            "drugs": list(self.drug_mechanisms.keys()),
            "mechanisms": list(self.mechanism_symptoms.keys()),
            "symptoms": list(set(symptom for symptoms in self.mechanism_symptoms.values() 
                               for symptom in symptoms))
        }
    
    def export_graph_data(self) -> Dict:
        """Export graph data for visualization"""
        nodes = []
        edges = []
        
        # Export nodes
        for node, data in self.fsm_graph.nodes(data=True):
            nodes.append({
                "id": node,
                "label": node,
                "layer": data.get("layer", "unknown"),
                "type": data.get("type", "unknown")
            })
        
        # Export edges
        for source, target, data in self.fsm_graph.edges(data=True):
            edges.append({
                "source": source,
                "target": target,
                "type": data.get("edge_type", "unknown"),
                "weight": data.get("weight", 1.0)
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "paths": self.valid_paths,
            "stats": {
                "total_drugs": len([n for n, d in self.fsm_graph.nodes(data=True) if d.get("layer") == "drug"]),
                "total_mechanisms": len([n for n, d in self.fsm_graph.nodes(data=True) if d.get("layer") == "mechanism"]),
                "total_symptoms": len([n for n, d in self.fsm_graph.nodes(data=True) if d.get("layer") == "symptom"]),
                "total_paths": len(self.valid_paths)
            }
        }

if __name__ == "__main__":
    # Test the FSM path loader
    fsm_loader = FSMPathLoader()
    
    print("🧬 FSM Path Loader Test")
    
    # Test drug paths
    paroxetine_paths = fsm_loader.get_drug_paths("帕罗西汀")
    print(f"\n帕罗西汀的治疗路径 ({len(paroxetine_paths)} paths):")
    for path in paroxetine_paths:
        explanation = fsm_loader.get_path_explanation(path)
        print(f"  {' → '.join(path)} ({explanation['confidence']:.2f})")
    
    # Test symptom-based drug recommendation
    target_symptoms = ["焦虑", "腹泻"]
    drug_recommendations = fsm_loader.find_optimal_drug_for_symptoms(target_symptoms)
    print(f"\n针对症状 {target_symptoms} 的药物推荐:")
    for drug, score in drug_recommendations.items():
        print(f"  {drug}: {score:.2f}")
    
    # Export graph data
    graph_data = fsm_loader.export_graph_data()
    print(f"\n图谱统计: {graph_data['stats']}") 