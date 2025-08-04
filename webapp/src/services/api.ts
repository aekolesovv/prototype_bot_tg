import axios from 'axios';
import {
  ScheduleResponse,
  UserProfile,
  ClubsResponse,
  TestsResponse,
  LessonsResponse,
  BookingRequest,
  BookingResponse,
  TestResult,
  TestSubmitResponse
} from '../types';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const apiService = {
  // Расписание
  async getSchedule(level?: string, userId?: string): Promise<ScheduleResponse> {
    const params = new URLSearchParams();
    if (level) params.append('level', level);
    if (userId) params.append('user_id', userId);
    
    const response = await api.get(`/schedule?${params.toString()}`);
    return response.data;
  },

  // Профиль пользователя
  async getProfile(userId: string): Promise<UserProfile> {
    const response = await api.get(`/profile?user_id=${userId}`);
    return response.data;
  },

  // Клубы
  async getClubs(): Promise<ClubsResponse> {
    const response = await api.get('/clubs');
    return response.data;
  },

  // Присоединиться к клубу
  async joinClub(clubId: number, userId: string): Promise<any> {
    const response = await api.post(`/clubs/${clubId}/join`, { user_id: userId });
    return response.data;
  },

  // Тесты
  async getTests(level?: string): Promise<TestsResponse> {
    const params = level ? `?level=${level}` : '';
    const response = await api.get(`/tests${params}`);
    return response.data;
  },

  // Уроки
  async getLessons(level?: string): Promise<LessonsResponse> {
    const params = level ? `?level=${level}` : '';
    const response = await api.get(`/lessons${params}`);
    return response.data;
  },

  // Бронирование урока
  async bookLesson(bookingData: BookingRequest): Promise<BookingResponse> {
    const response = await api.post('/book', bookingData);
    return response.data;
  },

  // Отправить результаты теста
  async submitTest(testData: TestResult): Promise<TestSubmitResponse> {
    const response = await api.post('/test', testData);
    return response.data;
  },

  // Проверка здоровья API
  async healthCheck(): Promise<any> {
    const response = await api.get('/ping');
    return response.data;
  },

  // Уведомления
  async getNotifications(userId: string): Promise<any> {
    const response = await api.get(`/notifications?user_id=${userId}`);
    return response.data;
  },

  async getNotificationSettings(userId: string): Promise<any> {
    const response = await api.get(`/notifications/settings?user_id=${userId}`);
    return response.data;
  },

  async markNotificationRead(notificationId: number, userId: string): Promise<any> {
    const response = await api.post(`/notifications/${notificationId}/read?user_id=${userId}`);
    return response.data;
  },

  async markAllNotificationsRead(userId: string): Promise<any> {
    const response = await api.post(`/notifications/read-all?user_id=${userId}`);
    return response.data;
  },

  async updateNotificationSettings(userId: string, settings: any): Promise<any> {
    const response = await api.post('/notifications/settings', {
      user_id: userId,
      ...settings
    });
    return response.data;
  },

  // CRM/LMS интеграция
  async getCRMStatus(): Promise<any> {
    const response = await api.get('/crm/status');
    return response.data;
  },

  async configureCRM(config: any): Promise<any> {
    const response = await api.post('/crm/configure', config);
    return response.data;
  },

  async testCRMConnection(): Promise<any> {
    const response = await api.get('/crm/test');
    return response.data;
  },

  async startCRMSync(): Promise<any> {
    const response = await api.get('/crm/sync/start');
    return response.data;
  },

  async stopCRMSync(): Promise<any> {
    const response = await api.get('/crm/sync/stop');
    return response.data;
  },

  async manualCRMSync(): Promise<any> {
    const response = await api.post('/crm/sync');
    return response.data;
  }
};

export default apiService; 