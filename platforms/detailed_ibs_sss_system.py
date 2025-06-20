#!/usr/bin/env python3
"""
详细IBS-SSS评分系统
细化评分维度，提供基于症状模式的个性化药物推荐
"""

from typing import Dict, List, Tuple
import numpy as np

class DetailedIBSSSS:
    """详细IBS-SSS评分系统"""
    
    def __init__(self):
        self.load_detailed_scoring_system()
        self.init_symptom_patterns()
        self.load_personalized_recommendations()
    
    def load_detailed_scoring_system(self):
        """加载详细评分系统"""
        self.scoring_dimensions = {
            "abdominal_pain": {
                "name": "腹痛严重程度",
                "max_score": 100,
                "sub_items": {
                    "intensity": {
                        "name": "疼痛强度",
                        "scale": "0-10 VAS",
                        "weight": 0.4,
                        "questions": [
                            "过去10天内最严重的腹痛程度"
                        ]
                    },
                    "frequency": {
                        "name": "疼痛频率", 
                        "scale": "0-4",
                        "weight": 0.3,
                        "questions": [
                            "过去10天内腹痛天数"
                        ],
                        "scoring": {
                            0: "无腹痛",
                            1: "1-2天", 
                            2: "3-5天",
                            3: "6-8天",
                            4: "每天都有"
                        }
                    },
                    "duration_per_episode": {
                        "name": "单次疼痛持续时间",
                        "scale": "0-4",
                        "weight": 0.3,
                        "questions": [
                            "每次腹痛通常持续多长时间"
                        ],
                        "scoring": {
                            0: "无疼痛",
                            1: "<1小时",
                            2: "1-4小时", 
                            3: "4-12小时",
                            4: ">12小时"
                        }
                    }
                }
            },
            
            "bowel_habit_disturbance": {
                "name": "排便习惯紊乱",
                "max_score": 100,
                "sub_items": {
                    "frequency_change": {
                        "name": "排便频率改变",
                        "scale": "0-4",
                        "weight": 0.35,
                        "questions": [
                            "过去10天排便频率较正常时的改变"
                        ],
                        "scoring": {
                            0: "无改变",
                            1: "轻度改变（±1次/天）",
                            2: "中度改变（±2-3次/天）",
                            3: "重度改变（±4-5次/天）",
                            4: "极度改变（±6次以上/天）"
                        }
                    },
                    "consistency_change": {
                        "name": "大便性状改变",
                        "scale": "Bristol便型量表",
                        "weight": 0.35,
                        "questions": [
                            "过去10天大便性状较正常时的改变"
                        ],
                        "scoring": {
                            0: "正常（Bristol 3-4型）",
                            1: "轻度改变（Bristol 2或5型）",
                            2: "中度改变（主要为Bristol 1或6型）",
                            3: "重度改变（经常为Bristol 1或6-7型）",
                            4: "极度改变（几乎全为Bristol 1或7型）"
                        }
                    },
                    "urgency": {
                        "name": "排便急迫感",
                        "scale": "0-4",
                        "weight": 0.3,
                        "questions": [
                            "过去10天排便急迫感程度"
                        ],
                        "scoring": {
                            0: "无急迫感",
                            1: "轻度急迫，但可控制",
                            2: "中度急迫，偶尔难以控制",
                            3: "重度急迫，经常难以控制",
                            4: "极度急迫，几乎无法控制"
                        }
                    }
                }
            },
            
            "abdominal_distension": {
                "name": "腹胀",
                "max_score": 100,
                "sub_items": {
                    "bloating_severity": {
                        "name": "腹胀严重程度",
                        "scale": "0-4",
                        "weight": 0.4,
                        "questions": [
                            "过去10天腹胀最严重程度"
                        ],
                        "scoring": {
                            0: "无腹胀",
                            1: "轻度腹胀，不影响日常活动",
                            2: "中度腹胀，轻度影响日常活动",
                            3: "重度腹胀，明显影响日常活动",
                            4: "极度腹胀，严重影响日常活动"
                        }
                    },
                    "bloating_frequency": {
                        "name": "腹胀频率",
                        "scale": "0-4", 
                        "weight": 0.3,
                        "questions": [
                            "过去10天腹胀出现频率"
                        ],
                        "scoring": {
                            0: "从不",
                            1: "偶尔（<25%时间）",
                            2: "有时（25-50%时间）",
                            3: "经常（50-75%时间）",
                            4: "几乎总是（>75%时间）"
                        }
                    },
                    "visible_distension": {
                        "name": "腹部可见膨隆",
                        "scale": "0-4",
                        "weight": 0.3,
                        "questions": [
                            "腹胀时腹部外观改变程度"
                        ],
                        "scoring": {
                            0: "无可见改变",
                            1: "轻微膨隆",
                            2: "中度膨隆",
                            3: "明显膨隆",
                            4: "极度膨隆，需要放松衣物"
                        }
                    }
                }
            },
            
            "bowel_satisfaction": {
                "name": "排便满意度",
                "max_score": 100,
                "sub_items": {
                    "incomplete_evacuation": {
                        "name": "排便不尽感",
                        "scale": "0-4",
                        "weight": 0.4,
                        "questions": [
                            "过去10天排便不完全的感觉"
                        ],
                        "scoring": {
                            0: "总是感觉排空",
                            1: "通常感觉排空",
                            2: "有时感觉未排空",
                            3: "经常感觉未排空",
                            4: "几乎总是感觉未排空"
                        }
                    },
                    "straining": {
                        "name": "排便费力程度",
                        "scale": "0-4",
                        "weight": 0.3,
                        "questions": [
                            "过去10天排便时需要用力程度"
                        ],
                        "scoring": {
                            0: "从不费力",
                            1: "偶尔费力",
                            2: "有时费力",
                            3: "经常费力",
                            4: "总是费力"
                        }
                    },
                    "stool_passage_difficulty": {
                        "name": "排便困难度",
                        "scale": "0-4",
                        "weight": 0.3,
                        "questions": [
                            "过去10天排便困难程度"
                        ],
                        "scoring": {
                            0: "从不困难",
                            1: "偶尔困难",
                            2: "有时困难",
                            3: "经常困难",
                            4: "总是困难"
                        }
                    }
                }
            },
            
            "quality_of_life_impact": {
                "name": "生活质量影响",
                "max_score": 100,
                "sub_items": {
                    "daily_activity_interference": {
                        "name": "日常活动干扰",
                        "scale": "0-4",
                        "weight": 0.25,
                        "questions": [
                            "肠道症状对日常活动的影响程度"
                        ],
                        "scoring": {
                            0: "无影响",
                            1: "轻度影响",
                            2: "中度影响",
                            3: "重度影响",
                            4: "严重影响，无法进行日常活动"
                        }
                    },
                    "social_impact": {
                        "name": "社交影响",
                        "scale": "0-4",
                        "weight": 0.25,
                        "questions": [
                            "症状对社交活动的影响"
                        ],
                        "scoring": {
                            0: "无影响",
                            1: "轻度影响，偶尔避免社交",
                            2: "中度影响，经常担心症状",
                            3: "重度影响，避免多数社交活动",
                            4: "严重影响，几乎不参加社交活动"
                        }
                    },
                    "work_impact": {
                        "name": "工作影响",
                        "scale": "0-4",
                        "weight": 0.25,
                        "questions": [
                            "症状对工作或学习的影响"
                        ],
                        "scoring": {
                            0: "无影响",
                            1: "轻度影响，偶尔分心",
                            2: "中度影响，影响工作效率",
                            3: "重度影响，经常请假",
                            4: "严重影响，无法正常工作"
                        }
                    },
                    "psychological_impact": {
                        "name": "心理影响",
                        "scale": "0-4",
                        "weight": 0.25,
                        "questions": [
                            "症状对心理状态的影响"
                        ],
                        "scoring": {
                            0: "无心理影响",
                            1: "偶尔担心或焦虑",
                            2: "经常担心症状",
                            3: "严重焦虑或抑郁",
                            4: "极度心理困扰"
                        }
                    }
                }
            }
        }
    
    def init_symptom_patterns(self):
        """初始化症状模式分类"""
        self.symptom_patterns = {
            "pain_predominant": {
                "name": "疼痛为主型",
                "criteria": {
                    "abdominal_pain": ">70",
                    "bowel_habit_disturbance": "<60",
                    "abdominal_distension": "任意"
                },
                "characteristics": [
                    "腹痛是主要症状",
                    "排便后疼痛可能缓解",
                    "疼痛与排便相关性强"
                ],
                "prevalence": "25-30%"
            },
            
            "diarrhea_predominant": {
                "name": "腹泻为主型",
                "criteria": {
                    "bowel_habit_disturbance": ">70",
                    "bristol_score": ">5",
                    "urgency": ">2"
                },
                "characteristics": [
                    "大便次数增多",
                    "大便性状偏稀",
                    "排便急迫感明显"
                ],
                "prevalence": "30-35%"
            },
            
            "constipation_predominant": {
                "name": "便秘为主型",
                "criteria": {
                    "bowel_habit_disturbance": ">60",
                    "bristol_score": "<3",
                    "straining": ">2",
                    "incomplete_evacuation": ">2"
                },
                "characteristics": [
                    "排便次数减少",
                    "大便干硬",
                    "排便费力，不完全感"
                ],
                "prevalence": "20-25%"
            },
            
            "mixed_pattern": {
                "name": "混合型",
                "criteria": {
                    "alternating_symptoms": True,
                    "variable_bristol": "1-7型交替"
                },
                "characteristics": [
                    "便秘和腹泻交替",
                    "症状变化不规律",
                    "难以预测症状模式"
                ],
                "prevalence": "15-20%"
            },
            
            "bloating_predominant": {
                "name": "腹胀为主型",
                "criteria": {
                    "abdominal_distension": ">80",
                    "visible_distension": ">2"
                },
                "characteristics": [
                    "腹胀是主要困扰",
                    "腹部可见膨隆",
                    "饭后症状加重"
                ],
                "prevalence": "10-15%"
            }
        }
    
    def load_personalized_recommendations(self):
        """加载个性化推荐策略"""
        self.personalized_strategies = {
            "pain_predominant": {
                "first_line": [
                    {
                        "drug": "美贝维林",
                        "rationale": "直接针对平滑肌痉挛",
                        "dosage": "135mg tid",
                        "expected_improvement": "疼痛评分改善40-60%"
                    },
                    {
                        "drug": "匹维溴铵",
                        "rationale": "选择性钙通道阻滞，抗痉挛",
                        "dosage": "50mg tid",
                        "expected_improvement": "疼痛频率减少50%"
                    }
                ],
                "adjuvant": [
                    {
                        "therapy": "热敷",
                        "rationale": "局部热疗缓解肌肉紧张"
                    },
                    {
                        "therapy": "腹式呼吸",
                        "rationale": "减少腹肌紧张"
                    }
                ],
                "severe_cases": [
                    {
                        "drug": "阿米替林",
                        "rationale": "调节内脏痛觉敏感性",
                        "dosage": "10-25mg qn",
                        "monitoring": "心电图、体重"
                    }
                ]
            },
            
            "diarrhea_predominant": {
                "first_line": [
                    {
                        "drug": "洛哌丁胺",
                        "rationale": "直接减缓肠蠕动，减少水分分泌",
                        "dosage": "2mg bid-qid",
                        "expected_improvement": "大便次数减少60-70%"
                    }
                ],
                "second_line": [
                    {
                        "drug": "地芬诺酯",
                        "rationale": "阿片样作用，减慢肠蠕动",
                        "dosage": "5mg qid",
                        "monitoring": "便秘风险"
                    }
                ],
                "severe_refractory": [
                    {
                        "drug": "阿洛司琼",
                        "rationale": "5-HT3受体拮抗，适用于女性重度IBS-D",
                        "dosage": "0.5-1mg bid",
                        "restrictions": "限制性处方，需要签署知情同意"
                    }
                ],
                "supportive": [
                    {
                        "therapy": "益生菌",
                        "rationale": "调节肠道菌群",
                        "recommendation": "含双歧杆菌制剂"
                    }
                ]
            },
            
            "constipation_predominant": {
                "first_line": [
                    {
                        "drug": "聚乙二醇",
                        "rationale": "渗透性泻药，增加肠道水分",
                        "dosage": "10-20g qd",
                        "expected_improvement": "排便频率增加，硬度改善"
                    }
                ],
                "second_line": [
                    {
                        "drug": "乳果糖",
                        "rationale": "渗透性泻药，同时有益生元作用",
                        "dosage": "10-20ml bid",
                        "side_effects": "初期可能胀气"
                    }
                ],
                "severe_cases": [
                    {
                        "drug": "利那洛肽",
                        "rationale": "激活鸟苷酸环化酶C，促进分泌和蠕动",
                        "dosage": "290mcg qd",
                        "cost": "高价药物，需要评估获益"
                    }
                ],
                "lifestyle": [
                    {
                        "intervention": "高纤维饮食",
                        "target": "每日25-35g膳食纤维"
                    },
                    {
                        "intervention": "充足水分",
                        "target": "每日2-3L水分摄入"
                    }
                ]
            },
            
            "bloating_predominant": {
                "primary_approach": [
                    {
                        "strategy": "饮食调整",
                        "rationale": "减少产气食物",
                        "specifics": "低FODMAP饮食"
                    }
                ],
                "pharmacological": [
                    {
                        "drug": "西甲硅油",
                        "rationale": "减少气体表面张力",
                        "dosage": "40mg tid"
                    },
                    {
                        "drug": "益生菌",
                        "rationale": "改善肠道菌群平衡",
                        "recommendation": "含乳酸杆菌制剂"
                    }
                ],
                "severe_cases": [
                    {
                        "drug": "利福昔明",
                        "rationale": "局部抗生素，减少小肠细菌过度生长",
                        "dosage": "400mg tid × 14天",
                        "indication": "疑似SIBO"
                    }
                ]
            }
        }
    
    def calculate_detailed_score(self, responses: Dict) -> Dict:
        """计算详细IBS-SSS评分"""
        detailed_scores = {}
        total_score = 0
        
        for dimension, dimension_data in self.scoring_dimensions.items():
            dimension_score = 0
            sub_scores = {}
            
            for sub_item, sub_data in dimension_data["sub_items"].items():
                # 获取该子项的回答
                response_value = responses.get(sub_item, 0)
                
                # 计算子项得分
                if sub_item == "intensity":
                    # VAS 0-10 转换为 0-40
                    sub_score = response_value * 4
                else:
                    # 0-4 量表转换为对应分数
                    sub_score = response_value * 25
                
                # 应用权重
                weighted_score = sub_score * sub_data["weight"]
                sub_scores[sub_item] = {
                    "raw_score": sub_score,
                    "weighted_score": weighted_score,
                    "interpretation": self._interpret_sub_score(sub_item, response_value)
                }
                
                dimension_score += weighted_score
            
            detailed_scores[dimension] = {
                "total_score": dimension_score,
                "sub_scores": sub_scores,
                "severity": self._categorize_severity(dimension_score),
                "interpretation": self._interpret_dimension_score(dimension, dimension_score)
            }
            
            total_score += dimension_score
        
        # 识别症状模式
        symptom_pattern = self._identify_symptom_pattern(detailed_scores, responses)
        
        return {
            "total_score": total_score,
            "detailed_scores": detailed_scores,
            "symptom_pattern": symptom_pattern,
            "severity_classification": self._classify_overall_severity(total_score),
            "personalized_recommendations": self._generate_personalized_recommendations(
                symptom_pattern, detailed_scores, total_score
            )
        }
    
    def _interpret_sub_score(self, sub_item: str, raw_value: int) -> str:
        """解释子项得分"""
        interpretations = {
            "intensity": ["无痛", "轻微", "轻度", "中度", "中重度", "重度", "严重", "极重度", "难以忍受", "最严重", "无法描述"],
            "frequency": ["从不", "很少", "偶尔", "经常", "总是"],
            "bloating_severity": ["无腹胀", "轻度腹胀", "中度腹胀", "重度腹胀", "极度腹胀"]
        }
        
        if sub_item in interpretations:
            return interpretations[sub_item][min(raw_value, len(interpretations[sub_item])-1)]
        else:
            return f"评分: {raw_value}"
    
    def _categorize_severity(self, score: float) -> str:
        """分类严重程度"""
        if score < 25:
            return "轻微"
        elif score < 50:
            return "轻度"
        elif score < 75:
            return "中度"
        elif score < 90:
            return "重度"
        else:
            return "极重度"
    
    def _interpret_dimension_score(self, dimension: str, score: float) -> str:
        """解释维度得分"""
        interpretations = {
            "abdominal_pain": {
                "focus": "腹痛管理",
                "mild": "疼痛轻微，生活质量影响小",
                "moderate": "疼痛明显，需要药物干预",
                "severe": "疼痛严重，显著影响日常生活"
            },
            "bowel_habit_disturbance": {
                "focus": "排便习惯调节",
                "mild": "排便习惯轻度改变",
                "moderate": "排便习惯明显紊乱",
                "severe": "排便习惯严重紊乱，急需干预"
            }
        }
        
        if dimension in interpretations:
            if score < 50:
                return interpretations[dimension]["mild"]
            elif score < 75:
                return interpretations[dimension]["moderate"]
            else:
                return interpretations[dimension]["severe"]
        
        return f"得分 {score:.1f}"
    
    def _identify_symptom_pattern(self, detailed_scores: Dict, responses: Dict) -> str:
        """识别症状模式"""
        pain_score = detailed_scores["abdominal_pain"]["total_score"]
        bowel_score = detailed_scores["bowel_habit_disturbance"]["total_score"]
        bloating_score = detailed_scores["abdominal_distension"]["total_score"]
        
        # 检查Bristol便型评分（需要在responses中）
        bristol_score = responses.get("bristol_score", 4)
        urgency_score = responses.get("urgency", 0)
        
        if pain_score > 70 and bowel_score < 60:
            return "pain_predominant"
        elif bowel_score > 70 and bristol_score >= 5 and urgency_score > 2:
            return "diarrhea_predominant"
        elif bowel_score > 60 and bristol_score <= 3:
            return "constipation_predominant"
        elif bloating_score > 80:
            return "bloating_predominant"
        else:
            return "mixed_pattern"
    
    def _classify_overall_severity(self, total_score: float) -> str:
        """总体严重程度分类"""
        if total_score < 75:
            return "轻度"
        elif total_score < 175:
            return "轻中度"
        elif total_score < 300:
            return "中度"
        elif total_score < 400:
            return "中重度"
        else:
            return "重度"
    
    def _generate_personalized_recommendations(self, pattern: str, detailed_scores: Dict, total_score: float) -> Dict:
        """生成个性化推荐"""
        if pattern in self.personalized_strategies:
            base_recommendations = self.personalized_strategies[pattern].copy()
            
            # 根据总分调整推荐强度
            if total_score > 300:
                # 重度病例，考虑更积极的治疗
                if "severe_cases" in base_recommendations:
                    base_recommendations["recommended_tier"] = "severe_cases"
                else:
                    base_recommendations["recommended_tier"] = "second_line"
            elif total_score > 175:
                # 中度病例
                base_recommendations["recommended_tier"] = "first_line"
            else:
                # 轻度病例，优先非药物治疗
                base_recommendations["recommended_tier"] = "lifestyle"
            
            # 根据具体维度得分进行微调
            pain_severity = detailed_scores["abdominal_pain"]["severity"]
            if pain_severity in ["重度", "极重度"]:
                base_recommendations["pain_management_priority"] = "high"
            
            return base_recommendations
        
        return {"error": "未识别的症状模式"}
    
    def generate_monitoring_plan(self, pattern: str, total_score: float) -> Dict:
        """生成监测计划"""
        monitoring_plan = {
            "assessment_frequency": {},
            "key_parameters": [],
            "early_warning_signs": [],
            "adjustment_triggers": []
        }
        
        if total_score > 300:
            monitoring_plan["assessment_frequency"]["initial"] = "每周"
            monitoring_plan["assessment_frequency"]["stable"] = "每2周"
        else:
            monitoring_plan["assessment_frequency"]["initial"] = "每2周"
            monitoring_plan["assessment_frequency"]["stable"] = "每月"
        
        # 根据症状模式确定关键监测参数
        if pattern == "diarrhea_predominant":
            monitoring_plan["key_parameters"].extend([
                "每日排便次数和性状",
                "脱水征象",
                "电解质平衡"
            ])
        elif pattern == "constipation_predominant":
            monitoring_plan["key_parameters"].extend([
                "排便频率",
                "排便费力程度",
                "腹胀程度"
            ])
        
        return monitoring_plan

def main():
    """测试详细IBS-SSS系统"""
    ibs_system = DetailedIBSSSS()
    
    # 模拟患者回答
    responses = {
        "intensity": 7,  # VAS 0-10
        "frequency": 3,  # 6-8天有腹痛
        "duration_per_episode": 2,  # 1-4小时
        "frequency_change": 3,  # 重度频率改变
        "consistency_change": 3,  # 重度性状改变
        "urgency": 4,  # 极度急迫
        "bristol_score": 6,  # 糊状便
        "bloating_severity": 2,  # 中度腹胀
        "bloating_frequency": 2,  # 有时腹胀
        "incomplete_evacuation": 1,  # 偶尔不完全感
        "daily_activity_interference": 3  # 重度影响日常活动
    }
    
    # 计算详细评分
    result = ibs_system.calculate_detailed_score(responses)
    
    print("📊 详细IBS-SSS评分结果:")
    print(f"总分: {result['total_score']:.1f}")
    print(f"症状模式: {result['symptom_pattern']}")
    print(f"总体严重程度: {result['severity_classification']}")
    
    print(f"\n🎯 个性化推荐:")
    recommendations = result['personalized_recommendations']
    if 'first_line' in recommendations:
        print(f"一线推荐: {len(recommendations['first_line'])}种药物")
    
    # 生成监测计划
    monitoring = ibs_system.generate_monitoring_plan(
        result['symptom_pattern'], 
        result['total_score']
    )
    print(f"\n📅 监测计划:")
    print(f"初期随访: {monitoring['assessment_frequency']['initial']}")

if __name__ == "__main__":
    main() 