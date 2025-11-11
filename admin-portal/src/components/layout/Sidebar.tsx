import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import {
  LayoutDashboard,
  Users,
  Ticket,
  BarChart3,
  Settings,
  Database,
  Activity,
  Shield,
  FileText,
} from 'lucide-react';

interface NavItem {
  icon: React.ReactNode;
  label: string;
  path: string;
  badge?: string;
}

const navItems: NavItem[] = [
  {
    icon: <LayoutDashboard size={20} />,
    label: 'Dashboard',
    path: '/',
  },
  {
    icon: <Users size={20} />,
    label: 'User Management',
    path: '/users',
  },
  {
    icon: <Ticket size={20} />,
    label: 'Tickets',
    path: '/tickets',
  },
  {
    icon: <BarChart3 size={20} />,
    label: 'Analytics',
    path: '/analytics',
  },
  {
    icon: <Database size={20} />,
    label: 'Data Management',
    path: '/data',
  },
  {
    icon: <Activity size={20} />,
    label: 'System Health',
    path: '/health',
  },
  {
    icon: <Shield size={20} />,
    label: 'Security',
    path: '/security',
  },
  {
    icon: <FileText size={20} />,
    label: 'Reports',
    path: '/reports',
  },
  {
    icon: <Settings size={20} />,
    label: 'Settings',
    path: '/settings',
  },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <aside className="fixed left-0 top-0 h-screen w-64 bg-surface elevation-2 z-40">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="p-6 border-b border-neutral-200">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-secondary-500 flex items-center justify-center">
              <span className="text-white font-bold text-lg">DN</span>
            </div>
            <div>
              <h1 className="text-lg font-semibold text-neutral-900">Data-Norm</h1>
              <p className="text-xs text-neutral-600">Admin Portal</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 overflow-y-auto">
          <ul className="space-y-1">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              return (
                <li key={item.path}>
                  <Link to={item.path}>
                    <motion.div
                      whileHover={{ x: 4 }}
                      whileTap={{ scale: 0.98 }}
                      className={`
                        flex items-center gap-3 px-4 py-3 rounded-xl transition-all
                        ${
                          isActive
                            ? 'bg-secondary-100 text-secondary-700 font-medium elevation-1'
                            : 'text-neutral-700 hover:bg-surface-container-high'
                        }
                      `}
                    >
                      <span className={isActive ? 'text-secondary-700' : 'text-neutral-600'}>
                        {item.icon}
                      </span>
                      <span>{item.label}</span>
                      {item.badge && (
                        <span className="ml-auto px-2 py-0.5 text-xs font-medium bg-error-100 text-error-700 rounded-full">
                          {item.badge}
                        </span>
                      )}
                    </motion.div>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-neutral-200">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-surface-container-high">
            <div className="w-8 h-8 rounded-full bg-primary-200 flex items-center justify-center">
              <span className="text-primary-700 font-medium text-sm">AD</span>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-neutral-900 truncate">Admin User</p>
              <p className="text-xs text-neutral-600 truncate">admin@datanorm.com</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  );
};
