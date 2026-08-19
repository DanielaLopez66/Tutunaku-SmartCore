// ============================================================
// TUTUNAKU — LearnPage (Mapa de Niveles)
// Navegación principal del contenido educativo
// ============================================================
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Lock, CheckCircle, Star, Flame, Zap, GraduationCap, CloudOff } from 'lucide-react'
import { courseApi, unitApi, lessonApi } from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import { DynamicIcon } from '@/utils/icons'
import type { Course, Unit } from '@/types'
import SkeletonPage from '@/components/ui/SkeletonPage'

// ────────────────────────────────────────────
// PATH DESIGN CONSTANTS
const PATH_OFFSETS = [0, 45, 75, 45, 0, -45, -75, -45]
// ────────────────────────────────────────────

// ── UnitSection ────────────────────────────────────────────────
function UnitSection({ unit, index }: { unit: Unit; index: number }) {
  const isLocked = unit.is_locked

  // Obtener lecciones de esta unidad
  const { data: lessons = [], isLoading } = useQuery({
    queryKey: ['lessons', unit.id],
    queryFn: () => lessonApi.getByUnit(unit.id).then((r) => r.data),
  })

  return (
    <div className="mb-14 relative animate-fade-in group/unit">
      {/* Banner de la Unidad */}
      <div
        className={`rounded-3xl p-6 text-white mb-6 shadow-md relative overflow-hidden transition-all ${isLocked ? 'grayscale opacity-70' : ''}`}
        style={{ backgroundColor: unit.color_hex }}
      >
        <div className="relative z-10 flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold opacity-90 mb-1 tracking-wide">UNIDAD {index + 1}</h3>
            <h2 className="text-2xl font-display font-bold">{unit.title}</h2>
            {unit.description && <p className="text-white/80 mt-1.5 text-sm max-w-sm">{unit.description}</p>}
          </div>
          <div className="bg-white/20 w-16 h-16 rounded-2xl flex items-center justify-center backdrop-blur-sm shrink-0 shadow-inner">
            <DynamicIcon name={unit.icon_emoji} fallback="book-open" size={30} className="text-white" />
          </div>
        </div>
      </div>

      {/* Caminito de lecciones */}
      <div className="relative py-4 flex flex-col items-center gap-4">
        {isLoading ? (
          <div className="animate-pulse space-y-6 flex flex-col items-center">
            {[1, 2, 3].map(i => <div key={i} className="w-16 h-16 bg-gray-200 dark:bg-dark-muted rounded-full" />)}
          </div>
        ) : lessons.length === 0 ? (
          <p className="text-[var(--color-muted)] text-sm">Próximamente más lecciones...</p>
        ) : (
          lessons.map((lesson: import('@/types').Lesson, i: number) => {
            const offset = PATH_OFFSETS[i % PATH_OFFSETS.length]
            const isLessonLocked = isLocked
            const isCompleted = false // TODO: Enlazar progreso real

            return (
              <div key={lesson.id} className="relative w-full flex justify-center py-2 group/node">
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  transition={{ delay: i * 0.05 }}
                  viewport={{ once: true, margin: "-50px" }}
                  style={{ transform: `translateX(${offset}px)` }}
                  className="relative cursor-pointer flex flex-col items-center"
                >
                  <Link
                    to={isLessonLocked ? '#' : `/lesson/${lesson.id}`}
                    onClick={(e) => isLessonLocked && e.preventDefault()}
                    className={`block relative z-10 w-20 h-20 rounded-full flex flex-col items-center justify-center
                      border-b-[6px] active:border-b-0 active:translate-y-[6px] transition-all duration-150
                      ${isLessonLocked
                        ? 'bg-[#e5e5e5] dark:bg-dark-muted border-[#cecece] dark:border-gray-700 cursor-not-allowed text-[#afafaf]'
                        : isCompleted
                          ? 'bg-yellow-400 border-yellow-500 text-white shadow-[0_0_15px_rgba(250,204,21,0.5)]'
                          : 'text-white hover:brightness-110 shadow-lg hover:-translate-y-1'}`}
                    style={!isLessonLocked && !isCompleted ? { backgroundColor: unit.color_hex, borderColor: `${unit.color_hex}99` } : {}}
                  >
                    {isLessonLocked ? (
                      <Lock size={28} />
                    ) : isCompleted ? (
                      <CheckCircle size={32} />
                    ) : (
                      <Star fill="currentColor" size={28} />
                    )}
                  </Link>

                  {/* Tooltip móvil (debajo del nodo) */}
                  <div className="mt-2 text-center sm:hidden min-h-[40px]">
                    <p className={`font-bold text-sm ${isLessonLocked ? 'text-[var(--color-muted)]' : 'text-[var(--color-text)]'}`}>
                      {lesson.title}
                    </p>
                  </div>

                  {/* Tooltip desktop (lateral flotante) */}
                  <div className={`absolute top-1/2 -translate-y-1/2 ${offset >= 0 ? 'right-full mr-5' : 'left-full ml-5'}
                                 opacity-0 group-hover/node:opacity-100 transition-opacity bg-white dark:bg-dark-surface
                                 px-4 py-2.5 rounded-2xl shadow-xl border-2 whitespace-nowrap z-20 pointer-events-none hidden sm:block`}
                    style={{ borderColor: isLessonLocked ? 'var(--color-border)' : unit.color_hex }}>
                    <div className="relative">
                      {/* Triangulito del tooltip */}
                      <div className={`absolute top-1/2 -translate-y-1/2 w-3 h-3 border-t-2 border-r-2 bg-white dark:bg-dark-surface
                                       ${offset >= 0 ? '-right-[23px] rotate-45 border-b-0 border-l-0' : '-left-[23px] -rotate-[135deg] border-b-0 border-l-0'}`}
                        style={{ borderColor: isLessonLocked ? 'var(--color-border)' : unit.color_hex }} />
                      <p className="font-display font-bold text-base text-[var(--color-text)]">{lesson.title}</p>
                      <p className="text-xs text-[var(--color-muted)] font-medium mt-0.5">Lección {i + 1}</p>
                    </div>
                  </div>
                </motion.div>
              </div>
            )
          })
        )}
      </div>
    </div>
  )
}

// ── CourseSection ────────────────────────────────────────────
function CourseSection({ course }: { course: Course }) {
  const { data: units = [], isLoading } = useQuery({
    queryKey: ['units', course.id],
    queryFn: () => unitApi.getByCourse(course.id).then((r) => r.data),
  })

  return (
    <section className="mb-12">
      {/* Header del curso */}
      <div className="flex items-center gap-4 mb-6 p-5 card">
        <div className="w-16 h-16 rounded-2xl bg-alebrije-gradient flex items-center
                        justify-center flex-shrink-0">
          <GraduationCap size={30} className="text-white" />
        </div>
        <div>
          <span className="badge bg-alebrije-coral/10 text-alebrije-coral mb-1">
            {course.difficulty === 'beginner' ? 'Principiante'
              : course.difficulty === 'intermediate' ? 'Intermedio' : 'Avanzado'}
          </span>
          <h2 className="font-display text-2xl font-bold">{course.title}</h2>
          {course.description && (
            <p className="text-sm text-[var(--color-muted)] mt-0.5">{course.description}</p>
          )}
        </div>
      </div>

      {/* Mapa de unidades */}
      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="card p-6 animate-pulse">
              <div className="flex gap-4">
                <div className="w-14 h-14 rounded-2xl bg-gray-200 dark:bg-dark-muted" />
                <div className="flex-1 space-y-3">
                  <div className="h-5 bg-gray-200 dark:bg-dark-muted rounded-full w-1/2" />
                  <div className="h-4 bg-gray-200 dark:bg-dark-muted rounded-full w-3/4" />
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="space-y-6 max-w-xl mx-auto">
          {units.map((unit: Unit, i: number) => (
            <UnitSection key={unit.id} unit={unit} index={i} />
          ))}
          {units.length === 0 && (
            <div className="text-center py-8 text-[var(--color-muted)]">
              Este curso no tiene unidades aún
            </div>
          )}
        </div>
      )}
    </section>
  )
}

// ── LearnPage ────────────────────────────────────────────────
export default function LearnPage() {
  const user = useAuthStore((s) => s.user)

  const { data: courses = [], isLoading, error } = useQuery({
    queryKey: ['courses'],
    queryFn: () => courseApi.list().then((r) => r.data),
  })

  if (isLoading) return <SkeletonPage />

  if (error) {
    return (
      <div className="text-center py-20">
        <CloudOff size={48} className="mx-auto text-[var(--color-muted)] mb-4" />
        <p className="text-[var(--color-muted)]">No se pudieron cargar los cursos</p>
      </div>
    )
  }

  return (
    <div className="max-w-2xl mx-auto">
      {/* Saludo */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        className="mb-8"
      >
        <h1 className="font-display text-3xl font-bold">
          ¡Hola, {user?.username}! 
        </h1>
        <p className="text-[var(--color-muted)] mt-1">
          Continúa tu aventura totonaca
        </p>

        {/* Stats rápidas */}
        <div className="mt-4 grid grid-cols-3 gap-3">
          {[
            { label: 'Racha', value: `${user?.current_streak || 0} días`, Icon: Flame, color: 'text-orange-500' },
            { label: 'Nivel', value: user?.level || 1, Icon: Star, color: 'text-yellow-500' },
            { label: 'XP Total', value: user?.xp_total || 0, Icon: Zap, color: 'text-alebrije-teal' },
          ].map(({ label, value, Icon, color }) => (
            <div key={label} className="card p-3 text-center">
              <Icon className={`mx-auto ${color}`} size={24} />
              <div className="font-display font-bold text-lg">{value}</div>
              <div className="text-xs text-[var(--color-muted)]">{label}</div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Cursos */}
      {courses.length === 0 ? (
        <div className="text-center py-16 card">
          <Star size={48} className="mx-auto text-[var(--color-muted)] mb-4" />
          <p className="font-display text-xl font-bold">No hay cursos disponibles aún</p>
          <p className="text-[var(--color-muted)] mt-2">Vuelve pronto</p>
        </div>
      ) : (
        courses.map((course: Course) => (
          <CourseSection key={course.id} course={course} />
        ))
      )}
    </div>
  )
}
