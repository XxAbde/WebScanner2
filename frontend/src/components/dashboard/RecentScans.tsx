
import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Clock, ExternalLink, AlertCircle, CheckCircle, XCircle, Loader } from 'lucide-react';
import { Scan } from '@/types';

interface RecentScansProps {
  scans: Scan[];
  onViewResults: (scanId: number) => void;
}

const getStatusIcon = (status: Scan['status']) => {
  switch (status) {
    case 'pending':
      return <Clock className="h-4 w-4" />;
    case 'running':
      return <Loader className="h-4 w-4 animate-spin" />;
    case 'completed':
      return <CheckCircle className="h-4 w-4" />;
    case 'failed':
      return <XCircle className="h-4 w-4" />;
  }
};

const getStatusColor = (status: Scan['status']) => {
  switch (status) {
    case 'pending':
      return 'bg-yellow-600';
    case 'running':
      return 'bg-blue-600';
    case 'completed':
      return 'bg-green-600';
    case 'failed':
      return 'bg-red-600';
  }
};

export const RecentScans: React.FC<RecentScansProps> = ({ scans, onViewResults }) => {
  if (scans.length === 0) {
    return (
      <Card className="bg-slate-800 border-slate-700">
        <CardHeader>
          <CardTitle className="text-white">Recent Scans</CardTitle>
          <CardDescription className="text-slate-300">
            Your scan history will appear here
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8">
            <AlertCircle className="h-12 w-12 text-slate-500 mx-auto mb-4" />
            <p className="text-slate-400">No scans yet. Start your first scan above!</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="bg-slate-800 border-slate-700">
      <CardHeader>
        <CardTitle className="text-white">Recent Scans</CardTitle>
        <CardDescription className="text-slate-300">
          View and manage your security scans
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {scans.map((scan) => (
            <div
              key={scan.id}
              className="flex items-center justify-between p-4 bg-slate-700 rounded-lg border border-slate-600"
            >
              <div className="flex items-center gap-3">
                <div className={`p-2 rounded-full ${getStatusColor(scan.status)} text-white`}>
                  {getStatusIcon(scan.status)}
                </div>
                <div>
                  <div className="flex items-center gap-2">
                    <span className="text-white font-medium">{scan.target_url}</span>
                    <ExternalLink className="h-4 w-4 text-slate-400" />
                  </div>
                  <div className="flex items-center gap-4 text-sm text-slate-400">
                    <span>Started: {new Date(scan.started_at).toLocaleString()}</span>
                    {scan.finished_at && (
                      <span>Finished: {new Date(scan.finished_at).toLocaleString()}</span>
                    )}
                  </div>
                </div>
              </div>
              
              <div className="flex items-center gap-2">
                <Badge className={getStatusColor(scan.status)}>
                  {scan.status}
                </Badge>
                {scan.status === 'completed' && (
                  <Button
                    onClick={() => onViewResults(scan.id)}
                    size="sm"
                    className="bg-cyan-600 hover:bg-cyan-700"
                  >
                    View Results
                  </Button>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};
