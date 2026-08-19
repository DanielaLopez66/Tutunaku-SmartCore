// ============================================================
// TUTUNAKU — App.tsx
// Router principal con rutas protegidas y lazy loading
// ============================================================
import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import MainLayout from '@/components/layout/MainLayout'
import AuthLayout from '@/components/layout/AuthLayout'
import SkeletonPage from '@/components/ui/SkeletonPage'
import SessionManager from '@/components/ui/SessionManager'

// ── Lazy imports ────────────────────────────────────────
const HomePage = lazy(() => import('@/pages/HomePage'))
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/RegisterPage'))
const ForgotPasswordPage = lazy(() => import('@/pages/ForgotPasswordPage'))
const ResetPasswordPage = lazy(() => import('@/pages/ResetPasswordPage'))
const VerifyEmailPage = lazy(() => import('@/pages/VerifyEmailPage'))
const LearnPage = lazy(() => import('@/pages/LearnPage'))
const LessonPage = lazy(() => import('@/pages/LessonPage'))
const ExercisePage = lazy(() => import('@/pages/ExercisePage'))
const ProfilePage = lazy(() => import('@/pages/ProfilePage'))
const AchievementsPage = lazy(() => import('@/pages/AchievementsPage'))
const LeaderboardPage = lazy(() => import('@/pages/LeaderboardPage'))
const SettingsPage = lazy(() => import('@/pages/SettingsPage'))
const AdminDashboard = lazy(() => import('@/pages/admin/AdminDashboard'))
const AdminUsers = lazy(() => import('@/pages/admin/AdminUsers'))
const AdminCourses = lazy(() => import('@/pages/admin/AdminCourses'))
const AdminUnits = lazy(() => import('@/pages/admin/AdminUnits'))
const AdminLessons = lazy(() => import('@/pages/admin/AdminLessons'))
const AdminMLDashboard = lazy(() => import('@/pages/admin/AdminMLDashboard'))
const SitemapPage = lazy(() => import('@/pages/SitemapPage'))
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'))

// ── Guards ───────────────────────────────────────────────
function RequireAuth({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  return isAuthenticated ? <>{children}</> : <Navigate to="/login" replace />
}

function RequireAdmin({ children }: { children: React.ReactNode }) {
  const user = useAuthStore((s) => s.user)
  if (!user) return <Navigate to="/login" replace />
  if (user.role !== 'admin') return <Navigate to="/learn" replace />
  return <>{children}</>
}

function RequireGuest({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, user } = useAuthStore()
  if (!isAuthenticated) return <>{children}</>
  return user?.role === 'admin' ? <Navigate to="/admin" replace /> : <Navigate to="/learn" replace />
}

// ────────────────────────────────────────────────────────
export default function App() {
  return (
    <>
      {/* Session Manager — maneja cookie de 5 min y auto-logout */}
      <SessionManager />

      <Suspense fallback={<SkeletonPage />}>
        <Routes>
          {/* ── Página pública ── */}
          <Route path="/" element={<MainLayout />}>
            <Route index element={<HomePage />} />
          </Route>

          {/* ── Auth (solo visitantes) ── */}
          <Route element={<RequireGuest><AuthLayout /></RequireGuest>}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/forgot-password" element={<ForgotPasswordPage />} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/verify-email" element={<VerifyEmailPage />} />
          </Route>

          {/* ── App protegida ── */}
          <Route element={<RequireAuth><MainLayout /></RequireAuth>}>
            <Route path="/learn" element={<LearnPage />} />
            <Route path="/lesson/:lessonId" element={<LessonPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/achievements" element={<AchievementsPage />} />
            <Route path="/leaderboard" element={<LeaderboardPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>

          {/* ── Ejercicio (full screen, sin nav) ── */}
          <Route
            path="/exercise/:lessonId"
            element={<RequireAuth><ExercisePage /></RequireAuth>}
          />

          {/* ── Admin ── */}
          <Route path="/admin" element={<RequireAdmin><MainLayout /></RequireAdmin>}>
            <Route index element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="courses" element={<AdminCourses />} />
            <Route path="units" element={<AdminUnits />} />
            <Route path="lessons" element={<AdminLessons />} />
            <Route path="ml" element={<AdminMLDashboard />} />
          </Route>

          <Route path="/sitemap" element={<MainLayout />}>
            <Route index element={<SitemapPage />} />
          </Route>

          {/* ── 404 ── */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </Suspense>
    </>
  )
}
