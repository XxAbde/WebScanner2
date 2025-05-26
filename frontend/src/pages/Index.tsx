
import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { AuthPage } from '@/components/auth/AuthPage';
import { Layout } from '@/components/Layout';
import { Dashboard } from '@/components/dashboard/Dashboard';
import { ScanResults } from '@/components/results/ScanResults';

const Index = () => {
  const { user } = useAuth();
  const [currentView, setCurrentView] = useState<'dashboard' | 'results'>('dashboard');
  const [selectedScanId, setSelectedScanId] = useState<number | null>(null);

  if (!user) {
    return <AuthPage />;
  }

  const handleViewResults = (scanId: number) => {
    setSelectedScanId(scanId);
    setCurrentView('results');
  };

  const handleBackToDashboard = () => {
    setCurrentView('dashboard');
    setSelectedScanId(null);
  };

  return (
    <Layout>
      {currentView === 'dashboard' ? (
        <Dashboard onViewResults={handleViewResults} />
      ) : (
        selectedScanId && (
          <ScanResults 
            scanId={selectedScanId} 
            onBack={handleBackToDashboard} 
          />
        )
      )}
    </Layout>
  );
};

export default Index;
