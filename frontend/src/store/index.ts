import { create } from 'zustand';
import { authService, courseService, liveSessionService } from '../services/api';

interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  role: 'owner' | 'admin' | 'teacher' | 'student';
}

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  checkAuth: () => Promise<void>;
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  isAuthenticated: false,
  isLoading: true,
  
  login: async (email: string, password: string) => {
    set({ isLoading: true });
    try {
      const data = await authService.login(email, password);
      set({ 
        user: data.user, 
        isAuthenticated: true, 
        isLoading: false 
      });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  
  logout: () => {
    authService.logout();
    set({ user: null, isAuthenticated: false });
  },
  
  checkAuth: async () => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      set({ isLoading: false });
      return;
    }
    
    try {
      const user = await authService.getCurrentUser();
      set({ user, isAuthenticated: true, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      authService.logout();
    }
  },
}));

interface CourseState {
  courses: any[];
  currentCourse: any | null;
  isLoading: boolean;
  fetchCourses: () => Promise<void>;
  fetchCourse: (id: number) => Promise<void>;
}

export const useCourseStore = create<CourseState>((set) => ({
  courses: [],
  currentCourse: null,
  isLoading: false,
  
  fetchCourses: async () => {
    set({ isLoading: true });
    try {
      const courses = await courseService.getAllCourses();
      set({ courses, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
  
  fetchCourse: async (id: number) => {
    set({ isLoading: true });
    try {
      const course = await courseService.getCourseById(id);
      set({ currentCourse: course, isLoading: false });
    } catch (error) {
      set({ isLoading: false });
      throw error;
    }
  },
}));

interface LiveSessionState {
  activeSession: any | null;
  isRecording: boolean;
  isInMCQ: boolean;
  currentMCQ: any | null;
  joinSession: (sessionId: number) => Promise<any>;
  leaveSession: () => void;
  toggleRecording: () => Promise<void>;
  launchMCQ: (quizId: number) => Promise<void>;
  endMCQ: () => void;
}

export const useLiveSessionStore = create<LiveSessionState>((set, get) => ({
  activeSession: null,
  isRecording: false,
  isInMCQ: false,
  currentMCQ: null,
  
  joinSession: async (sessionId: number) => {
    try {
      const sessionData = await liveSessionService.joinSession(sessionId);
      const tokenData = await liveSessionService.getSessionToken(sessionId);
      set({ 
        activeSession: { 
          ...sessionData, 
          token: tokenData.token, 
          roomName: tokenData.room_name 
        } 
      });
      return tokenData;
    } catch (error) {
      throw error;
    }
  },
  
  leaveSession: () => {
    set({ activeSession: null, isRecording: false, isInMCQ: false, currentMCQ: null });
  },
  
  toggleRecording: async () => {
    const { activeSession } = get();
    if (!activeSession) return;
    
    try {
      await liveSessionService.toggleRecording(activeSession.id);
      set((state) => ({ isRecording: !state.isRecording }));
    } catch (error) {
      console.error('Failed to toggle recording:', error);
    }
  },
  
  launchMCQ: async (quizId: number) => {
    const { activeSession } = get();
    if (!activeSession) return;
    
    try {
      const mcqData = await liveSessionService.launchMCQ(activeSession.id, quizId);
      set({ isInMCQ: true, currentMCQ: mcqData });
    } catch (error) {
      console.error('Failed to launch MCQ:', error);
    }
  },
  
  endMCQ: () => {
    set({ isInMCQ: false, currentMCQ: null });
  },
}));

interface UIState {
  isSidebarOpen: boolean;
  isChatOpen: boolean;
  isParticipantsOpen: boolean;
  toggleSidebar: () => void;
  toggleChat: () => void;
  toggleParticipants: () => void;
}

export const useUIStore = create<UIState>((set) => ({
  isSidebarOpen: true,
  isChatOpen: false,
  isParticipantsOpen: false,
  
  toggleSidebar: () => set((state) => ({ isSidebarOpen: !state.isSidebarOpen })),
  toggleChat: () => set((state) => ({ isChatOpen: !state.isChatOpen, isParticipantsOpen: false })),
  toggleParticipants: () => set((state) => ({ isParticipantsOpen: !state.isParticipantsOpen, isChatOpen: false })),
}));
