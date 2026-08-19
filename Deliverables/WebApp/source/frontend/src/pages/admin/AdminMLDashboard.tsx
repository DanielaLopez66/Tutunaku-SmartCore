// ============================================================
// TUTUNAKU — AdminMLDashboard
// Dashboard en tiempo real (Socket.IO) de la API Inteligente (/api/ml)
// ============================================================
import { useEffect, useRef, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { motion, AnimatePresence } from 'framer-motion'
import toast from 'react-hot-toast'
import {
  Activity, AlertTriangle, Brain, Radio, RefreshCw, ScrollText, Users2,
  Wifi, WifiOff, Zap, Sparkles, TrendingUp, Circle, type LucideIcon,
} from 'lucide-react'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
} from 'recharts'
import { mlApi } from '@/utils/api'
import { connectSocket, disconnectSocket, getSocket } from '@/utils/socket'
import type {
  AnomalyAlertEvent, MLModelInfo, NewPredictionEvent,
  PlatformLoadForecastResponse, UserProgressUpdateEvent,
} from '@/types'

const MAX_FEED_ITEMS = 15
const MAX_LOG_ITEMS = 40

const EVENT_META: Record<string, { Icon: LucideIcon; label: string; color: string }> = {
  connect: { Icon: Wifi, label: 'conectado', color: 'text-green-600' },
  disconnect: { Icon: WifiOff, label: 'desconectado', color: 'text-red-500' },
  new_prediction: { Icon: Sparkles, label: 'new_prediction', color: 'text-alebrije-coral' },
  anomaly_alert: { Icon: AlertTriangle, label: 'anomaly_alert', color: 'text-red-500' },
  platform_load_update: { Icon: TrendingUp, label: 'platform_load_update', color: 'text-alebrije-teal' },
  user_progress_update: { Icon: Users2, label: 'user_progress_update', color: 'text-alebrije-gold' },
}

interface RawEvent {
  id: number
  event: string
  at: string
  payload: unknown
}

function StatusPill({ connected, pulseKey }: { connected: boolean; pulseKey: number }) {
  return (
    <span
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-xs font-bold ${
        connected
          ? 'bg-green-50 dark:bg-green-900/20 text-green-600'
          : 'bg-red-50 dark:bg-red-900/20 text-red-500'
      }`}
    >
      {connected ? <Wifi size={14} /> : <WifiOff size={14} />}
      {connected ? 'Conectado en tiempo real' : 'Desconectado'}
      {connected && (
        <motion.span
          key={pulseKey}
          initial={{ scale: 2, opacity: 0.6 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="w-2 h-2 rounded-full bg-green-500"
          title="Último evento recibido"
        />
      )}
    </span>
  )
}

function EventLogPanel({ items, counts }: { items: RawEvent[]; counts: Record<string, number> }) {
  const total = Object.values(counts).reduce((a, b) => a + b, 0)

  return (
    <div className="card p-6">
      <div className="flex items-center justify-between mb-1 flex-wrap gap-2">
        <h2 className="font-display font-bold text-xl flex items-center gap-2">
          <ScrollText size={20} className="text-alebrije-violet" /> Bitácora de sockets en vivo
        </h2>
        <span className="badge bg-violet-50 dark:bg-violet-900/20 text-alebrije-violet">
          {total} eventos recibidos
        </span>
      </div>
      <p className="text-xs text-[var(--color-muted)] mb-3">
        Cada línea es un evento real recibido por Socket.IO, en el momento en que llega.
      </p>

      {Object.keys(counts).length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3">
          {Object.entries(counts).map(([event, count]) => {
            const Icon = EVENT_META[event]?.Icon ?? Circle
            return (
              <span key={event} className="badge bg-gray-100 dark:bg-dark-muted text-[var(--color-muted)] flex items-center gap-1">
                <Icon size={12} /> {EVENT_META[event]?.label ?? event}: {count}
              </span>
            )
          })}
        </div>
      )}

      <div className="bg-gray-900 dark:bg-black rounded-2xl p-3 max-h-80 overflow-y-auto font-mono text-xs space-y-1">
        {items.length === 0 && (
          <p className="text-gray-500">Esperando el primer evento…</p>
        )}
        <AnimatePresence initial={false}>
          {items.map((item) => {
            const meta = EVENT_META[item.event] ?? { Icon: Circle, label: item.event, color: 'text-gray-300' }
            const Icon = meta.Icon
            return (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, x: -8 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0 }}
                className="flex gap-2 text-gray-300"
              >
                <span className="text-gray-500 flex-shrink-0">{item.at}</span>
                <span className={`flex-shrink-0 font-bold flex items-center gap-1 ${meta.color}`}>
                  <Icon size={12} /> {meta.label}
                </span>
                <span className="text-gray-500 truncate">
                  {item.payload ? JSON.stringify(item.payload).slice(0, 140) : ''}
                </span>
              </motion.div>
            )
          })}
        </AnimatePresence>
      </div>
    </div>
  )
}

function ModelsPanel() {
  const { data: models, isLoading } = useQuery<MLModelInfo[]>({
    queryKey: ['ml-models'],
    queryFn: () => mlApi.listModels().then((r) => r.data),
    refetchInterval: 60_000,
  })

  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-4 flex items-center gap-2">
        <Brain size={20} className="text-alebrije-violet" /> Modelos entrenados
      </h2>
      {isLoading && <p className="text-sm text-[var(--color-muted)]">Cargando catálogo…</p>}
      <div className="space-y-2">
        {models?.map((m) => (
          <div
            key={m.model_name}
            className="flex items-center justify-between gap-3 p-3 rounded-2xl bg-gray-50 dark:bg-dark-muted"
          >
            <div>
              <p className="text-sm font-semibold">{m.model_name}</p>
              <p className="text-xs text-[var(--color-muted)]">
                {m.algorithm} · v{m.version} · {m.task}
              </p>
            </div>
            <span
              className={`badge ${
                m.loaded
                  ? 'bg-green-50 dark:bg-green-900/20 text-green-600'
                  : 'bg-red-50 dark:bg-red-900/20 text-red-500'
              }`}
            >
              {m.loaded ? 'activo' : 'no disponible'}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function PlatformLoadChart({ live }: { live: PlatformLoadForecastResponse | null }) {
  const { data: initial } = useQuery<PlatformLoadForecastResponse>({
    queryKey: ['ml-platform-load-forecast'],
    queryFn: () => mlApi.platformLoadForecast(6).then((r) => r.data),
    refetchOnWindowFocus: false,
  })

  const forecast = (live ?? initial)?.forecast ?? []

  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-1 flex items-center gap-2">
        <Activity size={20} className="text-alebrije-teal" /> Pronóstico de carga (S08)
      </h2>
      <p className="text-xs text-[var(--color-muted)] mb-4">
        Peticiones/minuto estimadas para las próximas horas — modelo entrenado, no aprendizaje en vivo.
        {live && <span className="text-alebrije-teal font-semibold"> · actualizado por socket</span>}
      </p>
      {forecast.length > 0 ? (
        <ResponsiveContainer width="100%" height={220}>
          <LineChart data={forecast}>
            <CartesianGrid strokeDasharray="3 3" opacity={0.2} />
            <XAxis dataKey="horizon_hours" tickFormatter={(h) => `+${h}h`} fontSize={12} />
            <YAxis fontSize={12} />
            <Tooltip labelFormatter={(h) => `Horizonte: +${h}h`} />
            <Line
              type="monotone"
              dataKey="predicted_requests_per_minute"
              stroke="#FF6B6B"
              strokeWidth={2}
              dot={{ r: 3 }}
              isAnimationActive
            />
          </LineChart>
        </ResponsiveContainer>
      ) : (
        <p className="text-sm text-[var(--color-muted)]">Sin datos de pronóstico todavía.</p>
      )}
    </div>
  )
}

function UserProgressPanel({ progress }: { progress: UserProgressUpdateEvent | null }) {
  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-4 flex items-center gap-2">
        <Users2 size={20} className="text-alebrije-gold" /> Progreso de usuarios (en vivo)
      </h2>
      {progress ? (
        <motion.div
          key={progress.timestamp}
          initial={{ opacity: 0.4 }}
          animate={{ opacity: 1 }}
          className="grid grid-cols-3 gap-3 text-center"
        >
          <div>
            <p className="text-2xl font-bold text-alebrije-coral">{progress.active_users}</p>
            <p className="text-xs text-[var(--color-muted)]">usuarios activos</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-alebrije-teal">{progress.attempts_count}</p>
            <p className="text-xs text-[var(--color-muted)]">intentos</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-alebrije-gold">{progress.xp_gained}</p>
            <p className="text-xs text-[var(--color-muted)]">XP ganado</p>
          </div>
        </motion.div>
      ) : (
        <p className="text-sm text-[var(--color-muted)]">Esperando la próxima actualización…</p>
      )}
    </div>
  )
}

function PredictionsFeed({ items }: { items: NewPredictionEvent[] }) {
  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-4 flex items-center gap-2">
        <Radio size={20} className="text-alebrije-coral" /> Predicciones recientes
      </h2>
      {items.length === 0 && (
        <p className="text-sm text-[var(--color-muted)]">
          Aún no hay predicciones. Prueba los formularios de abajo.
        </p>
      )}
      <div className="space-y-2 max-h-72 overflow-y-auto">
        <AnimatePresence initial={false}>
          {items.map((item, i) => (
            <motion.div
              key={`${item.inference_date}-${i}`}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className="flex items-center justify-between p-3 rounded-2xl bg-gray-50 dark:bg-dark-muted text-sm"
            >
              <span className="font-semibold">{item.endpoint}</span>
              <span className="text-xs text-[var(--color-muted)]">
                {new Date(item.inference_date).toLocaleTimeString('es')}
              </span>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </div>
  )
}

function AnomalyAlerts({ items }: { items: AnomalyAlertEvent[] }) {
  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-4 flex items-center gap-2">
        <AlertTriangle size={20} className="text-red-500" /> Alertas de anomalías (U04)
      </h2>
      {items.length === 0 && (
        <p className="text-sm text-[var(--color-muted)]">Sin alertas recientes.</p>
      )}
      <div className="space-y-2 max-h-56 overflow-y-auto">
        {items.map((item, i) => (
          <div
            key={i}
            className="flex items-center justify-between p-3 rounded-2xl bg-red-50 dark:bg-red-900/20 text-sm"
          >
            <span className="font-semibold text-red-600">Score: {item.anomaly_score.toFixed(2)}</span>
            <span className="text-xs text-[var(--color-muted)]">
              {new Date(item.inference_date).toLocaleTimeString('es')}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

// ── Forzar los jobs periódicos ahora, sin esperar el intervalo ──
function ForceUpdatesPanel() {
  const [loading, setLoading] = useState<string | null>(null)

  async function trigger(name: string, fn: () => Promise<unknown>) {
    setLoading(name)
    try {
      await fn()
      toast.success(`Evento "${name}" emitido`)
    } catch {
      toast.error(`No se pudo emitir "${name}"`)
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="card p-6">
      <h2 className="font-display font-bold text-xl mb-1 flex items-center gap-2">
        <RefreshCw size={20} className="text-alebrije-teal" /> Forzar actualización ahora
      </h2>
      <p className="text-xs text-[var(--color-muted)] mb-4">
        Los jobs automáticos corren cada {' '}
        <strong>20s</strong> (carga) y <strong>15s</strong> (progreso). Usa estos botones para verlos
        de inmediato en la bitácora de abajo.
      </p>
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => trigger('platform_load_update', mlApi.triggerPlatformLoadUpdate)}
          disabled={loading !== null}
          className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          <TrendingUp size={14} /> {loading === 'platform_load_update' ? 'Emitiendo…' : 'Forzar pronóstico de carga'}
        </button>
        <button
          onClick={() => trigger('user_progress_update', mlApi.triggerUserProgressUpdate)}
          disabled={loading !== null}
          className="btn-primary text-xs px-3 py-1.5 flex items-center gap-1.5"
        >
          <Users2 size={14} /> {loading === 'user_progress_update' ? 'Emitiendo…' : 'Forzar progreso de usuarios'}
        </button>
      </div>
    </div>
  )
}

// ── Formularios de prueba (consumo REAL de la API, sin simular) ──
function TryPredictTime() {
  const [result, setResult] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function run() {
    setLoading(true)
    setResult(null)
    try {
      const { data } = await mlApi.predictTime({
        attempt_number: 1, difficulty: 3, connectivity_quality: 0.75,
        device_type: 'mobile', hour_of_day: new Date().getHours(),
        day_of_week: new Date().getDay(), is_correct: true, hearts_before: 5,
      })
      setResult(`${data.predicted_time_seconds.toFixed(1)} s (modelo ${data.model})`)
    } catch {
      setResult('Error al consultar el modelo')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 rounded-2xl bg-gray-50 dark:bg-dark-muted">
      <p className="text-sm font-semibold mb-2">S02 · Predecir tiempo de respuesta</p>
      <button onClick={run} disabled={loading} className="btn-primary text-xs px-3 py-1.5">
        {loading ? 'Consultando…' : 'Probar con datos de ejemplo'}
      </button>
      {result && <p className="text-xs mt-2 text-[var(--color-muted)]">{result}</p>}
    </div>
  )
}

function TrySegmentUser() {
  const [result, setResult] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  async function run() {
    setLoading(true)
    setResult(null)
    try {
      const { data } = await mlApi.segmentUser({
        recency_days: 2, frequency_sessions: 18, educational_value_xp: 4200,
      })
      setResult(`Cluster ${data.cluster}: ${data.segment_label}`)
    } catch {
      setResult('Error al consultar el modelo (requiere rol admin)')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="p-4 rounded-2xl bg-gray-50 dark:bg-dark-muted">
      <p className="text-sm font-semibold mb-2">U07 · Segmentar usuario (RFM)</p>
      <button onClick={run} disabled={loading} className="btn-primary text-xs px-3 py-1.5">
        {loading ? 'Consultando…' : 'Probar con datos de ejemplo'}
      </button>
      {result && <p className="text-xs mt-2 text-[var(--color-muted)]">{result}</p>}
    </div>
  )
}

export default function AdminMLDashboard() {
  const [connected, setConnected] = useState(false)
  const [pulseKey, setPulseKey] = useState(0)
  const [predictions, setPredictions] = useState<NewPredictionEvent[]>([])
  const [alerts, setAlerts] = useState<AnomalyAlertEvent[]>([])
  const [loadUpdate, setLoadUpdate] = useState<PlatformLoadForecastResponse | null>(null)
  const [progress, setProgress] = useState<UserProgressUpdateEvent | null>(null)
  const [eventLog, setEventLog] = useState<RawEvent[]>([])
  const [eventCounts, setEventCounts] = useState<Record<string, number>>({})
  const nextId = useRef(1)

  useEffect(() => {
    const socket = connectSocket()

    function logEvent(event: string, payload: unknown) {
      setPulseKey((k) => k + 1)
      setEventCounts((prev) => ({ ...prev, [event]: (prev[event] ?? 0) + 1 }))
      setEventLog((prev) => [
        { id: nextId.current++, event, at: new Date().toLocaleTimeString('es'), payload },
        ...prev,
      ].slice(0, MAX_LOG_ITEMS))

      const meta = EVENT_META[event]
      if (meta && event !== 'connect' && event !== 'disconnect') {
        toast(meta.label, { duration: 2500 })
      }
    }

    const onConnect = () => { setConnected(true); logEvent('connect', null) }
    const onDisconnect = () => { setConnected(false); logEvent('disconnect', null) }
    const onPrediction = (payload: NewPredictionEvent) => {
      setPredictions((prev) => [payload, ...prev].slice(0, MAX_FEED_ITEMS))
      logEvent('new_prediction', payload)
    }
    const onAnomaly = (payload: AnomalyAlertEvent) => {
      setAlerts((prev) => [payload, ...prev].slice(0, MAX_FEED_ITEMS))
      logEvent('anomaly_alert', payload)
    }
    const onLoadUpdate = (payload: PlatformLoadForecastResponse) => {
      setLoadUpdate(payload)
      logEvent('platform_load_update', payload)
    }
    const onProgress = (payload: UserProgressUpdateEvent) => {
      setProgress(payload)
      logEvent('user_progress_update', payload)
    }

    socket.on('connect', onConnect)
    socket.on('disconnect', onDisconnect)
    socket.on('new_prediction', onPrediction)
    socket.on('anomaly_alert', onAnomaly)
    socket.on('platform_load_update', onLoadUpdate)
    socket.on('user_progress_update', onProgress)
    setConnected(getSocket().connected)

    return () => {
      socket.off('connect', onConnect)
      socket.off('disconnect', onDisconnect)
      socket.off('new_prediction', onPrediction)
      socket.off('anomaly_alert', onAnomaly)
      socket.off('platform_load_update', onLoadUpdate)
      socket.off('user_progress_update', onProgress)
      disconnectSocket()
    }
  }, [])

  return (
    <div className="space-y-8 animate-fade-in">
      <div className="flex items-start justify-between flex-wrap gap-3">
        <div>
          <h1 className="font-display text-3xl font-bold flex items-center gap-2">
            <Zap size={28} className="text-alebrije-coral" /> IA / Machine Learning
          </h1>
          <p className="text-[var(--color-muted)] mt-1">
            Predicciones, anomalías y progreso en tiempo real vía Socket.IO
          </p>
        </div>
        <StatusPill connected={connected} pulseKey={pulseKey} />
      </div>

      <EventLogPanel items={eventLog} counts={eventCounts} />

      <ForceUpdatesPanel />

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PlatformLoadChart live={loadUpdate} />
        <UserProgressPanel progress={progress} />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PredictionsFeed items={predictions} />
        <AnomalyAlerts items={alerts} />
      </div>

      <ModelsPanel />

      <div className="card p-6">
        <h2 className="font-display font-bold text-xl mb-4">Probar endpoints reales</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <TryPredictTime />
          <TrySegmentUser />
        </div>
      </div>
    </div>
  )
}
