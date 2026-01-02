import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { toast } from 'react-hot-toast';
import apiService from '@/services/api';
import { Application, ApplicationStats, PaginatedResponse } from '@/types/api';

export const useApplications = (filters?: Record<string, any>) => {
  return useQuery<PaginatedResponse<Application>>({
    queryKey: ['applications', filters],
    queryFn: () => apiService.getApplications(filters),
    keepPreviousData: true,
  });
};

export const useApplication = (id: number) => {
  return useQuery<Application>({
    queryKey: ['application', id],
    queryFn: () => apiService.getApplication(id),
  });
};

export const useApplicationStats = () => {
  return useQuery<ApplicationStats>({
    queryKey: ['applicationStats'],
    queryFn: apiService.getApplicationStats,
  });
};

export const useCreateApplication = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: apiService.createApplication,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['applicationStats'] });
      toast.success('Заявка успешно создана');
    },
    onError: (error) => {
      toast.error('Ошибка при создании заявки');
    },
  });
};

export const useUpdateApplication = (id: number) => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: Partial<Application>) => apiService.updateApplication(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['application', id] });
      queryClient.invalidateQueries({ queryKey: ['applications'] });
      queryClient.invalidateQueries({ queryKey: ['applicationStats'] });
      toast.success('Заявка обновлена');
    },
    onError: (error) => {
      toast.error('Ошибка при обновлении заявки');
    },
  });
};

export const useApplicationHistory = (id: number) => {
  return useQuery({
    queryKey: ['applicationHistory', id],
    queryFn: () => apiService.getApplicationHistory(id),
  });
};

export const useApplicationComments = (id: number) => {
  return useQuery({
    queryKey: ['applicationComments', id],
    queryFn: () => apiService.getApplicationComments(id),
  });
};