import React, { useState } from 'react';
import ApiService from '../services/api';

const ApiTest = () => {
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);

  const testConnection = async () => {
    setLoading(true);
    try {
      const result = await ApiService.testConnection();
      setResponse(JSON.stringify(result, null, 2));
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  const testRegistration = async () => {
    setLoading(true);
    try {
      const result = await ApiService.register({
        email: 'testuser@example.com',
        username: 'testuser',
        password: 'Password123'
      });
      setResponse(JSON.stringify(result, null, 2));
    } catch (error) {
      setResponse(`Error: ${error.message}`);
    }
    setLoading(false);
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>API Integration Test</h2>
      
      <div style={{ marginBottom: '10px' }}>
        <button onClick={testConnection} disabled={loading}>
          Test Connection
        </button>
        <button onClick={testRegistration} disabled={loading} style={{ marginLeft: '10px' }}>
          Test Registration
        </button>
      </div>
      
      {loading && <p>Loading...</p>}
      
      <pre style={{ 
        background: '#f4f4f4', 
        padding: '10px', 
        borderRadius: '4px',
        whiteSpace: 'pre-wrap'
      }}>
        {response || 'Click a button to test the API'}
      </pre>
    </div>
  );
};

export default ApiTest;