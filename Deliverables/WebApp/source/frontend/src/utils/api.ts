// ============================================================
// TUTUNAKU — API Client (Axios)
// Interceptors para JWT, refresh tokens y manejo de errores
// ============================================================
import axios, { type AxiosError } from 'axios'
import { useAuthStore } from '@/store/authStore'
import toast from 'react-hot-toast'

export const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1'
export const ROOT_URL = BASE_URL.replace('/api/v1', '')

export const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 15_000,
})

// ── Request Interceptor: adjuntar token ──────────────────
api.interceptors.request.use((config) => {
  const tokens = useAuthStore.getState().tokens
  if (tokens?.access_token) {
    config.headers.Authorization = `Bearer ${tokens.access_token}`
  }
  return config
})

// ── Response Interceptor: refresh token automático ──────
let isRefreshing = false
let pendingRequests: Array<(token: string) => void> = []

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const original = error.config as typeof error.config & { _retry?: boolean }

    if (error.response?.status === 401 && !original._retry) {
      const { tokens, setTokens, logout } = useAuthStore.getState()

      if (!tokens?.refresh_token) {
        logout()
        return Promise.reject(error)
      }

      if (isRefreshing) {
        // Encolar petición mientras se refresca
        return new Promise((resolve) => {
          pendingRequests.push((token) => {
            original!.headers!.Authorization = `Bearer ${token}`
            resolve(api(original!))
          })
        })
      }

      original._retry = true
      isRefreshing = true

      try {
        const { data } = await axios.post(`${BASE_URL}/auth/refresh`, {
          refresh_token: tokens.refresh_token,
        })
        const newTokens = data
        setTokens(newTokens)

        // Resolver peticiones pendientes
        pendingRequests.forEach((cb) => cb(newTokens.access_token))
        pendingRequests = []

        original!.headers!.Authorization = `Bearer ${newTokens.access_token}`
        return api(original!)
      } catch {
        logout()
        toast.error('Tu sesión expiró. Por favor inicia sesión de nuevo.')
        return Promise.reject(error)
      } finally {
        isRefreshing = false
      }
    }

    // Mostrar errores genéricos
    if (error.response?.status === 403) {
      toast.error('No tienes permiso para realizar esta acción')
    } else if (error.response?.status && error.response.status >= 500) {
      toast.error('Error del servidor. Intenta de nuevo.')
    }

    return Promise.reject(error)
  }
)

// ── Helpers tipados ──────────────────────────────────────
export const authApi = {
  register: (data: object) => api.post('/auth/register', data),
  login: (data: object) => api.post('/auth/login', data),
  logout: (refresh_token: string) => api.post('/auth/logout', { refresh_token }),
  refreshToken: (refresh_token: string) => api.post('/auth/refresh', { refresh_token }),
  verifyEmail: (token: string) => api.post(`/auth/verify-email?token=${token}`),
  getCaptcha: () => api.get('/auth/captcha'),
  forgotPassword: (data: { email: string; captcha_id: string; captcha_answer: string }) =>
    api.post('/auth/forgot-password', data),
  resetPassword: (data: object) => api.post('/auth/reset-password', data),
  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/auth/change-password', data),
}

export const userApi = {
  getMe: () => api.get('/users/me'),
  updateMe: (data: object) => api.patch('/users/me', data),
  getStats: () => api.get('/users/me/stats'),
  getLeaderboard: (limit = 20) => api.get(`/users/leaderboard?limit=${limit}`),
}

export const courseApi = {
  list: () => api.get('/courses'),
  get: (id: string) => api.get(`/courses/${id}`),
  create: (data: object) => api.post('/courses', data),
  update: (id: string, data: object) => api.patch(`/courses/${id}`, data),
  delete: (id: string) => api.delete(`/courses/${id}`),
}

export const unitApi = {
  getByCourse: (courseId: string) => api.get(`/units/course/${courseId}`),
  create: (data: object) => api.post('/units', data),
  update: (id: string, data: object) => api.patch(`/units/${id}`, data),
  delete: (id: string) => api.delete(`/units/${id}`),
}

export const lessonApi = {
  getByUnit: (unitId: string) => api.get(`/lessons/unit/${unitId}`),
  get: (id: string) => api.get(`/lessons/${id}`),
  create: (data: object) => api.post('/lessons', data),
  complete: (id: string) => api.post(`/lessons/${id}/complete`),
}

export const exerciseApi = {
  getByLesson: (lessonId: string) => api.get(`/exercises/lesson/${lessonId}`),
  create: (data: object) => api.post('/exercises', data),
  attempt: (exerciseId: string, data: object) =>
    api.post(`/exercises/${exerciseId}/attempt`, data),
}

export const achievementApi = {
  list: () => api.get('/achievements'),
  mine: () => api.get('/achievements/me'),
}

export const notificationApi = {
  list: () => api.get('/notifications'),
  markRead: (id: string) => api.patch(`/notifications/${id}/read`),
  markAllRead: () => api.patch('/notifications/read-all'),
}

export const reminderApi = {
  list: () => api.get('/reminders'),
  create: (data: object) => api.post('/reminders', data),
  update: (id: string, data: object) => api.patch(`/reminders/${id}`, data),
  delete: (id: string) => api.delete(`/reminders/${id}`),
}

export const adminApi = {
  getMetrics: () => api.get('/admin/metrics'),
  listUsers: (skip = 0, limit = 50) => api.get(`/admin/users?skip=${skip}&limit=${limit}`),
  updateUser: (id: string, data: object) => api.patch(`/admin/users/${id}`, data),
  resetProgress: (id: string) => api.delete(`/admin/users/${id}/progress`),
  awardAchievement: (achievementId: string, userId: string) =>
    api.post(`/admin/achievements/${achievementId}/award/${userId}`),
}

// ── API Inteligente (/api/ml) ────────────────────────────
// Vive fuera de /api/v1 (igual que en el backend). Se reutiliza la misma
// instancia de axios (para heredar los interceptors de auth/refresh), pero
// pasando `baseURL` explícito por request: así se ignora el `baseURL: /api/v1`
// de la instancia sin importar si ROOT_URL es una URL absoluta (dev, con
// host) o una cadena vacía (producción, VITE_API_URL relativo tipo
// "/api/v1") — con baseURL config vacío, axios usa la url tal cual, en vez
// de volver a anteponerle /api/v1 (eso causaba pedir /api/v1/api/ml/... y
// que nginx respondiera 404 en el dashboard de ML).
const ML_URL = `${ROOT_URL}/api/ml`
const mlConfig = { baseURL: ROOT_URL }

export const mlApi = {
  health: () => api.get(`${ML_URL}/health`, mlConfig),
  listModels: () => api.get(`${ML_URL}/models`, mlConfig),
  listInferences: (limit = 50) => api.get(`${ML_URL}/inferences?limit=${limit}`, mlConfig),
  predictTime: (data: object) => api.post(`${ML_URL}/predict-time`, data, mlConfig),
  predictSuccess: (data: object) => api.post(`${ML_URL}/predict-success`, data, mlConfig),
  detectAnomaly: (data: object) => api.post(`${ML_URL}/detect-anomaly`, data, mlConfig),
  segmentUser: (data: object) => api.post(`${ML_URL}/segment-user`, data, mlConfig),
  platformLoadForecast: (horizonHours = 6) =>
    api.get(`${ML_URL}/platform-load-forecast?horizon_hours=${horizonHours}`, mlConfig),
  analyzeNavigation: (data: object) => api.post(`${ML_URL}/analyze-navigation`, data, mlConfig),
  triggerPlatformLoadUpdate: () => api.post(`${ML_URL}/trigger/platform-load-update`, undefined, mlConfig),
  triggerUserProgressUpdate: () => api.post(`${ML_URL}/trigger/user-progress-update`, undefined, mlConfig),
}
