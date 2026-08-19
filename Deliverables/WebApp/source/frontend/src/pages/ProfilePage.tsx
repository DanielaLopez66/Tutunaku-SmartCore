// TUTUNAKU — ProfilePage con botón de cambiar contraseña
import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { userApi, authApi } from '@/utils/api'
import type { UserStats } from '@/types'
import { Eye, EyeOff, Lock, X, KeyRound, CheckCircle2, Shield, Sprout, Zap, Star, Flame, Trophy, BookOpen, Target } from 'lucide-react'
import toast from 'react-hot-toast'

// ── Modal de cambio de contraseña ──────────────
function ChangePasswordModal({ onClose }: { onClose: () => void }) {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showCurrent, setShowCurrent] = useState(false)
  const [showNew, setShowNew] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (!currentPassword) e.current = 'Ingresa tu contraseña actual'
    if (!newPassword) e.newPass = 'Ingresa la nueva contraseña'
    else if (newPassword.length < 8) e.newPass = 'Mínimo 8 caracteres'
    else if (!/[A-Z]/.test(newPassword)) e.newPass = 'Debe tener al menos una mayúscula'
    else if (!/[a-z]/.test(newPassword)) e.newPass = 'Debe tener al menos una minúscula'
    else if (!/\d/.test(newPassword)) e.newPass = 'Debe tener al menos un número'
    if (newPassword !== confirmPassword) e.confirm = 'Las contraseñas no coinciden'
    if (currentPassword === newPassword && newPassword) e.newPass = 'La nueva contraseña debe ser diferente'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await authApi.changePassword({
        current_password: currentPassword,
        new_password: newPassword,
      })
      setSuccess(true)
      toast.success('¡Contraseña actualizada!')
      setTimeout(onClose, 2000)
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message ||
        err?.response?.data?.detail ||
        'Error al cambiar la contraseña'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  // Strength indicator
  const getStrength = () => {
    let score = 0
    if (newPassword.length >= 8) score++
    if (/[A-Z]/.test(newPassword)) score++
    if (/[a-z]/.test(newPassword)) score++
    if (/\d/.test(newPassword)) score++
    if (/[^A-Za-z0-9]/.test(newPassword)) score++
    return score
  }
  const strength = getStrength()
  const strengthColor = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-alebrije-teal', 'bg-green-500'][strength] || ''

  if (success) {
    return (
      <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
        <div className="card p-8 max-w-md w-full mx-4 text-center">
          <div className="w-16 h-16 rounded-full bg-alebrije-teal/10 flex items-center justify-center mx-auto mb-4">
            <CheckCircle2 size={32} className="text-alebrije-teal" />
          </div>
          <h2 className="font-display text-2xl font-bold mb-2">¡Listo!</h2>
          <p className="text-[var(--color-muted)]">Tu contraseña ha sido actualizada</p>
        </div>
      </div>
    )
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm animate-fade-in">
      <div className="card p-8 max-w-md w-full mx-4 relative">
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 rounded-xl
                     hover:bg-gray-100 dark:hover:bg-dark-muted transition-colors
                     text-[var(--color-muted)] hover:text-[var(--color-text)]"
        >
          <X size={20} />
        </button>

        <div className="text-center mb-6">
          <div className="w-14 h-14 rounded-full bg-alebrije-violet/10 flex items-center justify-center mx-auto mb-3">
            <KeyRound size={28} className="text-alebrije-violet" />
          </div>
          <h2 className="font-display text-2xl font-bold">Cambiar contraseña</h2>
          <p className="text-sm text-[var(--color-muted)] mt-1">Ingresa tu contraseña actual y la nueva</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Contraseña actual */}
          <div>
            <label className="block text-sm font-bold mb-1.5">Contraseña actual</label>
            <div className="relative">
              <input
                type={showCurrent ? 'text' : 'password'}
                className={`input pr-12 ${errors.current ? 'border-alebrije-coral' : ''}`}
                placeholder="••••••••"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowCurrent(!showCurrent)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]
                           hover:text-[var(--color-text)] transition-colors"
              >
                {showCurrent ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.current && <p className="text-xs text-alebrije-coral mt-1">{errors.current}</p>}
          </div>

          {/* Nueva contraseña */}
          <div>
            <label className="block text-sm font-bold mb-1.5">Nueva contraseña</label>
            <div className="relative">
              <input
                type={showNew ? 'text' : 'password'}
                className={`input pr-12 ${errors.newPass ? 'border-alebrije-coral' : ''}`}
                placeholder="••••••••"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowNew(!showNew)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]
                           hover:text-[var(--color-text)] transition-colors"
              >
                {showNew ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.newPass && <p className="text-xs text-alebrije-coral mt-1">{errors.newPass}</p>}

            {/* Strength bar */}
            {newPassword && (
              <div className="mt-2 flex gap-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                      i <= strength ? strengthColor : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Confirmar */}
          <div>
            <label className="block text-sm font-bold mb-1.5">Confirmar nueva contraseña</label>
            <div className="relative">
              <input
                type={showConfirm ? 'text' : 'password'}
                className={`input pr-12 ${errors.confirm ? 'border-alebrije-coral' : ''}`}
                placeholder="••••••••"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
              <button
                type="button"
                onClick={() => setShowConfirm(!showConfirm)}
                className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]
                           hover:text-[var(--color-text)] transition-colors"
              >
                {showConfirm ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {errors.confirm && <p className="text-xs text-alebrije-coral mt-1">{errors.confirm}</p>}
          </div>

          <button
            type="submit"
            disabled={loading}
            className="btn-primary w-full text-base py-3"
          >
            {loading ? (
              <span className="flex items-center gap-2 justify-center">
                <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Actualizando...
              </span>
            ) : (
              <span className="flex items-center gap-2 justify-center">
                <Lock size={18} />
                Cambiar contraseña
              </span>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}

// ── Página de perfil principal ────────────────
export default function ProfilePage() {
  const user = useAuthStore((s) => s.user)
  const [showChangePassword, setShowChangePassword] = useState(false)

  const { data: stats } = useQuery<UserStats>({
    queryKey: ['user-stats'],
    queryFn: () => userApi.getStats().then((r) => r.data),
  })

  return (
    <div className="max-w-2xl mx-auto space-y-6 animate-fade-in">
      <div className="card p-8 text-center">
        <div className="w-24 h-24 rounded-full bg-alebrije-gradient flex items-center
                        justify-center text-4xl font-bold text-white mx-auto mb-4">
          {user?.username?.[0]?.toUpperCase()}
        </div>
        <h1 className="font-display text-3xl font-bold">{user?.username}</h1>
        <p className="text-[var(--color-muted)]">{user?.email}</p>
        <div className="flex justify-center gap-3 mt-4">
          <span className="badge bg-alebrije-violet/10 text-alebrije-violet">
            Nivel {user?.level}
          </span>
          <span className="badge bg-alebrije-coral/10 text-alebrije-coral flex items-center gap-1">
            {user?.role === 'admin' ? <><Shield size={12} /> Admin</> : <><Sprout size={12} /> Aprendiz</>}
          </span>
        </div>

        {/* Botón cambiar contraseña */}
        <button
          onClick={() => setShowChangePassword(true)}
          className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-2xl
                     font-bold text-sm
                     bg-alebrije-violet/10 hover:bg-alebrije-violet/20
                     text-alebrije-violet border border-alebrije-violet/30
                     active:scale-95 transition-all duration-150"
        >
          <KeyRound size={16} />
          Cambiar contraseña
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {[
            { label: 'XP Total', value: stats.xp_total, Icon: Zap, color: 'text-alebrije-gold' },
            { label: 'Nivel', value: stats.level, Icon: Star, color: 'text-yellow-500' },
            { label: 'Racha actual', value: `${stats.current_streak} días`, Icon: Flame, color: 'text-orange-500' },
            { label: 'Racha máxima', value: `${stats.longest_streak} días`, Icon: Trophy, color: 'text-alebrije-violet' },
            { label: 'Lecciones', value: stats.lessons_completed, Icon: BookOpen, color: 'text-alebrije-teal' },
            { label: 'Precisión', value: `${stats.accuracy_percentage}%`, Icon: Target, color: 'text-alebrije-coral' },
          ].map(({ label, value, Icon, color }) => (
            <div key={label} className="card p-4 text-center">
              <Icon className={`mx-auto mb-1 ${color}`} size={28} />
              <div className="font-display text-xl font-bold">{value}</div>
              <div className="text-xs text-[var(--color-muted)] mt-0.5">{label}</div>
            </div>
          ))}
        </div>
      )}

      {/* Modal de cambio de contraseña */}
      {showChangePassword && (
        <ChangePasswordModal onClose={() => setShowChangePassword(false)} />
      )}
    </div>
  )
}
