from datetime import datetime
from ..extensions import db

class ScanResult(db.Model):
    __tablename__ = 'scan_results'
    
    id = db.Column(db.Integer, primary_key=True)
    scan_id = db.Column(db.Integer, db.ForeignKey('scans.id'), nullable=False)
    tool_name = db.Column(db.String(50), nullable=False)  # nmap, sqlmap, nikto
    tool_version = db.Column(db.String(50))
    raw_data = db.Column(db.JSON, nullable=False)  # Raw tool output
    ai_analysis = db.Column(db.JSON)  # Processed AI insights
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    processing_time = db.Column(db.Float)  # Time taken to process in seconds
    
    def __init__(self, scan_id, tool_name, raw_data, tool_version=None, processing_time=None):
        self.scan_id = scan_id
        self.tool_name = tool_name
        self.raw_data = raw_data
        self.tool_version = tool_version
        self.processing_time = processing_time
    
    def set_ai_analysis(self, analysis):
        """Set AI analysis results"""
        self.ai_analysis = analysis
        db.session.commit()
    
    def get_severity(self):
        """Get vulnerability severity from AI analysis"""
        if self.ai_analysis and 'severity' in self.ai_analysis:
            return self.ai_analysis['severity']
        return 'unknown'
    
    def get_vulnerability_type(self):
        """Get vulnerability type from AI analysis"""
        if self.ai_analysis and 'vulnerability' in self.ai_analysis:
            return self.ai_analysis['vulnerability']
        return 'unknown'
    
    def has_vulnerabilities(self):
        """Check if this result contains vulnerabilities"""
        if not self.ai_analysis:
            return False
        return self.ai_analysis.get('has_vulnerabilities', False)
    
    def to_dict(self):
        """Convert result to dictionary"""
        return {
            'id': self.id,
            'scan_id': self.scan_id,
            'tool_name': self.tool_name,
            'tool_version': self.tool_version,
            'created_at': self.created_at.isoformat(),
            'processing_time': self.processing_time,
            'severity': self.get_severity(),
            'vulnerability_type': self.get_vulnerability_type(),
            'has_vulnerabilities': self.has_vulnerabilities(),
            'raw_data': self.raw_data,
            'ai_analysis': self.ai_analysis
        }
    
    def __repr__(self):
        return f'<ScanResult {self.id}: {self.tool_name}>'