// Типы для Telegram Web App
export interface TelegramUser {
  id: number;
  first_name: string;
  last_name?: string;
  username?: string;
  language_code?: string;
}

export interface TelegramWebApp {
  initData: string;
  initDataUnsafe: {
    query_id?: string;
    user?: TelegramUser;
    receiver?: TelegramUser;
    chat?: any;
    chat_type?: string;
    chat_instance?: string;
    start_param?: string;
    can_send_after?: number;
    auth_date?: number;
    hash?: string;
  };
  colorScheme: 'light' | 'dark';
  themeParams: {
    bg_color?: string;
    text_color?: string;
    hint_color?: string;
    link_color?: string;
    button_color?: string;
    button_text_color?: string;
  };
  isExpanded: boolean;
  viewportHeight: number;
  viewportStableHeight: number;
  headerColor: string;
  backgroundColor: string;
  isClosingConfirmationEnabled: boolean;
  backButton: {
    isVisible: boolean;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
  };
  mainButton: {
    text: string;
    color: string;
    textColor: string;
    isVisible: boolean;
    isProgressVisible: boolean;
    isActive: boolean;
    setText: (text: string) => void;
    onClick: (callback: () => void) => void;
    offClick: (callback: () => void) => void;
    show: () => void;
    hide: () => void;
    enable: () => void;
    disable: () => void;
    showProgress: (leaveActive?: boolean) => void;
    hideProgress: () => void;
  };
  HapticFeedback: {
    impactOccurred: (style: 'light' | 'medium' | 'heavy' | 'rigid' | 'soft') => void;
    notificationOccurred: (type: 'error' | 'success' | 'warning') => void;
    selectionChanged: () => void;
  };
  ready: () => void;
  expand: () => void;
  close: () => void;
}

// Типы для API
export interface ScheduleItem {
  id: number;
  title: string;
  teacher: string;
  time: string;
  location: string;
  level: 'beginner' | 'advanced';
  duration: string;
}

export interface Club {
  id: number;
  name: string;
  description: string;
  schedule: string;
  max_participants: number;
  current_participants: number;
}

export interface UserProfile {
  user_id: string;
  level: 'beginner' | 'advanced' | 'Не выбран';
  progress: number;
  lessons_completed: number;
  tests_passed: number;
  clubs_joined: number;
  points: number;
  current_streak: number;
  total_study_time: string;
  start_date: string;
  goal: string;
  study_time: number;
  recent_achievements?: Array<{
    title: string;
    date: string;
  }>;
  next_goals?: string[];
}

export interface Test {
  id: number;
  title: string;
  level: 'beginner' | 'advanced';
  questions_count: number;
  duration: string;
}

export interface Lesson {
  id: number;
  title: string;
  level: 'beginner' | 'advanced';
  duration: string;
  type: 'video' | 'interactive';
}

export interface BookingRequest {
  lesson_id: number;
  user_id: string;
  date?: string;
}

export interface TestResult {
  test_id: number;
  user_id: string;
  answers: Record<string, string>;
}

// API Response типы
export interface ApiResponse<T> {
  success?: boolean;
  error?: string;
  message?: string;
  data?: T;
}

export interface ScheduleResponse {
  schedule: ScheduleItem[];
  total: number;
  level?: string;
}

export interface ClubsResponse {
  clubs: Club[];
  total: number;
}

export interface TestsResponse {
  tests: Test[];
}

export interface LessonsResponse {
  lessons: Lesson[];
}

export interface BookingResponse {
  success: boolean;
  message: string;
  lesson: ScheduleItem;
  booking_id: string;
}

export interface TestSubmitResponse {
  success: boolean;
  score: number;
  correct_answers: number;
  total_questions: number;
  message: string;
}

// Навигация
export type AppRoute = '/' | '/schedule' | '/clubs' | '/profile' | '/tests' | '/lessons' | '/booking';

// Состояние приложения
export interface AppState {
  user: TelegramUser | null;
  profile: UserProfile | null;
  currentLevel: 'beginner' | 'advanced' | null;
  isLoading: boolean;
  error: string | null;
} 