from flask_restx import Namespace, Resource

# Create a namespace for report-related operations
reports_ns = Namespace('reports', description='Operations related to reports')

@reports_ns.route('/')
class ReportList(Resource):
    def get(self):
        """Get a list of all reports"""
        # Replace with actual database logic
        return {'message': 'List of reports'}, 200

    def post(self):
        """Create a new report"""
        # Replace with actual report creation logic
        return {'message': 'New report created'}, 201

@reports_ns.route('/<int:report_id>')
class ReportDetail(Resource):
    def get(self, report_id):
        """Get details of a specific report by ID"""
        # Replace with actual database logic
        return {'message': f'Details of report {report_id}'}, 200

    def delete(self, report_id):
        """Delete a specific report by ID"""
        # Replace with actual database logic
        return {'message': f'Report {report_id} deleted'}, 200