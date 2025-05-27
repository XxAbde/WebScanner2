from flask import request, jsonify
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

from ..models.scan import Scan
from ..models.user import User
from ..extensions import db
from ..tasks.scan_tasks import run_vulnerability_scan

# Create a namespace for scan-related operations
scans_ns = Namespace('scans', description='Operations related to scans')

# API Models
scan_request = scans_ns.model('ScanRequest', {
    'target_url': fields.String(required=True, description='Target URL to scan'),
    'scan_type': fields.String(description='Type of scan (full, quick, custom)', default='full')
})

scan_response = scans_ns.model('ScanResponse', {
    'id': fields.Integer(description='Scan ID'),
    'target_url': fields.String(description='Target URL'),
    'status': fields.String(description='Scan status'),
    'progress': fields.Integer(description='Scan progress (0-100)'),
    'started_at': fields.DateTime(description='Scan start time'),
    'total_vulnerabilities': fields.Integer(description='Total vulnerabilities found')
})

@scans_ns.route('/')
class ScanList(Resource):
    @jwt_required()
    @scans_ns.marshal_list_with(scan_response)
    def get(self):
        """Get list of user's scans"""
        current_user_id = get_jwt_identity()
        scans = Scan.query.filter_by(user_id=current_user_id).order_by(Scan.started_at.desc()).all()
        return [scan.to_dict() for scan in scans]

    @jwt_required()
    @scans_ns.expect(scan_request)
    @scans_ns.marshal_with(scan_response)
    def post(self):
        """Create and start a new scan"""
        current_user_id = get_jwt_identity()
        data = request.get_json()
        
        if not data or not data.get('target_url'):
            return {'error': 'target_url is required'}, 400
        
        # Check user scan limits
        user = User.query.get(current_user_id)
        if user.is_guest and user.scan_limit <= 0:
            return {'error': 'Scan limit exceeded for guest users'}, 403
        
        # Create new scan
        scan = Scan(
            user_id=current_user_id,
            target_url=data['target_url'],
            scan_type=data.get('scan_type', 'full'),
            status='pending'
        )
        
        db.session.add(scan)
        db.session.commit()
        
        # Decrease scan limit for guest users
        if user.is_guest:
            user.scan_limit -= 1
            db.session.commit()
        
        # Start background scan task
        run_vulnerability_scan.delay(scan.id)
        
        return scan.to_dict(), 201

@scans_ns.route('/<int:scan_id>')
class ScanDetail(Resource):
    @jwt_required()
    @scans_ns.marshal_with(scan_response)
    def get(self, scan_id):
        """Get details of a specific scan"""
        current_user_id = get_jwt_identity()
        scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
        
        if not scan:
            return {'error': 'Scan not found'}, 404
        
        return scan.to_dict()

    @jwt_required()
    def delete(self, scan_id):
        """Delete a specific scan"""
        current_user_id = get_jwt_identity()
        scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
        
        if not scan:
            return {'error': 'Scan not found'}, 404
        
        # Don't allow deletion of running scans
        if scan.status == 'running':
            return {'error': 'Cannot delete running scan'}, 400
        
        db.session.delete(scan)
        db.session.commit()
        
        return {'message': 'Scan deleted successfully'}, 200

@scans_ns.route('/<int:scan_id>/results')
class ScanResults(Resource):
    @jwt_required()
    def get(self, scan_id):
        """Get scan results"""
        current_user_id = get_jwt_identity()
        scan = Scan.query.filter_by(id=scan_id, user_id=current_user_id).first()
        
        if not scan:
            return {'error': 'Scan not found'}, 404
        
        from ..models.scan_result import ScanResult
        results = ScanResult.query.filter_by(scan_id=scan_id).all()
        
        return {
            'scan': scan.to_dict(),
            'results': [result.to_dict() for result in results]
        }