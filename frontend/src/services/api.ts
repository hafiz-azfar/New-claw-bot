export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';
export const WS_BASE_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

import axios from 'axios';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add JWT token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authService = {
  login: async (email: string, password: string) => {
    const response = await api.post('/auth/login/', { email, password });
    if (response.data.access) {
      localStorage.setItem('access_token', response.data.access);
      localStorage.setItem('refresh_token', response.data.refresh);
      localStorage.setItem('user_role', response.data.user.role);
    }
    return response.data;
  },

  register: async (userData: any) => {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  },

  logout: () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    localStorage.removeItem('user_role');
  },

  getCurrentUser: async () => {
    const response = await api.get('/auth/me/');
    return response.data;
  },

  resetPassword: async (email: string) => {
    const response = await api.post('/auth/password/reset/', { email });
    return response.data;
  },
};

export const courseService = {
  getAllCourses: async () => {
    const response = await api.get('/courses/');
    return response.data;
  },

  getCourseById: async (id: number) => {
    const response = await api.get(`/courses/${id}/`);
    return response.data;
  },

  getModules: async (courseId: number) => {
    const response = await api.get(`/courses/${courseId}/modules/`);
    return response.data;
  },

  submitQuizAttempt: async (quizId: number, answers: number[]) => {
    const response = await api.post(`/quizzes/${quizId}/attempt/`, { answers });
    return response.data;
  },
};

export const liveSessionService = {
  getLiveSessions: async () => {
    const response = await api.get('/live-sessions/');
    return response.data;
  },

  createSession: async (data: { course_id: number; title: string; scheduled_at: string }) => {
    const response = await api.post('/live-sessions/', data);
    return response.data;
  },

  getSessionToken: async (sessionId: number) => {
    const response = await api.post(`/live-sessions/${sessionId}/token/`);
    return response.data;
  },

  joinSession: async (sessionId: number) => {
    const response = await api.post(`/live-sessions/${sessionId}/join/`);
    return response.data;
  },

  endSession: async (sessionId: number) => {
    const response = await api.post(`/live-sessions/${sessionId}/end/`);
    return response.data;
  },

  toggleRecording: async (sessionId: number) => {
    const response = await api.post(`/live-sessions/${sessionId}/toggle-recording/`);
    return response.data;
  },

  launchMCQ: async (sessionId: number, quizId: number) => {
    const response = await api.post(`/live-sessions/${sessionId}/launch-mcq/`, { quiz_id: quizId });
    return response.data;
  },
};

export const messagingService = {
  getChatHistory: async (courseId: number) => {
    const response = await api.get(`/messaging/courses/${courseId}/history/`);
    return response.data;
  },

  sendMessage: async (courseId: number, content: string) => {
    const response = await api.post(`/messaging/courses/${courseId}/messages/`, { content });
    return response.data;
  },

  flagMessage: async (messageId: number, reason: string) => {
    const response = await api.post(`/messaging/messages/${messageId}/flag/`, { reason });
    return response.data;
  },
};

export const attendanceService = {
  getSessionAttendance: async (sessionId: number) => {
    const response = await api.get(`/live-sessions/${sessionId}/attendance/`);
    return response.data;
  },

  exportAttendance: async (sessionId: number) => {
    const response = await api.get(`/live-sessions/${sessionId}/attendance/export/`, {
      responseType: 'blob',
    });
    return response.data;
  },
};

export default api;
