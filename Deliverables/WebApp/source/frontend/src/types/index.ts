// ============================================================
// TUTUNAKU — TypeScript Types & Interfaces
// ============================================================

// ── Auth ──────────────────────────────────────────────────
export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: string
  expires_in: number
}

export interface RegisterRequest {
  email: string
  username: string
  password: string
  full_name?: string
}

export interface LoginRequest {
  email: string
  password: string
}

// ── User ──────────────────────────────────────────────────
export type UserRole = 'admin' | 'user' | 'visitor'

export interface User {
  id: string
  email: string
  username: string
  full_name?: string
  avatar_url?: string
  role: UserRole
  xp_total: number
  level: number
  hearts: number
  current_streak: number
  longest_streak: number
  is_active: boolean
  last_heart_refill?: string
  created_at: string
}

export interface UserStats {
  xp_total: number
  level: number
  hearts: number
  current_streak: number
  longest_streak: number
  lessons_completed: number
  exercises_correct: number
  exercises_total: number
  accuracy_percentage: number
  achievements_count: number
  last_heart_refill?: string
}

export interface LeaderboardEntry {
  rank: number
  id: string
  username: string
  avatar_url?: string
  xp_total: number
  level: number
  current_streak: number
  is_me: boolean
}

// ── Course ────────────────────────────────────────────────
export type DifficultyLevel = 'beginner' | 'intermediate' | 'advanced'

export interface Course {
  id: string
  title: string
  description?: string
  cover_image_url?: string
  color_hex: string
  difficulty: DifficultyLevel
  is_published: boolean
  order_index: number
  created_at: string
  units_count?: number
}

export interface Unit {
  id: string
  course_id: string
  title: string
  description?: string
  icon_emoji: string
  color_hex: string
  order_index: number
  is_locked: boolean
  xp_reward: number
  lessons?: Lesson[]
}

// ── Lesson ────────────────────────────────────────────────
export type ContentType = 'text' | 'video' | 'audio' | 'image' | 'example'

export interface ContentBlock {
  type: ContentType
  content: string
  language?: 'es' | 'toto'
  caption?: string
  pronunciation?: string
  example_sentence?: string
  audio_url?: string
}

export interface Lesson {
  id: string
  unit_id: string
  title: string
  description?: string
  order_index: number
  xp_reward: number
  content_type?: string
  content_data?: ContentBlock[]
  is_published: boolean
  exercises_count?: number
}

// ── Exercise ──────────────────────────────────────────────
export type ExerciseType = 'translation' | 'multiple_choice' | 'writing' | 'audio'

export interface Exercise {
  id: string
  lesson_id: string
  type: ExerciseType
  question: string
  options?: string[]
  hint?: string
  image_url?: string
  audio_url?: string
  xp_reward: number
  order_index: number
}

export interface ExerciseAttemptRequest {
  user_answer: string
  time_spent_seconds?: number
}

export interface ExerciseAttemptResponse {
  is_correct: boolean
  correct_answer: string
  explanation?: string
  xp_earned: number
  hearts_remaining: number
  user_stats?: {
    xp_total: number
    level: number
    current_streak: number
  }
}

// ── Progress ──────────────────────────────────────────────
export interface UserProgress {
  id: string
  lesson_id: string
  is_completed: boolean
  completion_percentage: number
  score: number
  xp_earned: number
  completed_at?: string
}

// ── Achievement ───────────────────────────────────────────
export interface Achievement {
  id: string
  title: string
  description?: string
  icon_emoji: string
  badge_color: string
  xp_reward: number
  condition_type?: string
  condition_value?: number
}

export interface UserAchievement {
  achievement: Achievement
  earned_at: string
}

// ── Notification ──────────────────────────────────────────
export type NotificationType = 'reminder' | 'achievement' | 'progress' | 'system'

export interface Notification {
  id: string
  type: NotificationType
  title: string
  message?: string
  icon_emoji?: string
  is_read: boolean
  action_url?: string
  created_at: string
}

// ── Reminder ──────────────────────────────────────────────
export interface Reminder {
  id: string
  hour: number
  minute: number
  timezone: string
  message: string
  days_of_week: number[]
  is_active: boolean
  last_sent_at?: string
  created_at: string
}

export interface ReminderCreate {
  hour: number
  minute: number
  timezone?: string
  message?: string
  days_of_week?: number[]
}

// ── Admin ─────────────────────────────────────────────────
export interface AdminMetrics {
  total_users: number
  active_users_7d: number
  total_courses: number
  total_lessons: number
  avg_completion_percentage: number
  total_exercise_attempts: number
  correct_attempts_percentage: number
  most_common_errors: Array<{ question: string; errors: number }>
  progress_by_lesson: Array<{ lesson: string; avg_completion: number; users: number }>
  new_users_30d: number
  daily_active_users: Array<{ date: string; active_users: number }>
}

// ── API Response ──────────────────────────────────────────
export interface StandardResponse<T = unknown> {
  success: boolean
  message: string
  data?: T
}

export interface ApiError {
  success: false
  error: {
    code: string
    message: string
    details?: Array<{ field: string; message: string }>
  }
}

// ── Machine Learning (/api/ml) ────────────────────────────
export type DeviceType = 'mobile' | 'desktop' | 'tablet'

export interface PredictTimeRequest {
  attempt_number: number
  difficulty: number
  connectivity_quality: number
  device_type: DeviceType
  hour_of_day: number
  day_of_week: number
  is_correct: boolean
  hearts_before: number
}

export interface PredictTimeResponse {
  predicted_time_seconds: number
  model: string
  model_version: string
  inference_date: string
}

export interface PredictSuccessRequest {
  difficulty: number
  num_exercises: number
  connectivity_quality: number
  device_type: DeviceType
  prior_success_rate_30d: number
  hearts_start: number
}

export interface PredictSuccessResponse {
  completed_with_lives: boolean
  probability: number
  model: string
  model_version: string
  inference_date: string
}

export interface DetectAnomalyRequest {
  xp_gained: number
  session_duration_seconds: number
  seconds_since_prev_event: number
  events_last_hour_user: number
}

export interface DetectAnomalyResponse {
  is_anomaly: boolean
  anomaly_score: number
  model: string
  model_version: string
  inference_date: string
}

export interface SegmentUserRequest {
  recency_days: number
  frequency_sessions: number
  educational_value_xp: number
}

export interface SegmentUserResponse {
  cluster: number
  segment_label: string
  distance_to_centroid: number
  model: string
  model_version: string
  inference_date: string
}

export interface PlatformLoadForecastPoint {
  horizon_hours: number
  predicted_requests_per_minute: number
}

export interface PlatformLoadForecastResponse {
  forecast: PlatformLoadForecastPoint[]
  model: string
  model_version: string
  inference_date: string
}

export interface MLModelInfo {
  model_name: string
  version: string
  algorithm: string
  task: string
  metrics: Record<string, unknown>
  trained_at?: string
  loaded: boolean
  error?: string
}

export interface MLInferenceRecord {
  id: number
  model_name: string
  model_version?: string
  endpoint: string
  confidence?: number
  created_at: string
}

// ── Socket.IO (Dashboard en tiempo real) ──────────────────
export interface NewPredictionEvent {
  endpoint: string
  model: string
  model_version: string
  inference_date: string
  [key: string]: unknown
}

export interface AnomalyAlertEvent {
  is_anomaly: boolean
  anomaly_score: number
  model: string
  model_version: string
  inference_date: string
}

export type PlatformLoadUpdateEvent = PlatformLoadForecastResponse

export interface UserProgressUpdateEvent {
  window_minutes: number
  attempts_count: number
  xp_gained: number
  active_users: number
  timestamp: string
}

// ── Actividad en vivo para admin (Socket.IO, sala "admin") ─
export interface AdminNewUserEvent {
  user_id: string
  username: string
  email: string
  created_at: string
}

export interface AdminLessonCompletedEvent {
  user_id: string
  username: string
  lesson_id: string
  lesson_title: string
  xp_earned: number
  completed_at: string
}

export interface AdminXpRecordEvent {
  user_id: string
  username: string
  xp_total: number
  previous_record: number
  timestamp: string
}

// ── UI State ──────────────────────────────────────────────
export interface ToastMessage {
  id: string
  type: 'success' | 'error' | 'info' | 'warning'
  title: string
  message?: string
}

export interface LessonSession {
  lesson: Lesson
  exercises: Exercise[]
  currentIndex: number
  answers: Record<string, ExerciseAttemptResponse>
  startedAt: Date
  lives: number
  xpEarned: number
}
