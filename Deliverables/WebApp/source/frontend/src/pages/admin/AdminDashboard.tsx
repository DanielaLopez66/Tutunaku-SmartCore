// ============================================================
// TUTUNAKU — AdminDashboard
// Panel de métricas globales del administrador
// ============================================================
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Users, BookOpen, Target, TrendingUp, Award, AlertCircle, BarChart3, XCircle } from 'lucide-react'
import { adminApi } from '@/utils/api'
import type { AdminMetrics } from '@/types'

interface MetricCardProps {
  title: string
  value: string | number
  subtitle?: string
  icon: React.ReactNode
  color: string
  bg: string
  index: number
}

function MetricCard({ title, value, subtitle, icon, color, bg, index }: MetricCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.07 }}
      className="card p-5"
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-sm text-[var(--color-muted)] font-semibold">{title}</p>
          <p className={`font-display text-3xl font-bold mt-1 ${color}`}>{value}</p>
          {subtitle && (
            <p className="text-xs text-[var(--color-muted)] mt-1">{subtitle}</p>
          )}
        </div>
        <div className={`w-12 h-12 rounded-2xl ${bg} flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </motion.div>
  )
}

function SkeletonCard() {
  return (
    <div className="card p-5 animate-pulse">
      <div className="flex justify-between">
        <div className="space-y-2 flex-1">
          <div className="h-3 bg-gray-200 dark:bg-dark-muted rounded w-1/2" />
          <div className="h-8 bg-gray-200 dark:bg-dark-muted rounded w-1/3" />
          <div className="h-3 bg-gray-200 dark:bg-dark-muted rounded w-2/3" />
        </div>
        <div className="w-12 h-12 rounded-2xl bg-gray-200 dark:bg-dark-muted" />
      </div>
    </div>
  )
}

export default function AdminDashboard() {
  const { data: metrics, isLoading, error } = useQuery<AdminMetrics>({
    queryKey: ['admin-metrics'],
    queryFn: () => adminApi.getMetrics().then((r) => r.data),
    refetchInterval: 30_000, // Actualizar cada 30s
  })

  if (error) {
    return (
      <div className="flex items-center gap-3 p-6 card text-alebrije-coral">
        <AlertCircle size={24} />
        <p className="font-semibold">Error al cargar métricas. Verifica tu sesión de admin.</p>
      </div>
    )
  }

  const metricCards = metrics
    ? [
        {
          title: 'Usuarios totales',
          value: metrics.total_users.toLocaleString(),
          subtitle: `+${metrics.new_users_30d} en últimos 30 días`,
          icon: <Users size={22} className="text-alebrije-coral" />,
          color: 'text-alebrije-coral',
          bg: 'bg-red-50 dark:bg-red-900/20',
        },
        {
          title: 'Usuarios activos (7d)',
          value: metrics.active_users_7d.toLocaleString(),
          subtitle: `${((metrics.active_users_7d / metrics.total_users) * 100).toFixed(1)}% del total`,
          icon: <TrendingUp size={22} className="text-alebrije-teal" />,
          color: 'text-alebrije-teal',
          bg: 'bg-teal-50 dark:bg-teal-900/20',
        },
        {
          title: 'Cursos publicados',
          value: metrics.total_courses,
          subtitle: `${metrics.total_lessons} lecciones totales`,
          icon: <BookOpen size={22} className="text-alebrije-violet" />,
          color: 'text-alebrije-violet',
          bg: 'bg-violet-50 dark:bg-violet-900/20',
        },
        {
          title: 'Intentos de ejercicios',
          value: metrics.total_exercise_attempts.toLocaleString(),
          subtitle: `${metrics.correct_attempts_percentage.toFixed(1)}% correctos`,
          icon: <Target size={22} className="text-alebrije-gold" />,
          color: 'text-yellow-600',
          bg: 'bg-yellow-50 dark:bg-yellow-900/20',
        },
        {
          title: 'Completación promedio',
          value: `${metrics.avg_completion_percentage.toFixed(1)}%`,
          subtitle: 'Progreso por lección',
          icon: <Award size={22} className="text-alebrije-magenta" />,
          color: 'text-alebrije-magenta',
          bg: 'bg-pink-50 dark:bg-pink-900/20',
        },
        {
          title: 'Tasa de aciertos',
          value: `${metrics.correct_attempts_percentage.toFixed(1)}%`,
          subtitle: 'Respuestas correctas',
          icon: <Target size={22} className="text-alebrije-lime" />,
          color: 'text-green-600',
          bg: 'bg-green-50 dark:bg-green-900/20',
        },
      ]
    : []

  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="font-display text-3xl font-bold flex items-center gap-2">
          <BarChart3 className="text-alebrije-coral" /> Dashboard de Administración
        </h1>
        <p className="text-[var(--color-muted)] mt-1">
          Métricas globales de Tutunaku en tiempo real
        </p>
      </div>

      {/* Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)
          : metricCards.map((card, i) => (
              <MetricCard key={card.title} {...card} index={i} />
            ))}
      </div>

      {/* Daily Active Users Chart (simple bar) */}
      {metrics && metrics.daily_active_users.length > 0 && (
        <div className="card p-6">
          <h2 className="font-display font-bold text-xl mb-5 flex items-center gap-2">
            <TrendingUp size={20} className="text-alebrije-teal" /> Usuarios activos — últimos 7 días
          </h2>
          <div className="flex items-end gap-3 h-40">
            {metrics.daily_active_users.map((day, i) => {
              const maxVal = Math.max(...metrics.daily_active_users.map((d) => d.active_users), 1)
              const pct = (day.active_users / maxVal) * 100
              return (
                <div key={i} className="flex-1 flex flex-col items-center gap-1">
                  <span className="text-xs font-bold text-[var(--color-muted)]">
                    {day.active_users}
                  </span>
                  <motion.div
                    initial={{ height: 0 }}
                    animate={{ height: `${pct}%` }}
                    transition={{ delay: i * 0.08, duration: 0.5 }}
                    className="w-full rounded-t-xl bg-alebrije-gradient min-h-[4px]"
                  />
                  <span className="text-xs text-[var(--color-muted)]">
                    {new Date(day.date).toLocaleDateString('es', { weekday: 'short' })}
                  </span>
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Most Common Errors */}
      {metrics && metrics.most_common_errors.length > 0 && (
        <div className="card p-6">
          <h2 className="font-display font-bold text-xl mb-5 flex items-center gap-2">
            <XCircle size={20} className="text-alebrije-coral" /> Ejercicios con más errores
          </h2>
          <div className="space-y-3">
            {metrics.most_common_errors.map((item, i) => (
              <div key={i} className="flex items-center justify-between gap-4 p-3
                                      rounded-2xl bg-gray-50 dark:bg-dark-muted">
                <p className="text-sm font-medium flex-1 line-clamp-1">{item.question}</p>
                <span className="badge bg-red-50 dark:bg-red-900/20 text-red-500 flex-shrink-0">
                  {item.errors} errores
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Progress by lesson */}
      {metrics && metrics.progress_by_lesson.length > 0 && (
        <div className="card p-6">
          <h2 className="font-display font-bold text-xl mb-5 flex items-center gap-2">
            <BookOpen size={20} className="text-alebrije-violet" /> Progreso por lección
          </h2>
          <div className="space-y-4">
            {metrics.progress_by_lesson.map((item, i) => (
              <div key={i}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="font-semibold line-clamp-1 flex-1">{item.lesson}</span>
                  <span className="text-[var(--color-muted)] ml-2 flex-shrink-0">
                    {item.avg_completion}% · {item.users} usuarios
                  </span>
                </div>
                <div className="xp-bar h-2.5">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${item.avg_completion}%` }}
                    transition={{ delay: i * 0.1, duration: 0.6 }}
                    className="xp-bar-fill"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
