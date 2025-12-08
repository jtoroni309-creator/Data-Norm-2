/**
 * R&D Client Portal - Main Application
 *
 * A professional portal for R&D Tax Credit clients to:
 * - Complete eligibility questionnaires
 * - Add and describe R&D projects with AI assistance
 * - Manage team members
 * - Upload tax returns and supporting documents
 */

import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AnimatePresence } from 'framer-motion';
import { useAuthStore } from './store/auth';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import ForgotPasswordPage from './pages/ForgotPasswordPage';
import ResetPasswordPage from './pages/ResetPasswordPage';
import DashboardPage from './pages/DashboardPage';
import EligibilityPage from './pages/EligibilityPage';
import ProjectsPage from './pages/ProjectsPage';
import EmployeesPage from './pages/EmployeesPage';
import TaxReturnsPage from './pages/TaxReturnsPage';
import DocumentsPage from './pages/DocumentsPage';
import TeamPage from './pages/TeamPage';
import SettingsPage from './pages/SettingsPage';

// Layout
import MainLayout from './components/layout/MainLayout';

// Protected Route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();
  const location = useLocation();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <>{children}</>;
}

// Public Route wrapper (redirect if already logged in)
function PublicRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuthStore();

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

// App initialization
function AppInit() {
  const { setLoading, token } = useAuthStore();

  useEffect(() => {
    // Check if we have a stored token and validate it
    const initAuth = async () => {
      if (token) {
        try {
          // Token exists, keep user logged in
          setLoading(false);
        } catch {
          // Invalid token, logout
          useAuthStore.getState().logout();
        }
      } else {
        setLoading(false);
      }
    };

    initAuth();
  }, [token, setLoading]);

  return null;
}

function App() {
  return (
    <BrowserRouter>
      <AppInit />
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#fff',
            color: '#171717',
            borderRadius: '8px',
            padding: '12px 16px',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            fontSize: '0.875rem',
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

      <AnimatePresence mode="wait">
        <Routes>
          {/* Public Routes */}
          <Route
            path="/login"
            element={
              <PublicRoute>
                <LoginPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          <Route
            path="/register/:token"
            element={
              <PublicRoute>
                <RegisterPage />
              </PublicRoute>
            }
          />
          <Route path="/forgot-password" element={<ForgotPasswordPage />} />
          <Route path="/reset-password" element={<ResetPasswordPage />} />
          <Route path="/reset-password/:token" element={<ResetPasswordPage />} />

          {/* Protected Routes with Layout */}
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <DashboardPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/eligibility"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <EligibilityPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/projects"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <ProjectsPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/employees"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <EmployeesPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/tax-returns"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <TaxReturnsPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/documents"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <DocumentsPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/team"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <TeamPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <ProtectedRoute>
                <MainLayout>
                  <SettingsPage />
                </MainLayout>
              </ProtectedRoute>
            }
          />

          {/* Default redirect */}
          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </AnimatePresence>
    </BrowserRouter>
  );
}

export default App;
