import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useRouter } from 'next/navigation';
import Cookies from 'js-cookie';
import apiService from '@/services/api';
import { User, LoginRequest, LoginResponse } from '@/types/api';

export const useAuth = () => {
  const router = useRouter();
  const queryClient = useQueryClient();

  const { data: user, isLoading, error } = useQuery<User>({
    queryKey: ['currentUser'],
    queryFn: apiService.getCurrentUser,
    retry: false,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  const loginMutation = useMutation<LoginResponse, Error, LoginRequest>({
    mutationFn: (credentials) => apiService.login(credentials.username, credentials.password),
    onSuccess: (data) => {
      Cookies.set('access_token', data.access_token, { expires: 7 });
      queryClient.setQueryData(['currentUser'], data.user);
      router.push('/dashboard');
    },
  });

  const logoutMutation = useMutation({
    mutationFn: apiService.logout,
    onSuccess: () => {
      Cookies.remove('access_token');
      queryClient.clear();
      router.push('/login');
    },
  });

  const isAuthenticated = !!user && !error;

  return {
    user,
    isLoading,
    error,
    isAuthenticated,
    login: loginMutation.mutate,
    logout: logoutMutation.mutate,
    loginPending: loginMutation.isPending,
  };
};

export const useProfile = () => {
  return useQuery({
    queryKey: ['profile'],
    queryFn: apiService.getProfile,
  });
};