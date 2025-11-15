'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  FolderOpen,
  BarChart3,
  GitCompare,
  CheckCircle2,
  FileText,
  Users,
  Settings,
  Sparkles,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Engagements', href: '/dashboard/engagements', icon: FolderOpen },
  { name: 'Analytics', href: '/dashboard/analytics', icon: BarChart3 },
  { name: 'Normalize', href: '/dashboard/normalize', icon: GitCompare },
  { name: 'Quality Control', href: '/dashboard/qc', icon: CheckCircle2 },
  { name: 'Reports', href: '/dashboard/reports', icon: FileText },
  { name: 'Team', href: '/dashboard/team', icon: Users },
  { name: 'Settings', href: '/dashboard/settings', icon: Settings },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="flex h-full w-64 flex-col bg-gradient-to-b from-gray-50 to-white dark:from-gray-950 dark:to-gray-900 border-r border-gray-200 dark:border-gray-800">
      {/* Logo */}
      <div className="flex h-16 items-center border-b border-gray-200 dark:border-gray-800 px-6 bg-gradient-to-r from-purple-500/5 to-blue-500/5">
        <Link href="/dashboard" className="flex items-center space-x-3 group">
          <div className="relative flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-purple-600 to-blue-600 text-white shadow-lg group-hover:shadow-xl transition-all group-hover:scale-105">
            <Sparkles className="h-5 w-5" />
            <div className="absolute inset-0 rounded-xl bg-gradient-to-br from-purple-400 to-blue-400 opacity-0 group-hover:opacity-20 blur-sm transition-opacity"></div>
          </div>
          <span className="text-lg font-bold bg-gradient-to-r from-purple-600 to-blue-600 bg-clip-text text-transparent">
            Aura Audit AI
          </span>
        </Link>
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 px-3 py-6">
        {navigation.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(`${item.href}/`);
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                'group relative flex items-center rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200',
                isActive
                  ? 'bg-gradient-to-r from-purple-600 to-blue-600 text-white shadow-lg shadow-purple-500/30'
                  : 'text-gray-700 dark:text-gray-300 hover:bg-gradient-to-r hover:from-purple-50 hover:to-blue-50 dark:hover:from-purple-950/50 dark:hover:to-blue-950/50 hover:text-purple-700 dark:hover:text-purple-300'
              )}
            >
              {isActive && (
                <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-purple-600 to-blue-600 opacity-100 blur-md -z-10"></div>
              )}
              <item.icon
                className={cn(
                  'mr-3 h-5 w-5 flex-shrink-0 transition-all duration-200',
                  isActive
                    ? 'text-white'
                    : 'text-gray-500 dark:text-gray-400 group-hover:text-purple-600 dark:group-hover:text-purple-400 group-hover:scale-110'
                )}
              />
              <span className={isActive ? 'font-semibold' : ''}>{item.name}</span>
              {isActive && (
                <div className="ml-auto h-2 w-2 rounded-full bg-white animate-pulse"></div>
              )}
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="border-t border-gray-200 dark:border-gray-800 p-4 bg-gradient-to-r from-purple-500/5 to-blue-500/5">
        <div className="rounded-lg bg-gradient-to-br from-purple-50 to-blue-50 dark:from-purple-950/50 dark:to-blue-950/50 p-3 border border-purple-200 dark:border-purple-900">
          <div className="text-xs space-y-1">
            <div className="flex items-center justify-between">
              <span className="text-gray-600 dark:text-gray-400">Version</span>
              <span className="font-semibold text-purple-600 dark:text-purple-400">1.0.0</span>
            </div>
            <div className="pt-2 text-gray-500 dark:text-gray-500 text-center">
              © 2024 Aura Audit AI
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
