
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Checkbox } from '@/components/ui/checkbox';
import { useAuth } from '@/contexts/AuthContext';
import { Search, AlertTriangle } from 'lucide-react';
import { toast } from '@/hooks/use-toast';

interface ScanFormProps {
  onScanStart: (url: string) => void;
}

export const ScanForm: React.FC<ScanFormProps> = ({ onScanStart }) => {
  const [url, setUrl] = useState('');
  const [acceptPolicy, setAcceptPolicy] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { user } = useAuth();

  const validateUrl = (url: string): boolean => {
    try {
      const urlObj = new URL(url);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateUrl(url)) {
      toast({
        title: "Invalid URL",
        description: "Please enter a valid HTTP or HTTPS URL",
        variant: "destructive",
      });
      return;
    }
    
    if (!acceptPolicy) {
      toast({
        title: "Policy required",
        description: "Please accept the ethical scanning policy",
        variant: "destructive",
      });
      return;
    }
    
    if (user?.is_guest && (user.scan_limit || 0) <= 0) {
      toast({
        title: "Scan limit reached",
        description: "Please create an account for unlimited scans",
        variant: "destructive",
      });
      return;
    }
    
    setIsLoading(true);
    try {
      await onScanStart(url);
      setUrl('');
      setAcceptPolicy(false);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white flex items-center gap-2">
          <Search className="h-5 w-5 text-cyan-400" />
          Start Security Scan
        </CardTitle>
        <CardDescription className="text-slate-300">
          Enter a target URL to begin comprehensive security testing
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="url" className="text-white">Target URL</Label>
            <Input
              id="url"
              type="url"
              value={url}
              onChange={(e) => setUrl(e.target.value)}
              placeholder="https://example.com"
              required
              className="bg-slate-700 border-slate-600 text-white placeholder:text-slate-400"
            />
          </div>
          
          <div className="bg-amber-900/20 border border-amber-700 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <AlertTriangle className="h-5 w-5 text-amber-400 mt-0.5" />
              <div className="space-y-2">
                <h4 className="text-amber-400 font-medium">Ethical Scanning Policy</h4>
                <p className="text-sm text-slate-300">
                  You may only scan websites you own or have explicit permission to test. 
                  Unauthorized scanning may violate laws and terms of service.
                </p>
                <div className="flex items-center space-x-2">
                  <Checkbox
                    id="policy"
                    checked={acceptPolicy}
                    onCheckedChange={(checked) => setAcceptPolicy(checked as boolean)}
                    className="border-amber-600"
                  />
                  <Label htmlFor="policy" className="text-sm text-slate-300">
                    I confirm I have permission to scan this target
                  </Label>
                </div>
              </div>
            </div>
          </div>
          
          <Button 
            type="submit" 
            className="w-full bg-cyan-600 hover:bg-cyan-700"
            disabled={isLoading || !acceptPolicy}
          >
            {isLoading ? "Starting scan..." : "Start Scan"}
          </Button>
          
          {user?.is_guest && (
            <p className="text-sm text-amber-400 text-center">
              Guest mode: {user.scan_limit || 0} scans remaining
            </p>
          )}
        </form>
      </CardContent>
    </Card>
  );
};
