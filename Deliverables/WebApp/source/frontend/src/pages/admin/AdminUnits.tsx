// TUTUNAKU — AdminUnits
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Plus, Edit, Trash2, BookOpen } from 'lucide-react'
import { courseApi, unitApi } from '@/utils/api'
import { DynamicIcon, UNIT_ICON_OPTIONS, ICON_LABELS } from '@/utils/icons'
import type { Course, Unit } from '@/types'
import toast from 'react-hot-toast'

export default function AdminUnits() {
  const qc = useQueryClient()
  const [selectedCourse, setSelectedCourse] = useState('')
  const [showForm, setShowForm] = useState(false)
  const [editingUnit, setEditingUnit] = useState<Unit | null>(null)
  const [form, setForm] = useState({
    course_id: '', title: '', description: '', icon_emoji: 'book-open', color_hex: '#FF6B6B',
    order_index: 0, is_locked: true, xp_reward: 50,
  })

  const { data: courses = [] } = useQuery<Course[]>({
    queryKey: ['courses-admin'],
    queryFn: () => courseApi.list().then((r) => r.data),
  })

  const { data: units = [] } = useQuery<Unit[]>({
    queryKey: ['units-admin', selectedCourse],
    queryFn: () => unitApi.getByCourse(selectedCourse).then((r) => r.data),
    enabled: !!selectedCourse,
  })

  const createMutation = useMutation({
    mutationFn: () => unitApi.create(form),
    onSuccess: () => {
      toast.success('Unidad creada')
      qc.invalidateQueries({ queryKey: ['units-admin'] })
      resetForm()
    },
    onError: () => toast.error('Error al crear unidad'),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: object }) => unitApi.update(id, data),
    onSuccess: () => {
      toast.success('Unidad actualizada')
      qc.invalidateQueries({ queryKey: ['units-admin'] })
      resetForm()
    },
    onError: () => toast.error('Error al actualizar'),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => unitApi.delete(id),
    onSuccess: () => {
      toast.success('Unidad eliminada')
      qc.invalidateQueries({ queryKey: ['units-admin'] })
    },
    onError: () => toast.error('Error al eliminar'),
  })

  const resetForm = () => {
    setShowForm(false)
    setEditingUnit(null)
    setForm({
      course_id: selectedCourse, title: '', description: '', icon_emoji: 'book-open', color_hex: '#FF6B6B',
      order_index: 0, is_locked: true, xp_reward: 50,
    })
  }

  const startEdit = (unit: Unit) => {
    setEditingUnit(unit)
    setForm({
      course_id: unit.course_id, title: unit.title, description: unit.description || '',
      icon_emoji: unit.icon_emoji, color_hex: unit.color_hex,
      order_index: unit.order_index, is_locked: unit.is_locked, xp_reward: unit.xp_reward,
    })
    setShowForm(true)
  }

  const handleSubmit = () => {
    if (editingUnit) {
      updateMutation.mutate({ id: editingUnit.id, data: form })
    } else {
      createMutation.mutate()
    }
  }

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold flex items-center gap-2">
            <BookOpen className="text-alebrije-violet" /> Gestión de Unidades
          </h1>
          <p className="text-[var(--color-muted)] mt-0.5">
            Crea y organiza las unidades de los cursos
          </p>
        </div>
        <button onClick={() => { setForm({ ...form, course_id: selectedCourse }); setShowForm(!showForm) }} className="btn-primary" disabled={!selectedCourse}>
          <Plus size={18} /> Nueva unidad
        </button>
      </div>

      {/* Selector de curso */}
      <div className="card p-4">
        <label className="block text-sm font-bold mb-2">Seleccionar curso</label>
        <select className="input" value={selectedCourse}
          onChange={(e) => { setSelectedCourse(e.target.value); resetForm() }}>
          <option value="">-- Seleccionar curso --</option>
          {courses.map((c) => (
            <option key={c.id} value={c.id}>{c.title}</option>
          ))}
        </select>
      </div>

      {/* Lista de unidades */}
      {selectedCourse && (
        <div className="grid gap-4">
          {units.map((unit) => (
            <div key={unit.id} className="card p-4 flex items-center justify-between"
              style={{ borderLeft: `4px solid ${unit.color_hex}` }}>
              <div className="flex items-center gap-3">
                <DynamicIcon name={unit.icon_emoji} fallback="book-open" size={28} style={{ color: unit.color_hex }} />
                <div>
                  <h3 className="font-bold">{unit.title}</h3>
                  <p className="text-sm text-[var(--color-muted)]">{unit.description}</p>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="badge" style={{ backgroundColor: unit.color_hex }}>
                      {unit.color_hex}
                    </span>
                    <span className="text-xs">XP: {unit.xp_reward}</span>
                  </div>
                </div>
              </div>
              <div className="flex gap-2">
                <button onClick={() => startEdit(unit)} className="btn-ghost">
                  <Edit size={16} />
                </button>
                <button onClick={() => deleteMutation.mutate(unit.id)} className="btn-ghost text-red-500">
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Formulario */}
      {showForm && (
        <div className="card p-6 border-2 border-alebrije-coral/30 animate-slide-down">
          <h3 className="font-display font-bold text-lg mb-4">
            {editingUnit ? 'Editar unidad' : 'Crear nueva unidad'}
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-bold mb-1">Título *</label>
              <input className="input" placeholder="Título de la unidad"
                value={form.title} onChange={(e) => setForm({ ...form, title: e.target.value })} />
            </div>
            <div>
              <label className="block text-sm font-bold mb-1">Descripción</label>
              <textarea className="input resize-none h-24" placeholder="Descripción..."
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })} />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-bold mb-1">Ícono</label>
                <div className="flex items-center gap-2">
                  <div className="w-10 h-10 rounded-lg flex items-center justify-center shrink-0"
                    style={{ backgroundColor: `${form.color_hex}20` }}>
                    <DynamicIcon name={form.icon_emoji} fallback="book-open" size={20} style={{ color: form.color_hex }} />
                  </div>
                  <select className="input" value={form.icon_emoji}
                    onChange={(e) => setForm({ ...form, icon_emoji: e.target.value })}>
                    {UNIT_ICON_OPTIONS.map((key) => (
                      <option key={key} value={key}>{ICON_LABELS[key]}</option>
                    ))}
                  </select>
                </div>
              </div>
              <div>
                <label className="block text-sm font-bold mb-1">Color</label>
                <input type="color" className="input h-10" value={form.color_hex}
                  onChange={(e) => setForm({ ...form, color_hex: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-bold mb-1">Orden</label>
                <input type="number" className="input" value={form.order_index}
                  onChange={(e) => setForm({ ...form, order_index: +e.target.value })} />
              </div>
              <div>
                <label className="block text-sm font-bold mb-1">XP Recompensa</label>
                <input type="number" className="input" value={form.xp_reward}
                  onChange={(e) => setForm({ ...form, xp_reward: +e.target.value })} />
              </div>
              <div className="flex items-center">
                <label className="flex items-center gap-2 cursor-pointer">
                  <input type="checkbox" checked={form.is_locked}
                    onChange={(e) => setForm({ ...form, is_locked: e.target.checked })} />
                  <span className="text-sm font-semibold">Bloqueada</span>
                </label>
              </div>
            </div>
            <div className="flex gap-3">
              <button onClick={handleSubmit} disabled={!form.title || createMutation.isPending || updateMutation.isPending}
                className="btn-primary flex-1">
                {createMutation.isPending || updateMutation.isPending ? 'Guardando...' : (editingUnit ? 'Actualizar' : 'Crear unidad')}
              </button>
              <button onClick={resetForm} className="btn-secondary">Cancelar</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}