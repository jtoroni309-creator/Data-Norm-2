/**
 * Service Context - Manages enabled services per firm
 * Fetches firm's enabled_services from the API and provides access control
 */
import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import toast from 'react-hot-toast';

// Service ID to route mapping
export const SERVICE_ROUTES: Record<string, string[]> = {
  'core-financial-audit': ['/firm/audits', '/firm/engagements'],
  'ai-assistant': ['/firm/ai-agents'],
  'edgar-integration': [], // Used within other pages
  'rd-study-automation': ['/firm/rd-studies'],
  'client-portal': [], // Client portal access
  'risk-assessment': ['/firm/engagements'], // Risk assessment within engagements
  'tax-optimization': ['/firm/tax-returns'],
  'fraud-detection': ['/firm/fraud-detection'],
  'soc-compliance': ['/firm/soc-engagements'],
  'group-audit': ['/firm/group-audits'],
};

// Navigation item to service mapping
export const NAV_SERVICE_MAP: Record<string, string> = {
  'ai-agents': 'ai-assistant',
  'audits': 'core-financial-audit',
  'group-audits': 'group-audit',
  'soc': 'soc-compliance',
  'rd-studies': 'rd-study-automation',
  'tax-returns': 'tax-optimization',
  'fraud-detection': 'fraud-detection',
};

// Services that are always enabled (core features)
const ALWAYS_ENABLED = ['dashboard', 'clients', 'employees', 'reports', 'settings'];

interface ServiceContextType {
  enabledServices: Record<string, boolean>;
  isServiceEnabled: (serviceId: string) => boolean;
  isNavItemEnabled: (navId: string) => boolean;
  isRouteEnabled: (route: string) => boolean;
  loading: boolean;
  refreshServices: () => Promise<void>;
  firmName: string | null;
}

const ServiceContext = createContext<ServiceContextType>({
  enabledServices: {},
  isServiceEnabled: () => true,
  isNavItemEnabled: () => true,
  isRouteEnabled: () => true,
  loading: true,
  refreshServices: async () => {},
  firmName: null,
});

export const useServices = () => useContext(ServiceContext);

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';

export const ServiceProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [enabledServices, setEnabledServices] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [firmName, setFirmName] = useState<string | null>(null);

  const fetchServices = useCallback(async () => {
    const token = localStorage.getItem('access_token') || localStorage.getItem('token');
    if (!token) {
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/identity/organizations/me/details`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setEnabledServices(data.enabled_services || {});
        setFirmName(data.firm_name || null);
      } else if (response.status === 401) {
        // Token expired or invalid
        console.warn('Session expired, please log in again');
      } else {
        console.warn('Failed to fetch firm services');
      }
    } catch (error) {
      console.error('Error fetching services:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchServices();
  }, [fetchServices]);

  // Listen for storage changes (login/logout)
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'access_token' || e.key === 'token') {
        fetchServices();
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, [fetchServices]);

  const isServiceEnabled = useCallback((serviceId: string): boolean => {
    // If no services configured, assume all are enabled (backwards compatibility)
    if (Object.keys(enabledServices).length === 0) {
      return true;
    }
    // Check if explicitly enabled (true) or not configured (default to enabled)
    return enabledServices[serviceId] !== false;
  }, [enabledServices]);

  const isNavItemEnabled = useCallback((navId: string): boolean => {
    // Always-enabled items
    if (ALWAYS_ENABLED.includes(navId)) {
      return true;
    }
    // Map nav item to service
    const serviceId = NAV_SERVICE_MAP[navId];
    if (!serviceId) {
      return true; // Unknown nav items default to enabled
    }
    return isServiceEnabled(serviceId);
  }, [isServiceEnabled]);

  const isRouteEnabled = useCallback((route: string): boolean => {
    // Check if route matches any disabled service
    for (const [serviceId, routes] of Object.entries(SERVICE_ROUTES)) {
      if (routes.some(r => route.startsWith(r))) {
        if (!isServiceEnabled(serviceId)) {
          return false;
        }
      }
    }
    return true;
  }, [isServiceEnabled]);

  const refreshServices = useCallback(async () => {
    setLoading(true);
    await fetchServices();
  }, [fetchServices]);

  return (
    <ServiceContext.Provider
      value={{
        enabledServices,
        isServiceEnabled,
        isNavItemEnabled,
        isRouteEnabled,
        loading,
        refreshServices,
        firmName,
      }}
    >
      {children}
    </ServiceContext.Provider>
  );
};

// Service Guard Component - Blocks access to disabled services
export const ServiceGuard: React.FC<{
  serviceId: string;
  children: React.ReactNode;
  fallback?: React.ReactNode;
}> = ({ serviceId, children, fallback }) => {
  const { isServiceEnabled, loading } = useServices();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
      </div>
    );
  }

  if (!isServiceEnabled(serviceId)) {
    if (fallback) {
      return <>{fallback}</>;
    }
    return (
      <div className="flex flex-col items-center justify-center h-64 text-center">
        <div className="w-16 h-16 bg-neutral-100 dark:bg-gray-700 rounded-full flex items-center justify-center mb-4">
          <svg className="w-8 h-8 text-neutral-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-neutral-700 dark:text-gray-200 mb-2">
          Service Not Available
        </h3>
        <p className="text-neutral-500 dark:text-gray-400 max-w-md">
          This feature is not enabled for your organization. Contact your administrator or upgrade your subscription to access this feature.
        </p>
      </div>
    );
  }

  return <>{children}</>;
};

export default ServiceContext;
