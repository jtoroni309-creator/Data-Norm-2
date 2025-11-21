/**
 * Main App Component
 * Microsoft Fluent Design System inspired layout and routing
 */

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Users,
  Settings,
  FileText,
  BarChart3,
  Menu,
  Search,
  Bell,
  User,
  LogOut,
  Building2,
  ChevronRight,
} from 'lucide-react';

// Pages
import { LoginPage } from './pages/LoginPage';
import { HomePage } from './pages/HomePage';
import FirmDashboard from './pages/FirmDashboard';
import FirmSettings from './pages/FirmSettings';
import EmployeeManagement from './pages/EmployeeManagement';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { IntegrationsPage } from './pages/IntegrationsPage';

const navigation = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/firm/dashboard' },
  { id: 'employees', label: 'Team', icon: Users, path: '/firm/employees' },
  { id: 'audits', label: 'Audits', icon: FileText, path: '/firm/audits' },
  { id: 'reports', label: 'Reports', icon: BarChart3, path: '/firm/reports' },
  { id: 'settings', label: 'Settings', icon: Settings, path: '/firm/settings' },
];

const SmartRedirect: React.FC = () => {
  const isCpaPortal = window.location.hostname.startsWith('cpa.');
  const targetPath = isCpaPortal ? "/firm/dashboard" : "/client/dashboard";

  return <Navigate to={targetPath} replace />;
};

// Route guard component to ensure correct portal access based on subdomain
const RouteGuard: React.FC<{ children: React.ReactNode; portalType: 'firm' | 'client' }> = ({ children, portalType }) => {
  const navigate = useNavigate();
  const isCpaPortal = window.location.hostname.startsWith('cpa.');

  React.useEffect(() => {
    // If on CPA subdomain but trying to access client routes, redirect to firm dashboard
    if (isCpaPortal && portalType === 'client') {
      console.log('RouteGuard: Redirecting from client route to firm dashboard');
      navigate('/firm/dashboard', { replace: true });
      return;
    }

    // If NOT on CPA subdomain but trying to access firm routes, redirect to client dashboard
    if (!isCpaPortal && portalType === 'firm') {
      console.log('RouteGuard: Redirecting from firm route to client dashboard');
      navigate('/client/dashboard', { replace: true });
      return;
    }
  }, [isCpaPortal, portalType, navigate]);

  // Block rendering during redirect
  if (isCpaPortal && portalType === 'client') {
    return null;
  }

  if (!isCpaPortal && portalType === 'firm') {
    return null;
  }

  return <>{children}</>;
};

const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [searchOpen, setSearchOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#faf9f8]">
      {/* Sidebar Navigation */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 280 : 72 }}
        transition={{ duration: 0.2, ease: [0.1, 0.9, 0.2, 1] }}
        className="fixed top-0 left-0 h-screen bg-white border-r border-neutral-200 z-50"
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="h-16 flex items-center justify-between px-4 border-b border-neutral-200">
            <AnimatePresence mode="wait">
              {sidebarOpen && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 0.15 }}
                  className="flex items-center gap-3"
                >
                  <div className="w-8 h-8 bg-primary-500 rounded-fluent flex items-center justify-center">
                    <Building2 className="w-5 h-5 text-white" />
                  </div>
                  <div>
                    <h1 className="text-body-strong text-neutral-900">Aura CPA</h1>
                    <p className="text-caption text-neutral-600">Portal</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 hover:bg-neutral-100 rounded-fluent-sm transition-colors"
              aria-label="Toggle sidebar"
            >
              <Menu className="w-5 h-5 text-neutral-700" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              return (
                <button
                  key={item.id}
                  onClick={() => navigate(item.path)}
                  className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-fluent transition-all duration-100 ${
                    isActive
                      ? 'bg-primary-50 text-primary-600 font-semibold'
                      : 'text-neutral-700 hover:bg-neutral-50 font-medium'
                  }`}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary-600' : 'text-neutral-600'}`} />
                  <AnimatePresence mode="wait">
                    {sidebarOpen && (
                      <motion.span
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: 'auto' }}
                        exit={{ opacity: 0, width: 0 }}
                        transition={{ duration: 0.15 }}
                        className="text-body-strong whitespace-nowrap overflow-hidden"
                      >
                        {item.label}
                      </motion.span>
                    )}
                  </AnimatePresence>
                  {isActive && sidebarOpen && (
                    <motion.div
                      layoutId="activeIndicator"
                      className="ml-auto w-1 h-4 bg-primary-500 rounded-full"
                      transition={{ duration: 0.2, ease: [0.1, 0.9, 0.2, 1] }}
                    />
                  )}
                </button>
              );
            })}
          </nav>

          {/* User Profile */}
          <div className="p-3 border-t border-neutral-200">
            <div className="flex items-center gap-3 px-3 py-2.5">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white text-body-strong flex-shrink-0">
                F
              </div>
              <AnimatePresence mode="wait">
                {sidebarOpen && (
                  <motion.div
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ duration: 0.15 }}
                    className="flex-1 min-w-0 overflow-hidden"
                  >
                    <p className="text-body-strong text-neutral-900 truncate">Firm Admin</p>
                    <p className="text-caption text-neutral-600 truncate">admin@firm.com</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <button
              onClick={() => navigate('/login')}
              className="w-full flex items-center gap-3 px-3 py-2.5 text-error-500 hover:bg-error-50 rounded-fluent transition-colors mt-2"
              title={!sidebarOpen ? 'Logout' : undefined}
            >
              <LogOut className="w-5 h-5 flex-shrink-0" />
              <AnimatePresence mode="wait">
                {sidebarOpen && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ duration: 0.15 }}
                    className="text-body-strong whitespace-nowrap overflow-hidden"
                  >
                    Logout
                  </motion.span>
                )}
              </AnimatePresence>
            </button>
          </div>
        </div>
      </motion.aside>

      {/* Main Content */}
      <motion.main
        animate={{ marginLeft: sidebarOpen ? 280 : 72 }}
        transition={{ duration: 0.2, ease: [0.1, 0.9, 0.2, 1] }}
        className="min-h-screen"
      >
        {/* Command Bar / Top Navigation */}
        <div className="h-16 bg-white border-b border-neutral-200 sticky top-0 z-40 fluent-acrylic">
          <div className="h-full flex items-center justify-between px-6">
            {/* Search */}
            <div className="flex-1 max-w-xl">
              {searchOpen ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="relative"
                >
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-neutral-500 w-4 h-4" />
                  <input
                    type="text"
                    placeholder="Search for anything..."
                    autoFocus
                    onBlur={() => setSearchOpen(false)}
                    className="w-full pl-10 pr-4 py-2 bg-neutral-50 border border-neutral-200 rounded-fluent text-body focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_1px_#0078d4]"
                  />
                </motion.div>
              ) : (
                <button
                  onClick={() => setSearchOpen(true)}
                  className="flex items-center gap-2 px-4 py-2 bg-neutral-50 hover:bg-neutral-100 rounded-fluent transition-colors w-full max-w-md"
                >
                  <Search className="w-4 h-4 text-neutral-500" />
                  <span className="text-body text-neutral-600">Search</span>
                  <span className="ml-auto text-caption text-neutral-500 font-mono">Ctrl+K</span>
                </button>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 ml-6">
              <button className="relative p-2.5 hover:bg-neutral-100 rounded-fluent transition-colors">
                <Bell className="w-5 h-5 text-neutral-700" />
                <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-error-500 rounded-full ring-2 ring-white"></span>
              </button>
              <button className="p-2.5 hover:bg-neutral-100 rounded-fluent transition-colors">
                <User className="w-5 h-5 text-neutral-700" />
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2, ease: [0.1, 0.9, 0.2, 1] }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.main>
    </div>
  );
};

const App: React.FC = () => {
  return (
    <BrowserRouter>
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          className: 'fluent-card',
          style: {
            background: '#fff',
            color: '#171717',
            borderRadius: '8px',
            padding: '12px 16px',
            boxShadow: '0 2.4px 7.2px rgba(0, 0, 0, 0.1), 0 12.8px 28.8px rgba(0, 0, 0, 0.13)',
            fontSize: '0.875rem',
            fontWeight: 600,
          },
          success: {
            iconTheme: {
              primary: '#10893e',
              secondary: '#fff',
            },
          },
          error: {
            iconTheme: {
              primary: '#e81123',
              secondary: '#fff',
            },
          },
        }}
      />

      <Routes>
        {/* Auth Routes */}
        <Route path="/login" element={<LoginPage />} />

        {/* Firm Portal Routes with Layout - Protected by RouteGuard */}
        <Route path="/firm/dashboard" element={<RouteGuard portalType="firm"><AppLayout><FirmDashboard /></AppLayout></RouteGuard>} />
        <Route path="/firm/settings" element={<RouteGuard portalType="firm"><AppLayout><FirmSettings /></AppLayout></RouteGuard>} />
        <Route path="/firm/employees" element={<RouteGuard portalType="firm"><AppLayout><EmployeeManagement /></AppLayout></RouteGuard>} />
        <Route
          path="/firm/audits"
          element={
            <RouteGuard portalType="firm">
              <AppLayout>
                <div className="text-center py-20">
                  <FileText className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                  <h2 className="text-title-large text-neutral-900 mb-2">Audits Coming Soon</h2>
                  <p className="text-body text-neutral-600">This feature is currently in development</p>
                </div>
              </AppLayout>
            </RouteGuard>
          }
        />
        <Route
          path="/firm/reports"
          element={
            <RouteGuard portalType="firm">
              <AppLayout>
                <div className="text-center py-20">
                  <BarChart3 className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
                  <h2 className="text-title-large text-neutral-900 mb-2">Reports Coming Soon</h2>
                  <p className="text-body text-neutral-600">This feature is currently in development</p>
                </div>
              </AppLayout>
            </RouteGuard>
          }
        />

        {/* Customer Portal Routes - Protected by RouteGuard */}
        <Route path="/customer/dashboard" element={<RouteGuard portalType="client"><DashboardPage /></RouteGuard>} />
        <Route path="/customer/documents" element={<RouteGuard portalType="client"><DocumentsPage /></RouteGuard>} />
        <Route path="/customer/integrations" element={<RouteGuard portalType="client"><IntegrationsPage /></RouteGuard>} />

        {/* Client Portal Routes (Audit Client Portal - alias for /customer/*) - Protected by RouteGuard */}
        <Route path="/client/dashboard" element={<RouteGuard portalType="client"><DashboardPage /></RouteGuard>} />
        <Route path="/client/documents" element={<RouteGuard portalType="client"><DocumentsPage /></RouteGuard>} />
        <Route path="/client/integrations" element={<RouteGuard portalType="client"><IntegrationsPage /></RouteGuard>} />

        {/* Landing Page - Microsoft Fluent Design */}
        <Route path="/" element={<HomePage />} />

        {/* Fallback - redirect to home */}
        <Route path="*" element={<HomePage />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
