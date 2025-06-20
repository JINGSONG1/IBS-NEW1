#!/usr/bin/env python3
"""
患者随访评价系统
包含副作用监测、换药评估、满意度跟踪和长期疗效评估
"""

from typing import Dict, List, Optional, Tuple
import json
from datetime import datetime, timedelta
import numpy as np

class PatientFollowupSystem:
    """患者随访评价系统"""
    
    def __init__(self):
        self.load_adverse_event_database()
        self.init_satisfaction_metrics()
        self.load_switching_criteria()
        self.init_outcome_tracking()
    
    def load_adverse_event_database(self):
        """加载药物副作用数据库"""
        self.adverse_events = {
            "洛哌丁胺": {
                "common_aes": [
                    {
                        "name": "便秘",
                        "frequency": "很常见（>10%）",
                        "severity": "轻到中度",
                        "onset": "2-7天",
                        "management": "减量、停药2-3天后重新开始",
                        "monitoring": "排便频率和硬度"
                    },
                    {
                        "name": "腹胀",
                        "frequency": "常见（1-10%）",
                        "severity": "轻度",
                        "onset": "数小时到几天",
                        "management": "西甲硅油、饮食调整",
                        "monitoring": "腹围变化"
                    }
                ],
                "serious_aes": [
                    {
                        "name": "肠梗阻",
                        "frequency": "罕见（<0.1%）",
                        "severity": "严重",
                        "onset": "过量使用时",
                        "management": "立即停药，就医",
                        "monitoring": "腹痛、呕吐、停止排气排便"
                    }
                ],
                "monitoring_plan": {
                    "week_1": ["便秘症状", "腹胀程度", "排便频率"],
                    "week_2": ["症状改善程度", "副作用持续性"],
                    "month_1": ["长期耐受性", "效果维持"],
                    "ongoing": ["依赖性评估"]
                }
            },
            
            "美贝维林": {
                "common_aes": [
                    {
                        "name": "头晕",
                        "frequency": "常见（1-10%）",
                        "severity": "轻度",
                        "onset": "用药后1-2小时",
                        "management": "避免突然站立，餐后服药",
                        "monitoring": "血压变化"
                    }
                ],
                "serious_aes": [
                    {
                        "name": "过敏反应",
                        "frequency": "罕见（<0.1%）",
                        "severity": "可能严重",
                        "onset": "首次用药后",
                        "management": "立即停药，抗过敏治疗",
                        "monitoring": "皮疹、呼吸困难"
                    }
                ],
                "monitoring_plan": {
                    "day_1": ["过敏反应"],
                    "week_1": ["头晕症状", "胃肠道症状改善"],
                    "month_1": ["整体耐受性"],
                    "ongoing": ["长期安全性"]
                }
            },
            
            "帕罗西汀": {
                "common_aes": [
                    {
                        "name": "恶心",
                        "frequency": "很常见（>10%）",
                        "severity": "轻到中度",
                        "onset": "用药初期",
                        "management": "餐后服药，缓慢增量",
                        "monitoring": "食欲、体重变化"
                    },
                    {
                        "name": "性功能障碍",
                        "frequency": "常见（1-10%）",
                        "severity": "中度",
                        "onset": "2-4周后",
                        "management": "剂量调整、药物假期、换药",
                        "monitoring": "性功能评估问卷"
                    },
                    {
                        "name": "停药综合征",
                        "frequency": "常见（1-10%）",
                        "severity": "轻到中度",
                        "onset": "停药后24-72小时",
                        "management": "缓慢减量，停药计划",
                        "monitoring": "头晕、电击感、流感样症状"
                    }
                ],
                "monitoring_plan": {
                    "week_1_2": ["胃肠道副作用", "情绪变化", "自杀意念"],
                    "week_4_6": ["性功能评估", "体重监测"],
                    "month_3": ["长期疗效评估"],
                    "停药期": ["停药综合征监测"]
                }
            },
            
            "阿米替林": {
                "common_aes": [
                    {
                        "name": "口干",
                        "frequency": "很常见（>10%）",
                        "severity": "轻到中度",
                        "onset": "数天",
                        "management": "多饮水、无糖口香糖、人工唾液",
                        "monitoring": "口腔卫生状况"
                    },
                    {
                        "name": "便秘",
                        "frequency": "很常见（>10%）",
                        "severity": "轻到中度", 
                        "onset": "数天到1周",
                        "management": "高纤维饮食、泻药",
                        "monitoring": "排便频率"
                    },
                    {
                        "name": "嗜睡",
                        "frequency": "很常见（>10%）",
                        "severity": "轻到中度",
                        "onset": "用药后数小时",
                        "management": "睡前给药、剂量调整",
                        "monitoring": "日间嗜睡程度"
                    }
                ],
                "serious_aes": [
                    {
                        "name": "心律失常",
                        "frequency": "罕见（<1%）",
                        "severity": "严重",
                        "onset": "剂量相关",
                        "management": "心电图监测，剂量调整或停药",
                        "monitoring": "心电图、心率"
                    }
                ],
                "monitoring_plan": {
                    "baseline": ["心电图", "血压", "体重"],
                    "week_1": ["抗胆碱能副作用"],
                    "week_4": ["心电图复查", "体重监测"],
                    "ongoing": ["定期心电图监测"]
                }
            }
        }
    
    def init_satisfaction_metrics(self):
        """初始化满意度评估指标"""
        self.satisfaction_metrics = {
            "treatment_satisfaction": {
                "questions": [
                    {
                        "id": "overall_satisfaction",
                        "question": "总体而言，您对目前的治疗满意吗？",
                        "scale": "1-10分",
                        "interpretation": {
                            "9-10": "非常满意",
                            "7-8": "满意",
                            "5-6": "一般",
                            "3-4": "不满意", 
                            "1-2": "非常不满意"
                        }
                    },
                    {
                        "id": "symptom_improvement",
                        "question": "您觉得症状改善程度如何？",
                        "scale": "1-10分",
                        "interpretation": {
                            "9-10": "显著改善",
                            "7-8": "明显改善",
                            "5-6": "轻度改善",
                            "3-4": "无明显改善",
                            "1-2": "症状加重"
                        }
                    },
                    {
                        "id": "side_effect_tolerability",
                        "question": "副作用对您的影响程度？",
                        "scale": "1-10分（10=完全无副作用）",
                        "interpretation": {
                            "9-10": "无副作用或可忽略",
                            "7-8": "轻微副作用，可耐受",
                            "5-6": "中度副作用，影响生活",
                            "3-4": "重度副作用，严重影响",
                            "1-2": "无法耐受的副作用"
                        }
                    },
                    {
                        "id": "medication_adherence",
                        "question": "您按医嘱服药的依从性如何？",
                        "scale": "百分比",
                        "interpretation": {
                            ">90%": "依从性极好",
                            "80-90%": "依从性良好",
                            "60-79%": "依从性一般",
                            "40-59%": "依从性较差",
                            "<40%": "依从性很差"
                        }
                    }
                ]
            },
            
            "quality_of_life": {
                "domains": [
                    {
                        "name": "身体功能",
                        "questions": [
                            "腹痛对日常活动的影响",
                            "排便问题对外出的限制",
                            "睡眠质量的改变"
                        ]
                    },
                    {
                        "name": "社会功能",
                        "questions": [
                            "与家人朋友关系的影响",
                            "工作学习效率的变化",
                            "社交活动参与度"
                        ]
                    },
                    {
                        "name": "心理状况",
                        "questions": [
                            "对疾病的担忧程度",
                            "情绪状态的改善",
                            "对未来的信心"
                        ]
                    }
                ]
            },
            
            "treatment_expectations": {
                "met_expectations": "治疗结果是否符合期望",
                "realistic_goals": "对治疗目标的重新评估",
                "future_treatment_willingness": "继续治疗的意愿"
            }
        }
    
    def load_switching_criteria(self):
        """加载换药标准"""
        self.switching_criteria = {
            "efficacy_failure": {
                "primary_criteria": [
                    {
                        "criterion": "症状无改善",
                        "threshold": "治疗4-6周后IBS-SSS改善<25%",
                        "action": "考虑换药或加药"
                    },
                    {
                        "criterion": "症状恶化",
                        "threshold": "IBS-SSS评分较基线增加>20%",
                        "action": "立即重新评估治疗方案"
                    }
                ],
                "secondary_criteria": [
                    {
                        "criterion": "部分应答",
                        "threshold": "症状改善25-50%但仍影响生活质量",
                        "action": "考虑剂量优化或联合治疗"
                    }
                ]
            },
            
            "tolerability_issues": {
                "major_criteria": [
                    {
                        "criterion": "严重副作用",
                        "examples": ["过敏反应", "严重便秘", "心律失常"],
                        "action": "立即停药，选择替代方案"
                    },
                    {
                        "criterion": "中度副作用持续",
                        "threshold": "副作用评分<5分，持续>2周",
                        "action": "考虑减量或换药"
                    }
                ],
                "minor_criteria": [
                    {
                        "criterion": "轻度副作用",
                        "threshold": "副作用评分5-7分",
                        "action": "症状管理，观察2-4周"
                    }
                ]
            },
            
            "patient_preference": {
                "criteria": [
                    {
                        "factor": "给药频次偏好",
                        "consideration": "患者更偏好较少的给药次数"
                    },
                    {
                        "factor": "成本考虑",
                        "consideration": "经济负担过重"
                    },
                    {
                        "factor": "心理因素",
                        "consideration": "对特定药物的恐惧或偏见"
                    }
                ]
            }
        }
    
    def init_outcome_tracking(self):
        """初始化结局追踪系统"""
        self.outcome_measures = {
            "primary_outcomes": [
                {
                    "measure": "IBS-SSS评分变化",
                    "assessment_time": ["基线", "2周", "4周", "8周", "12周"],
                    "clinically_significant": "改善≥50分",
                    "response_definition": "改善≥25%"
                },
                {
                    "measure": "整体改善评估",
                    "scale": "7分Likert量表",
                    "response_definition": "明显改善或非常改善"
                }
            ],
            
            "secondary_outcomes": [
                {
                    "measure": "生活质量评分",
                    "tool": "IBS-QOL量表",
                    "assessment_frequency": "每月"
                },
                {
                    "measure": "症状日记",
                    "parameters": ["疼痛程度", "排便次数", "便型", "腹胀"],
                    "assessment_frequency": "每日"
                },
                {
                    "measure": "工作生产力",
                    "tool": "WPAI-IBS量表",
                    "assessment_frequency": "每月"
                }
            ],
            
            "safety_outcomes": [
                {
                    "measure": "不良事件记录",
                    "classification": "按CTCAE分级",
                    "assessment_frequency": "每次随访"
                },
                {
                    "measure": "严重不良事件",
                    "reporting": "24小时内报告",
                    "follow_up": "持续监测至恢复"
                }
            ]
        }
    
    def conduct_followup_assessment(self, patient_id: str, 
                                  timepoint: str, 
                                  assessment_data: Dict) -> Dict:
        """进行随访评估"""
        
        followup_result = {
            "patient_id": patient_id,
            "assessment_date": datetime.now().isoformat(),
            "timepoint": timepoint,
            "assessments": {}
        }
        
        # 疗效评估
        efficacy = self._assess_efficacy(assessment_data)
        followup_result["assessments"]["efficacy"] = efficacy
        
        # 安全性评估
        safety = self._assess_safety(assessment_data)
        followup_result["assessments"]["safety"] = safety
        
        # 满意度评估
        satisfaction = self._assess_satisfaction(assessment_data)
        followup_result["assessments"]["satisfaction"] = satisfaction
        
        # 依从性评估
        adherence = self._assess_adherence(assessment_data)
        followup_result["assessments"]["adherence"] = adherence
        
        # 换药建议
        switching_recommendation = self._evaluate_switching_need(
            efficacy, safety, satisfaction, adherence
        )
        followup_result["switching_recommendation"] = switching_recommendation
        
        # 下次随访计划
        next_followup = self._plan_next_followup(
            timepoint, efficacy, safety, switching_recommendation
        )
        followup_result["next_followup"] = next_followup
        
        return followup_result
    
    def _assess_efficacy(self, data: Dict) -> Dict:
        """评估疗效"""
        efficacy = {
            "ibs_sss_change": 0,
            "response_achieved": False,
            "symptom_improvement": {},
            "overall_impression": ""
        }
        
        baseline_score = data.get("baseline_ibs_sss", 0)
        current_score = data.get("current_ibs_sss", baseline_score)
        
        efficacy["ibs_sss_change"] = baseline_score - current_score
        efficacy["response_achieved"] = efficacy["ibs_sss_change"] >= 50
        
        # 各症状改善评估
        for symptom in ["pain", "bowel_habits", "bloating", "satisfaction"]:
            baseline = data.get(f"baseline_{symptom}", 0)
            current = data.get(f"current_{symptom}", baseline)
            improvement = baseline - current
            improvement_pct = (improvement / baseline * 100) if baseline > 0 else 0
            
            efficacy["symptom_improvement"][symptom] = {
                "absolute_change": improvement,
                "percent_change": improvement_pct,
                "interpretation": self._interpret_symptom_change(improvement_pct)
            }
        
        # 整体印象
        overall_score = data.get("global_improvement_scale", 4)
        efficacy["overall_impression"] = self._interpret_global_improvement(overall_score)
        
        return efficacy
    
    def _assess_safety(self, data: Dict) -> Dict:
        """评估安全性"""
        safety = {
            "adverse_events": [],
            "severity_assessment": {},
            "causality_assessment": {},
            "action_required": False
        }
        
        # 不良事件记录
        aes = data.get("adverse_events", [])
        for ae in aes:
            ae_assessment = {
                "event": ae.get("name", ""),
                "severity": ae.get("severity", ""),
                "onset": ae.get("onset", ""),
                "duration": ae.get("duration", ""),
                "causality": self._assess_causality(ae),
                "management": ae.get("management", "")
            }
            safety["adverse_events"].append(ae_assessment)
            
            # 判断是否需要采取行动
            if ae.get("severity") in ["严重", "中度"]:
                safety["action_required"] = True
        
        return safety
    
    def _assess_satisfaction(self, data: Dict) -> Dict:
        """评估满意度"""
        satisfaction = {
            "overall_score": data.get("overall_satisfaction", 5),
            "improvement_score": data.get("symptom_improvement_satisfaction", 5),
            "tolerability_score": data.get("side_effect_tolerability", 8),
            "adherence_score": data.get("medication_adherence", 80),
            "interpretation": {}
        }
        
        # 解释各项评分
        for metric, score in satisfaction.items():
            if metric != "interpretation" and isinstance(score, (int, float)):
                satisfaction["interpretation"][metric] = self._interpret_satisfaction_score(metric, score)
        
        return satisfaction
    
    def _assess_adherence(self, data: Dict) -> Dict:
        """评估依从性"""
        adherence = {
            "medication_adherence_pct": data.get("medication_adherence", 80),
            "missed_doses": data.get("missed_doses", 0),
            "reasons_for_non_adherence": data.get("non_adherence_reasons", []),
            "intervention_needed": False
        }
        
        if adherence["medication_adherence_pct"] < 80:
            adherence["intervention_needed"] = True
        
        return adherence
    
    def _evaluate_switching_need(self, efficacy: Dict, safety: Dict, 
                                satisfaction: Dict, adherence: Dict) -> Dict:
        """评估是否需要换药"""
        switching = {
            "recommendation": "继续当前治疗",
            "reasons": [],
            "urgency": "无",
            "alternative_options": []
        }
        
        # 疗效不佳
        if not efficacy["response_achieved"] and efficacy["ibs_sss_change"] < 25:
            switching["reasons"].append("疗效不佳")
            switching["recommendation"] = "考虑换药或加药"
        
        # 安全性问题
        if safety["action_required"]:
            switching["reasons"].append("安全性问题")
            switching["urgency"] = "紧急"
            switching["recommendation"] = "立即评估换药"
        
        # 耐受性差
        if satisfaction["tolerability_score"] < 5:
            switching["reasons"].append("耐受性差")
            switching["recommendation"] = "考虑换药"
        
        # 依从性差
        if adherence["medication_adherence_pct"] < 60:
            switching["reasons"].append("依从性差")
            switching["recommendation"] = "优化治疗方案"
        
        return switching
    
    def _plan_next_followup(self, current_timepoint: str, efficacy: Dict, 
                           safety: Dict, switching: Dict) -> Dict:
        """规划下次随访"""
        next_followup = {
            "recommended_interval": "4周",
            "focus_areas": [],
            "required_assessments": []
        }
        
        # 根据当前时间点确定间隔
        timepoint_intervals = {
            "2周": "2周",
            "4周": "4周", 
            "8周": "8周",
            "12周": "12周"
        }
        
        next_followup["recommended_interval"] = timepoint_intervals.get(current_timepoint, "4周")
        
        # 根据问题确定重点关注领域
        if not efficacy["response_achieved"]:
            next_followup["focus_areas"].append("疗效评估")
        
        if safety["action_required"]:
            next_followup["focus_areas"].append("安全性监测")
            next_followup["recommended_interval"] = "1-2周"
        
        if switching["urgency"] == "紧急":
            next_followup["recommended_interval"] = "1周"
        
        return next_followup
    
    def _interpret_symptom_change(self, percent_change: float) -> str:
        """解释症状变化百分比"""
        if percent_change >= 75:
            return "显著改善"
        elif percent_change >= 50:
            return "明显改善"
        elif percent_change >= 25:
            return "轻度改善"
        elif percent_change >= 0:
            return "无明显改善"
        else:
            return "症状恶化"
    
    def _interpret_global_improvement(self, score: int) -> str:
        """解释整体改善印象"""
        interpretations = {
            1: "非常明显改善",
            2: "明显改善", 
            3: "轻度改善",
            4: "无变化",
            5: "轻度恶化",
            6: "明显恶化",
            7: "非常明显恶化"
        }
        return interpretations.get(score, "未评估")
    
    def _assess_causality(self, ae: Dict) -> str:
        """评估不良事件因果关系"""
        # 简化的因果关系评估
        onset = ae.get("onset", "")
        known_ae = ae.get("known_ae", False)
        
        if known_ae and "用药后" in onset:
            return "很可能相关"
        elif known_ae:
            return "可能相关"
        else:
            return "可能无关"
    
    def _interpret_satisfaction_score(self, metric: str, score: float) -> str:
        """解释满意度评分"""
        if metric == "adherence_score":
            if score >= 90:
                return "依从性极好"
            elif score >= 80:
                return "依从性良好"
            elif score >= 60:
                return "依从性一般"
            else:
                return "依从性差"
        else:
            if score >= 8:
                return "满意"
            elif score >= 6:
                return "一般"
            elif score >= 4:
                return "不满意"
            else:
                return "非常不满意"
    
    def generate_followup_report(self, patient_id: str, 
                                followup_data: List[Dict]) -> Dict:
        """生成随访报告"""
        report = {
            "patient_id": patient_id,
            "report_date": datetime.now().isoformat(),
            "followup_summary": {},
            "trend_analysis": {},
            "recommendations": {}
        }
        
        # 疗效趋势分析
        ibs_scores = [f["assessments"]["efficacy"]["ibs_sss_change"] 
                     for f in followup_data if "efficacy" in f["assessments"]]
        
        if len(ibs_scores) >= 2:
            report["trend_analysis"]["efficacy_trend"] = {
                "improvement_trajectory": "递增" if ibs_scores[-1] > ibs_scores[0] else "平稳或下降",
                "latest_change": ibs_scores[-1],
                "peak_improvement": max(ibs_scores)
            }
        
        # 安全性汇总
        all_aes = []
        for f in followup_data:
            if "safety" in f["assessments"]:
                all_aes.extend(f["assessments"]["safety"]["adverse_events"])
        
        report["followup_summary"]["total_adverse_events"] = len(all_aes)
        report["followup_summary"]["serious_aes"] = len([ae for ae in all_aes if ae.get("severity") == "严重"])
        
        # 总体建议
        latest_followup = followup_data[-1] if followup_data else {}
        if latest_followup:
            report["recommendations"] = latest_followup.get("switching_recommendation", {})
        
        return report

def main():
    """测试患者随访系统"""
    followup_system = PatientFollowupSystem()
    
    # 模拟随访数据
    assessment_data = {
        "baseline_ibs_sss": 320,
        "current_ibs_sss": 245,
        "baseline_pain": 80,
        "current_pain": 55,
        "overall_satisfaction": 7,
        "side_effect_tolerability": 6,
        "medication_adherence": 85,
        "adverse_events": [
            {
                "name": "轻度便秘",
                "severity": "轻度",
                "onset": "用药后3天",
                "known_ae": True
            }
        ]
    }
    
    # 进行随访评估
    result = followup_system.conduct_followup_assessment(
        patient_id="P001",
        timepoint="4周",
        assessment_data=assessment_data
    )
    
    print("📋 随访评估结果:")
    print(f"患者ID: {result['patient_id']}")
    print(f"评估时间点: {result['timepoint']}")
    print(f"疗效评估: IBS-SSS改善 {result['assessments']['efficacy']['ibs_sss_change']} 分")
    print(f"换药建议: {result['switching_recommendation']['recommendation']}")
    print(f"下次随访: {result['next_followup']['recommended_interval']}")

if __name__ == "__main__":
    main() 