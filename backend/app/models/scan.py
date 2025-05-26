from datetime import datetime
from ..extensions import db

class Scan(db.Model):
    __tablename__ = 'scans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_url = db.Column(db.String(500), nullable=False)
    scan_type = db.Column(db.String(50), nullable=False, default='full')  # full, quick, custom
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, running, completed, failed
    progress = db.Column(db.Integer, default=0)  # 0-100 percentage
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    total_vulnerabilities = db.Column(db.Integer, default=0)
    high_severity_count = db.Column(db.Integer, default=0)
    medium_severity_count = db.Column(db.Integer, default=0)
    low_severity_count = db.Column(db.Integer, default=0)
    scan_config = db.Column(db.JSON)  # Store scan configuration as JSON
    error_message = db.Column(db.Text)
    
    # Relationship with user
    user = db.relationship('User', backref=db.backref('scans', lazy=True))
    
    def to_dict(self):
        """Convert scan to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'target_url': self.target_url,
            'scan_type': self.scan_type,
            'status': self.status,
            'progress': self.progress,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_vulnerabilities': self.total_vulnerabilities,
            'high_severity_count': self.high_severity_count,
            'medium_severity_count': self.medium_severity_count,
            'low_severity_count': self.low_severity_count,
            'error_message': self.error_message
        }
    
    def __repr__(self):
        return f'<Scan {self.id}: {self.target_url}>'

class ScanResult(db.Model):
    __tablename__ = 'scan_results'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    vulnerability_type = db.Column(db.String(100), nullable=False)
    severity = db.Column(db.String(20), nullable=False)  # low, medium, high, critical
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    affected_url = db.Column(db.String(500))
    evidence = db.Column(db.Text)
    recommendation = db.Column(db.Text)
    cve_id = db.Column(db.String(20))  # CVE identifier if applicable
    cvss_score = db.Column(db.Float)
    found_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with scan
    scan = db.relationship('Scan', backref=db.backref('results', lazy=True))
    
    def to_dict(self):
        """Convert scan result to dictionary"""
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'vulnerability_type': self.vulnerability_type,
            'severity': self.severity,
            'title': self.title,
            'description': self.description,
            'affected_url': self.affected_url,
            'evidence': self.evidence,
            'recommendation': self.recommendation,
            'cve_id': self.cve_id,
            'cvss_score': self.cvss_score,
            'found_at': self.found_at.isoformat()
        }
    
    def __repr__(self):
        return f'<ScanResult {self.id}: {self.vulnerability_type}>'