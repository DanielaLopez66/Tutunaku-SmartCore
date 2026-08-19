// TUTUNAKU — LessonPage
// Muestra el contenido educativo (clase) antes de los ejercicios
import { useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Play, BookOpen, Volume2, Zap, AlertTriangle, ChevronLeft, ChevronRight } from 'lucide-react'
import { lessonApi, unitApi, ROOT_URL } from '@/utils/api'
import toast from 'react-hot-toast'
import SkeletonPage from '@/components/ui/SkeletonPage'
import { ContentBlock, Lesson } from '@/types'

function ContentBlockRenderer({ block, index }: { block: ContentBlock; index: number }) {
  console.log('Rendering block:', index, block)
  const isTotonaco = block.language === 'toto'

  return (
    <motion.div
      initial={{ opacity: 0, y: 15 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
    >
      {block.type === 'text' && (
        <p className="text-[var(--color-text)] leading-relaxed text-base">{block.content}</p>
      )}

      {block.type === 'example' && (
        <div className={`rounded-2xl p-5 border-2 ${isTotonaco
            ? 'border-alebrije-coral bg-alebrije-coral/5'
            : 'border-alebrije-teal bg-alebrije-teal/5'
          }`}>
          <div className="flex items-start justify-between gap-3">
            <div>
              <span className={`badge mb-2 ${isTotonaco
                  ? 'bg-alebrije-coral/10 text-alebrije-coral'
                  : 'bg-alebrije-teal/10 text-alebrije-teal'
                }`}>
                {isTotonaco ? 'Totonaco' : 'Español'}
              </span>
              <p className={`font-display font-bold text-xl ${isTotonaco ? 'text-alebrije-coral' : 'text-[var(--color-text)]'
                }`}>
                {block.content}
              </p>
              {block.pronunciation && (
                <p className="text-sm font-medium text-alebrije-violet mt-1">
                  {block.pronunciation}
                </p>
              )}
              {block.caption && (
                <p className="text-sm text-[var(--color-muted)] mt-1 italic">
                  → {block.caption}
                </p>
              )}
              {block.example_sentence && (
                <div className="mt-3 bg-[var(--color-surface)] p-3 rounded-xl border border-[var(--color-border)]">
                  <p className="text-sm italic">"{block.example_sentence}"</p>
                </div>
              )}
            </div>
            {isTotonaco && block.audio_url && (
              <button 
                onClick={() => new Audio(block.audio_url?.startsWith('http') ? block.audio_url : ROOT_URL + block.audio_url).play()}
                className="p-2 rounded-xl bg-alebrije-coral/10 hover:bg-alebrije-coral/20
                                  text-alebrije-coral transition-colors flex-shrink-0">
                <Volume2 size={18} />
              </button>
            )}
          </div>
        </div>
      )}

      {block.type === 'image' && (
        <img src={block.content} alt={block.caption} className="rounded-2xl w-full" />
      )}

      {block.type === 'video' && (
        <div className="aspect-video rounded-2xl overflow-hidden bg-black">
          <iframe src={block.content} className="w-full h-full" allowFullScreen title="Video" />
        </div>
      )}

      {block.type === 'audio' && (
        <div className="flex items-center gap-3 p-4 rounded-2xl bg-alebrije-violet/10 border border-alebrije-violet/20">
          <Volume2 className="text-alebrije-violet flex-shrink-0" size={22} />
          <audio controls src={block.content} className="flex-1" />
        </div>
      )}
    </motion.div>
  )
}

export default function LessonPage() {
  const { lessonId } = useParams<{ lessonId: string }>()
  const navigate = useNavigate()

  if (!lessonId) {
    console.log('No lessonId, redirecting')
    navigate('/learn')
    return null
  }

  console.log('LessonPage rendering with lessonId:', lessonId)

  const { data: lesson, isLoading: lessonLoading } = useQuery<Lesson>({
    queryKey: ['lesson', lessonId],
    queryFn: () => lessonApi.get(lessonId!).then((r) => r.data),
    enabled: !!lessonId,
  })

  console.log('LessonPage - Lesson ID:', lessonId, 'Lesson:', lesson, 'Loading:', lessonLoading)

  const { data: unitLessons = [], isLoading: lessonsLoading } = useQuery<Lesson[]>({
    queryKey: ['lessons', lesson?.unit_id],
    queryFn: () => lessonApi.getByUnit(lesson!.unit_id).then((r) => r.data),
    enabled: !!lesson?.unit_id,
  })

  console.log('LessonPage - Unit Lessons:', unitLessons, 'Lessons Loading:', lessonsLoading)

  if (lessonLoading || lessonsLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-alebrije-coral/30 border-t-alebrije-coral
                        rounded-full animate-spin" />
      </div>
    )
  }
  if (!lesson) {
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="card p-10 text-center max-w-md w-full">
          <BookOpen size={56} className="mx-auto mb-4 text-[var(--color-muted)]" />
          <h2 className="font-display text-2xl font-bold mb-2">Lección no encontrada</h2>
          <p className="text-[var(--color-muted)] mb-6">
            La lección que buscas no existe o ha sido eliminada.
          </p>
          <button onClick={() => navigate('/learn')} className="btn-primary w-full">
            Volver al mapa de aprendizaje
          </button>
        </div>
      </div>
    )
  }

  const currentIndex = unitLessons.findIndex(l => l.id === lessonId)
  const nextLesson = unitLessons[currentIndex + 1]
  const prevLesson = unitLessons[currentIndex - 1]

  const hasContent = lesson.content_data && Array.isArray(lesson.content_data) && lesson.content_data.length > 0

  try {
    return (
      <div className="max-w-2xl mx-auto py-4 animate-fade-in">
        {/* Header */}
        <div className="card p-6 mb-6">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 rounded-2xl bg-alebrije-gradient flex items-center
                            justify-center text-2xl">
                <BookOpen className="text-white" size={22} />
              </div>
              <div>
                <p className="text-xs font-bold text-alebrije-coral uppercase tracking-wider">
                  Lección {currentIndex + 1} de {unitLessons.length}
                </p>
                <h1 className="font-display text-2xl font-bold">{lesson.title}</h1>
              </div>
            </div>
            <div className="flex gap-2">
              {prevLesson && (
                <Link
                  to={`/lesson/${prevLesson.id}`}
                  className="btn-ghost p-2"
                  title="Lección anterior"
                >
                  <ChevronLeft size={18} />
                </Link>
              )}
              {nextLesson && (
                <Link
                  to={`/lesson/${nextLesson.id}`}
                  className="btn-ghost p-2"
                  title="Siguiente lección"
                >
                  <ChevronRight size={18} />
                </Link>
              )}
            </div>
          </div>
          {lesson.description && (
            <p className="text-[var(--color-muted)] text-sm leading-relaxed">
              {lesson.description}
            </p>
          )}
          <div className="mt-3 flex items-center gap-2">
            <span className="badge bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 flex items-center gap-1">
              <Zap size={12} /> +{lesson.xp_reward} XP al completar
            </span>
            {lesson.exercises_count != null && (
              <span className="badge bg-alebrije-violet/10 text-alebrije-violet">
                {lesson.exercises_count} ejercicios
              </span>
            )}
          </div>
        </div>

        {/* Contenido educativo */}
        {hasContent ? (
          <div className="card p-6 mb-6 space-y-5">
            <h2 className="font-display text-xl font-bold flex items-center gap-2">
              <BookOpen size={20} className="text-alebrije-teal" />
              Aprende antes de practicar
            </h2>
            {lesson.content_data!.map((block, i) => {
              console.log('Mapping block:', i, block)
              return <ContentBlockRenderer key={i} block={block} index={i} />
            })}
          </div>
        ) : (
          <div className="card p-6 mb-6 text-center">
            <p className="text-[var(--color-muted)]">Esta lección no tiene contenido teórico</p>
          </div>
        )}

        {/* CTA para iniciar ejercicios */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="space-y-3"
        >
          <Link
            to={`/exercise/${lessonId}`}
            className="btn-primary w-full text-lg py-4 justify-center"
          >
            <Play size={20} />
            ¡Comenzar ejercicios!
          </Link>
          <button
            onClick={() => navigate(-1)}
            className="btn-ghost w-full text-sm text-[var(--color-muted)] flex items-center gap-1 justify-center"
          >
            <ChevronLeft size={16} /> Volver al mapa
          </button>
        </motion.div>
      </div>
    )
  } catch (error) {
    console.error('Error rendering lesson page:', error)
    return (
      <div className="min-h-screen flex items-center justify-center p-6">
        <div className="card p-10 text-center max-w-md w-full">
          <AlertTriangle size={56} className="mx-auto mb-4 text-alebrije-coral" />
          <h2 className="font-display text-2xl font-bold mb-2">Error al cargar la lección</h2>
          <p className="text-[var(--color-muted)] mb-6">
            Ha ocurrido un error al mostrar el contenido de la lección.
          </p>
          <button onClick={() => navigate('/learn')} className="btn-primary w-full">
            Volver al mapa de aprendizaje
          </button>
        </div>
      </div>
    )
  }
}
