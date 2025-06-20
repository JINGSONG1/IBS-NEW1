#!/usr/bin/env python3
"""
增强合并疾病系统
包含完整的IBS相关合并疾病谱系和评估工具
"""

from typing import Dict, List, Tuple
import json

class EnhancedComorbiditySystem:
    """增强合并疾病评估系统"""
    
    def __init__(self):
        self.load_comorbidity_database()
        self.init_screening_tools()
        self.load_drug_considerations()
    
    def load_comorbidity_database(self):
        """加载完整的合并疾病数据库"""
        self.comorbidities = {
            # 精神心理疾病
            "psychiatric_disorders": {
                "焦虑症": {
                    "prevalence_in_ibs": "50-90%",
                    "screening_tool": "GAD-7",
                    "threshold": 7,
                    "impact_on_ibs": "加重症状，降低生活质量",
                    "treatment_considerations": [
                        "SSRI类药物可能加重IBS-D",
                        "三环类药物可能改善IBS-D",
                        "认知行为疗法有效"
                    ],
                    "drug_interactions": {
                        "beneficial": ["阿米替林", "度洛西汀"],
                        "caution": ["帕罗西汀", "氟西汀"],
                        "avoid": []
                    }
                },
                
                "抑郁症": {
                    "prevalence_in_ibs": "20-50%",
                    "screening_tool": "PHQ-9",
                    "threshold": 9,
                    "impact_on_ibs": "显著加重症状，影响治疗依从性",
                    "treatment_considerations": [
                        "肠-脑轴密切相关",
                        "抗抑郁药物可能改善IBS症状",
                        "需要多学科协作治疗"
                    ],
                    "drug_interactions": {
                        "beneficial": ["阿米替林", "文拉法辛", "度洛西汀"],
                        "caution": ["SSRI类药物"],
                        "avoid": []
                    }
                },
                
                "双相情感障碍": {
                    "prevalence_in_ibs": "5-15%",
                    "screening_tool": "MDQ",
                    "threshold": 7,
                    "impact_on_ibs": "症状波动与情绪周期相关",
                    "treatment_considerations": [
                        "避免单独使用抗抑郁药",
                        "锂盐可能影响肠道功能",
                        "情绪稳定剂为首选",
                        "需要精神科会诊"
                    ],
                    "drug_interactions": {
                        "beneficial": ["加巴喷丁（辅助）"],
                        "caution": ["锂盐（腹泻风险）", "丙戊酸（胃肠反应）"],
                        "avoid": ["单独使用SSRI（躁狂风险）"]
                    }
                },
                
                "惊恐障碍": {
                    "prevalence_in_ibs": "15-30%",
                    "screening_tool": "PDSS",
                    "threshold": 8,
                    "impact_on_ibs": "惊恐发作可诱发IBS症状",
                    "treatment_considerations": [
                        "β受体阻滞剂可能有效",
                        "苯二氮䓬类短期使用",
                        "暴露治疗重要"
                    ],
                    "drug_interactions": {
                        "beneficial": ["普萘洛尔", "阿普唑仑（短期）"],
                        "caution": ["长期苯二氮䓬类"],
                        "avoid": []
                    }
                },
                
                "创伤后应激障碍": {
                    "prevalence_in_ibs": "10-25%",
                    "screening_tool": "PCL-5",
                    "threshold": 33,
                    "impact_on_ibs": "创伤经历与肠道症状密切相关",
                    "treatment_considerations": [
                        "EMDR治疗可能有效",
                        "α1受体阻滞剂可考虑",
                        "避免成瘾性药物"
                    ],
                    "drug_interactions": {
                        "beneficial": ["哌唑嗪", "文拉法辛"],
                        "caution": ["苯二氮䓬类"],
                        "avoid": ["酒精类药物"]
                    }
                }
            },
            
            # 妇科疾病
            "gynecological_disorders": {
                "子宫内膜异位症": {
                    "prevalence_in_ibs": "女性IBS患者中15-25%",
                    "screening_tool": "临床症状+超声",
                    "threshold": "痛经VAS≥7",
                    "impact_on_ibs": "月经期症状加重，激素影响肠道",
                    "treatment_considerations": [
                        "激素治疗可能影响IBS",
                        "NSAIDs可能加重肠道症状",
                        "手术治疗需要考虑肠道并发症"
                    ],
                    "drug_interactions": {
                        "beneficial": ["GnRH激动剂（短期）"],
                        "caution": ["雌激素制剂", "NSAIDs"],
                        "avoid": ["长期激素抑制"]
                    }
                },
                
                "多囊卵巢综合征": {
                    "prevalence_in_ibs": "20-35%",
                    "screening_tool": "Rotterdam标准",
                    "threshold": "2/3项阳性",
                    "impact_on_ibs": "胰岛素抵抗、激素紊乱影响肠道",
                    "treatment_considerations": [
                        "二甲双胍可能改善症状",
                        "生活方式干预重要",
                        "体重管理必要"
                    ],
                    "drug_interactions": {
                        "beneficial": ["二甲双胍", "肌醇"],
                        "caution": ["避孕药"],
                        "avoid": []
                    }
                },
                
                "功能性痛经": {
                    "prevalence_in_ibs": "60-80%",
                    "screening_tool": "痛经VAS评分",
                    "threshold": 5,
                    "impact_on_ibs": "前列腺素影响肠道蠕动",
                    "treatment_considerations": [
                        "NSAIDs需要谨慎使用",
                        "热敷、针灸可能有效",
                        "口服避孕药可考虑"
                    ],
                    "drug_interactions": {
                        "beneficial": ["布洛芬（短期）", "对乙酰氨基酚"],
                        "caution": ["长期NSAIDs"],
                        "avoid": []
                    }
                }
            },
            
            # 消化系统疾病
            "gastrointestinal_disorders": {
                "胃食管反流病": {
                    "prevalence_in_ibs": "30-60%",
                    "screening_tool": "GERD-Q",
                    "threshold": 8,
                    "impact_on_ibs": "上下消化道症状相互影响",
                    "treatment_considerations": [
                        "PPI类药物长期使用需要监测",
                        "H2受体阻滞剂可能更合适",
                        "生活方式调整重要"
                    ],
                    "drug_interactions": {
                        "beneficial": ["雷贝拉唑", "法莫替丁"],
                        "caution": ["长期PPI（肠道菌群）"],
                        "avoid": []
                    }
                },
                
                "功能性消化不良": {
                    "prevalence_in_ibs": "50-70%",
                    "screening_tool": "Rome IV标准",
                    "threshold": "符合诊断标准",
                    "impact_on_ibs": "胃肠道功能障碍重叠",
                    "treatment_considerations": [
                        "促胃动力药物可能有效",
                        "抗酸药物根据症状使用",
                        "饮食调整至关重要"
                    ],
                    "drug_interactions": {
                        "beneficial": ["多潘立酮", "莫沙必利"],
                        "caution": ["西沙必利（已撤市）"],
                        "avoid": []
                    }
                },
                
                "幽门螺杆菌感染": {
                    "prevalence_in_ibs": "30-50%",
                    "screening_tool": "C13呼气试验",
                    "threshold": "阳性",
                    "impact_on_ibs": "可能加重症状，根除治疗后症状改善",
                    "treatment_considerations": [
                        "四联根除治疗",
                        "根除后症状可能暂时加重",
                        "益生菌辅助治疗"
                    ],
                    "drug_interactions": {
                        "beneficial": ["标准四联方案"],
                        "caution": ["抗生素相关腹泻"],
                        "avoid": []
                    }
                }
            },
            
            # 代谢内分泌疾病
            "metabolic_endocrine_disorders": {
                "糖尿病": {
                    "prevalence_in_ibs": "15-25%",
                    "screening_tool": "糖化血红蛋白",
                    "threshold": 6.5,
                    "impact_on_ibs": "糖尿病胃轻瘫、肠病变",
                    "treatment_considerations": [
                        "血糖控制是基础",
                        "GLP-1激动剂可能有双重获益",
                        "二甲双胍可能加重腹泻"
                    ],
                    "drug_interactions": {
                        "beneficial": ["利拉鲁肽", "度拉糖肽"],
                        "caution": ["二甲双胍（腹泻）", "阿卡波糖（胀气）"],
                        "avoid": []
                    }
                },
                
                "甲状腺功能异常": {
                    "prevalence_in_ibs": "10-20%",
                    "screening_tool": "TSH, FT3, FT4",
                    "threshold": "异常范围",
                    "impact_on_ibs": "甲亢加重腹泻，甲减加重便秘",
                    "treatment_considerations": [
                        "甲状腺功能正常化是前提",
                        "甲状腺药物剂量调整期症状可能波动",
                        "定期监测甲状腺功能"
                    ],
                    "drug_interactions": {
                        "beneficial": ["左甲状腺素（甲减）", "甲巯咪唑（甲亢）"],
                        "caution": ["药物吸收相互影响"],
                        "avoid": []
                    }
                }
            },
            
            # 免疫系统疾病
            "immune_disorders": {
                "系统性红斑狼疮": {
                    "prevalence_in_ibs": "5-10%",
                    "screening_tool": "ANA, Anti-dsDNA",
                    "threshold": "阳性+临床表现",
                    "impact_on_ibs": "免疫抑制剂、激素影响肠道",
                    "treatment_considerations": [
                        "激素使用需要胃保护",
                        "免疫抑制剂监测感染",
                        "生物制剂可能影响肠道菌群"
                    ],
                    "drug_interactions": {
                        "beneficial": ["美沙拉嗪（肠道抗炎）"],
                        "caution": ["激素", "免疫抑制剂"],
                        "avoid": ["活疫苗"]
                    }
                },
                
                "类风湿关节炎": {
                    "prevalence_in_ibs": "8-15%",
                    "screening_tool": "RF, CCP",
                    "threshold": "阳性+关节症状",
                    "impact_on_ibs": "NSAIDs长期使用损伤肠道",
                    "treatment_considerations": [
                        "避免长期大剂量NSAIDs",
                        "生物制剂可能改善肠道炎症",
                        "定期胃肠道检查"
                    ],
                    "drug_interactions": {
                        "beneficial": ["生物制剂", "小剂量激素"],
                        "caution": ["NSAIDs", "甲氨蝶呤"],
                        "avoid": ["大剂量长期NSAIDs"]
                    }
                }
            }
        }
    
    def init_screening_tools(self):
        """初始化筛查工具"""
        self.screening_tools = {
            "GAD-7": {
                "questions": [
                    "感到紧张、焦虑或急切",
                    "无法停止或控制担忧",
                    "对各种各样的事情担忧过多",
                    "很难放松下来",
                    "坐立不安，难以静坐",
                    "变得容易烦恼或急躁",
                    "感到好像有什么可怕的事情会发生"
                ],
                "scoring": "0-3分每题，总分0-21分",
                "interpretation": {
                    "0-4": "最小焦虑",
                    "5-9": "轻度焦虑", 
                    "10-14": "中度焦虑",
                    "15-21": "重度焦虑"
                }
            },
            
            "PHQ-9": {
                "questions": [
                    "做事时提不起劲或没有兴趣",
                    "感到心情低落、沮丧或绝望",
                    "入睡困难、睡不安稳或睡眠过多",
                    "感觉疲倦或没有活力",
                    "食欲不振或吃太多",
                    "觉得自己很糟或是个失败者",
                    "对事物专注有困难",
                    "动作或说话速度缓慢或相反",
                    "有不如死掉或伤害自己的念头"
                ],
                "scoring": "0-3分每题，总分0-27分",
                "interpretation": {
                    "0-4": "无抑郁症状",
                    "5-9": "轻度抑郁",
                    "10-14": "中度抑郁", 
                    "15-19": "中重度抑郁",
                    "20-27": "重度抑郁"
                }
            },
            
            "MDQ": {
                "questions": [
                    "您是否曾经有一段时间感到非常高兴或兴奋",
                    "您是否变得比平时更加自信",
                    "您是否睡眠需求减少",
                    "您是否比平时更加健谈",
                    "您的思维是否比平时更加迅速",
                    "您是否更容易分心",
                    "您的精力或活动是否增加",
                    "您是否变得更加外向或社交",
                    "您是否更加性兴奋",
                    "您的行为是否让别人担心",
                    "您是否在金钱上更加不计后果",
                    "您的判断力是否受到影响",
                    "您的行为是否给您造成了麻烦"
                ],
                "scoring": "是/否，7个或以上为阳性",
                "interpretation": {
                    "0-6": "双相障碍可能性低",
                    "7-13": "提示双相障碍，需要进一步评估"
                }
            }
        }
    
    def load_drug_considerations(self):
        """加载药物使用注意事项"""
        self.drug_considerations = {
            "psychiatric_drugs": {
                "SSRI类": {
                    "ibs_effects": {
                        "IBS-D": "可能加重腹泻（5-HT刺激）",
                        "IBS-C": "可能改善便秘", 
                        "IBS-M": "效果不确定"
                    },
                    "monitoring": ["胃肠道症状变化", "自杀风险", "性功能"],
                    "adjustment": "从小剂量开始，缓慢增量"
                },
                
                "三环类": {
                    "ibs_effects": {
                        "IBS-D": "可能改善腹泻（抗胆碱作用）",
                        "IBS-C": "可能加重便秘",
                        "疼痛": "可能改善内脏疼痛"
                    },
                    "monitoring": ["心电图", "便秘", "体重变化"],
                    "adjustment": "睡前给药，从10mg开始"
                },
                
                "情绪稳定剂": {
                    "ibs_effects": {
                        "锂盐": "可能引起腹泻、恶心",
                        "丙戊酸": "可能引起胃肠道反应",
                        "拉莫三嗪": "胃肠道反应较少"
                    },
                    "monitoring": ["血药浓度", "肝肾功能", "血常规"],
                    "adjustment": "需要精神科医生指导"
                }
            },
            
            "hormone_drugs": {
                "雌激素": {
                    "ibs_effects": "可能影响肠道蠕动，症状周期性变化",
                    "monitoring": ["月经周期症状记录", "血栓风险"],
                    "adjustment": "考虑使用最低有效剂量"
                },
                
                "孕激素": {
                    "ibs_effects": "可能减慢肠道蠕动，加重便秘",
                    "monitoring": ["便秘症状", "情绪变化"],
                    "adjustment": "可能需要增加泻药"
                }
            }
        }
    
    def comprehensive_screening(self, patient_data: Dict) -> Dict:
        """综合疾病筛查"""
        screening_results = {
            "high_risk_comorbidities": [],
            "moderate_risk_comorbidities": [],
            "low_risk_comorbidities": [],
            "recommended_tests": [],
            "immediate_referrals": []
        }
        
        # 基于症状和问卷评估
        if patient_data.get("anxiety_score", 0) >= 10:
            screening_results["high_risk_comorbidities"].append({
                "condition": "焦虑症",
                "score": patient_data["anxiety_score"],
                "severity": "中重度",
                "impact_on_ibs": "显著加重症状"
            })
        
        if patient_data.get("depression_score", 0) >= 15:
            screening_results["high_risk_comorbidities"].append({
                "condition": "抑郁症", 
                "score": patient_data["depression_score"],
                "severity": "中重度",
                "impact_on_ibs": "显著影响治疗效果"
            })
        
        # 基于性别和年龄的筛查
        if patient_data.get("gender") == "女" and patient_data.get("age", 0) >= 18:
            if patient_data.get("menstrual_pain", 0) >= 7:
                screening_results["moderate_risk_comorbidities"].append({
                    "condition": "子宫内膜异位症",
                    "risk_factors": ["严重痛经", "IBS症状"],
                    "recommended_tests": ["盆腔超声", "妇科检查"]
                })
        
        # 其他筛查建议
        if patient_data.get("family_history_diabetes"):
            screening_results["recommended_tests"].append("糖化血红蛋白")
        
        if patient_data.get("thyroid_symptoms"):
            screening_results["recommended_tests"].append("甲状腺功能")
        
        return screening_results
    
    def get_treatment_modifications(self, comorbidities: List[str], 
                                  current_ibs_treatment: List[str]) -> Dict:
        """根据合并症调整治疗方案"""
        modifications = {
            "drug_adjustments": [],
            "contraindications": [],
            "additional_treatments": [],
            "monitoring_requirements": []
        }
        
        for comorbidity in comorbidities:
            # 查找合并症对应的治疗考虑
            for category in self.comorbidities.values():
                if comorbidity in category:
                    condition_data = category[comorbidity]
                    
                    # 药物相互作用检查
                    for drug in current_ibs_treatment:
                        if drug in condition_data["drug_interactions"]["avoid"]:
                            modifications["contraindications"].append({
                                "drug": drug,
                                "reason": f"{comorbidity}患者禁用",
                                "alternative": "需要选择替代药物"
                            })
                        elif drug in condition_data["drug_interactions"]["caution"]:
                            modifications["monitoring_requirements"].append({
                                "drug": drug,
                                "condition": comorbidity,
                                "monitoring": "需要密切监测不良反应"
                            })
                    
                    # 有益药物推荐
                    for beneficial_drug in condition_data["drug_interactions"]["beneficial"]:
                        if beneficial_drug not in current_ibs_treatment:
                            modifications["additional_treatments"].append({
                                "drug": beneficial_drug,
                                "indication": f"同时治疗{comorbidity}和IBS",
                                "priority": "推荐"
                            })
        
        return modifications
    
    def generate_followup_plan(self, comorbidities: List[str]) -> Dict:
        """生成随访计划"""
        followup_plan = {
            "short_term": [],  # 2-4周
            "medium_term": [],  # 3个月
            "long_term": []  # 6-12个月
        }
        
        for comorbidity in comorbidities:
            if comorbidity == "双相情感障碍":
                followup_plan["short_term"].append({
                    "assessment": "情绪稳定性评估",
                    "frequency": "每2周",
                    "duration": "前3个月"
                })
                followup_plan["medium_term"].append({
                    "assessment": "药物血药浓度",
                    "frequency": "每3个月",
                    "specialist": "精神科医生"
                })
            
            elif comorbidity == "子宫内膜异位症":
                followup_plan["short_term"].append({
                    "assessment": "疼痛评估",
                    "frequency": "月经周期记录",
                    "tool": "疼痛日记"
                })
                followup_plan["medium_term"].append({
                    "assessment": "盆腔检查",
                    "frequency": "每6个月",
                    "specialist": "妇科医生"
                })
        
        return followup_plan

def main():
    """测试增强合并疾病系统"""
    system = EnhancedComorbiditySystem()
    
    # 模拟患者数据
    patient_data = {
        "gender": "女",
        "age": 28,
        "anxiety_score": 12,
        "depression_score": 16,
        "menstrual_pain": 8,
        "family_history_diabetes": True
    }
    
    # 综合筛查
    screening = system.comprehensive_screening(patient_data)
    print("🔍 合并疾病筛查结果:")
    print(f"高风险疾病: {len(screening['high_risk_comorbidities'])}种")
    print(f"推荐检查: {len(screening['recommended_tests'])}项")
    
    # 治疗调整
    modifications = system.get_treatment_modifications(
        comorbidities=["焦虑症", "抑郁症", "子宫内膜异位症"],
        current_ibs_treatment=["美贝维林", "洛哌丁胺"]
    )
    print(f"\n💊 治疗调整建议:")
    print(f"需要调整: {len(modifications['drug_adjustments'])}项")
    print(f"附加治疗: {len(modifications['additional_treatments'])}项")

if __name__ == "__main__":
    main() 