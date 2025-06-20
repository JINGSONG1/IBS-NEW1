#!/usr/bin/env python3
"""
真实患者数据处理模块
支持多种数据格式，确保隐私保护和数据质量

针对您提到的23位患者样本数据处理
"""

import pandas as pd
import numpy as np
import json
import hashlib
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class RealPatientData:
    """真实患者数据结构 - 支持您的23位患者样本"""
    patient_id: str
    age: int
    gender: str
    ethnicity: str
    bmi: float
    
    # IBS症状评分 (1-10量表)
    abdominal_pain: int
    bloating: int
    bowel_movement_frequency: int
    stool_consistency: int
    symptom_duration_months: int
    
    # Rome IV诊断
    rome_iv_subtype: str  # IBS-D, IBS-C, IBS-M, IBS-U
    rome_iv_confidence: float  # 诊断置信度
    
    # 合并症
    anxiety_score: Optional[int] = None
    depression_score: Optional[int] = None
    endometriosis: bool = False
    other_comorbidities: List[str] = None
    
    # 治疗历史
    previous_treatments: List[str] = None
    treatment_durations: List[int] = None  # 天数
    treatment_responses: List[int] = None  # 1-10效果评分
    
    # 实验室检查
    inflammatory_markers: Dict[str, float] = None
    microbiome_data: Dict[str, float] = None
    
    # 治疗结局 (核心验证指标)
    baseline_symptom_severity: int = 0  # 治疗前
    followup_symptom_severity: List[int] = None  # 1,3,6个月随访
    quality_of_life_scores: List[int] = None  # QoL评分
    treatment_satisfaction: int = 0  # 患者满意度
    adverse_events: List[str] = None
    
    def __post_init__(self):
        if self.other_comorbidities is None:
            self.other_comorbidities = []
        if self.previous_treatments is None:
            self.previous_treatments = []
        if self.treatment_durations is None:
            self.treatment_durations = []
        if self.treatment_responses is None:
            self.treatment_responses = []
        if self.inflammatory_markers is None:
            self.inflammatory_markers = {}
        if self.microbiome_data is None:
            self.microbiome_data = {}
        if self.adverse_events is None:
            self.adverse_events = []

class RealPatientDataHandler:
    """真实患者数据处理器"""
    
    def __init__(self, privacy_protection: bool = True):
        self.privacy_protection = privacy_protection
        self.patients: List[RealPatientData] = []
        self.data_quality_report = {}
        
    def load_from_excel(self, file_path: str, sheet_name: str = 'Sheet1') -> bool:
        """
        从Excel文件加载患者数据
        支持标准的临床数据表格格式
        """
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            logger.info(f"加载Excel文件: {file_path}, 发现 {len(df)} 位患者")
            
            for _, row in df.iterrows():
                patient = self._convert_row_to_patient(row)
                if patient:
                    self.patients.append(patient)
            
            logger.info(f"成功处理 {len(self.patients)} 位患者数据")
            return True
            
        except Exception as e:
            logger.error(f"Excel文件加载失败: {e}")
            return False
    
    def load_from_csv(self, file_path: str, encoding: str = 'utf-8') -> bool:
        """从CSV文件加载患者数据"""
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            logger.info(f"加载CSV文件: {file_path}, 发现 {len(df)} 位患者")
            
            for _, row in df.iterrows():
                patient = self._convert_row_to_patient(row)
                if patient:
                    self.patients.append(patient)
            
            logger.info(f"成功处理 {len(self.patients)} 位患者数据")
            return True
            
        except Exception as e:
            logger.error(f"CSV文件加载失败: {e}")
            return False
    
    def load_from_json(self, file_path: str) -> bool:
        """从JSON文件加载患者数据"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if isinstance(data, list):
                for patient_dict in data:
                    patient = RealPatientData(**patient_dict)
                    self.patients.append(patient)
            elif isinstance(data, dict) and 'patients' in data:
                for patient_dict in data['patients']:
                    patient = RealPatientData(**patient_dict)
                    self.patients.append(patient)
            
            logger.info(f"成功从JSON加载 {len(self.patients)} 位患者数据")
            return True
            
        except Exception as e:
            logger.error(f"JSON文件加载失败: {e}")
            return False
    
    def load_manual_entry(self, patient_data_list: List[Dict]) -> bool:
        """
        手动输入患者数据
        适用于您需要逐个输入23位患者数据的情况
        """
        try:
            for patient_dict in patient_data_list:
                # 验证必需字段
                required_fields = ['patient_id', 'age', 'gender', 'ethnicity', 'bmi',
                                 'abdominal_pain', 'bloating', 'bowel_movement_frequency',
                                 'stool_consistency', 'symptom_duration_months',
                                 'rome_iv_subtype', 'baseline_symptom_severity']
                
                missing_fields = [field for field in required_fields if field not in patient_dict]
                if missing_fields:
                    logger.warning(f"患者 {patient_dict.get('patient_id', 'Unknown')} 缺少字段: {missing_fields}")
                    continue
                
                patient = RealPatientData(**patient_dict)
                
                # 隐私保护处理
                if self.privacy_protection:
                    patient = self._anonymize_patient(patient)
                
                self.patients.append(patient)
            
            logger.info(f"手动录入完成，共处理 {len(self.patients)} 位患者")
            return True
            
        except Exception as e:
            logger.error(f"手动录入失败: {e}")
            return False
    
    def _convert_row_to_patient(self, row) -> Optional[RealPatientData]:
        """将数据行转换为患者对象"""
        try:
            # 基础映射 - 您可以根据实际的列名调整
            patient_dict = {
                'patient_id': str(row.get('患者ID', row.get('patient_id', f'P{len(self.patients)+1:03d}'))),
                'age': int(row.get('年龄', row.get('age', 0))),
                'gender': str(row.get('性别', row.get('gender', 'Unknown'))),
                'ethnicity': str(row.get('种族', row.get('ethnicity', 'Unknown'))),
                'bmi': float(row.get('BMI', row.get('bmi', 0.0))),
                
                # 症状评分
                'abdominal_pain': int(row.get('腹痛评分', row.get('abdominal_pain', 0))),
                'bloating': int(row.get('腹胀评分', row.get('bloating', 0))),
                'bowel_movement_frequency': int(row.get('排便频率', row.get('bowel_movement_frequency', 0))),
                'stool_consistency': int(row.get('便便性状', row.get('stool_consistency', 0))),
                'symptom_duration_months': int(row.get('症状持续月数', row.get('symptom_duration_months', 0))),
                
                # Rome IV诊断
                'rome_iv_subtype': str(row.get('Rome_IV亚型', row.get('rome_iv_subtype', 'Unknown'))),
                'rome_iv_confidence': float(row.get('诊断置信度', row.get('rome_iv_confidence', 0.0))),
                
                # 合并症
                'anxiety_score': self._safe_int(row.get('焦虑评分', row.get('anxiety_score'))),
                'depression_score': self._safe_int(row.get('抑郁评分', row.get('depression_score'))),
                'endometriosis': self._safe_bool(row.get('子宫内膜异位症', row.get('endometriosis', False))),
                
                # 治疗结局
                'baseline_symptom_severity': int(row.get('基线症状严重程度', row.get('baseline_symptom_severity', 0))),
                'treatment_satisfaction': int(row.get('治疗满意度', row.get('treatment_satisfaction', 5)))
            }
            
            # 处理列表类型的字段
            followup_cols = [col for col in row.index if '随访' in str(col) or 'followup' in str(col)]
            if followup_cols:
                patient_dict['followup_symptom_severity'] = [int(row[col]) for col in followup_cols if pd.notna(row[col])]
            else:
                patient_dict['followup_symptom_severity'] = []
            
            # 处理既往治疗
            treatment_cols = [col for col in row.index if '既往治疗' in str(col) or 'previous_treatment' in str(col)]
            if treatment_cols:
                patient_dict['previous_treatments'] = [str(row[col]) for col in treatment_cols if pd.notna(row[col])]
            else:
                patient_dict['previous_treatments'] = []
            
            patient = RealPatientData(**patient_dict)
            
            # 隐私保护
            if self.privacy_protection:
                patient = self._anonymize_patient(patient)
            
            return patient
            
        except Exception as e:
            logger.error(f"数据行转换失败: {e}")
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """安全转换为整数"""
        try:
            return int(value) if pd.notna(value) else None
        except:
            return None
    
    def _safe_bool(self, value) -> bool:
        """安全转换为布尔值"""
        if pd.isna(value):
            return False
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes', '是', 'y']
        return bool(value)
    
    def _anonymize_patient(self, patient: RealPatientData) -> RealPatientData:
        """患者数据匿名化处理"""
        # 生成匿名ID
        hash_input = f"{patient.patient_id}_{patient.age}_{patient.gender}"
        anonymous_id = hashlib.md5(hash_input.encode()).hexdigest()[:8].upper()
        patient.patient_id = f"ANON_{anonymous_id}"
        
        return patient
    
    def validate_data_quality(self) -> Dict:
        """数据质量验证"""
        if not self.patients:
            return {'error': '没有患者数据'}
        
        quality_report = {
            'total_patients': len(self.patients),
            'data_completeness': {},
            'data_consistency': {},
            'outlier_detection': {},
            'missing_data_analysis': {}
        }
        
        # 数据完整性检查
        required_fields = ['age', 'gender', 'ethnicity', 'bmi', 'abdominal_pain', 
                          'bloating', 'bowel_movement_frequency', 'stool_consistency',
                          'baseline_symptom_severity']
        
        for field in required_fields:
            complete_count = sum(1 for p in self.patients if getattr(p, field, None) is not None and getattr(p, field, 0) != 0)
            quality_report['data_completeness'][field] = {
                'complete_count': complete_count,
                'completion_rate': complete_count / len(self.patients) * 100
            }
        
        # 数据一致性检查
        age_range = [p.age for p in self.patients if p.age > 0]
        bmi_range = [p.bmi for p in self.patients if p.bmi > 0]
        
        quality_report['data_consistency'] = {
            'age_range': (min(age_range) if age_range else 0, max(age_range) if age_range else 0),
            'bmi_range': (min(bmi_range) if bmi_range else 0, max(bmi_range) if bmi_range else 0),
            'gender_distribution': self._count_categorical('gender'),
            'ethnicity_distribution': self._count_categorical('ethnicity'),
            'rome_iv_distribution': self._count_categorical('rome_iv_subtype')
        }
        
        # 异常值检测
        symptom_scores = [p.baseline_symptom_severity for p in self.patients if p.baseline_symptom_severity > 0]
        if symptom_scores:
            q1, q3 = np.percentile(symptom_scores, [25, 75])
            iqr = q3 - q1
            outlier_threshold_low = q1 - 1.5 * iqr
            outlier_threshold_high = q3 + 1.5 * iqr
            
            outliers = [score for score in symptom_scores 
                       if score < outlier_threshold_low or score > outlier_threshold_high]
            
            quality_report['outlier_detection'] = {
                'symptom_severity_outliers': len(outliers),
                'outlier_percentage': len(outliers) / len(symptom_scores) * 100 if symptom_scores else 0,
                'outlier_threshold': (outlier_threshold_low, outlier_threshold_high)
            }
        
        # 缺失数据分析
        missing_followup = sum(1 for p in self.patients if not p.followup_symptom_severity)
        missing_comorbidity = sum(1 for p in self.patients if p.anxiety_score is None and p.depression_score is None)
        
        quality_report['missing_data_analysis'] = {
            'missing_followup_data': missing_followup,
            'missing_comorbidity_data': missing_comorbidity,
            'missing_followup_percentage': missing_followup / len(self.patients) * 100,
            'missing_comorbidity_percentage': missing_comorbidity / len(self.patients) * 100
        }
        
        self.data_quality_report = quality_report
        logger.info(f"数据质量验证完成: {quality_report['total_patients']}位患者")
        
        return quality_report
    
    def _count_categorical(self, field: str) -> Dict:
        """统计分类变量分布"""
        values = [getattr(p, field, 'Unknown') for p in self.patients]
        from collections import Counter
        return dict(Counter(values))
    
    def generate_summary_statistics(self) -> Dict:
        """生成描述性统计"""
        if not self.patients:
            return {}
        
        # 基础统计
        ages = [p.age for p in self.patients if p.age > 0]
        bmis = [p.bmi for p in self.patients if p.bmi > 0]
        
        # 症状评分统计
        pain_scores = [p.abdominal_pain for p in self.patients if p.abdominal_pain > 0]
        bloating_scores = [p.bloating for p in self.patients if p.bloating > 0]
        
        # 治疗结局统计
        baseline_severity = [p.baseline_symptom_severity for p in self.patients if p.baseline_symptom_severity > 0]
        
        stats = {
            'demographics': {
                'age_mean': np.mean(ages) if ages else 0,
                'age_std': np.std(ages) if ages else 0,
                'age_range': (min(ages), max(ages)) if ages else (0, 0),
                'bmi_mean': np.mean(bmis) if bmis else 0,
                'bmi_std': np.std(bmis) if bmis else 0,
                'gender_counts': self._count_categorical('gender'),
                'ethnicity_counts': self._count_categorical('ethnicity')
            },
            'symptoms': {
                'pain_mean': np.mean(pain_scores) if pain_scores else 0,
                'pain_std': np.std(pain_scores) if pain_scores else 0,
                'bloating_mean': np.mean(bloating_scores) if bloating_scores else 0,
                'bloating_std': np.std(bloating_scores) if bloating_scores else 0,
                'baseline_severity_mean': np.mean(baseline_severity) if baseline_severity else 0,
                'baseline_severity_std': np.std(baseline_severity) if baseline_severity else 0
            },
            'comorbidities': {
                'endometriosis_count': sum(1 for p in self.patients if p.endometriosis),
                'anxiety_patients': sum(1 for p in self.patients if p.anxiety_score and p.anxiety_score > 5),
                'depression_patients': sum(1 for p in self.patients if p.depression_score and p.depression_score > 5)
            },
            'rome_iv_distribution': self._count_categorical('rome_iv_subtype')
        }
        
        return stats
    
    def export_for_analysis(self, output_path: str = 'processed_patient_data.json') -> bool:
        """导出处理后的数据用于分析"""
        try:
            export_data = {
                'metadata': {
                    'total_patients': len(self.patients),
                    'export_timestamp': datetime.now().isoformat(),
                    'privacy_protected': self.privacy_protection
                },
                'patients': [asdict(patient) for patient in self.patients],
                'summary_statistics': self.generate_summary_statistics(),
                'data_quality_report': self.data_quality_report
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"数据导出成功: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"数据导出失败: {e}")
            return False
    
    def create_sample_data_template(self, output_path: str = 'patient_data_template.xlsx') -> bool:
        """
        创建患者数据录入模板
        方便您录入23位患者的数据
        """
        try:
            # 创建模板数据
            template_data = {
                '患者ID': ['P001', 'P002', 'P003'],
                '年龄': [45, 38, 52],
                '性别': ['Female', 'Male', 'Female'],
                '种族': ['Asian', 'Caucasian', 'Hispanic'],
                'BMI': [23.5, 26.2, 28.1],
                '腹痛评分(1-10)': [7, 6, 8],
                '腹胀评分(1-10)': [6, 7, 9],
                '排便频率评分(1-10)': [8, 5, 7],
                '便便性状评分(1-10)': [6, 4, 8],
                '症状持续月数': [36, 24, 48],
                'Rome_IV亚型': ['IBS-D', 'IBS-C', 'IBS-M'],
                '诊断置信度(0-1)': [0.85, 0.78, 0.92],
                '焦虑评分(1-10)': [5, 3, 7],
                '抑郁评分(1-10)': [4, 2, 6],
                '子宫内膜异位症(True/False)': [True, False, False],
                '基线症状严重程度(1-10)': [8, 6, 9],
                '1个月随访症状严重程度': [6, 4, 7],
                '3个月随访症状严重程度': [4, 3, 5],
                '6个月随访症状严重程度': [3, 2, 4],
                '治疗满意度(1-10)': [7, 8, 6],
                '既往治疗1': ['洛哌丁胺', '聚乙二醇', '益生菌'],
                '既往治疗2': ['抗痉挛药', '', '抗抑郁药'],
                '备注': ['合并焦虑', '症状较轻', '合并内异症']
            }
            
            df = pd.DataFrame(template_data)
            df.to_excel(output_path, index=False)
            
            logger.info(f"患者数据模板已创建: {output_path}")
            print(f"✅ 已创建患者数据录入模板: {output_path}")
            print("📝 请按照模板格式录入您的23位患者数据")
            
            return True
            
        except Exception as e:
            logger.error(f"模板创建失败: {e}")
            return False

# 使用示例和快速测试
if __name__ == "__main__":
    # 创建数据处理器
    handler = RealPatientDataHandler(privacy_protection=True)
    
    # 创建数据录入模板
    handler.create_sample_data_template()
    
    # 示例：手动录入几个患者数据进行测试
    sample_patients = [
        {
            'patient_id': 'TEST001',
            'age': 42,
            'gender': 'Female',
            'ethnicity': 'Asian',
            'bmi': 24.5,
            'abdominal_pain': 7,
            'bloating': 8,
            'bowel_movement_frequency': 6,
            'stool_consistency': 5,
            'symptom_duration_months': 36,
            'rome_iv_subtype': 'IBS-D',
            'rome_iv_confidence': 0.85,
            'endometriosis': True,
            'baseline_symptom_severity': 8,
            'followup_symptom_severity': [6, 4, 3],
            'treatment_satisfaction': 7
        },
        {
            'patient_id': 'TEST002',
            'age': 38,
            'gender': 'Male',
            'ethnicity': 'Caucasian',
            'bmi': 26.2,
            'abdominal_pain': 5,
            'bloating': 6,
            'bowel_movement_frequency': 4,
            'stool_consistency': 3,
            'symptom_duration_months': 24,
            'rome_iv_subtype': 'IBS-C',
            'rome_iv_confidence': 0.78,
            'endometriosis': False,
            'baseline_symptom_severity': 6,
            'followup_symptom_severity': [4, 3, 2],
            'treatment_satisfaction': 8
        }
    ]
    
    # 测试数据加载
    handler.load_manual_entry(sample_patients)
    
    # 数据质量验证
    quality_report = handler.validate_data_quality()
    print("\n📊 数据质量报告:")
    print(f"总患者数: {quality_report['total_patients']}")
    print(f"数据完整性: {quality_report['data_completeness']}")
    
    # 生成统计摘要
    stats = handler.generate_summary_statistics()
    print(f"\n📈 描述性统计:")
    print(f"平均年龄: {stats['demographics']['age_mean']:.1f}岁")
    print(f"性别分布: {stats['demographics']['gender_counts']}")
    
    # 导出数据
    handler.export_for_analysis('test_export.json')
    
    print("\n✅ 真实患者数据处理器测试完成!")
    print("📋 请使用生成的模板录入您的23位患者数据") 