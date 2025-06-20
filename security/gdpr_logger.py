"""
GDPR Logger - Privacy Compliance Audit and Logging System
Handles audit logs, consent tracking, and GDPR/HIPAA compliance monitoring
"""

import logging
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib

class DataProcessingPurpose(Enum):
    MEDICAL_DIAGNOSIS = "medical_diagnosis"
    TREATMENT_RECOMMENDATION = "treatment_recommendation"
    RESEARCH_ANALYTICS = "research_analytics"
    SYSTEM_IMPROVEMENT = "system_improvement"
    LEGAL_COMPLIANCE = "legal_compliance"

class ConsentStatus(Enum):
    GRANTED = "granted"
    WITHDRAWN = "withdrawn"
    PENDING = "pending"
    EXPIRED = "expired"

@dataclass
class AuditLogEntry:
    """Audit log entry for GDPR compliance"""
    timestamp: str
    user_id: str
    patient_id: str
    action: str
    data_type: str
    purpose: str
    legal_basis: str
    consent_status: str
    retention_period: Optional[int] = None
    encryption_status: bool = False
    anonymization_status: bool = False
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    session_id: Optional[str] = None

@dataclass
class ConsentRecord:
    """Patient consent record"""
    patient_id: str
    consent_id: str
    purpose: str
    status: str
    granted_date: Optional[str] = None
    withdrawn_date: Optional[str] = None
    expiry_date: Optional[str] = None
    consent_text: Optional[str] = None
    version: str = "1.0"

class GDPRLogger:
    """
    GDPR compliance logger and audit system
    Handles consent management, audit logging, and compliance monitoring
    """
    
    def __init__(self, db_path: str = "gdpr_audit.db", retention_days: int = 2555):  # 7 years default
        self.db_path = db_path
        self.retention_days = retention_days
        
        # Initialize database
        self._init_database()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
        # Create audit log handler
        self._setup_audit_logging()
    
    def _init_database(self):
        """Initialize SQLite database for audit logs and consent records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create audit logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_id TEXT NOT NULL,
                patient_id TEXT NOT NULL,
                action TEXT NOT NULL,
                data_type TEXT NOT NULL,
                purpose TEXT NOT NULL,
                legal_basis TEXT NOT NULL,
                consent_status TEXT NOT NULL,
                retention_period INTEGER,
                encryption_status BOOLEAN,
                anonymization_status BOOLEAN,
                ip_address TEXT,
                user_agent TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create consent records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS consent_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id TEXT NOT NULL,
                consent_id TEXT UNIQUE NOT NULL,
                purpose TEXT NOT NULL,
                status TEXT NOT NULL,
                granted_date TEXT,
                withdrawn_date TEXT,
                expiry_date TEXT,
                consent_text TEXT,
                version TEXT DEFAULT '1.0',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indices
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_patient ON audit_logs(patient_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_logs(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_consent_patient ON consent_records(patient_id)')
        
        conn.commit()
        conn.close()
    
    def _setup_audit_logging(self):
        """Setup file-based audit logging"""
        audit_logger = logging.getLogger('gdpr_audit')
        audit_logger.setLevel(logging.INFO)
        
        # Create logs directory
        os.makedirs('logs', exist_ok=True)
        
        # File handler for audit logs
        audit_handler = logging.FileHandler('logs/gdpr_audit.log')
        audit_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        audit_handler.setFormatter(audit_formatter)
        audit_logger.addHandler(audit_handler)
        
        self.audit_logger = audit_logger
    
    def log_data_access(self, 
                       user_id: str,
                       patient_id: str,
                       action: str,
                       data_type: str,
                       purpose: DataProcessingPurpose,
                       legal_basis: str = "legitimate_interest",
                       **kwargs) -> str:
        """
        Log data access event for audit trail
        
        Args:
            user_id: User performing the action
            patient_id: Patient whose data is being accessed
            action: Type of action (read, write, delete, etc.)
            data_type: Type of data being accessed
            purpose: Purpose of data processing
            legal_basis: Legal basis for processing
            **kwargs: Additional context information
            
        Returns:
            audit_id: Unique audit entry identifier
        """
        # Create audit log entry
        audit_entry = AuditLogEntry(
            timestamp=datetime.now().isoformat(),
            user_id=user_id,
            patient_id=patient_id,
            action=action,
            data_type=data_type,
            purpose=purpose.value,
            legal_basis=legal_basis,
            consent_status="granted",
            **kwargs
        )
        
        # Store in database
        audit_id = self._store_audit_log(audit_entry)
        
        # Log to file
        self.audit_logger.info(f"Data access logged: {audit_id} - {user_id} accessed {data_type} for {patient_id}")
        
        return audit_id
    
    def _store_audit_log(self, audit_entry: AuditLogEntry) -> str:
        """Store audit log entry in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO audit_logs (
                timestamp, user_id, patient_id, action, data_type, purpose,
                legal_basis, consent_status, retention_period, encryption_status,
                anonymization_status, ip_address, user_agent, session_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            audit_entry.timestamp,
            audit_entry.user_id,
            audit_entry.patient_id,
            audit_entry.action,
            audit_entry.data_type,
            audit_entry.purpose,
            audit_entry.legal_basis,
            audit_entry.consent_status,
            audit_entry.retention_period,
            audit_entry.encryption_status,
            audit_entry.anonymization_status,
            audit_entry.ip_address,
            audit_entry.user_agent,
            audit_entry.session_id
        ))
        
        audit_id = f"AUDIT_{cursor.lastrowid:08d}"
        conn.commit()
        conn.close()
        
        return audit_id
    
    def record_consent(self, 
                      patient_id: str,
                      purpose: DataProcessingPurpose,
                      status: ConsentStatus,
                      consent_text: Optional[str] = None,
                      expiry_days: Optional[int] = None) -> str:
        """
        Record patient consent for data processing
        
        Args:
            patient_id: Patient identifier
            purpose: Purpose of data processing
            status: Consent status
            consent_text: Text of consent agreement
            expiry_days: Days until consent expires
            
        Returns:
            consent_id: Unique consent record identifier
        """
        # Generate consent ID
        consent_id = f"CONSENT_{hashlib.md5(f'{patient_id}_{purpose.value}_{datetime.now()}'.encode()).hexdigest()[:8]}"
        
        # Calculate expiry date
        expiry_date = None
        if expiry_days:
            expiry_date = (datetime.now() + timedelta(days=expiry_days)).isoformat()
        
        # Create consent record
        consent_record = ConsentRecord(
            patient_id=patient_id,
            consent_id=consent_id,
            purpose=purpose.value,
            status=status.value,
            granted_date=datetime.now().isoformat() if status == ConsentStatus.GRANTED else None,
            withdrawn_date=datetime.now().isoformat() if status == ConsentStatus.WITHDRAWN else None,
            expiry_date=expiry_date,
            consent_text=consent_text
        )
        
        # Store in database
        self._store_consent_record(consent_record)
        
        # Log the consent action
        self.audit_logger.info(f"Consent recorded: {consent_id} - {patient_id} {status.value} for {purpose.value}")
        
        return consent_id
    
    def _store_consent_record(self, consent_record: ConsentRecord):
        """Store consent record in database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO consent_records (
                patient_id, consent_id, purpose, status, granted_date,
                withdrawn_date, expiry_date, consent_text, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            consent_record.patient_id,
            consent_record.consent_id,
            consent_record.purpose,
            consent_record.status,
            consent_record.granted_date,
            consent_record.withdrawn_date,
            consent_record.expiry_date,
            consent_record.consent_text,
            consent_record.version
        ))
        
        conn.commit()
        conn.close()
    
    def _check_consent_status(self, patient_id: str, purpose: str) -> ConsentStatus:
        """Check current consent status for patient and purpose"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT status, expiry_date FROM consent_records
            WHERE patient_id = ? AND purpose = ?
            ORDER BY created_at DESC LIMIT 1
        ''', (patient_id, purpose))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return ConsentStatus.PENDING
        
        status, expiry_date = result
        
        # Check if consent has expired
        if expiry_date and datetime.fromisoformat(expiry_date) < datetime.now():
            return ConsentStatus.EXPIRED
        
        return ConsentStatus(status)
    
    def generate_compliance_report(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """
        Generate GDPR compliance report for specified date range
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            compliance_report: Comprehensive compliance report
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get audit statistics
        cursor.execute('''
            SELECT 
                COUNT(*) as total_accesses,
                COUNT(DISTINCT patient_id) as unique_patients,
                COUNT(DISTINCT user_id) as unique_users,
                purpose,
                legal_basis
            FROM audit_logs
            WHERE timestamp BETWEEN ? AND ?
            GROUP BY purpose, legal_basis
        ''', (start_date, end_date))
        
        audit_stats = cursor.fetchall()
        
        # Get consent statistics
        cursor.execute('''
            SELECT 
                status,
                COUNT(*) as count
            FROM consent_records
            WHERE created_at BETWEEN ? AND ?
            GROUP BY status
        ''', (start_date, end_date))
        
        consent_stats = cursor.fetchall()
        
        conn.close()
        
        # Compile report
        report = {
            'report_period': {
                'start_date': start_date,
                'end_date': end_date
            },
            'audit_statistics': {
                'total_data_accesses': sum(stat[0] for stat in audit_stats),
                'unique_patients_accessed': len(set(stat[1] for stat in audit_stats)),
                'unique_users': len(set(stat[2] for stat in audit_stats)),
                'by_purpose': {}
            },
            'consent_statistics': {
                'total_consents': sum(stat[1] for stat in consent_stats),
                'by_status': dict(consent_stats)
            },
            'compliance_score': self._calculate_compliance_score(audit_stats, consent_stats),
            'recommendations': self._generate_compliance_recommendations(audit_stats, consent_stats)
        }
        
        return report
    
    def _calculate_compliance_score(self, audit_stats: List, consent_stats: List) -> float:
        """Calculate overall compliance score (0-100)"""
        # Simple scoring algorithm
        score = 100.0
        
        # Deduct points for missing consents
        total_consents = sum(stat[1] for stat in consent_stats)
        if total_consents == 0:
            score -= 50
        
        # Deduct points for expired or withdrawn consents
        withdrawn_consents = sum(stat[1] for stat in consent_stats if stat[0] == 'withdrawn')
        if withdrawn_consents > 0:
            score -= min(20, withdrawn_consents * 2)
        
        return max(0, score)
    
    def _generate_compliance_recommendations(self, audit_stats: List, consent_stats: List) -> List[str]:
        """Generate compliance recommendations"""
        recommendations = []
        
        total_consents = sum(stat[1] for stat in consent_stats)
        if total_consents == 0:
            recommendations.append("Implement patient consent collection process")
        
        withdrawn_consents = sum(stat[1] for stat in consent_stats if stat[0] == 'withdrawn')
        if withdrawn_consents > 0:
            recommendations.append("Review and address withdrawn consents")
        
        if not audit_stats:
            recommendations.append("Ensure all data access events are properly logged")
        
        return recommendations

if __name__ == "__main__":
    # Test the GDPR logger
    gdpr_logger = GDPRLogger()
    
    print("🔐 GDPR Logger Test")
    
    # Test consent recording
    consent_id = gdpr_logger.record_consent(
        patient_id="PATIENT_001",
        purpose=DataProcessingPurpose.MEDICAL_DIAGNOSIS,
        status=ConsentStatus.GRANTED,
        consent_text="I consent to the processing of my medical data for diagnosis purposes.",
        expiry_days=365
    )
    print(f"Consent recorded: {consent_id}")
    
    # Test data access logging
    audit_id = gdpr_logger.log_data_access(
        user_id="DOC_001",
        patient_id="PATIENT_001",
        action="read",
        data_type="medical_questionnaire",
        purpose=DataProcessingPurpose.MEDICAL_DIAGNOSIS,
        encryption_status=True,
        anonymization_status=False
    )
    print(f"Data access logged: {audit_id}")
    
    # Test compliance report
    report = gdpr_logger.generate_compliance_report(
        start_date="2024-01-01",
        end_date="2024-12-31"
    )
    print(f"Compliance report generated: Score {report['compliance_score']}/100") 