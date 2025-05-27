
import React, { useState, useEffect } from 'react';
import { ScanForm } from './ScanForm';
import { RecentScans } from './RecentScans';
import { Scan } from '@/types';
import { useAuth } from '@/contexts/AuthContext';
import { toast } from '@/hooks/use-toast';

interface DashboardProps {
  onViewResults: (scanId: number) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ onViewResults }) => {
  const [scans, setScans] = useState<Scan[]>([]);
  const { user } = useAuth();

  // Mock data for demonstration
  useEffect(() => {
    if (!user?.is_guest) {
      const mockScans: Scan[] = [
        {
          id: 3,
          user_id: user?.id || 1,
          target_url: 'https://vulnerable-app.com',
          status: 'failed',
          started_at: new Date(Date.now() - 7200000).toISOString(),
          finished_at: new Date(Date.now() - 6900000).toISOString(),
        },
      ];
      setScans(mockScans);
    }
  }, [user]);

  const handleScanStart = async (url: string) => {
    try {
      // Mock API call
      const newScan: Scan = {
        id: Date.now(),
        user_id: user?.id || 0,
        target_url: url,
        status: 'pending',
        started_at: new Date().toISOString(),
      };

      setScans(prevScans => [newScan, ...prevScans]);

      // Simulate scan progression
      setTimeout(() => {
        setScans(prevScans =>
          prevScans.map(scan =>
            scan.id === newScan.id ? { ...scan, status: 'running' as const } : scan
          )
        );
      }, 2000);

      setTimeout(() => {
        setScans(prevScans =>
          prevScans.map(scan =>
            scan.id === newScan.id
              ? {
                  ...scan,
                  status: 'completed' as const,
                  finished_at: new Date().toISOString(),
                }
              : scan
          )
        );
      }, 8000);

      toast({
        title: "Scan started",
        description: `Security scan initiated for ${url}`,
      });

      // Update guest scan limit
      if (user?.is_guest && user.scan_limit) {
        user.scan_limit--;
      }
    } catch (error) {
      toast({
        title: "Scan failed",
        description: "Unable to start scan. Please try again.",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="space-y-8">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <ScanForm onScanStart={handleScanStart} />
        <div className="space-y-4">
          <div className="bg-gradient-to-r from-cyan-600 to-blue-600 rounded-lg p-6 text-white">
            <h3 className="text-lg font-semibold mb-2">Security Scanning Tools</h3>
            <div className="grid grid-cols-3 gap-4 text-sm">
              <div className="text-center">
                <div className="font-medium">SQLmap</div>
                <div className="text-cyan-200">SQL Injection</div>
              </div>
              <div className="text-center">
                <div className="font-medium">Nmap</div>
                <div className="text-cyan-200">Port Scanning</div>
              </div>
              <div className="text-center">
                <div className="font-medium">Nikto</div>
                <div className="text-cyan-200">Web Vulnerabilities</div>
              </div>
              <div className="text-center">
                <div className="font-medium">Wapiti</div>
                <div className="text-cyan-200">Port Scanning</div>
              </div>
              <div className="text-center">
                <div className="font-medium">Dirsearch</div>
                <div className="text-cyan-200">Port Scanning</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <RecentScans scans={scans} onViewResults={onViewResults} />
    </div>
  );
};
