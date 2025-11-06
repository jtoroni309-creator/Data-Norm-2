import { useAuthStore } from '@/store/auth-store';
import { useMutation, useQuery } from '@tanstack/react-query';
import { api } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { toast } from 'sonner';

export function useAuth() {
  const router = useRouter();
  const { user, token, isAuthenticated, login, logout, setLoading } = useAuthStore();

  // Login mutation
  const loginMutation = useMutation({
    mutationFn: async ({ email, password }: { email: string; password: string }) => {
      setLoading(true);
      try {
        const response = await api.auth.login({ email, password });
        return response;
      } finally {
        setLoading(false);
      }
    },
    onSuccess: (data) => {
      login(data.user, data.access_token);
      toast.success('Login successful!');
      router.push('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Login failed. Please try again.');
    },
  });

  // Register mutation
  const registerMutation = useMutation({
    mutationFn: async ({ email, password, full_name }: { email: string; password: string; full_name: string }) => {
      setLoading(true);
      try {
        const response = await api.auth.register({ email, password, full_name });
        return response;
      } finally {
        setLoading(false);
      }
    },
    onSuccess: (data) => {
      login(data.user, data.access_token);
      toast.success('Account created successfully!');
      router.push('/dashboard');
    },
    onError: (error: any) => {
      toast.error(error.response?.data?.message || 'Registration failed. Please try again.');
    },
  });

  // Logout function
  const handleLogout = async () => {
    try {
      await api.auth.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      logout();
      toast.success('Logged out successfully');
      router.push('/login');
    }
  };

  // Get current user
  const { data: currentUser, isLoading: isLoadingUser } = useQuery({
    queryKey: ['currentUser'],
    queryFn: () => api.auth.me(),
    enabled: isAuthenticated && !!token,
    retry: false,
  });

  return {
    user: currentUser || user,
    isAuthenticated,
    isLoading: isLoadingUser || loginMutation.isPending || registerMutation.isPending,
    login: loginMutation.mutate,
    register: registerMutation.mutate,
    logout: handleLogout,
    loginError: loginMutation.error,
    registerError: registerMutation.error,
  };
}
