
import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Shield, ArrowLeft, Download, FileText, RotateCcw, Clock, AlertTriangle } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface Vulnerability {
  id: string;
  tool: 'sqlmap' | 'nmap' | 'nikto';
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  suggestedFix: string;
}

interface ScanResult {
  id: string;
  url: string;
  status: 'completed' | 'running' | 'failed';
  startTime: string;
  endTime?: string;
  totalVulnerabilities: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
  vulnerabilities: Vulnerability[];
}

const ScanResults = () => {
  const { scanId } = useParams();
  const navigate = useNavigate();
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('auth_token') || localStorage.getItem('guest_token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Mock API call to fetch scan results
    setTimeout(() => {
      const mockVulnerabilities: Vulnerability[] = [
        {
          id: '1',
          tool: 'sqlmap',
          type: 'SQL Injection',
          severity: 'critical',
          description: 'SQL injection vulnerability found in login form parameter "username"',
          suggestedFix: 'Use parameterized queries or prepared statements to prevent SQL injection attacks'
        },
        {
          id: '2',
          tool: 'nikto',
          type: 'Cross-Site Scripting (XSS)',
          severity: 'high',
          description: 'Reflected XSS vulnerability in search parameter',
          suggestedFix: 'Implement proper input validation and output encoding for all user inputs'
        },
        {
          id: '3',
          tool: 'nmap',
          type: 'Open Port',
          severity: 'medium',
          description: 'Unnecessary port 23 (Telnet) found open',
          suggestedFix: 'Close unused ports and disable unnecessary services'
        },
        {
          id: '4',
          tool: 'nikto',
          type: 'Information Disclosure',
          severity: 'low',
          description: 'Server version information exposed in HTTP headers',
          suggestedFix: 'Configure server to hide version information in response headers'
        }
      ];

      const mockResult: ScanResult = {
        id: scanId || '1',
        url: 'https://example.com',
        status: 'completed',
        startTime: '2024-01-15T10:30:00Z',
        endTime: '2024-01-15T10:35:00Z',
        totalVulnerabilities: mockVulnerabilities.length,
        riskLevel: 'critical',
        vulnerabilities: mockVulnerabilities
      };

      setScanResult(mockResult);
      setLoading(false);
    }, 1000);
  }, [scanId, navigate]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getToolIcon = (tool: string) => {
    const iconClass = "h-4 w-4";
    switch (tool) {
      case 'sqlmap': return <div className={`${iconClass} bg-blue-500 rounded`}></div>;
      case 'nmap': return <div className={`${iconClass} bg-green-500 rounded`}></div>;
      case 'nikto': return <div className={`${iconClass} bg-purple-500 rounded`}></div>;
      default: return <div className={`${iconClass} bg-gray-500 rounded`}></div>;
    }
  };

  const handleGenerateReport = () => {
    toast({
      title: "Generating report",
      description: "Your PDF report is being generated...",
    });
    // Mock report generation
    setTimeout(() => {
      toast({
        title: "Report ready",
        description: "Your PDF report has been downloaded.",
      });
    }, 2000);
  };

  const handleRescan = () => {
    toast({
      title: "Rescan initiated",
      description: "Starting a new scan for this URL...",
    });
    navigate('/dashboard');
  };

  const calculateDuration = () => {
    if (!scanResult?.startTime || !scanResult?.endTime) return 'N/A';
    const start = new Date(scanResult.startTime);
    const end = new Date(scanResult.endTime);
    const duration = Math.round((end.getTime() - start.getTime()) / 1000);
    return `${duration}s`;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!scanResult) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Scan not found</h1>
          <Button onClick={() => navigate('/dashboard')} className="bg-blue-600 hover:bg-blue-700">
            Back to Dashboard
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <Button
                onClick={() => navigate('/dashboard')}
                variant="ghost"
                size="sm"
                className="text-gray-300 hover:text-white"
              >
                <ArrowLeft className="h-4 w-4 mr-2" />
                Back
              </Button>
              <div className="bg-blue-600 p-2 rounded-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Scan Results</h1>
                <p className="text-sm text-gray-400">{scanResult.url}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-3">
              <Button
                onClick={handleRescan}
                variant="outline"
                className="border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                <RotateCcw className="h-4 w-4 mr-2" />
                Rescan
              </Button>
              <Button
                onClick={handleGenerateReport}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <FileText className="h-4 w-4 mr-2" />
                Generate Report
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Vulnerabilities</p>
                  <p className="text-3xl font-bold text-white">{scanResult.totalVulnerabilities}</p>
                </div>
                <AlertTriangle className="h-8 w-8 text-red-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Risk Level</p>
                  <Badge className={`${getSeverityColor(scanResult.riskLevel)} text-white mt-2`}>
                    {scanResult.riskLevel.toUpperCase()}
                  </Badge>
                </div>
                <div className={`h-8 w-8 rounded-full ${getSeverityColor(scanResult.riskLevel)}`}></div>
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Scan Duration</p>
                  <p className="text-2xl font-bold text-white">{calculateDuration()}</p>
                </div>
                <Clock className="h-8 w-8 text-blue-500" />
              </div>
            </CardContent>
          </Card>

          <Card className="bg-gray-800 border-gray-700">
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Status</p>
                  <p className="text-xl font-bold text-green-400 capitalize">{scanResult.status}</p>
                </div>
                <div className="h-8 w-8 rounded-full bg-green-500"></div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Vulnerabilities Table */}
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-white">Detected Vulnerabilities</CardTitle>
            <CardDescription className="text-gray-400">
              Detailed analysis of security issues found during the scan
            </CardDescription>
          </CardHeader>
          <CardContent>
            {scanResult.vulnerabilities.length === 0 ? (
              <div className="text-center py-8">
                <div className="bg-green-900/20 border border-green-800 rounded-lg p-6">
                  <div className="text-green-400 text-lg font-semibold mb-2">
                    🎉 No vulnerabilities found!
                  </div>
                  <p className="text-gray-400">
                    Your website appears to be secure based on our scan.
                  </p>
                </div>
              </div>
            ) : (
              <Table>
                <TableHeader>
                  <TableRow className="border-gray-700">
                    <TableHead className="text-gray-300">Tool</TableHead>
                    <TableHead className="text-gray-300">Type</TableHead>
                    <TableHead className="text-gray-300">Severity</TableHead>
                    <TableHead className="text-gray-300">Description</TableHead>
                    <TableHead className="text-gray-300">Suggested Fix</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {scanResult.vulnerabilities.map((vuln) => (
                    <TableRow key={vuln.id} className="border-gray-700">
                      <TableCell>
                        <div className="flex items-center space-x-2">
                          {getToolIcon(vuln.tool)}
                          <span className="text-gray-300 font-mono text-sm">{vuln.tool}</span>
                        </div>
                      </TableCell>
                      <TableCell className="text-gray-300 font-medium">{vuln.type}</TableCell>
                      <TableCell>
                        <Badge className={`${getSeverityColor(vuln.severity)} text-white`}>
                          {vuln.severity.toUpperCase()}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-gray-300 max-w-md">
                        {vuln.description}
                      </TableCell>
                      <TableCell className="text-gray-300 max-w-md">
                        {vuln.suggestedFix}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            )}
          </CardContent>
        </Card>

        {/* Action Buttons */}
        <div className="mt-8 flex justify-center space-x-4">
          <Button
            onClick={handleGenerateReport}
            className="bg-green-600 hover:bg-green-700"
          >
            <Download className="h-4 w-4 mr-2" />
            Download Raw Data (JSON)
          </Button>
        </div>
      </div>
    </div>
  );
};

export default ScanResults;
