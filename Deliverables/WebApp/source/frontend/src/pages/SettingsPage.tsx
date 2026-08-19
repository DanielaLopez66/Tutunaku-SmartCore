// TUTUNAKU — SettingsPage (recordatorios para usuarios, actividad en vivo para admin)
import { useEffect, useRef, useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import { Moon, Sun, Bell, BellOff, Trash2, Plus, UserPlus, GraduationCap, Trophy, Palette, Clock, Radio, Settings as SettingsIcon } from 'lucide-react'
import toast from 'react-hot-toast'
import { useThemeStore } from '@/store/themeStore'
import { useAuthStore } from '@/store/authStore'
import { reminderApi } from '@/utils/api'
import { connectSocket, disconnectSocket } from '@/utils/socket'
import type {
  AdminLessonCompletedEvent, AdminNewUserEvent, AdminXpRecordEvent, Reminder, ReminderCreate,
} from '@/types'

const DAYS = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const MAX_ADMIN_FEED = 20

function AppearanceCard() {
  const { isDark, toggle } = useThemeStore()
  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-4 flex items-center gap-2">
        <Palette size={20} className="text-alebrije-violet" /> Apariencia
      </h2>
      <div className="flex items-center justify-between">
        <div>
          <p className="font-semibold">Modo oscuro</p>
          <p className="text-sm text-[var(--color-muted)]">
            Cambia entre tema claro y oscuro
          </p>
        </div>
        <button
          onClick={toggle}
          className={`w-14 h-7 rounded-full transition-all duration-300 relative ${
            isDark ? 'bg-alebrije-coral' : 'bg-gray-300'
          }`}
        >
          <span
            className={`absolute top-0.5 w-6 h-6 bg-white rounded-full shadow transition-all duration-300 ${
              isDark ? 'left-7' : 'left-0.5'
            }`}
          />
        </button>
      </div>
    </div>
  )
}

// ── Vista de usuario: recordatorios de estudio (con detección de zona horaria) ──
function UserReminders() {
  const qc = useQueryClient()

  const [newHour, setNewHour] = useState(8)
  const [newMin, setNewMin] = useState(0)
  const [newDays, setNewDays] = useState([0, 1, 2, 3, 4, 5, 6])

  const { data: reminders = [] } = useQuery<Reminder[]>({
    queryKey: ['reminders'],
    queryFn: () => reminderApi.list().then((r) => r.data),
  })

  const createMutation = useMutation({
    mutationFn: (d: ReminderCreate) => reminderApi.create(d),
    onSuccess: () => {
      toast.success('Recordatorio creado')
      qc.invalidateQueries({ queryKey: ['reminders'] })
    },
    onError: (e: any) => toast.error(e?.response?.data?.detail || 'Error al crear recordatorio'),
  })

  const toggleMutation = useMutation({
    mutationFn: ({ id, is_active }: { id: string; is_active: boolean }) =>
      reminderApi.update(id, { is_active }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['reminders'] }),
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => reminderApi.delete(id),
    onSuccess: () => {
      toast.success('Recordatorio eliminado')
      qc.invalidateQueries({ queryKey: ['reminders'] })
    },
  })

  const toggleDay = (d: number) =>
    setNewDays((prev) =>
      prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d].sort()
    )

  function handleCreate() {
    const timezone = Intl.DateTimeFormat().resolvedOptions().timeZone
    createMutation.mutate({ hour: newHour, minute: newMin, days_of_week: newDays, timezone })
  }

  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-4 flex items-center gap-2">
        <Clock size={20} className="text-alebrije-coral" /> Recordatorios de estudio
      </h2>
      <p className="text-sm text-[var(--color-muted)] mb-5">
        Configura alarmas diarias para recordarte estudiar totonaco. Se envían de verdad
        (revisa la campana de notificaciones a la hora programada).
      </p>

      {/* Recordatorios existentes */}
      {reminders.length > 0 && (
        <div className="space-y-3 mb-6">
          {reminders.map((r) => (
            <div key={r.id}
              className="flex items-center justify-between p-4 rounded-2xl
                         bg-gray-50 dark:bg-dark-muted">
              <div>
                <p className="font-bold font-display text-xl">
                  {String(r.hour).padStart(2, '0')}:{String(r.minute).padStart(2, '0')}
                </p>
                <p className="text-xs text-[var(--color-muted)] mt-0.5">
                  {r.days_of_week.map((d) => DAYS[d]).join(', ')}
                </p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => toggleMutation.mutate({ id: r.id, is_active: !r.is_active })}
                  className={`p-2 rounded-xl transition-colors ${
                    r.is_active
                      ? 'bg-alebrije-teal/10 text-alebrije-teal'
                      : 'bg-gray-200 dark:bg-dark-border text-[var(--color-muted)]'
                  }`}
                >
                  {r.is_active ? <Bell size={18} /> : <BellOff size={18} />}
                </button>
                <button
                  onClick={() => deleteMutation.mutate(r.id)}
                  className="p-2 rounded-xl bg-red-50 dark:bg-red-900/20 text-red-500"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Crear nuevo */}
      {reminders.length < 3 && (
        <div className="border-2 border-dashed border-[var(--color-border)] rounded-2xl p-5">
          <p className="font-semibold mb-4 text-sm">Nuevo recordatorio</p>

          <div className="flex gap-3 mb-4">
            <div className="flex-1">
              <label className="text-xs font-bold text-[var(--color-muted)] block mb-1">
                Hora
              </label>
              <select
                className="input text-center"
                value={newHour}
                onChange={(e) => setNewHour(Number(e.target.value))}
              >
                {Array.from({ length: 24 }, (_, i) => (
                  <option key={i} value={i}>
                    {String(i).padStart(2, '0')}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="text-xs font-bold text-[var(--color-muted)] block mb-1">
                Minutos
              </label>
              <select
                className="input text-center"
                value={newMin}
                onChange={(e) => setNewMin(Number(e.target.value))}
              >
                {[0, 15, 30, 45].map((m) => (
                  <option key={m} value={m}>
                    {String(m).padStart(2, '0')}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="mb-4">
            <label className="text-xs font-bold text-[var(--color-muted)] block mb-2">
              Días
            </label>
            <div className="flex gap-1.5 flex-wrap">
              {DAYS.map((d, i) => (
                <button
                  key={d}
                  onClick={() => toggleDay(i)}
                  className={`w-10 h-10 rounded-xl text-xs font-bold transition-all ${
                    newDays.includes(i)
                      ? 'bg-alebrije-coral text-white'
                      : 'bg-gray-100 dark:bg-dark-muted text-[var(--color-muted)]'
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <p className="text-xs text-[var(--color-muted)] mb-4">
            Zona horaria detectada: <strong>{Intl.DateTimeFormat().resolvedOptions().timeZone}</strong>
          </p>

          <button
            onClick={handleCreate}
            disabled={createMutation.isPending || newDays.length === 0}
            className="btn-primary w-full"
          >
            <Plus size={18} />
            Agregar recordatorio
          </button>
        </div>
      )}

      {reminders.length >= 3 && (
        <p className="text-center text-sm text-[var(--color-muted)]">
          Máximo 3 recordatorios permitidos
        </p>
      )}
    </div>
  )
}

// ── Vista de admin: actividad en vivo en vez de recordatorios ──
type AdminFeedItem =
  | { id: number; kind: 'new_user'; at: string; data: AdminNewUserEvent }
  | { id: number; kind: 'lesson_completed'; at: string; data: AdminLessonCompletedEvent }
  | { id: number; kind: 'xp_record'; at: string; data: AdminXpRecordEvent }

function AdminLiveActivity() {
  const [items, setItems] = useState<AdminFeedItem[]>([])
  const nextId = useRef(1)

  useEffect(() => {
    const socket = connectSocket()

    const onNewUser = (payload: AdminNewUserEvent) => {
      const item: AdminFeedItem = {
        id: nextId.current++, kind: 'new_user', at: new Date().toLocaleTimeString('es'), data: payload,
      }
      setItems((prev) => [item, ...prev].slice(0, MAX_ADMIN_FEED))
    }

    const onLessonCompleted = (payload: AdminLessonCompletedEvent) => {
      const item: AdminFeedItem = {
        id: nextId.current++, kind: 'lesson_completed', at: new Date().toLocaleTimeString('es'), data: payload,
      }
      setItems((prev) => [item, ...prev].slice(0, MAX_ADMIN_FEED))
    }

    const onXpRecord = (payload: AdminXpRecordEvent) => {
      const item: AdminFeedItem = {
        id: nextId.current++, kind: 'xp_record', at: new Date().toLocaleTimeString('es'), data: payload,
      }
      setItems((prev) => [item, ...prev].slice(0, MAX_ADMIN_FEED))
    }

    socket.on('admin_new_user', onNewUser)
    socket.on('admin_lesson_completed', onLessonCompleted)
    socket.on('admin_xp_record', onXpRecord)

    return () => {
      socket.off('admin_new_user', onNewUser)
      socket.off('admin_lesson_completed', onLessonCompleted)
      socket.off('admin_xp_record', onXpRecord)
      disconnectSocket()
    }
  }, [])

  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-1 flex items-center gap-2">
        <Radio size={20} className="text-alebrije-teal" /> Actividad en vivo
      </h2>
      <p className="text-sm text-[var(--color-muted)] mb-5">
        Nuevos usuarios, lecciones completadas y récords de XP, en tiempo real vía Socket.IO.
      </p>

      {items.length === 0 && (
        <p className="text-sm text-[var(--color-muted)] text-center py-6">
          Sin actividad todavía. Aparecerá aquí en cuanto ocurra.
        </p>
      )}

      <div className="space-y-2 max-h-[28rem] overflow-y-auto">
        <AnimatePresence initial={false}>
          {items.map((item) => (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-start gap-3 p-3 rounded-2xl bg-gray-50 dark:bg-dark-muted"
            >
              {item.kind === 'new_user' && (
                <>
                  <UserPlus size={18} className="text-alebrije-teal mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">
                      Nuevo usuario: {item.data.username}
                    </p>
                    <p className="text-xs text-[var(--color-muted)] truncate">{item.data.email}</p>
                  </div>
                </>
              )}
              {item.kind === 'lesson_completed' && (
                <>
                  <GraduationCap size={18} className="text-alebrije-violet mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">
                      {item.data.username} completó "{item.data.lesson_title}"
                    </p>
                    <p className="text-xs text-[var(--color-muted)]">+{item.data.xp_earned} XP</p>
                  </div>
                </>
              )}
              {item.kind === 'xp_record' && (
                <>
                  <Trophy size={18} className="text-alebrije-gold mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">
                      {item.data.username} es el nuevo #1 del ranking
                    </p>
                    <p className="text-xs text-[var(--color-muted)]">
                      {item.data.xp_total} XP (superó {item.data.previous_record})
                    </p>
                  </div>
                </>
              )}
              <span className="text-xs text-[var(--color-muted)] flex-shrink-0">{item.at}</span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}

export default function SettingsPage() {
  const user = useAuthStore((s) => s.user)
  const isAdmin = user?.role === 'admin'

  return (
    <div className="max-w-xl mx-auto space-y-8 animate-fade-in">
      <h1 className="font-display text-3xl font-bold flex items-center gap-2">
        <SettingsIcon className="text-alebrije-coral" /> Configuración
      </h1>

      <AppearanceCard />

      {isAdmin ? <AdminLiveActivity /> : <UserReminders />}
    </div>
  )
}
