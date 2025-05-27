import subprocess
import json
import os
import logging
import tempfile
from datetime import datetime
from typing import Dict, Any, Optional
from urllib.parse import urlparse

from ..models.scan_result import ScanResult
from ..extensions import db

logger = logging.getLogger(__name__)

class ScannerService:
    """Service to handle vulnerability scanning with multiple tools"""
    
    def __init__(self):
        self.tools = {
            'sqlmap': self._run_sqlmap,
            'nmap': self._run_nmap,
            'nikto': self._run_nikto
        }
    
    def run_all_scans(self, scan_id: int, target_url: str) -> Dict[str, Any]:
        """Run all scanning tools for a given target URL"""
        results = {}
        
        logger.info(f"Starting comprehensive scan for {target_url} (scan_id: {scan_id})")
        
        for tool_name, tool_func in self.tools.items():
            try:
                logger.info(f"Running {tool_name} scan...")
                start_time = datetime.utcnow()
                
                result = tool_func(target_url)
                
                end_time = datetime.utcnow()
                processing_time = (end_time - start_time).total_seconds()
                
                # Store result in database
                scan_result = ScanResult(
                    scan_id=scan_id,
                    tool_name=tool_name,
                    raw_data=result,
                    processing_time=processing_time
                )
                
                db.session.add(scan_result)
                db.session.commit()
                
                results[tool_name] = {
                    'success': True,
                    'result_id': scan_result.id,
                    'processing_time': processing_time,
                    'vulnerabilities_found': self._count_vulnerabilities(tool_name, result)
                }
                
                logger.info(f"{tool_name} scan completed in {processing_time:.2f}s")
                
            except Exception as e:
                logger.error(f"Error running {tool_name}: {str(e)}")
                results[tool_name] = {
                    'success': False,
                    'error': str(e),
                    'processing_time': 0
                }
        
        return results
    
    def _run_sqlmap(self, target_url: str) -> Dict[str, Any]:
        """Run SQLMap scan"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = os.path.join(temp_dir, 'sqlmap_results')
            
            cmd = [
                'sqlmap',
                '-u', target_url,
                '--batch',
                '--level=2',
                '--risk=1',
                f'--output-dir={output_dir}',
                '--format=json'
            ]
            
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minutes timeout
                    check=False
                )
                
                # Parse SQLMap output
                output_data = {
                    'command': ' '.join(cmd),
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'return_code': result.returncode,
                    'vulnerabilities': self._parse_sqlmap_output(result.stdout)
                }
                
                return output_data
                
            except subprocess.TimeoutExpired:
                return {
                    'command': ' '.join(cmd),
                    'error': 'SQLMap scan timed out after 5 minutes',
                    'return_code': -1
                }
            except FileNotFoundError:
                return {
                    'command': ' '.join(cmd),
                    'error': 'SQLMap not found. Please install sqlmap.',
                    'return_code': -1
                }
    
    def _run_nmap(self, target_url: str) -> Dict[str, Any]:
        """Run Nmap scan"""
        # Extract domain from URL
        parsed_url = urlparse(target_url)
        target_host = parsed_url.netloc or parsed_url.path
        
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.xml', delete=False) as temp_file:
            output_file = temp_file.name
        
        try:
            cmd = [
                'nmap',
                '-T4',
                '-F',
                '-Pn',
                target_host,
                '-oX', output_file
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minutes timeout
                check=False
            )
            
            # Read XML output
            xml_content = ""
            try:
                with open(output_file, 'r') as f:
                    xml_content = f.read()
            except:
                pass
            finally:
                # Cleanup temp file
                try:
                    os.unlink(output_file)
                except:
                    pass
            
            output_data = {
                'command': ' '.join(cmd),
                'target': target_host,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'xml_output': xml_content,
                'parsed_results': self._parse_nmap_output(xml_content)
            }
            
            return output_data
            
        except subprocess.TimeoutExpired:
            return {
                'command': ' '.join(cmd),
                'error': 'Nmap scan timed out after 5 minutes',
                'return_code': -1
            }
        except FileNotFoundError:
            return {
                'command': ' '.join(cmd),
                'error': 'Nmap not found. Please install nmap.',
                'return_code': -1
            }
    
    def _run_nikto(self, target_url: str) -> Dict[str, Any]:
        """Run Nikto scan"""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as temp_file:
            output_file = temp_file.name
        
        try:
            cmd = [
                'nikto',
                '-h', target_url,
                '-Tuning', 'x',
                '2',
                '-o', output_file,
                '-Format', 'json'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=600,  # 10 minutes timeout for Nikto
                check=False
            )
            
            # Read JSON output
            json_content = ""
            try:
                with open(output_file, 'r') as f:
                    json_content = f.read()
            except:
                pass
            finally:
                # Cleanup temp file
                try:
                    os.unlink(output_file)
                except:
                    pass
            
            output_data = {
                'command': ' '.join(cmd),
                'stdout': result.stdout,
                'stderr': result.stderr,
                'return_code': result.returncode,
                'json_output': json_content,
                'parsed_results': self._parse_nikto_output(json_content)
            }
            
            return output_data
            
        except subprocess.TimeoutExpired:
            return {
                'command': ' '.join(cmd),
                'error': 'Nikto scan timed out after 10 minutes',
                'return_code': -1
            }
        except FileNotFoundError:
            return {
                'command': ' '.join(cmd),
                'error': 'Nikto not found. Please install nikto.',
                'return_code': -1
            }
    
    def _parse_sqlmap_output(self, stdout: str) -> Dict[str, Any]:
        """Parse SQLMap output for vulnerabilities"""
        vulnerabilities = []
        
        # Look for common SQLMap vulnerability indicators
        if 'vulnerable' in stdout.lower():
            lines = stdout.split('\n')
            for line in lines:
                if 'vulnerable' in line.lower() or 'injection' in line.lower():
                    vulnerabilities.append({
                        'type': 'SQL Injection',
                        'description': line.strip(),
                        'severity': 'high'
                    })
        
        return {
            'vulnerabilities': vulnerabilities,
            'total_found': len(vulnerabilities)
        }
    
    def _parse_nmap_output(self, xml_content: str) -> Dict[str, Any]:
        """Parse Nmap XML output for open ports"""
        import xml.etree.ElementTree as ET
        
        ports = []
        services = []
        
        try:
            if xml_content:
                root = ET.fromstring(xml_content)
                
                for host in root.findall('host'):
                    for ports_elem in host.findall('ports'):
                        for port in ports_elem.findall('port'):
                            port_id = port.get('portid')
                            protocol = port.get('protocol')
                            
                            state_elem = port.find('state')
                            state = state_elem.get('state') if state_elem is not None else 'unknown'
                            
                            service_elem = port.find('service')
                            service_name = service_elem.get('name') if service_elem is not None else 'unknown'
                            
                            if state == 'open':
                                ports.append({
                                    'port': int(port_id),
                                    'protocol': protocol,
                                    'state': state,
                                    'service': service_name
                                })
                                
                                services.append(service_name)
        
        except ET.ParseError:
            pass
        
        return {
            'open_ports': ports,
            'services': list(set(services)),
            'total_ports': len(ports)
        }
    
    def _parse_nikto_output(self, json_content: str) -> Dict[str, Any]:
        """Parse Nikto JSON output for vulnerabilities"""
        vulnerabilities = []
        
        try:
            if json_content:
                data = json.loads(json_content)
                
                # Nikto JSON structure may vary, adapt as needed
                if isinstance(data, dict) and 'vulnerabilities' in data:
                    for vuln in data['vulnerabilities']:
                        vulnerabilities.append({
                            'type': vuln.get('type', 'Web Vulnerability'),
                            'description': vuln.get('description', ''),
                            'severity': vuln.get('severity', 'medium'),
                            'url': vuln.get('url', '')
                        })
                
        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract from text
            if 'ERROR' in json_content or 'OSVDB' in json_content:
                vulnerabilities.append({
                    'type': 'Web Vulnerability',
                    'description': 'Nikto found potential issues',
                    'severity': 'medium'
                })
        
        return {
            'vulnerabilities': vulnerabilities,
            'total_found': len(vulnerabilities)
        }
    
    def _count_vulnerabilities(self, tool_name: str, result: Dict[str, Any]) -> int:
        """Count vulnerabilities found by a tool"""
        if tool_name == 'sqlmap':
            return result.get('vulnerabilities', {}).get('total_found', 0)
        elif tool_name == 'nmap':
            return result.get('parsed_results', {}).get('total_ports', 0)
        elif tool_name == 'nikto':
            return result.get('parsed_results', {}).get('total_found', 0)
        
        return 0