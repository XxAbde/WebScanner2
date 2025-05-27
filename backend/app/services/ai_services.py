import json
import logging
from typing import Dict, Any
import openai
from flask import current_app

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI analysis of scan results"""
    
    def __init__(self):
        openai.api_key = current_app.config.get('OPENAI_API_KEY')
    
    def analyze_scan_result(self, raw_data: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """Analyze scan result using AI"""
        
        try:
            prompt = self._create_analysis_prompt(raw_data, tool_name)
            
            if not openai.api_key:
                # Fallback analysis without AI
                return self._fallback_analysis(raw_data, tool_name)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert analyzing vulnerability scan results."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            analysis_text = response.choices[0].message.content
            return self._parse_ai_response(analysis_text, tool_name)
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return self._fallback_analysis(raw_data, tool_name)
    
    def _create_analysis_prompt(self, raw_data: Dict[str, Any], tool_name: str) -> str:
        """Create prompt for AI analysis"""
        
        data_summary = json.dumps(raw_data, indent=2)[:1000]  # Limit size
        
        prompt = f"""
        Analyze the following {tool_name} scan results and provide a security assessment:

        Scan Data:
        {data_summary}

        Please provide:
        1. Whether vulnerabilities were found (true/false)
        2. Primary vulnerability type
        3. Severity level (low, medium, high, critical)
        4. Brief description of findings
        5. Recommended remediation steps

        Format your response as JSON with keys: has_vulnerabilities, vulnerability, severity, description, solution
        """
        
        return prompt
    
    def _parse_ai_response(self, response_text: str, tool_name: str) -> Dict[str, Any]:
        """Parse AI response into structured format"""
        
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
        except:
            pass
        
        # Fallback parsing
        return {
            'has_vulnerabilities': 'vulnerability' in response_text.lower() or 'risk' in response_text.lower(),
            'vulnerability': f'{tool_name} findings',
            'severity': 'medium',
            'description': response_text[:200],
            'solution': 'Review findings and apply security best practices'
        }
    
    def _fallback_analysis(self, raw_data: Dict[str, Any], tool_name: str) -> Dict[str, Any]:
        """Provide basic analysis without AI"""
        
        has_vulns = False
        severity = 'low'
        vuln_type = 'Unknown'
        description = 'Scan completed'
        solution = 'Review results manually'
        
        if tool_name == 'sqlmap':
            if raw_data.get('vulnerabilities', {}).get('total_found', 0) > 0:
                has_vulns = True
                severity = 'high'
                vuln_type = 'SQL Injection'
                description = 'Potential SQL injection vulnerabilities detected'
                solution = 'Use parameterized queries and input validation'
        
        elif tool_name == 'nmap':
            open_ports = raw_data.get('parsed_results', {}).get('total_ports', 0)
            if open_ports > 0:
                has_vulns = True
                severity = 'medium'
                vuln_type = 'Open Ports'
                description = f'{open_ports} open ports detected'
                solution = 'Close unnecessary ports and secure services'
        
        elif tool_name == 'nikto':
            if raw_data.get('parsed_results', {}).get('total_found', 0) > 0:
                has_vulns = True
                severity = 'medium'
                vuln_type = 'Web Vulnerabilities'
                description = 'Web application vulnerabilities detected'
                solution = 'Update software and configure security headers'
        
        return {
            'has_vulnerabilities': has_vulns,
            'vulnerability': vuln_type,
            'severity': severity,
            'description': description,
            'solution': solution
        }