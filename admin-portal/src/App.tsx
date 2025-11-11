import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/Layout';
import { Dashboard } from './pages/Dashboard';
import { UserManagement } from './pages/UserManagement';
import { Settings } from './pages/Settings';
import { TicketManagement } from './components/TicketManagement';

function App() {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/users" element={<UserManagement />} />
          <Route path="/tickets" element={<TicketManagement />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/analytics" element={<Dashboard />} />
          <Route path="/data" element={<Dashboard />} />
          <Route path="/health" element={<Dashboard />} />
          <Route path="/security" element={<Dashboard />} />
          <Route path="/reports" element={<Dashboard />} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;
