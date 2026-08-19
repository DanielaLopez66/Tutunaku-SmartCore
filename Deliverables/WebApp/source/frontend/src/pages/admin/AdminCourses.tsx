// TUTUNAKU — AdminCourses
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2, Eye, EyeOff, GraduationCap, Check } from 'lucide-react'
import { courseApi } from '@/utils/api'
import type { Course } from '@/types'
import toast from 'react-hot-toast'

export default function AdminCourses() {
  const qc = useQueryClient()
  const [showForm, setShowForm] = useState(false)
  const [form, setForm] = useState({
    title: '', description: '', difficulty: 'beginner', is_published: false, order_index: 0, color_hex: '#FF6B6B',
  })

  const { data: courses = [], isLoading } = useQuery<Course[]>({
    queryKey: ['admin-courses'],
    queryFn: () => courseApi.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: () => courseApi.create(form),
    onSuccess: () => {
      toast.success('Curso creado')
      qc.invalidateQueries({ queryKey: ['admin-courses'] })
      setShowForm(false)
      setForm({ title: '', description: '', difficulty: 'beginner', is_published: false, order_index: 0, color_hex: '#FF6B6B' })
    },
    onError: () => toast.error('Error al crear curso'),
  })

  const togglePublish = useMutation({
    mutationFn: ({ id, is_published }: { id: string; is_published: boolean }) =>
      courseApi.update(id, { is_published }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['admin-courses'] }),
  })

  const deleteCourse = useMutation({
    mutationFn: (id: string) => courseApi.delete(id),
    onSuccess: () => {
      toast.success('Curso eliminado')
      qc.invalidateQueries({ queryKey: ['admin-courses'] })
    },
    onError: () => toast.error('Error al eliminar'),
  })

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold flex items-center gap-2">
            <GraduationCap className="text-alebrije-violet" /> Gestión de Cursos
          </h1>
          <p className="text-[var(--color-muted)] mt-0.5">{courses.length} cursos</p>
        </div>
        <button onClick={() => setShowForm(!showForm)} className="btn-primary">
          <Plus size={18} /> Nuevo curso
        </button>
      </div>

      {/* Formulario */}
      {showForm && (
        <div className="card p-6 border-2 border-alebrije-coral/30 animate-slide-down">
          <h3 className="font-display font-bold text-lg mb-4">Crear nuevo curso</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold mb-1">Título *</label>
              <input className="input" placeholder="Título del curso"
                value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-bold mb-1">Descripción</label>
              <textarea className="input resize-none h-24" placeholder="Descripción..."
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-bold mb-1">Color del curso</label>
              <input type="color" className="input h-12" value={form.color_hex}
                onChange={(e) => setForm({ ...form, color_hex: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold mb-1">Dificultad</label>
                <select className="input" value={form.difficulty}
                  onChange={(e) => setForm({ ...form, difficulty: e.target.value })}>
                  <option value="beginner">Principiante</option>
                  <option value="intermediate">Intermedio</option>
                  <option value="advanced">Avanzado</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-bold mb-1">Orden</label>
                <input type="number" className="input" value={form.order_index}
                  onChange={(e) => setForm({ ...form, order_index: +e.target.value })} />
              </div>
            </div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" checked={form.is_published}
                onChange={(e) => setForm({ ...form, is_published: e.target.checked })} />
              <span className="text-sm font-semibold">Publicar inmediatamente</span>
            </label>
            <div className="flex gap-3">
              <button onClick={() => createMutation.mutate()} disabled={!form.title || createMutation.isPending}
                className="btn-primary flex-1">
                {createMutation.isPending ? 'Creando...' : 'Crear curso'}
              </button>
              <button onClick={() => setShowForm(false)} className="btn-ghost">Cancelar</button>
            </div>
          </div>
        </div>
      )}

      {/* Lista de cursos */}
      <div className="space-y-3">
        {isLoading ? (
          Array.from({ length: 3 }).map((_, i) => (
            <div key={i} className="card p-5 animate-pulse">
              <div className="h-5 bg-gray-200 dark:bg-dark-muted rounded w-1/3 mb-2" />
              <div className="h-4 bg-gray-200 dark:bg-dark-muted rounded w-2/3" />
            </div>
          ))
        ) : courses.length === 0 ? (
          <div className="text-center py-12 card text-[var(--color-muted)]">
            No hay cursos. Crea el primero.
          </div>
        ) : (
          courses.map((course) => (
            <div key={course.id} className="card p-5 flex items-center gap-4">
              <div className="w-12 h-12 rounded-2xl bg-alebrije-gradient flex items-center
                              justify-center flex-shrink-0">
                <GraduationCap size={22} className="text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 flex-wrap">
                  <h3 className="font-bold">{course.title}</h3>
                  <span className={`badge text-xs flex items-center gap-1 ${
                    course.is_published
                      ? 'bg-green-50 dark:bg-green-900/20 text-green-600'
                      : 'bg-gray-100 dark:bg-dark-muted text-[var(--color-muted)]'
                  }`}>
                    {course.is_published ? <><Check size={12} /> Publicado</> : 'Borrador'}
                  </span>
                  <span className="badge bg-alebrije-violet/10 text-alebrije-violet text-xs">
                    {course.difficulty}
                  </span>
                </div>
                {course.description && (
                  <p className="text-sm text-[var(--color-muted)] line-clamp-1 mt-0.5">
                    {course.description}
                  </p>
                )}
              </div>
              <div className="flex items-center gap-2 flex-shrink-0">
                <button
                  onClick={() => togglePublish.mutate({ id: course.id, is_published: !course.is_published })}
                  className="p-2 rounded-xl hover:bg-gray-100 dark:hover:bg-dark-muted transition-colors"
                  title={course.is_published ? 'Despublicar' : 'Publicar'}
                >
                  {course.is_published
                    ? <EyeOff size={16} className="text-[var(--color-muted)]" />
                    : <Eye size={16} className="text-alebrije-teal" />}
                </button>
                <button
                  onClick={() => confirm(`¿Eliminar "${course.title}"?`) && deleteCourse.mutate(course.id)}
                  className="p-2 rounded-xl hover:bg-red-50 dark:hover:bg-red-900/20
                             transition-colors text-red-400"
                >
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
