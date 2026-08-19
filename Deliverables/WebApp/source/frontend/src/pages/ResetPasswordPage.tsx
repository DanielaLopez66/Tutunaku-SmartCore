// TUTUNAKU — ResetPasswordPage (usar token del URL)
import { useState } from 'react'
import { Link, useSearchParams, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, Lock, ArrowLeft, CheckCircle2, ShieldAlert } from 'lucide-react'
import { authApi } from '@/utils/api'
import toast from 'react-hot-toast'

export default function ResetPasswordPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const token = searchParams.get('token')

  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPass, setShowPass] = useState(false)
  const [showConfirm, setShowConfirm] = useState(false)
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  if (!token) {
    return (
      <div className="animate-fade-in text-center">
        <div className="w-20 h-20 rounded-full bg-alebrije-coral/10 flex items-center justify-center mx-auto mb-6">
          <ShieldAlert size={40} className="text-alebrije-coral" />
        </div>
        <h1 className="font-display text-2xl font-bold mb-3">Enlace inválido</h1>
        <p className="text-[var(--color-muted)] mb-6">
          Este enlace de recuperación no es válido o ha expirado.
        </p>
        <Link to="/forgot-password" className="btn-primary inline-flex items-center gap-2">
          Solicitar nuevo enlace
        </Link>
      </div>
    )
  }

  const validate = () => {
    const e: Record<string, string> = {}
    if (!password) e.password = 'La contraseña es obligatoria'
    else if (password.length < 8) e.password = 'Mínimo 8 caracteres'
    else if (!/[A-Z]/.test(password)) e.password = 'Debe tener al menos una mayúscula'
    else if (!/[a-z]/.test(password)) e.password = 'Debe tener al menos una minúscula'
    else if (!/\d/.test(password)) e.password = 'Debe tener al menos un número'
    if (password !== confirmPassword) e.confirm = 'Las contraseñas no coinciden'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await authApi.resetPassword({ token, new_password: password })
      setSuccess(true)
      toast.success('¡Contraseña restablecida!')
      setTimeout(() => navigate('/login'), 3000)
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || err?.response?.data?.detail || 'Token inválido o expirado'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  if (success) {
    return (
      <div className="animate-fade-in text-center">
        <div className="w-20 h-20 rounded-full bg-alebrije-teal/10 flex items-center justify-center mx-auto mb-6">
          <CheckCircle2 size={40} className="text-alebrije-teal" />
        </div>
        <h1 className="font-display text-3xl font-bold mb-3">¡Listo!</h1>
        <p className="text-[var(--color-muted)] mb-4">
          Tu contraseña ha sido restablecida exitosamente.
        </p>
        <p className="text-sm text-[var(--color-muted)]">
          Serás redirigido al login en unos segundos...
        </p>
      </div>
    )
  }

  // Strength indicator
  const getStrength = () => {
    let score = 0
    if (password.length >= 8) score++
    if (/[A-Z]/.test(password)) score++
    if (/[a-z]/.test(password)) score++
    if (/\d/.test(password)) score++
    if (/[^A-Za-z0-9]/.test(password)) score++
    return score
  }
  const strength = getStrength()
  const strengthLabel = ['', 'Muy débil', 'Débil', 'Regular', 'Fuerte', 'Muy fuerte'][strength] || ''
  const strengthColor = ['', 'bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-alebrije-teal', 'bg-green-500'][strength] || ''

  return (
    <div className="animate-fade-in">
      <div className="mb-8 text-center">
        <div className="w-16 h-16 rounded-full bg-alebrije-violet/10 flex items-center justify-center mx-auto mb-4">
          <Lock size={32} className="text-alebrije-violet" />
        </div>
        <h1 className="font-display text-3xl font-bold">Nueva contraseña</h1>
        <p className="text-[var(--color-muted)] mt-2">Crea una contraseña segura para tu cuenta</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Nueva contraseña */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Nueva contraseña</label>
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              className={`input pr-12 ${errors.password ? 'border-alebrije-coral' : ''}`}
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
            <button
              type="button"
              onClick={() => setShowPass(!showPass)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]
                         hover:text-[var(--color-text)] transition-colors"
            >
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          {errors.password && <p className="text-xs text-alebrije-coral mt-1">{errors.password}</p>}

          {/* Strength bar */}
          {password && (
            <div className="mt-2">
              <div className="flex gap-1 mb-1">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className={`h-1.5 flex-1 rounded-full transition-all duration-300 ${
                      i <= strength ? strengthColor : 'bg-gray-200 dark:bg-gray-700'
                    }`}
                  />
                ))}
              </div>
              <p className="text-xs text-[var(--color-muted)]">{strengthLabel}</p>
            </div>
          )}
        </div>

        {/* Confirmar */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Confirmar contraseña</label>
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
          className="btn-primary w-full text-base py-3.5"
        >
          {loading ? (
            <span className="flex items-center gap-2 justify-center">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Guardando...
            </span>
          ) : (
            <span className="flex items-center gap-2 justify-center">
              <Lock size={18} />
              Restablecer contraseña
            </span>
          )}
        </button>
      </form>

      <p className="text-center mt-6 text-sm text-[var(--color-muted)]">
        <Link to="/login" className="text-alebrije-coral font-bold hover:underline inline-flex items-center gap-1">
          <ArrowLeft size={14} />
          Volver al inicio de sesión
        </Link>
      </p>
    </div>
  )
}
