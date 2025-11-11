import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, Bell, Moon, Sun, Menu } from 'lucide-react';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';

interface HeaderProps {
  onMenuClick?: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onMenuClick }) => {
  const [darkMode, setDarkMode] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  const notifications = [
    { id: 1, title: 'New user registered', time: '5 min ago', unread: true },
    { id: 2, title: 'System update available', time: '1 hour ago', unread: true },
    { id: 3, title: 'Backup completed', time: '2 hours ago', unread: false },
  ];

  const unreadCount = notifications.filter((n) => n.unread).length;

  return (
    <header className="fixed top-0 left-64 right-0 h-16 bg-surface elevation-2 z-30">
      <div className="flex items-center justify-between h-full px-6">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <Input
            variant="outlined"
            placeholder="Search users, tickets, reports..."
            icon={<Search size={18} />}
            iconPosition="left"
            className="bg-surface-container-low"
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 ml-6">
          {/* Dark Mode Toggle */}
          <Button
            variant="text"
            size="small"
            onClick={() => setDarkMode(!darkMode)}
            icon={darkMode ? <Sun size={18} /> : <Moon size={18} />}
          />

          {/* Notifications */}
          <div className="relative">
            <Button
              variant="text"
              size="small"
              onClick={() => setShowNotifications(!showNotifications)}
              icon={<Bell size={18} />}
            />
            {unreadCount > 0 && (
              <span className="absolute top-0 right-0 w-5 h-5 bg-error-500 text-white text-xs font-medium rounded-full flex items-center justify-center">
                {unreadCount}
              </span>
            )}

            <AnimatePresence>
              {showNotifications && (
                <motion.div
                  initial={{ opacity: 0, y: -10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  exit={{ opacity: 0, y: -10, scale: 0.95 }}
                  className="absolute right-0 mt-2 w-80 bg-surface rounded-2xl elevation-4 overflow-hidden"
                >
                  <div className="p-4 border-b border-neutral-200">
                    <h3 className="text-lg font-semibold text-neutral-900">Notifications</h3>
                  </div>
                  <div className="max-h-96 overflow-y-auto">
                    {notifications.map((notification) => (
                      <div
                        key={notification.id}
                        className={`p-4 border-b border-neutral-200 hover:bg-surface-container-low cursor-pointer transition-colors ${
                          notification.unread ? 'bg-primary-50' : ''
                        }`}
                      >
                        <div className="flex items-start gap-3">
                          {notification.unread && (
                            <div className="w-2 h-2 mt-2 bg-primary-500 rounded-full" />
                          )}
                          <div className="flex-1">
                            <p className="text-sm font-medium text-neutral-900">
                              {notification.title}
                            </p>
                            <p className="text-xs text-neutral-600 mt-1">{notification.time}</p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="p-4">
                    <Button variant="text" size="small" fullWidth>
                      View all notifications
                    </Button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>
          </div>

          {/* Quick Actions */}
          <Button variant="filled" size="small">
            Quick Actions
          </Button>
        </div>
      </div>
    </header>
  );
};
