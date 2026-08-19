// TUTUNAKU — AdminContent (Reemplazo de Lecciones)
import { useState, useMemo } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, BookOpen, MessageCircle } from 'lucide-react'
import { motion } from 'framer-motion'
import { courseApi, unitApi, lessonApi } from '@/utils/api'
import type { Course, Unit } from '@/types'
import toast from 'react-hot-toast'

export default function AdminLessons() {
  const qc = useQueryClient()

  // Asumimos que operamos sobre el primer curso disponible por defecto
  const { data: courses = [] } = useQuery<Course[]>({
    queryKey: ['courses-admin'],
    queryFn: () => courseApi.list().then((r) => r.data),
  })

  const courseId = courses[0]?.id || ''

  const { data: units = [] } = useQuery<Unit[]>({
    queryKey: ['units-admin', courseId],
    queryFn: () => unitApi.getByCourse(courseId).then((r) => r.data),
    enabled: !!courseId,
  })

  const [form, setForm] = useState({
    categoria_id: '',
    nueva_categoria: '',
    palabra: '',
    significado: '',
    frase: ''
  })

  const createUnitMutation = useMutation({
    mutationFn: (title: string) => unitApi.create({
      course_id: courseId,
      title: title,
      description: 'Categoría autogenerada',
      icon_emoji: 'package',
      color_hex: '#8B5CF6',
      order_index: units.length + 1,
      is_locked: false,
      xp_reward: 50
    })
  })

  const createLessonMutation = useMutation({
    mutationFn: ({ unitId, data }: { unitId: string, data: any }) =>
      lessonApi.create({
        unit_id: unitId,
        title: data.palabra,
        description: data.frase,
        order_index: 0,
        xp_reward: 20,
        content_type: 'mixed',
        content_data: [
          {
            type: 'example',
            content: data.palabra,
            caption: data.significado,
            language: 'toto'
          }
        ],
        is_published: true
      }),
    onSuccess: () => {
      toast.success('¡Palabra agregada con éxito!')
      setForm(prev => ({ ...prev, palabra: '', significado: '', frase: '' }))
      qc.invalidateQueries({ queryKey: ['units-admin'] })
      qc.invalidateQueries({ queryKey: ['lessons-admin'] })
    },
    onError: () => toast.error('Error al agregar el contenido')
  })

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!form.palabra || !form.significado) {
      return toast.error('Palabra y significado son obligatorios')
    }

    try {
      let finalUnitId = form.categoria_id

      // Si el usuario eligió crear una nueva categoría en su lugar
      if (form.categoria_id === 'NUEVA' && form.nueva_categoria) {
        const newUnitRes = await createUnitMutation.mutateAsync(form.nueva_categoria)
        finalUnitId = newUnitRes.data.id
        setForm(prev => ({ ...prev, categoria_id: finalUnitId }))
      }

      if (!finalUnitId || finalUnitId === 'NUEVA') {
        return toast.error('Debe seleccionar o ingresar una categoría')
      }

      createLessonMutation.mutate({ unitId: finalUnitId, data: form })
    } catch (err) {
      toast.error('Ocurrió un error en el proceso')
    }
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-2xl">
      <div>
        <h1 className="font-display text-3xl font-bold flex items-center gap-3">
          <MessageCircle className="text-alebrije-teal" size={32} />
          Agregar Nuevo Contenido
        </h1>
        <p className="text-[var(--color-muted)] mt-1">
          Añade fácilmente palabras a tu diccionario o crea nuevas categorías de estudio.
        </p>
      </div>

      <div className="card p-6 border-2 border-alebrije-teal/20 shadow-md">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* Categoría */}
          <div className="p-4 bg-gray-50 dark:bg-dark-muted rounded-xl space-y-3">
            <h3 className="font-bold text-sm tracking-widest text-[var(--color-muted)] uppercase">1. Clasificación</h3>
            <div>
              <label className="block text-sm font-bold mb-1">Categoría (Unidad)</label>
              <select
                className="input"
                value={form.categoria_id}
                onChange={e => setForm({ ...form, categoria_id: e.target.value })}
              >
                <option value="">-- Selecciona una categoría existente --</option>
                {units.map((u: Unit) => (
                  <option key={u.id} value={u.id}>{u.title}</option>
                ))}
                <option value="NUEVA">+ Crear una Categoría Nueva</option>
              </select>
            </div>

            {form.categoria_id === 'NUEVA' && (
              <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
                <label className="block text-sm font-bold mt-2 mb-1 text-alebrije-teal">Nombre de la nueva categoría</label>
                <input
                  type="text"
                  className="input border-alebrije-teal"
                  placeholder="Ej: Medios de Transporte"
                  value={form.nueva_categoria}
                  onChange={e => setForm({ ...form, nueva_categoria: e.target.value })}
                />
              </motion.div>
            )}
          </div>

          {/* Palabra */}
          <div className="p-4 bg-gray-50 dark:bg-dark-muted rounded-xl space-y-4">
            <h3 className="font-bold text-sm tracking-widest text-[var(--color-muted)] uppercase">2. Contenido de la Lección</h3>
            <div>
              <label className="block text-sm font-bold mb-1">Palabra (Totonaco) *</label>
              <input
                className="input text-lg font-semibold text-alebrije-coral"
                placeholder="Ej: Mistu"
                value={form.palabra}
                onChange={e => setForm({ ...form, palabra: e.target.value })}
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold mb-1">Significado (Español) *</label>
                <input
                  className="input"
                  placeholder="Ej: Gato"
                  value={form.significado}
                  onChange={e => setForm({ ...form, significado: e.target.value })}
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-bold mb-1">Frase de ejemplo</label>
                <input
                  className="input italic"
                  placeholder="Ej: Putsenke mistu (Gato negro)"
                  value={form.frase}
                  onChange={e => setForm({ ...form, frase: e.target.value })}
                />
              </div>
            </div>
          </div>

          <div className="pt-2">
            <button
              type="submit"
              disabled={createUnitMutation.isPending || createLessonMutation.isPending || (!form.categoria_id && form.categoria_id !== 'NUEVA')}
              className="btn-primary w-full py-3 text-lg"
            >
              {createUnitMutation.isPending || createLessonMutation.isPending ? 'Guardando...' : 'Guardar Nueva Palabra'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
