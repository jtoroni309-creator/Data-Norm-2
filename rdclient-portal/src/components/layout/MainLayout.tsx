/**
 * Main Layout Component
 * Provides the navigation sidebar and header for authenticated pages
 */

import { useState, useRef, useEffect } from 'react';
import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  ClipboardCheck,
  FolderKanban,
  Users,
  FileText,
  Upload,
  Settings,
  LogOut,
  Menu,
  X,
  Bell,
  User,
  ChevronRight,
  HelpCircle,
  FlaskConical,
} from 'lucide-react';
import { useAuthStore } from '../../store/auth';
import authService from '../../services/auth.service';
import toast from 'react-hot-toast';

interface NavItem {
  id: string;
  label: string;
  icon: React.ElementType;
  path: string;
  badge?: number;
}

const navigation: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
  { id: 'eligibility', label: 'Eligibility', icon: ClipboardCheck, path: '/eligibility' },
  { id: 'projects', label: 'R&D Projects', icon: FolderKanban, path: '/projects' },
  { id: 'employees', label: 'Employees', icon: Users, path: '/employees' },
  { id: 'tax-returns', label: 'Tax Returns', icon: FileText, path: '/tax-returns' },
  { id: 'documents', label: 'Documents', icon: Upload, path: '/documents' },
  { id: 'team', label: 'Team', icon: Users, path: '/team' },
];

interface MainLayoutProps {
  children: React.ReactNode;
}

export default function MainLayout({ children }: MainLayoutProps) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const userMenuRef = useRef<HTMLDivElement>(null);
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  // Close user menu when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setUserMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleLogout = async () => {
    try {
      await authService.logout();
    } finally {
      logout();
      toast.success('Logged out successfully');
      navigate('/login');
    }
  };

  const getPageTitle = () => {
    const currentNav = navigation.find((item) => item.path === location.pathname);
    return currentNav?.label || 'Dashboard';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Mobile Menu Overlay */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-black/50 lg:hidden"
            onClick={() => setMobileMenuOpen(false)}
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{
          width: sidebarOpen ? 280 : 72,
          x: mobileMenuOpen ? 0 : (typeof window !== 'undefined' && window.innerWidth < 1024 ? -280 : 0),
        }}
        transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
        className={`fixed top-0 left-0 h-screen z-50 bg-white border-r border-gray-200 flex flex-col
          lg:translate-x-0 ${mobileMenuOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}`}
      >
        {/* Logo Area */}
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-100">
          <AnimatePresence mode="wait">
            {sidebarOpen && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="flex items-center gap-3"
              >
                <div className="w-10 h-10 bg-gradient-to-br from-primary-600 to-accent-600 rounded-xl flex items-center justify-center">
                  <FlaskConical className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h1 className="text-lg font-bold text-gray-900">Aura AI</h1>
                  <p className="text-xs text-gray-500">R&D Tax Credit Portal</p>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors hidden lg:flex"
          >
            <Menu className="w-5 h-5 text-gray-600" />
          </button>
          <button
            onClick={() => setMobileMenuOpen(false)}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors lg:hidden"
          >
            <X className="w-5 h-5 text-gray-600" />
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
          {navigation.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;

            return (
              <NavLink
                key={item.id}
                to={item.path}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-all duration-150 group
                  ${isActive
                    ? 'bg-primary-50 text-primary-700 font-semibold'
                    : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                title={!sidebarOpen ? item.label : undefined}
              >
                <Icon className={`w-5 h-5 flex-shrink-0 ${isActive ? 'text-primary-600' : 'text-gray-500 group-hover:text-gray-700'}`} />
                <AnimatePresence mode="wait">
                  {sidebarOpen && (
                    <motion.span
                      initial={{ opacity: 0, width: 0 }}
                      animate={{ opacity: 1, width: 'auto' }}
                      exit={{ opacity: 0, width: 0 }}
                      className="whitespace-nowrap overflow-hidden"
                    >
                      {item.label}
                    </motion.span>
                  )}
                </AnimatePresence>
                {item.badge && sidebarOpen && (
                  <span className="ml-auto bg-primary-100 text-primary-700 text-xs font-medium px-2 py-0.5 rounded-full">
                    {item.badge}
                  </span>
                )}
                {isActive && sidebarOpen && (
                  <motion.div
                    layoutId="activeIndicator"
                    className="ml-auto w-1 h-4 bg-primary-600 rounded-full"
                  />
                )}
              </NavLink>
            );
          })}
        </nav>

        {/* Bottom Section */}
        <div className="p-3 border-t border-gray-100">
          <NavLink
            to="/settings"
            className={`flex items-center gap-3 px-3 py-2.5 rounded-lg transition-colors
              ${location.pathname === '/settings'
                ? 'bg-primary-50 text-primary-700'
                : 'text-gray-600 hover:bg-gray-100'
              }`}
            title={!sidebarOpen ? 'Settings' : undefined}
          >
            <Settings className="w-5 h-5" />
            {sidebarOpen && <span>Settings</span>}
          </NavLink>

          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-red-600 hover:bg-red-50 transition-colors mt-1"
            title={!sidebarOpen ? 'Logout' : undefined}
          >
            <LogOut className="w-5 h-5" />
            {sidebarOpen && <span>Logout</span>}
          </button>
        </div>
      </motion.aside>

      {/* Main Content */}
      <motion.main
        animate={{ marginLeft: sidebarOpen ? 280 : 72 }}
        transition={{ duration: 0.2, ease: [0.4, 0, 0.2, 1] }}
        className="min-h-screen lg:ml-[280px]"
        style={{ marginLeft: typeof window !== 'undefined' && window.innerWidth < 1024 ? 0 : undefined }}
      >
        {/* Header */}
        <header className="sticky top-0 z-30 h-16 bg-white/95 backdrop-blur-sm border-b border-gray-200">
          <div className="h-full flex items-center justify-between px-4 lg:px-6">
            {/* Mobile menu button */}
            <button
              onClick={() => setMobileMenuOpen(true)}
              className="p-2 rounded-lg hover:bg-gray-100 transition-colors lg:hidden"
            >
              <Menu className="w-5 h-5 text-gray-600" />
            </button>

            {/* Page Title */}
            <div className="flex items-center gap-2">
              <h2 className="text-lg font-semibold text-gray-900">{getPageTitle()}</h2>
            </div>

            {/* Header Actions */}
            <div className="flex items-center gap-2">
              {/* Help */}
              <button className="p-2 rounded-lg hover:bg-gray-100 transition-colors" title="Help">
                <HelpCircle className="w-5 h-5 text-gray-600" />
              </button>

              {/* Notifications */}
              <button className="relative p-2 rounded-lg hover:bg-gray-100 transition-colors" title="Notifications">
                <Bell className="w-5 h-5 text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-red-500 rounded-full" />
              </button>

              {/* User Menu */}
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                >
                  <div className="w-8 h-8 bg-gradient-to-br from-primary-500 to-accent-500 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                    {user?.full_name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <ChevronRight className={`w-4 h-4 text-gray-400 transition-transform ${userMenuOpen ? 'rotate-90' : ''}`} />
                </button>

                <AnimatePresence>
                  {userMenuOpen && (
                    <motion.div
                      initial={{ opacity: 0, y: -10, scale: 0.95 }}
                      animate={{ opacity: 1, y: 0, scale: 1 }}
                      exit={{ opacity: 0, y: -10, scale: 0.95 }}
                      transition={{ duration: 0.15 }}
                      className="absolute right-0 mt-2 w-64 bg-white rounded-xl shadow-lg border border-gray-200 overflow-hidden"
                    >
                      <div className="p-4 border-b border-gray-100">
                        <p className="font-semibold text-gray-900">{user?.full_name || 'User'}</p>
                        <p className="text-sm text-gray-500">{user?.email}</p>
                        <p className="text-xs text-gray-400 mt-1">{user?.company_name}</p>
                      </div>
                      <div className="p-2">
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            navigate('/settings');
                          }}
                          className="w-full flex items-center gap-3 px-3 py-2 text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
                        >
                          <User className="w-4 h-4" />
                          <span>Profile Settings</span>
                        </button>
                        <button
                          onClick={() => {
                            setUserMenuOpen(false);
                            handleLogout();
                          }}
                          className="w-full flex items-center gap-3 px-3 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span>Logout</span>
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="p-4 lg:p-6">
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              {children}
            </motion.div>
          </AnimatePresence>
        </div>
      </motion.main>
    </div>
  );
}
