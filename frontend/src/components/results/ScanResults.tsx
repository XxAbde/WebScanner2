
import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  ArrowLeft, 
  Download, 
  FileText, 
  Mail, 
  RefreshCw, 
  Shield, 
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle
} from 'lucide-react';
import { ScanResult } from '@/types';
import { toast } from '@/hooks/use-toast';

interface ScanResultsProps {
  scanId: number;
  onBack: () => void;
}

const getSeverityColor = (severity: ScanResult['severity']) => {
  switch (severity) {
    case 'low':
      return 'bg-green-600';
    case 'medium':
      return 'bg-yellow-600';
    case 'high':
      return 'bg-orange-600';
    case 'critical':
      return 'bg-red-600';
  }
};

const getSeverityIcon = (severity: ScanResult['severity']) => {
  switch (severity) {
    case 'low':
      return <Info className="h-4 w-4" />;
    case 'medium':
      return <AlertCircle className="h-4 w-4" />;
    case 'high':
      return <AlertTriangle className="h-4 w-4" />;
    case 'critical':
      return <Shield className="h-4 w-4" />;
  }
};

export const ScanResults: React.FC<ScanResultsProps> = ({ scanId, onBack }) => {
  const [results, setResults] = useState<ScanResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isGeneratingReport, setIsGeneratingReport] = useState(false);

  useEffect(() => {
    // Mock data for demonstration
    const mockResults: ScanResult[] = [
      {
        id: 1,
        scan_id: scanId,
        tool_used: 'sqlmap',
        raw_output: JSON.stringify({ vulnerability: 'SQL Injection', endpoint: '/login' }),
        ai_analysis: 'SQL injection vulnerability detected in login endpoint. User input is not properly sanitized.',
        severity: 'critical',
        vulnerability_type: 'SQL Injection',
        suggested_fix: 'Use parameterized queries and input validation. Implement ORM or prepared statements.'
      },
      {
        id: 2,
        scan_id: scanId,
        tool_used: 'nikto',
        raw_output: JSON.stringify({ vulnerability: 'XSS', endpoint: '/search' }),
        ai_analysis: 'Cross-site scripting vulnerability found in search functionality.',
        severity: 'high',
        vulnerability_type: 'Cross-Site Scripting (XSS)',
        suggested_fix: 'Sanitize all user inputs and implement Content Security Policy (CSP).'
      },
      {
        id: 3,
        scan_id: scanId,
        tool_used: 'nmap',
        raw_output: JSON.stringify({ open_ports: [22, 80, 443, 3306] }),
        ai_analysis: 'Database port 3306 is exposed to the internet, which poses a security risk.',
        severity: 'medium',
        vulnerability_type: 'Exposed Database Port',
        suggested_fix: 'Configure firewall to block external access to database ports.'
      },
      {
        id: 4,
        scan_id: scanId,
        tool_used: 'nikto',
        raw_output: JSON.stringify({ headers: 'missing security headers' }),
        ai_analysis: 'Missing security headers like X-Frame-Options and X-XSS-Protection.',
        severity: 'low',
        vulnerability_type: 'Missing Security Headers',
        suggested_fix: 'Add security headers to web server configuration.'
      }
    ];

    setTimeout(() => {
      setResults(mockResults);
      setIsLoading(false);
    }, 1000);
  }, [scanId]);

  const severityCounts = results.reduce(
    (acc, result) => {
      acc[result.severity]++;
      return acc;
    },
    { critical: 0, high: 0, medium: 0, low: 0 }
  );

  const totalVulnerabilities = results.length;
  const riskScore = (severityCounts.critical * 10 + severityCounts.high * 7 + severityCounts.medium * 4 + severityCounts.low * 1) / Math.max(totalVulnerabilities, 1);

  const handleGenerateReport = async () => {
    setIsGeneratingReport(true);
    try {
      // Mock PDF generation
      await new Promise(resolve => setTimeout(resolve, 2000));
      toast({
        title: "Report generated",
        description: "PDF report is ready for download",
      });
    } finally {
      setIsGeneratingReport(false);
    }
  };

  const handleRescan = async () => {
    toast({
      title: "Rescan initiated",
      description: "Starting a new scan of the target",
    });
    onBack();
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-96">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-cyan-400 mx-auto mb-4" />
          <p className="text-white">Loading scan results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <Button
          onClick={onBack}
          variant="ghost"
          className="text-white hover:bg-slate-700"
        >
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to Dashboard
        </Button>
        
        <div className="flex gap-2">
          <Button
            onClick={handleRescan}
            variant="outline"
            className="border-slate-600 text-white hover:bg-slate-700"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Rescan
          </Button>
          <Button
            onClick={handleGenerateReport}
            disabled={isGeneratingReport}
            className="bg-cyan-600 hover:bg-cyan-700"
          >
            {isGeneratingReport ? (
              <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
            ) : (
              <FileText className="h-4 w-4 mr-2" />
            )}
            Generate Report
          </Button>
        </div>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Total Vulnerabilities</p>
                <p className="text-2xl font-bold text-white">{totalVulnerabilities}</p>
              </div>
              <Shield className="h-8 w-8 text-cyan-400" />
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Risk Score</p>
                <p className="text-2xl font-bold text-white">{riskScore.toFixed(1)}/10</p>
              </div>
              <AlertTriangle className="h-8 w-8 text-orange-400" />
            </div>
            <Progress value={riskScore * 10} className="mt-2" />
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Critical Issues</p>
                <p className="text-2xl font-bold text-red-400">{severityCounts.critical}</p>
              </div>
              <div className="text-red-400">
                <AlertTriangle className="h-8 w-8" />
              </div>
            </div>
          </CardContent>
        </Card>

        <Card className="bg-slate-800 border-slate-700">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-slate-400 text-sm">Scan Time</p>
                <p className="text-2xl font-bold text-white">4.2m</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-400" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Results Table */}
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Vulnerability Details</CardTitle>
          <CardDescription className="text-slate-300">
            Detailed analysis of discovered security issues
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs defaultValue="vulnerabilities" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-slate-700">
              <TabsTrigger value="vulnerabilities" className="text-white">Vulnerabilities</TabsTrigger>
              <TabsTrigger value="raw" className="text-white">Raw Output</TabsTrigger>
            </TabsList>
            
            <TabsContent value="vulnerabilities" className="space-y-4">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-4 bg-slate-700 rounded-lg border border-slate-600"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-full ${getSeverityColor(result.severity)} text-white`}>
                        {getSeverityIcon(result.severity)}
                      </div>
                      <div>
                        <h4 className="font-semibold text-white">
                          {result.vulnerability_type}
                        </h4>
                        <p className="text-sm text-slate-400">
                          Detected by {result.tool_used}
                        </p>
                      </div>
                    </div>
                    <Badge className={getSeverityColor(result.severity)}>
                      {result.severity}
                    </Badge>
                  </div>
                  
                  {result.ai_analysis && (
                    <div className="mb-3">
                      <h5 className="text-sm font-medium text-white mb-1">Analysis</h5>
                      <p className="text-sm text-slate-300">{result.ai_analysis}</p>
                    </div>
                  )}
                  
                  {result.suggested_fix && (
                    <div>
                      <h5 className="text-sm font-medium text-white mb-1">Suggested Fix</h5>
                      <p className="text-sm text-green-300">{result.suggested_fix}</p>
                    </div>
                  )}
                </div>
              ))}
            </TabsContent>
            
            <TabsContent value="raw" className="space-y-4">
              {results.map((result) => (
                <div
                  key={result.id}
                  className="p-4 bg-slate-700 rounded-lg border border-slate-600"
                >
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-semibold text-white">{result.tool_used}</h4>
                    <Badge className={getSeverityColor(result.severity)}>
                      {result.severity}
                    </Badge>
                  </div>
                  <pre className="text-sm text-slate-300 bg-slate-800 p-3 rounded overflow-x-auto">
                    {JSON.stringify(JSON.parse(result.raw_output), null, 2)}
                  </pre>
                </div>
              ))}
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  );
};
