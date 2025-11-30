/**
 * Main App Component
 * Microsoft Fluent Design System inspired layout and routing
 * Enhanced with Dark/Light mode, notifications, and user menu
 */

import React, { useState, useEffect, createContext, useContext, useRef } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import toast from 'react-hot-toast';
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
  Shield,
  FlaskConical,
  Calculator,
  ShieldAlert,
  Network,
  Brain,
  Moon,
  Sun,
  X,
  Check,
  Clock,
  AlertCircle,
  Info,
  CheckCircle,
  UserCircle,
  Palette,
} from 'lucide-react';

// ========================================
// Theme Context for Dark/Light Mode
// ========================================
type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  theme: ThemeMode;
  toggleTheme: () => void;
  setTheme: (theme: ThemeMode) => void;
}

const ThemeContext = createContext<ThemeContextType>({
  theme: 'light',
  toggleTheme: () => {},
  setTheme: () => {},
});

export const useTheme = () => useContext(ThemeContext);

const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [theme, setThemeState] = useState<ThemeMode>(() => {
    const saved = localStorage.getItem('aura_theme');
    return (saved as ThemeMode) || 'light';
  });

  useEffect(() => {
    localStorage.setItem('aura_theme', theme);
    if (theme === 'dark') {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [theme]);

  const toggleTheme = () => {
    setThemeState(prev => prev === 'light' ? 'dark' : 'light');
  };

  const setTheme = (newTheme: ThemeMode) => {
    setThemeState(newTheme);
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
};

// ========================================
// Notification Types and Hook
// ========================================
interface Notification {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title: string;
  message: string;
  time: string;
  read: boolean;
}

const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>(() => {
    const saved = localStorage.getItem('aura_notifications');
    return saved ? JSON.parse(saved) : [
      { id: '1', type: 'success', title: 'Engagement Completed', message: 'Acme Corp 2024 Audit has been finalized.', time: '5m ago', read: false },
      { id: '2', type: 'info', title: 'New Client Onboarded', message: 'Welcome Tech Solutions Inc. to the platform.', time: '1h ago', read: false },
      { id: '3', type: 'warning', title: 'Deadline Approaching', message: 'Beta LLC tax return due in 3 days.', time: '2h ago', read: false },
      { id: '4', type: 'info', title: 'AI Analysis Complete', message: 'Risk assessment for Delta Corp is ready.', time: '3h ago', read: true },
    ];
  });

  useEffect(() => {
    localStorage.setItem('aura_notifications', JSON.stringify(notifications));
  }, [notifications]);

  const markAsRead = (id: string) => {
    setNotifications(prev => prev.map(n => n.id === id ? { ...n, read: true } : n));
  };

  const markAllAsRead = () => {
    setNotifications(prev => prev.map(n => ({ ...n, read: true })));
  };

  const clearNotification = (id: string) => {
    setNotifications(prev => prev.filter(n => n.id !== id));
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return { notifications, markAsRead, markAllAsRead, clearNotification, unreadCount };
};

// Pages
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';
import { AcceptInvitation } from './pages/AcceptInvitation';
import { ForgotPasswordPage } from './pages/ForgotPasswordPage';
import { ResetPasswordPage } from './pages/ResetPasswordPage';
import { HomePage } from './pages/HomePage';
import FirmDashboard from './pages/FirmDashboard';
import FirmSettings from './pages/FirmSettings';
import EmployeeManagement from './pages/EmployeeManagement';
import FirmClients from './pages/FirmClients';
import FirmAudits from './pages/FirmAudits';
import FirmReports from './pages/FirmReports';
import { DashboardPage } from './pages/DashboardPage';
import { DocumentsPage } from './pages/DocumentsPage';
import { IntegrationsPage } from './pages/IntegrationsPage';
// Engagement Workspace Pages
import EngagementWorkspace from './pages/EngagementWorkspace';
import WorkpaperManager from './pages/WorkpaperManager';
import AnalyticalProcedures from './pages/AnalyticalProcedures';
import AuditTesting from './pages/AuditTesting';
import RiskAssessment from './pages/RiskAssessment';
import DocumentRepository from './pages/DocumentRepository';
import AuditReporting from './pages/AuditReporting';
import SOCEngagements from './pages/SOCEngagements';
import AIAuditPlanning from './pages/AIAuditPlanning';
// R&D Tax Credit Pages
import RDStudies from './pages/RDStudies';
import RDStudyWorkspace from './pages/RDStudyWorkspace';
// Tax Engine Pages
import TaxReturns from './pages/TaxReturns';
import TaxReturnWorkspace from './pages/TaxReturnWorkspace';
// Fraud Detection Pages
import FraudDetection from './pages/FraudDetection';
import FraudCaseWorkspace from './pages/FraudCaseWorkspace';
// Group Audit Management
import GroupAuditManagement from './pages/GroupAuditManagement';
// R&D Client Data Collection (Public Page for invited clients)
import { RDStudyClientDataCollection } from './pages/RDStudyClientDataCollection';
// AI Agent Dashboard - Autonomous AI Operations
import AIAgentDashboard from './pages/AIAgentDashboard';

const navigation = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/firm/dashboard' },
  { id: 'ai-agents', label: 'AI Agents', icon: Brain, path: '/firm/ai-agents' },
  { id: 'clients', label: 'Clients', icon: Building2, path: '/firm/clients' },
  { id: 'audits', label: 'Audits', icon: FileText, path: '/firm/audits' },
  { id: 'group-audits', label: 'Group Audits', icon: Network, path: '/firm/group-audits' },
  { id: 'soc', label: 'SOC Audits', icon: Shield, path: '/firm/soc-engagements' },
  { id: 'rd-studies', label: 'R&D Credits', icon: FlaskConical, path: '/firm/rd-studies' },
  { id: 'tax-returns', label: 'Tax Returns', icon: Calculator, path: '/firm/tax-returns' },
  { id: 'fraud-detection', label: 'Fraud Detection', icon: ShieldAlert, path: '/firm/fraud-detection' },
  { id: 'employees', label: 'Team', icon: Users, path: '/firm/employees' },
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
      navigate('/firm/dashboard', { replace: true });
      return;
    }

    // If NOT on CPA subdomain but trying to access firm routes, redirect to client dashboard
    if (!isCpaPortal && portalType === 'firm') {
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
  const [notificationsOpen, setNotificationsOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { notifications, markAsRead, markAllAsRead, clearNotification, unreadCount } = useNotifications();
  const notificationRef = useRef<HTMLDivElement>(null);
  const userMenuRef = useRef<HTMLDivElement>(null);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (notificationRef.current && !notificationRef.current.contains(event.target as Node)) {
        setNotificationsOpen(false);
      }
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Load user data from localStorage
  const getUserData = () => {
    try {
      const userStr = localStorage.getItem('user');
      return userStr ? JSON.parse(userStr) : null;
    } catch {
      return null;
    }
  };
  const user = getUserData();

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user');
    localStorage.removeItem('token');
    toast.success('Logged out successfully');
    navigate('/login');
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'success': return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'warning': return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'error': return <AlertCircle className="w-4 h-4 text-red-500" />;
      default: return <Info className="w-4 h-4 text-blue-500" />;
    }
  };

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'bg-gray-900' : 'bg-[#faf9f8]'}`}>
      {/* Sidebar Navigation */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarOpen ? 280 : 72 }}
        transition={{ duration: 0.2, ease: [0.1, 0.9, 0.2, 1] }}
        className={`fixed top-0 left-0 h-screen z-50 ${
          theme === 'dark'
            ? 'bg-gray-800 border-r border-gray-700'
            : 'bg-white border-r border-neutral-200'
        }`}
      >
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className={`h-16 flex items-center justify-between px-4 border-b ${theme === 'dark' ? 'border-gray-700' : 'border-neutral-200'}`}>
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
                    <h1 className={`text-body-strong ${theme === 'dark' ? 'text-white' : 'text-neutral-900'}`}>Aura CPA</h1>
                    <p className={`text-caption ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-600'}`}>Portal</p>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className={`p-2 rounded-fluent-sm transition-colors ${theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-neutral-100'}`}
              aria-label="Toggle sidebar"
            >
              <Menu className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-300' : 'text-neutral-700'}`} />
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
                      ? theme === 'dark'
                        ? 'bg-primary-900/30 text-primary-400 font-semibold'
                        : 'bg-primary-50 text-primary-600 font-semibold'
                      : theme === 'dark'
                        ? 'text-gray-300 hover:bg-gray-700 font-medium'
                        : 'text-neutral-700 hover:bg-neutral-50 font-medium'
                  }`}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <Icon className={`w-5 h-5 flex-shrink-0 ${
                    isActive
                      ? theme === 'dark' ? 'text-primary-400' : 'text-primary-600'
                      : theme === 'dark' ? 'text-gray-400' : 'text-neutral-600'
                  }`} />
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
          <div className={`p-3 border-t ${theme === 'dark' ? 'border-gray-700' : 'border-neutral-200'}`}>
            <div className="flex items-center gap-3 px-3 py-2.5">
              <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white text-body-strong flex-shrink-0">
                {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
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
                    <p className={`text-body-strong truncate ${theme === 'dark' ? 'text-white' : 'text-neutral-900'}`}>{user?.full_name || 'User'}</p>
                    <p className={`text-caption truncate ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-600'}`}>{user?.email || ''}</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
            <button
              onClick={handleLogout}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-fluent transition-colors mt-2 ${
                theme === 'dark'
                  ? 'text-red-400 hover:bg-red-900/30'
                  : 'text-error-500 hover:bg-error-50'
              }`}
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
        <div className={`h-16 sticky top-0 z-40 fluent-acrylic border-b ${
          theme === 'dark'
            ? 'bg-gray-800 border-gray-700'
            : 'bg-white border-neutral-200'
        }`}>
          <div className="h-full flex items-center justify-between px-6">
            {/* Search */}
            <div className="flex-1 max-w-xl">
              {searchOpen ? (
                <motion.div
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  className="relative"
                >
                  <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-500'}`} />
                  <input
                    type="text"
                    placeholder="Search for anything..."
                    autoFocus
                    onBlur={() => setSearchOpen(false)}
                    className={`w-full pl-10 pr-4 py-2 rounded-fluent text-body focus:outline-none focus:border-primary-500 focus:shadow-[0_0_0_1px_#0078d4] ${
                      theme === 'dark'
                        ? 'bg-gray-700 border-gray-600 text-white placeholder-gray-400'
                        : 'bg-neutral-50 border border-neutral-200'
                    }`}
                  />
                </motion.div>
              ) : (
                <button
                  onClick={() => setSearchOpen(true)}
                  className={`flex items-center gap-2 px-4 py-2 rounded-fluent transition-colors w-full max-w-md ${
                    theme === 'dark'
                      ? 'bg-gray-700 hover:bg-gray-600'
                      : 'bg-neutral-50 hover:bg-neutral-100'
                  }`}
                >
                  <Search className={`w-4 h-4 ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-500'}`} />
                  <span className={`text-body ${theme === 'dark' ? 'text-gray-300' : 'text-neutral-600'}`}>Search</span>
                  <span className={`ml-auto text-caption font-mono ${theme === 'dark' ? 'text-gray-500' : 'text-neutral-500'}`}>Ctrl+K</span>
                </button>
              )}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2 ml-6">
              {/* Dark Mode Toggle */}
              <button
                onClick={toggleTheme}
                className={`p-2.5 rounded-fluent transition-colors ${
                  theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-neutral-100'
                }`}
                title={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {theme === 'dark' ? (
                  <Sun className="w-5 h-5 text-yellow-400" />
                ) : (
                  <Moon className="w-5 h-5 text-neutral-700" />
                )}
              </button>

              {/* Notifications Dropdown */}
              <div className="relative" ref={notificationRef}>
                <button
                  onClick={() => {
                    setNotificationsOpen(!notificationsOpen);
                    setUserMenuOpen(false);
                  }}
                  className={`relative p-2.5 rounded-fluent transition-colors ${
                    theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-neutral-100'
                  }`}
                >
                  <Bell className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-300' : 'text-neutral-700'}`} />
                  {unreadCount > 0 && (
                    <span className={`absolute top-1.5 right-1.5 min-w-[16px] h-4 px-1 text-xs font-bold text-white bg-error-500 rounded-full flex items-center justify-center ring-2 ${theme === 'dark' ? 'ring-gray-800' : 'ring-white'}`}>
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Notification Dropdown Panel */}
                <AnimatePresence>
                  {notificationsOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className={`absolute right-0 mt-2 w-96 rounded-lg shadow-2xl overflow-hidden ${
                        theme === 'dark' ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-neutral-200'
                      }`}
                    >
                      {/* Header */}
                      <div className={`px-4 py-3 border-b flex items-center justify-between ${
                        theme === 'dark' ? 'border-gray-700' : 'border-neutral-200'
                      }`}>
                        <h3 className={`font-semibold ${theme === 'dark' ? 'text-white' : 'text-neutral-900'}`}>
                          Notifications
                        </h3>
                        {unreadCount > 0 && (
                          <button
                            onClick={markAllAsRead}
                            className="text-sm text-primary-500 hover:text-primary-600 font-medium"
                          >
                            Mark all as read
                          </button>
                        )}
                      </div>

                      {/* Notification List */}
                      <div className="max-h-96 overflow-y-auto">
                        {notifications.length === 0 ? (
                          <div className={`px-4 py-8 text-center ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-500'}`}>
                            <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                            <p>No notifications</p>
                          </div>
                        ) : (
                          notifications.map((notification) => (
                            <div
                              key={notification.id}
                              onClick={() => markAsRead(notification.id)}
                              className={`px-4 py-3 cursor-pointer transition-colors flex gap-3 ${
                                notification.read
                                  ? theme === 'dark' ? 'bg-gray-800' : 'bg-white'
                                  : theme === 'dark' ? 'bg-gray-700/50' : 'bg-primary-50/50'
                              } ${
                                theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-neutral-50'
                              } border-b ${theme === 'dark' ? 'border-gray-700' : 'border-neutral-100'}`}
                            >
                              <div className="flex-shrink-0 mt-0.5">
                                {getNotificationIcon(notification.type)}
                              </div>
                              <div className="flex-1 min-w-0">
                                <p className={`font-medium text-sm ${theme === 'dark' ? 'text-white' : 'text-neutral-900'}`}>
                                  {notification.title}
                                </p>
                                <p className={`text-sm mt-0.5 ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-600'}`}>
                                  {notification.message}
                                </p>
                                <p className={`text-xs mt-1 flex items-center gap-1 ${theme === 'dark' ? 'text-gray-500' : 'text-neutral-400'}`}>
                                  <Clock className="w-3 h-3" />
                                  {notification.time}
                                </p>
                              </div>
                              <button
                                onClick={(e) => {
                                  e.stopPropagation();
                                  clearNotification(notification.id);
                                }}
                                className={`flex-shrink-0 p-1 rounded-full transition-colors ${
                                  theme === 'dark' ? 'hover:bg-gray-600' : 'hover:bg-neutral-200'
                                }`}
                              >
                                <X className={`w-4 h-4 ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-400'}`} />
                              </button>
                            </div>
                          ))
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>

              {/* User Menu Dropdown */}
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => {
                    setUserMenuOpen(!userMenuOpen);
                    setNotificationsOpen(false);
                  }}
                  className={`p-2.5 rounded-fluent transition-colors ${
                    theme === 'dark' ? 'hover:bg-gray-700' : 'hover:bg-neutral-100'
                  }`}
                >
                  <User className={`w-5 h-5 ${theme === 'dark' ? 'text-gray-300' : 'text-neutral-700'}`} />
                </button>

                {/* User Menu Dropdown Panel */}
                <AnimatePresence>
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className={`absolute right-0 mt-2 w-64 rounded-lg shadow-2xl overflow-hidden ${
                        theme === 'dark' ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-neutral-200'
                      }`}
                    >
                      {/* User Info */}
                      <div className={`px-4 py-3 border-b ${theme === 'dark' ? 'border-gray-700' : 'border-neutral-200'}`}>
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-primary-600 rounded-full flex items-center justify-center text-white font-semibold">
                            {user?.full_name ? user.full_name.charAt(0).toUpperCase() : 'U'}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`font-medium truncate ${theme === 'dark' ? 'text-white' : 'text-neutral-900'}`}>
                              {user?.full_name || 'User'}
                            </p>
                            <p className={`text-sm truncate ${theme === 'dark' ? 'text-gray-400' : 'text-neutral-500'}`}>
                              {user?.email || ''}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Menu Items */}
                      <div className="py-2">
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            navigate('/firm/settings');
                          }}
                          className={`w-full px-4 py-2.5 flex items-center gap-3 transition-colors ${
                            theme === 'dark' ? 'hover:bg-gray-700 text-gray-200' : 'hover:bg-neutral-50 text-neutral-700'
                          }`}
                        >
                          <Settings className="w-5 h-5" />
                          <span className="font-medium">Settings</span>
                        </button>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            navigate('/firm/settings');
                          }}
                          className={`w-full px-4 py-2.5 flex items-center gap-3 transition-colors ${
                            theme === 'dark' ? 'hover:bg-gray-700 text-gray-200' : 'hover:bg-neutral-50 text-neutral-700'
                          }`}
                        >
                          <Palette className="w-5 h-5" />
                          <span className="font-medium">Appearance</span>
                        </button>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            navigate('/firm/settings');
                          }}
                          className={`w-full px-4 py-2.5 flex items-center gap-3 transition-colors ${
                            theme === 'dark' ? 'hover:bg-gray-700 text-gray-200' : 'hover:bg-neutral-50 text-neutral-700'
                          }`}
                        >
                          <UserCircle className="w-5 h-5" />
                          <span className="font-medium">Profile</span>
                        </button>
                      </div>

                      {/* Logout */}
                      <div className={`py-2 border-t ${theme === 'dark' ? 'border-gray-700' : 'border-neutral-200'}`}>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            handleLogout();
                          }}
                          className={`w-full px-4 py-2.5 flex items-center gap-3 transition-colors ${
                            theme === 'dark'
                              ? 'hover:bg-red-900/30 text-red-400'
                              : 'hover:bg-red-50 text-red-600'
                          }`}
                        >
                          <LogOut className="w-5 h-5" />
                          <span className="font-medium">Logout</span>
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className={`p-8 ${theme === 'dark' ? 'bg-gray-900' : ''}`}>
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

// Layout wrapper that provides theme context
const ThemedAppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ThemeProvider>
      <AppLayout>{children}</AppLayout>
    </ThemeProvider>
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
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/accept-invitation" element={<AcceptInvitation />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/reset-password" element={<ResetPasswordPage />} />

        {/* R&D Study Client Data Collection - Public page for invited clients (no auth required) */}
        <Route path="/rd-study-data-collection" element={<RDStudyClientDataCollection />} />

        {/* Firm Portal Routes with Layout - Protected by RouteGuard */}
        <Route path="/firm/dashboard" element={<RouteGuard portalType="firm"><ThemedAppLayout><FirmDashboard /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/ai-agents" element={<RouteGuard portalType="firm"><ThemedAppLayout><AIAgentDashboard /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/clients" element={<RouteGuard portalType="firm"><ThemedAppLayout><FirmClients /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/settings" element={<RouteGuard portalType="firm"><ThemedAppLayout><FirmSettings /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/employees" element={<RouteGuard portalType="firm"><ThemedAppLayout><EmployeeManagement /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/audits" element={<RouteGuard portalType="firm"><ThemedAppLayout><FirmAudits /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/soc-engagements" element={<RouteGuard portalType="firm"><ThemedAppLayout><SOCEngagements /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/rd-studies" element={<RouteGuard portalType="firm"><ThemedAppLayout><RDStudies /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/rd-studies/:id" element={<RouteGuard portalType="firm"><ThemedAppLayout><RDStudyWorkspace /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/tax-returns" element={<RouteGuard portalType="firm"><ThemedAppLayout><TaxReturns /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/tax-returns/:id" element={<RouteGuard portalType="firm"><ThemedAppLayout><TaxReturnWorkspace /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/fraud-detection" element={<RouteGuard portalType="firm"><ThemedAppLayout><FraudDetection /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/fraud-detection/cases/:id" element={<RouteGuard portalType="firm"><ThemedAppLayout><FraudCaseWorkspace /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/group-audits" element={<RouteGuard portalType="firm"><ThemedAppLayout><GroupAuditManagement /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/reports" element={<RouteGuard portalType="firm"><ThemedAppLayout><FirmReports /></ThemedAppLayout></RouteGuard>} />
        {/* Engagement Workspace Routes - Protected by RouteGuard */}
        <Route path="/firm/engagements/:id" element={<RouteGuard portalType="firm"><ThemedAppLayout><EngagementWorkspace /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/workspace" element={<RouteGuard portalType="firm"><ThemedAppLayout><EngagementWorkspace /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/workpapers" element={<RouteGuard portalType="firm"><ThemedAppLayout><WorkpaperManager /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/analytics" element={<RouteGuard portalType="firm"><ThemedAppLayout><AnalyticalProcedures /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/testing" element={<RouteGuard portalType="firm"><ThemedAppLayout><AuditTesting /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/risk" element={<RouteGuard portalType="firm"><ThemedAppLayout><RiskAssessment /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/documents" element={<RouteGuard portalType="firm"><ThemedAppLayout><DocumentRepository /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/reports" element={<RouteGuard portalType="firm"><ThemedAppLayout><AuditReporting /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/ai-planning" element={<RouteGuard portalType="firm"><ThemedAppLayout><AIAuditPlanning /></ThemedAppLayout></RouteGuard>} />
        <Route path="/firm/engagements/:id/group-audit" element={<RouteGuard portalType="firm"><ThemedAppLayout><GroupAuditManagement /></ThemedAppLayout></RouteGuard>} />

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
