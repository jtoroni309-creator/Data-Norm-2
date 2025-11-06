/**
 * Main App Component
 * Configures routing for the CPA Firm Portal
 */

import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';

// Pages
import LoginPage from './pages/LoginPage';
import FirmDashboard from './pages/FirmDashboard';
import FirmSettings from './pages/FirmSettings';
import EmployeeManagement from './pages/EmployeeManagement';
import RegABAudit from './pages/RegABAudit';

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#333',
            color: '#fff',
          },
          success: {
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />

      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<LoginPage />} />

        {/* Firm Portal Routes */}
        <Route path="/firm/dashboard" element={<FirmDashboard />} />
        <Route path="/firm/settings" element={<FirmSettings />} />
        <Route path="/firm/employees" element={<EmployeeManagement />} />

        {/* Audit Features */}
        <Route path="/audit/reg-ab" element={<RegABAudit />} />

        {/* Default redirect */}
        <Route path="/" element={<Navigate to="/firm/dashboard" replace />} />
        <Route path="*" element={<Navigate to="/firm/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
