import axios, { AxiosInstance, AxiosRequestConfig, AxiosError } from 'axios';
import Cookies from 'js-cookie';

class APIService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        const token = Cookies.get('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        return response;
      },
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle token refresh or redirect to login
          Cookies.remove('access_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth
  async login(username: string, password: string) {
    const response = await this.client.post('/auth/login/', {
      username,
      password,
    });
    return response.data;
  }

  async logout() {
    const response = await this.client.post('/auth/logout/');
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/current/');
    return response.data;
  }

  // Applications
  async getApplications(params?: Record<string, any>) {
    const response = await this.client.get('/applications/', { params });
    return response.data;
  }

  async getApplication(id: number) {
    const response = await this.client.get(`/applications/${id}/`);
    return response.data;
  }

  async createApplication(data: any) {
    const response = await this.client.post('/applications/', data);
    return response.data;
  }

  async updateApplication(id: number, data: any) {
    const response = await this.client.patch(`/applications/${id}/`, data);
    return response.data;
  }

  async getApplicationStats() {
    const response = await this.client.get('/applications/stats/');
    return response.data;
  }

  // Documents
  async getDocumentTemplates() {
    const response = await this.client.get('/documents/templates/');
    return response.data;
  }

  async getDocumentTemplate(code: string) {
    const response = await this.client.get(`/documents/templates/${code}/`);
    return response.data;
  }

  async getDocuments() {
    const response = await this.client.get('/documents/');
    return response.data;
  }

  async generateDocument(data: any) {
    const response = await this.client.post('/documents/', data);
    return response.data;
  }

  async downloadDocument(id: number) {
    const response = await this.client.get(`/documents/${id}/download/`, {
      responseType: 'blob',
    });
    return response.data;
  }

  // Notifications
  async getNotifications() {
    const response = await this.client.get('/notifications/');
    return response.data;
  }

  async getUnreadNotificationCount() {
    const response = await this.client.get('/notifications/unread-count/');
    return response.data;
  }

  async markNotificationAsRead(id: number) {
    const response = await this.client.post(`/notifications/${id}/read/`);
    return response.data;
  }

  async markAllNotificationsAsRead() {
    const response = await this.client.post('/notifications/mark-all-read/');
    return response.data;
  }

  // AI Chat
  async sendAIMessage(message: string, sessionId?: string, applicationId?: number) {
    const response = await this.client.post('/ai/chat/', {
      message,
      session_id: sessionId,
      application_id: applicationId,
    });
    return response.data;
  }

  async getAIConversations() {
    const response = await this.client.get('/ai/conversations/');
    return response.data;
  }

  async getAIConversationHistory(sessionId: string) {
    const response = await this.client.get(`/ai/conversations/${sessionId}/history/`);
    return response.data;
  }

  async closeAIConversation(sessionId: string) {
    const response = await this.client.post(`/ai/conversations/${sessionId}/close/`);
    return response.data;
  }

  // Profile
  async getProfile() {
    const response = await this.client.get('/auth/profile/');
    return response.data;
  }

  async updateProfile(data: any) {
    const response = await this.client.patch('/auth/profile/', data);
    return response.data;
  }

  // Users
  async getUsers() {
    const response = await this.client.get('/auth/users/');
    return response.data;
  }

  async getUser(id: number) {
    const response = await this.client.get(`/auth/users/${id}/`);
    return response.data;
  }
}

export const apiService = new APIService();
export default apiService;