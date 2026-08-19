// ============================================================
// TUTUNAKU — SessionManager
// Componente que maneja la cookie de sesión de 5 minutos.
// - Verifica cada 10 segundos si la cookie ha expirado
// - Renueva la cookie con cada interacción del usuario
// - Muestra alerta 1 minuto antes de expirar
// - Auto-logout cuando la cookie expira
// ============================================================
import { useEffect, useRef, useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/store/authStore'
import { Clock, LogOut, RefreshCw, CheckCircle } from 'lucide-react'
import toast from 'react-hot-toast'

const SESSION_MINUTES = 5
const CHECK_INTERVAL_MS = 10_000        // Verificar cada 10 seg
const WARNING_BEFORE_MS = 60_000        // Avisar 1 minuto antes

export default function SessionManager() {
  const navigate = useNavigate()
  const { isAuthenticated, logout, checkSession, refreshSession, sessionExpiredAt } = useAuthStore()
  const [showWarning, setShowWarning] = useState(false)
  const [secondsLeft, setSecondsLeft] = useState(0)
  const warningShownRef = useRef(false)
  const loggedOutRef = useRef(false)

  // ── Renovar sesión con interacción del usuario ──
  const handleUserActivity = useCallback(() => {
    if (!isAuthenticated) return
    refreshSession()
    setShowWarning(false)
    warningShownRef.current = false
  }, [isAuthenticated, refreshSession])

  // ── Registrar eventos de actividad ──
  useEffect(() => {
    if (!isAuthenticated) return

    const events = ['mousedown', 'keydown', 'scroll', 'touchstart']
    events.forEach((event) => window.addEventListener(event, handleUserActivity, { passive: true }))

    return () => {
      events.forEach((event) => window.removeEventListener(event, handleUserActivity))
    }
  }, [isAuthenticated, handleUserActivity])

  // ── Verificar sesión periódicamente ──
  useEffect(() => {
    if (!isAuthenticated) {
      setShowWarning(false)
      return
    }

    loggedOutRef.current = false
    warningShownRef.current = false

    const interval = setInterval(() => {
      // Verificar cookie
      const valid = checkSession()

      if (!valid && !loggedOutRef.current) {
        loggedOutRef.current = true
        setShowWarning(false)
        toast.error('Tu sesión ha expirado. Por favor inicia sesión de nuevo.', {
          duration: 5000,
          icon: <Clock size={16} />,
        })
        navigate('/login', { replace: true })
        return
      }

      // Verificar si estamos cerca de expirar
      const expiredAt = useAuthStore.getState().sessionExpiredAt
      if (expiredAt) {
        const remaining = expiredAt - Date.now()
        setSecondsLeft(Math.max(0, Math.ceil(remaining / 1000)))

        if (remaining <= WARNING_BEFORE_MS && remaining > 0 && !warningShownRef.current) {
          setShowWarning(true)
          warningShownRef.current = true
        }

        if (remaining <= 0 && !loggedOutRef.current) {
          loggedOutRef.current = true
          logout()
          setShowWarning(false)
          toast.error('Tu sesión ha expirado. Por favor inicia sesión de nuevo.', {
            duration: 5000,
            icon: <Clock size={16} />,
          })
          navigate('/login', { replace: true })
        }
      }
    }, CHECK_INTERVAL_MS)

    return () => clearInterval(interval)
  }, [isAuthenticated, checkSession, logout, navigate])

  // ── Verificar al montar (por si la cookie expiró durante recarga) ──
  useEffect(() => {
    if (isAuthenticated) {
      const valid = checkSession()
      if (!valid) {
        toast.error('Tu sesión ha expirado. Por favor inicia sesión de nuevo.', {
          duration: 5000,
          icon: <Clock size={16} />,
        })
        navigate('/login', { replace: true })
      }
    }
  }, []) // eslint-disable-line react-hooks/exhaustive-deps

  if (!showWarning || !isAuthenticated) return null

  const minutes = Math.floor(secondsLeft / 60)
  const secs = secondsLeft % 60

  return (
    <div className="fixed bottom-6 right-6 z-50 animate-fade-in">
      <div className="card p-5 max-w-sm shadow-2xl border-2 border-alebrije-coral/50
                      bg-[var(--color-surface)] backdrop-blur-xl">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 rounded-full bg-alebrije-coral/10 flex items-center justify-center flex-shrink-0">
            <Clock size={20} className="text-alebrije-coral" />
          </div>
          <div className="flex-1">
            <p className="font-bold text-sm">Sesión por expirar</p>
            <p className="text-xs text-[var(--color-muted)] mt-0.5">
              Tu sesión se cerrará en{' '}
              <span className="font-bold text-alebrije-coral">
                {minutes}:{String(secs).padStart(2, '0')}
              </span>
            </p>
            <div className="flex gap-2 mt-3">
              <button
                onClick={() => {
                  handleUserActivity()
                  toast.success('Sesión renovada por 5 minutos más', { icon: <CheckCircle size={16} /> })
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold
                           bg-alebrije-teal/10 text-alebrije-teal hover:bg-alebrije-teal/20
                           transition-all active:scale-95"
              >
                <RefreshCw size={14} />
                Renovar
              </button>
              <button
                onClick={() => {
                  logout()
                  navigate('/login', { replace: true })
                }}
                className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-bold
                           bg-alebrije-coral/10 text-alebrije-coral hover:bg-alebrije-coral/20
                           transition-all active:scale-95"
              >
                <LogOut size={14} />
                Cerrar sesión
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
