
import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Shield, Search, LogOut, User, AlertTriangle, CheckCircle, XCircle } from "lucide-react";
import { toast } from "@/hooks/use-toast";

interface Scan {
  id: string;
  url: string;
  status: 'completed' | 'running' | 'failed';
  date: string;
  vulnerabilities: number;
  riskLevel: 'low' | 'medium' | 'high' | 'critical';
}

const Dashboard = () => {
  const [user, setUser] = useState<any>(null);
  const [targetUrl, setTargetUrl] = useState("");
  const [ethicalPolicyAccepted, setEthicalPolicyAccepted] = useState(false);
  const [scanning, setScanning] = useState(false);
  const [recentScans, setRecentScans] = useState<Scan[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('auth_token') || localStorage.getItem('guest_token');
    const userData = localStorage.getItem('user_data');
    
    if (!token || !userData) {
      navigate('/login');
      return;
    }

    const parsedUser = JSON.parse(userData);
    setUser(parsedUser);

    // Load mock recent scans
    const mockScans: Scan[] = [
      {
        id: '1',
        url: 'https://example.com',
        status: 'completed',
        date: '2024-01-15',
        vulnerabilities: 3,
        riskLevel: 'medium'
      },
      {
        id: '2',
        url: 'https://testsite.org',
        status: 'completed',
        date: '2024-01-14',
        vulnerabilities: 0,
        riskLevel: 'low'
      },
      {
        id: '3',
        url: 'https://vulnerable-app.com',
        status: 'completed',
        date: '2024-01-13',
        vulnerabilities: 12,
        riskLevel: 'critical'
      }
    ];
    setRecentScans(mockScans);
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('guest_token');
    localStorage.removeItem('user_data');
    navigate('/login');
  };

  const validateUrl = (url: string) => {
    try {
      new URL(url);
      return url.startsWith('http://') || url.startsWith('https://');
    } catch {
      return false;
    }
  };

  const handleStartScan = async () => {
    if (!validateUrl(targetUrl)) {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid HTTP or HTTPS URL.",
        variant: "destructive",
      });
      return;
    }

    if (!ethicalPolicyAccepted) {
      toast({
        title: "Ethical policy required",
        description: "Please accept the ethical scanning policy to continue.",
        variant: "destructive",
      });
      return;
    }

    setScanning(true);

    // Mock scanning process
    setTimeout(() => {
      const scanId = Date.now().toString();
      const newScan: Scan = {
        id: scanId,
        url: targetUrl,
        status: 'completed',
        date: new Date().toISOString().split('T')[0],
        vulnerabilities: Math.floor(Math.random() * 15),
        riskLevel: ['low', 'medium', 'high', 'critical'][Math.floor(Math.random() * 4)] as any
      };

      setRecentScans(prev => [newScan, ...prev]);
      setScanning(false);
      setTargetUrl("");
      setEthicalPolicyAccepted(false);

      toast({
        title: "Scan completed",
        description: `Found ${newScan.vulnerabilities} potential vulnerabilities`,
      });

      navigate(`/scan-results/${scanId}`);
    }, 3000);
  };

  const getRiskBadgeColor = (risk: string) => {
    switch (risk) {
      case 'low': return 'bg-green-500';
      case 'medium': return 'bg-yellow-500';
      case 'high': return 'bg-orange-500';
      case 'critical': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'running': return <div className="h-4 w-4 rounded-full bg-blue-500 animate-pulse" />;
      case 'failed': return <XCircle className="h-4 w-4 text-red-500" />;
      default: return null;
    }
  };

  if (!user) {
    return <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-500"></div>
    </div>;
  }

  return (
    <div className="min-h-screen bg-gray-900">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Shield className="h-6 w-6 text-white" />
              </div>
              <h1 className="text-xl font-bold text-white">VulnerabilityScanner</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <User className="h-4 w-4 text-gray-400" />
                <span className="text-gray-300">{user.username}</span>
                {user.plan === 'guest' && (
                  <Badge variant="outline" className="text-orange-400 border-orange-400">
                    Guest ({user.scanLimit} scans left)
                  </Badge>
                )}
              </div>
              <Button
                onClick={handleLogout}
                variant="outline"
                size="sm"
                className="border-gray-600 text-gray-300 hover:bg-gray-700"
              >
                <LogOut className="h-4 w-4 mr-2" />
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Scan Input Section */}
          <div className="lg:col-span-1">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white flex items-center">
                  <Search className="h-5 w-5 mr-2" />
                  New Scan
                </CardTitle>
                <CardDescription className="text-gray-400">
                  Enter a URL to scan for vulnerabilities
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="url" className="text-gray-300">Target URL</Label>
                  <Input
                    id="url"
                    type="url"
                    value={targetUrl}
                    onChange={(e) => setTargetUrl(e.target.value)}
                    className="bg-gray-700 border-gray-600 text-white"
                    placeholder="https://example.com"
                    disabled={scanning}
                  />
                </div>

                <div className="flex items-start space-x-2">
                  <Checkbox
                    id="ethical-policy"
                    checked={ethicalPolicyAccepted}
                    onCheckedChange={(checked) => setEthicalPolicyAccepted(checked as boolean)}
                    disabled={scanning}
                  />
                  <Label htmlFor="ethical-policy" className="text-sm text-gray-300 leading-5">
                    I confirm that I have authorization to scan this website and will use this tool ethically
                  </Label>
                </div>

                <Button
                  onClick={handleStartScan}
                  className="w-full bg-blue-600 hover:bg-blue-700"
                  disabled={scanning || !targetUrl || !ethicalPolicyAccepted}
                >
                  {scanning ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Scanning...
                    </div>
                  ) : (
                    "Start Scan"
                  )}
                </Button>

                {user.plan === 'guest' && (
                  <div className="bg-orange-900/20 border border-orange-800 rounded-lg p-3">
                    <div className="flex items-center text-orange-400 text-sm">
                      <AlertTriangle className="h-4 w-4 mr-2" />
                      Guest mode: Limited to {user.scanLimit} scans
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Recent Scans */}
          <div className="lg:col-span-2">
            <Card className="bg-gray-800 border-gray-700">
              <CardHeader>
                <CardTitle className="text-white">Recent Scans</CardTitle>
                <CardDescription className="text-gray-400">
                  View your scanning history and results
                </CardDescription>
              </CardHeader>
              <CardContent>
                {recentScans.length === 0 ? (
                  <div className="text-center py-8 text-gray-400">
                    No scans yet. Start your first scan to see results here.
                  </div>
                ) : (
                  <Table>
                    <TableHeader>
                      <TableRow className="border-gray-700">
                        <TableHead className="text-gray-300">Status</TableHead>
                        <TableHead className="text-gray-300">URL</TableHead>
                        <TableHead className="text-gray-300">Date</TableHead>
                        <TableHead className="text-gray-300">Vulnerabilities</TableHead>
                        <TableHead className="text-gray-300">Risk Level</TableHead>
                        <TableHead className="text-gray-300">Actions</TableHead>
                      </TableRow>
                    </TableHeader>
                    <TableBody>
                      {recentScans.map((scan) => (
                        <TableRow key={scan.id} className="border-gray-700 hover:bg-gray-700/50">
                          <TableCell>
                            <div className="flex items-center space-x-2">
                              {getStatusIcon(scan.status)}
                              <span className="text-gray-300 capitalize">{scan.status}</span>
                            </div>
                          </TableCell>
                          <TableCell className="text-gray-300 font-mono text-sm">
                            {scan.url}
                          </TableCell>
                          <TableCell className="text-gray-300">{scan.date}</TableCell>
                          <TableCell className="text-gray-300">{scan.vulnerabilities}</TableCell>
                          <TableCell>
                            <Badge className={`${getRiskBadgeColor(scan.riskLevel)} text-white`}>
                              {scan.riskLevel.toUpperCase()}
                            </Badge>
                          </TableCell>
                          <TableCell>
                            <Button
                              onClick={() => navigate(`/scan-results/${scan.id}`)}
                              variant="outline"
                              size="sm"
                              className="border-gray-600 text-gray-300 hover:bg-gray-700"
                            >
                              View Details
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
