import os
import logging
from celery import current_app
from datetime import datetime

from ..services.scanner_service import ScannerService
from ..models.scan import Scan
from ..extensions import db

logger = logging.getLogger(__name__)

@current_app.task(bind=True)
def run_vulnerability_scan(self, scan_id):
    """Celery task to run vulnerability scan in background"""
    
    try:
        # Update scan status to running
        scan = Scan.query.get(scan_id)
        if not scan:
            logger.error(f"Scan {scan_id} not found")
            return {'success': False, 'error': 'Scan not found'}
        
        scan.status = 'running'
        scan.started_at = datetime.utcnow()
        scan.progress = 10
        db.session.commit()
        
        logger.info(f"Starting vulnerability scan for {scan.target_url}")
        
        # Initialize scanner service
        scanner = ScannerService()
        
        # Update progress
        scan.progress = 25
        db.session.commit()
        
        # Run all scans
        results = scanner.run_all_scans(scan_id, scan.target_url)
        
        # Update progress
        scan.progress = 80
        db.session.commit()
        
        # Process results and update scan
        total_vulnerabilities = sum(
            result.get('vulnerabilities_found', 0) 
            for result in results.values() 
            if result.get('success', False)
        )
        
        # Count vulnerabilities by severity (this would be done by AI analysis later)
        scan.total_vulnerabilities = total_vulnerabilities
        scan.progress = 100
        scan.status = 'completed'
        scan.completed_at = datetime.utcnow()
        
        db.session.commit()
        
        logger.info(f"Scan {scan_id} completed successfully")
        
        return {
            'success': True,
            'scan_id': scan_id,
            'results': results,
            'total_vulnerabilities': total_vulnerabilities
        }
        
    except Exception as e:
        logger.error(f"Scan {scan_id} failed: {str(e)}")
        
        # Update scan status to failed
        try:
            scan = Scan.query.get(scan_id)
            if scan:
                scan.status = 'failed'
                scan.error_message = str(e)
                scan.completed_at = datetime.utcnow()
                db.session.commit()
        except:
            pass
        
        return {
            'success': False,
            'scan_id': scan_id,
            'error': str(e)
        }

@current_app.task(bind=True)
def process_scan_results_with_ai(self, scan_id):
    """Process scan results with AI analysis"""
    
    try:
        from ..services.ai_service import AIService
        
        scan_results = ScanResult.query.filter_by(scan_id=scan_id).all()
        ai_service = AIService()
        
        for result in scan_results:
            if not result.ai_analysis:
                analysis = ai_service.analyze_scan_result(result.raw_data, result.tool_name)
                result.set_ai_analysis(analysis)
        
        logger.info(f"AI analysis completed for scan {scan_id}")
        
        return {'success': True, 'scan_id': scan_id}
        
    except Exception as e:
        logger.error(f"AI analysis failed for scan {scan_id}: {str(e)}")
        return {'success': False, 'error': str(e)}