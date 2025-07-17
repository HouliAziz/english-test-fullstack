const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:5001/api';

export interface User {
  id: number;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  level: 'beginner' | 'intermediate' | 'advanced';
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface AuthResponse {
  message: string;
  user: User;
  token: string;
}

export interface ApiError {
  error: string;
  details?: string;
}

class ApiClient {
  private token: string | null = null;

  constructor() {
    // Load token from localStorage on initialization
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('auth_token');
    }
  }

  setToken(token: string) {
    this.token = token;
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  clearToken() {
    this.token = null;
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    if (this.token) {
      headers.Authorization = `Bearer ${this.token}`;
    }

    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...(options.headers as Record<string, string>),
      },
    });

    if (!response.ok) {
      const errorData: ApiError = await response.json().catch(() => ({
        error: `HTTP error! status: ${response.status}`,
      }));
      throw new Error(errorData.error || 'An error occurred');
    }

    return response.json();
  }

  // Authentication methods
  async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
    level?: string;
  }): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData),
    });

    this.setToken(response.token);
    return response;
  }

  async login(credentials: {
    username: string;
    password: string;
  }): Promise<AuthResponse> {
    const response = await this.request<AuthResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials),
    });

    this.setToken(response.token);
    return response;
  }

  async getProfile(): Promise<{ user: User }> {
    return this.request<{ user: User }>('/auth/profile');
  }

  async updateProfile(updates: Partial<User>): Promise<{ message: string; user: User }> {
    return this.request<{ message: string; user: User }>('/auth/profile', {
      method: 'PUT',
      body: JSON.stringify(updates),
    });
  }

  async changePassword(passwords: {
    current_password: string;
    new_password: string;
  }): Promise<{ message: string }> {
    return this.request<{ message: string }>('/auth/change-password', {
      method: 'POST',
      body: JSON.stringify(passwords),
    });
  }

  async deleteAccount(): Promise<any> {
    return this.request<any>('/auth/delete-account', { method: 'DELETE' });
  }

  // Lessons methods
  async getLessons(): Promise<any[]> {
    return this.request<any[]>('/lessons');
  }

  async getLesson(id: number): Promise<any> {
    return this.request<any>(`/lessons/${id}`);
  }

  async generateLesson(data: {
    topic: string;
    level: string;
    lesson_type: string;
  }): Promise<any> {
    return this.request<any>('/lessons/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Quiz methods
  async getQuizzes(): Promise<any[]> {
    return this.request<any[]>('/quizzes');
  }

  async getQuiz(id: number): Promise<any> {
    return this.request<any>(`/quizzes/${id}`);
  }

  async getQuizWithAnswers(id: number): Promise<any> {
    return this.request<any>(`/quizzes/${id}/answers`);
  }


  async generateQuizWithLesson(data: {
    topic: string;
    level: string;
    num_questions: number;
    duration_minutes?: number;
  }): Promise<any> {
    // First, generate the lesson
    const lessonRes = await this.request<any>('/lessons/generate', {
      method: 'POST',
      body: JSON.stringify({
        topic: data.topic,
        level: data.level,
        duration_minutes: data.duration_minutes || 15
      }),
    });
    const lesson_id = lessonRes.lesson?.id;
    if (!lesson_id) throw new Error('Lesson generation failed');

    // Then, generate the quiz
    const quizRes = await this.request<any>('/quizzes/generate', {
      method: 'POST',
      body: JSON.stringify({
        topic: data.topic,
        level: data.level,
        lesson_id,
        num_questions: data.num_questions
      }),
    });
    return quizRes;
  }

  async submitQuizAttempt(quizId: number, answers: Record<string, string>): Promise<any> {
    // Accept answers as a dictionary and send as { answers: dict }
    // Ensure answers is a dictionary, not an array
    return this.request<any>(`/quizzes/${quizId}/submit`, {
      method: 'POST',
      body: JSON.stringify({ answers }),
    });
  }

  // Statistics methods
  async getStatistics(): Promise<any> {
    return this.request<any>('/statistics');
  }

  async getAchievements(): Promise<any> {
    return this.request<any>('/statistics/achievements');
  }

  async getDashboard(): Promise<any> {
    return this.request<any>('/statistics/dashboard');
  }

  logout() {
    this.clearToken();
  }
}

export const apiClient = new ApiClient();

