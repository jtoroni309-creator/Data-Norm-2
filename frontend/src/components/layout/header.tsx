'use client';

import { Bell, Moon, Sun, LogOut, User, Settings } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useAuth } from '@/hooks/use-auth';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { getInitials } from '@/lib/utils';

export function Header() {
  const { theme, setTheme } = useTheme();
  const { user, logout } = useAuth();

  return (
    <header className="flex h-16 items-center justify-between border-b bg-card px-6">
      {/* Left side - could add breadcrumbs here */}
      <div className="flex-1">
        <h2 className="text-xl font-semibold">Welcome back, {user?.full_name?.split(' ')[0] || 'User'}!</h2>
      </div>

      {/* Right side - actions */}
      <div className="flex items-center space-x-4">
        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="icon"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
          title="Toggle theme"
        >
          {theme === 'dark' ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="icon" title="Notifications">
          <Bell className="h-5 w-5" />
        </Button>

        {/* User Menu */}
        <div className="flex items-center space-x-3">
          <div className="hidden text-right md:block">
            <p className="text-sm font-medium">{user?.full_name || 'User'}</p>
            <p className="text-xs text-muted-foreground">{user?.email}</p>
          </div>

          <div className="relative group">
            <Avatar className="h-10 w-10 cursor-pointer ring-2 ring-transparent transition-all group-hover:ring-primary">
              <AvatarFallback className="bg-primary text-primary-foreground">
                {getInitials(user?.full_name || 'User')}
              </AvatarFallback>
            </Avatar>

            {/* Dropdown Menu */}
            <div className="absolute right-0 top-12 z-50 hidden w-56 rounded-md border bg-card shadow-lg group-hover:block">
              <div className="p-2">
                <button
                  className="flex w-full items-center rounded-md px-3 py-2 text-sm hover:bg-accent"
                  onClick={() => window.location.href = '/dashboard/profile'}
                >
                  <User className="mr-2 h-4 w-4" />
                  Profile
                </button>
                <button
                  className="flex w-full items-center rounded-md px-3 py-2 text-sm hover:bg-accent"
                  onClick={() => window.location.href = '/dashboard/settings'}
                >
                  <Settings className="mr-2 h-4 w-4" />
                  Settings
                </button>
                <div className="my-1 h-px bg-border" />
                <button
                  className="flex w-full items-center rounded-md px-3 py-2 text-sm text-destructive hover:bg-destructive/10"
                  onClick={logout}
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign out
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}
