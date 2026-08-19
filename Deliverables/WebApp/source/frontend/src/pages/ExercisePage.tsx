// ============================================================
// TUTUNAKU — ExercisePage
// Motor de ejercicios: pantalla completa, corazones, XP, feedback
// ============================================================
import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import {
  X, Volume2, Lightbulb, ArrowRight, Heart, Hourglass, PartyPopper, HeartCrack,
  Map, FileQuestion, Repeat, ListChecks, PenLine,
} from 'lucide-react'
import { exerciseApi, lessonApi, ROOT_URL } from '@/utils/api'
import { useAuthStore } from '@/store/authStore'
import type { Exercise, ExerciseAttemptResponse } from '@/types'
import toast from 'react-hot-toast'
import { useHeartTimer } from '@/hooks/useHeartTimer'

// ── ProgressBar ────────────────────────────────────────────
function ProgressBar({ current, total }: { current: number; total: number }) {
  const pct = total > 0 ? (current / total) * 100 : 0
  return (
    <div className="xp-bar h-4">
      <motion.div
        className="xp-bar-fill"
        animate={{ width: `${pct}%` }}
        transition={{ duration: 0.5 }}
      />
    </div>
  )
}

// ── HeartsBar ──────────────────────────────────────────────
function HeartsBar({ hearts, lastHeartRefill }: { hearts: number, lastHeartRefill?: string }) {
  const timeLeft = useHeartTimer(hearts, lastHeartRefill)

  return (
    <div className="flex items-center gap-2">
      <div className="flex gap-1">
        {Array.from({ length: 5 }).map((_, i) => (
          <motion.span
            key={i}
            animate={i >= hearts ? { scale: [1, 0.5, 1] } : {}}
            className={i < hearts ? '' : 'grayscale opacity-30'}
          >
            <Heart size={18} fill="currentColor" className="text-red-500" />
          </motion.span>
        ))}
      </div>
      {timeLeft && (
        <span className="flex items-center gap-1 text-sm font-bold text-red-400 bg-red-50 dark:bg-red-900/20 px-2 py-0.5 rounded-full whitespace-nowrap">
          <Hourglass size={12} /> {timeLeft}
        </span>
      )}
    </div>
  )
}

// ── FeedbackOverlay ─────────────────────────────────────────
function FeedbackOverlay({
  result,
  onNext,
}: {
  result: ExerciseAttemptResponse
  onNext: () => void
}) {
  return (
    <motion.div
      initial={{ y: '100%' }}
      animate={{ y: 0 }}
      exit={{ y: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 300 }}
      className={`fixed bottom-0 left-0 right-0 z-50 p-6 rounded-t-3xl ${
        result.is_correct
          ? 'bg-alebrije-teal text-white'
          : 'bg-alebrije-coral text-white'
      }`}
    >
      <div className="max-w-xl mx-auto">
        <div className="flex items-center gap-3 mb-3">
          {result.is_correct ? <PartyPopper size={30} /> : <HeartCrack size={30} />}
          <div>
            <p className="font-display font-bold text-xl">
              {result.is_correct ? '¡Correcto!' : 'Casi...'}
            </p>
            {!result.is_correct && (
              <p className="text-white/90 text-sm">
                Respuesta: <strong>{result.correct_answer}</strong>
              </p>
            )}
          </div>
          {result.is_correct && (
            <div className="ml-auto flex items-center gap-1 bg-white/20 px-3 py-1 rounded-full">
              <span className="font-bold">+{result.xp_earned} XP</span>
            </div>
          )}
        </div>
        {result.explanation && (
          <p className="text-sm text-white/85 mb-4 leading-relaxed">{result.explanation}</p>
        )}
        <button
          onClick={onNext}
          className="w-full bg-white text-[var(--color-text)] font-bold py-3.5 rounded-2xl
                     hover:bg-white/90 transition-colors flex items-center justify-center gap-2"
        >
          Continuar <ArrowRight size={18} />
        </button>
      </div>
    </motion.div>
  )
}

// ── Exercise renderers ──────────────────────────────────────
function MultipleChoice({
  exercise,
  selected,
  onSelect,
  disabled,
}: {
  exercise: Exercise
  selected: string | null
  onSelect: (v: string) => void
  disabled: boolean
}) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
      {exercise.options?.map((opt) => (
        <motion.button
          key={opt}
          whileHover={!disabled ? { scale: 1.02 } : {}}
          whileTap={!disabled ? { scale: 0.98 } : {}}
          onClick={() => !disabled && onSelect(opt)}
          className={`p-4 rounded-2xl text-left font-semibold border-2 transition-all duration-150 ${
            selected === opt
              ? 'border-alebrije-coral bg-alebrije-coral/10 text-alebrije-coral'
              : 'border-[var(--color-border)] bg-[var(--color-surface)] hover:border-alebrije-coral/40'
          } ${disabled ? 'cursor-not-allowed opacity-80' : 'cursor-pointer'}`}
        >
          {opt}
        </motion.button>
      ))}
    </div>
  )
}

function TextInput({
  value,
  onChange,
  disabled,
  placeholder,
}: {
  value: string
  onChange: (v: string) => void
  disabled: boolean
  placeholder?: string
}) {
  return (
    <input
      type="text"
      className="input text-lg text-center"
      value={value}
      onChange={(e) => onChange(e.target.value)}
      disabled={disabled}
      placeholder={placeholder || 'Escribe tu respuesta...'}
      autoFocus
    />
  )
}

// ── Main ExercisePage ────────────────────────────────────────
export default function ExercisePage() {
  const { lessonId } = useParams<{ lessonId: string }>()
  const navigate = useNavigate()
  const { user, updateUser } = useAuthStore()

  if (!lessonId) {
    navigate('/learn')
    return null
  }

  const [currentIndex, setCurrentIndex] = useState(0)
  const [answer, setAnswer] = useState('')
  const [result, setResult] = useState<ExerciseAttemptResponse | null>(null)
  const [showHint, setShowHint] = useState(false)
  const [hearts, setHearts] = useState(user?.hearts ?? 5)
  const [lastHeartRefill, setLastHeartRefill] = useState(user?.last_heart_refill)
  const [totalXP, setTotalXP] = useState(0)
  const [loading, setLoading] = useState(false)
  const [startTime, setStartTime] = useState(Date.now())
  const [isFinished, setIsFinished] = useState(false)

  const { data: exercises = [], isLoading } = useQuery({
    queryKey: ['exercises', lessonId],
    queryFn: () => exerciseApi.getByLesson(lessonId!).then((r) => r.data),
    enabled: !!lessonId,
  })

  console.log('Exercises:', exercises, 'Loading:', isLoading)

  const currentExercise: Exercise | undefined = exercises[currentIndex]

  useEffect(() => {
    setStartTime(Date.now())
    setAnswer('')
    setShowHint(false)
  }, [currentIndex])

  const handleSubmit = useCallback(async () => {
    if (!answer.trim() || !currentExercise || loading) return
    setLoading(true)
    const elapsed = Math.round((Date.now() - startTime) / 1000)
    try {
      const { data } = await exerciseApi.attempt(currentExercise.id, {
        user_answer: answer.trim(),
        time_spent_seconds: elapsed,
      })
      setResult(data)
      setHearts(data.hearts_remaining)
      if (data.is_correct) setTotalXP((xp) => xp + data.xp_earned)
      if (data.user_stats) {
        updateUser(data.user_stats)
        setLastHeartRefill(data.user_stats.last_heart_refill)
      }
    } catch (err: any) {
      if (err?.response?.status === 403) {
        toast.error('¡Sin corazones! Espera a que se regeneren.')
        navigate('/learn')
      } else {
        toast.error('Error al enviar respuesta')
      }
    } finally {
      setLoading(false)
    }
  }, [answer, currentExercise, loading, startTime])

  const handleNext = useCallback(async () => {
    setResult(null)
    if (currentIndex + 1 >= exercises.length) {
      // Completar lección
      try {
        await lessonApi.complete(lessonId!)
        setIsFinished(true)
      } catch {
        setIsFinished(true)
      }
    } else {
      setCurrentIndex((i) => i + 1)
    }
  }, [currentIndex, exercises.length, lessonId])

  // Enter para confirmar
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Enter' && !result && answer.trim()) handleSubmit()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [handleSubmit, result, answer])

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-alebrije-coral/30 border-t-alebrije-coral
                        rounded-full animate-spin" />
      </div>
    )
  }

  // ── Pantalla de fin de lección ──────────────────────────
  if (isFinished) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="card p-10 text-center max-w-md w-full"
        >
          <PartyPopper size={56} className="mx-auto mb-4 text-alebrije-gold" />
          <h2 className="font-display text-4xl font-bold mb-2">¡Lección completa!</h2>
          <p className="text-[var(--color-muted)] mb-6">Excelente trabajo, sigue así</p>

          <div className="grid grid-cols-2 gap-4 mb-8">
            <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-2xl p-4">
              <div className="text-3xl font-display font-bold text-yellow-600">+{totalXP}</div>
              <div className="text-sm text-[var(--color-muted)]">XP ganado</div>
            </div>
            <div className="bg-red-50 dark:bg-red-900/20 rounded-2xl p-4">
              <div className="text-3xl font-display font-bold text-alebrije-coral">{hearts}</div>
              <div className="text-sm text-[var(--color-muted)]">Corazones</div>
            </div>
          </div>

          <button onClick={() => navigate('/learn')} className="btn-primary w-full text-lg py-3.5 flex items-center gap-2 justify-center">
            <Map size={18} /> Volver al mapa
          </button>
        </motion.div>
      </div>
    )
  }

  if (!currentExercise) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="card p-10 text-center max-w-md w-full">
          <FileQuestion size={56} className="mx-auto mb-4 text-[var(--color-muted)]" />
          <h2 className="font-display text-2xl font-bold mb-2">No hay ejercicios aún</h2>
          <p className="text-[var(--color-muted)] mb-6">
            Esta lección no tiene ejercicios configurados. Los administradores pueden agregar ejercicios desde el panel de administración.
          </p>
          <button onClick={() => navigate('/learn')} className="btn-primary w-full">
            Volver al mapa de aprendizaje
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen flex flex-col bg-[var(--color-bg)]">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-[var(--color-surface)]/95 backdrop-blur-sm
                      border-b border-[var(--color-border)] px-4 py-3">
        <div className="max-w-xl mx-auto flex items-center gap-4">
          <button
            onClick={() => navigate('/learn')}
            className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-muted transition-colors"
          >
            <X size={22} />
          </button>
          <div className="flex-1">
            <ProgressBar current={currentIndex} total={exercises.length} />
          </div>
          <HeartsBar hearts={hearts} lastHeartRefill={lastHeartRefill} />
        </div>
      </div>

      {/* Contenido */}
      <div className="flex-1 flex flex-col items-center justify-center p-6">
        <div className="w-full max-w-xl">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentIndex}
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -40 }}
              className="space-y-6"
            >
              {/* Badge tipo de ejercicio */}
              <div className="flex items-center gap-2">
                <span className="badge bg-alebrije-violet/10 text-alebrije-violet flex items-center gap-1">
                  {currentExercise.type === 'translation' ? <><Repeat size={12} /> Traducción</>
                    : currentExercise.type === 'multiple_choice' ? <><ListChecks size={12} /> Selección múltiple</>
                    : currentExercise.type === 'writing' ? <><PenLine size={12} /> Escritura</>
                    : <><Volume2 size={12} /> Audio</>}
                </span>
                <span className="text-xs text-[var(--color-muted)] font-semibold">
                  {currentIndex + 1} / {exercises.length}
                </span>
              </div>

              {/* Imagen */}
              {currentExercise.image_url && (
                <img
                  src={currentExercise.image_url}
                  alt="ejercicio"
                  className="w-full max-h-48 object-cover rounded-2xl"
                />
              )}

              {/* Audio */}
              {currentExercise.audio_url && (
                <button 
                  onClick={() => new Audio(currentExercise.audio_url?.startsWith('http') ? currentExercise.audio_url : ROOT_URL + currentExercise.audio_url).play()}
                  className="flex items-center gap-2 btn-secondary"
                >
                  <Volume2 size={18} />
                  Escuchar pronunciación
                </button>
              )}

              {/* Pregunta */}
              <h2 className="font-display text-2xl font-bold leading-tight">
                {currentExercise.question}
              </h2>

              {/* Hint */}
              {currentExercise.hint && (
                <div>
                  <button
                    onClick={() => setShowHint(!showHint)}
                    className="flex items-center gap-1.5 text-sm text-alebrije-gold font-semibold"
                  >
                    <Lightbulb size={16} />
                    {showHint ? 'Ocultar pista' : 'Ver pista'}
                  </button>
                  <AnimatePresence>
                    {showHint && (
                      <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: 'auto', opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        className="mt-2 p-3 rounded-xl bg-yellow-50 dark:bg-yellow-900/20
                                   text-yellow-700 dark:text-yellow-400 text-sm font-medium
                                   flex items-start gap-1.5"
                      >
                        <Lightbulb size={14} className="flex-shrink-0 mt-0.5" /> {currentExercise.hint}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              )}

              {/* Input según tipo */}
              <div className={result ? 'pointer-events-none' : ''}>
                {currentExercise.type === 'multiple_choice' ? (
                  <MultipleChoice
                    exercise={currentExercise}
                    selected={answer}
                    onSelect={setAnswer}
                    disabled={!!result}
                  />
                ) : (
                  <TextInput
                    value={answer}
                    onChange={setAnswer}
                    disabled={!!result}
                    placeholder={
                      currentExercise.type === 'translation'
                        ? 'Escribe la traducción...'
                        : 'Tu respuesta...'
                    }
                  />
                )}
              </div>

              {/* Botón confirmar */}
              {!result && (
                <motion.button
                  whileTap={{ scale: 0.97 }}
                  onClick={handleSubmit}
                  disabled={!answer.trim() || loading}
                  className="btn-primary w-full text-lg py-4"
                >
                  {loading ? (
                    <span className="flex items-center justify-center gap-2">
                      <span className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Verificando...
                    </span>
                  ) : (
                    'Verificar respuesta'
                  )}
                </motion.button>
              )}
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Feedback overlay */}
      <AnimatePresence>
        {result && <FeedbackOverlay result={result} onNext={handleNext} />}
      </AnimatePresence>
    </div>
  )
}
