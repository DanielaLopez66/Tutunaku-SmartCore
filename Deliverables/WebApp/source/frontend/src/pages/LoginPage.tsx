// TUTUNAKU — LoginPage
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, LogIn } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { authApi, userApi } from '@/utils/api'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { setTokens, setUser } = useAuthStore()
  const [form, setForm] = useState({ email: '', password: '' })
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (!form.email) e.email = 'El email es obligatorio'
    if (!form.password) e.password = 'La contraseña es obligatoria'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      const { data: tokens } = await authApi.login(form)
      setTokens(tokens)
      const { data: me } = await userApi.getMe()
      setUser(me)
      toast.success(`¡Bienvenido de vuelta, ${me.username}!`)
      if (me.role === 'admin') {
        navigate('/admin')
      } else {
        navigate('/learn')
      }
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al iniciar sesión'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      <div className="mb-8 text-center">
        <h1 className="font-display text-3xl font-bold">¡Bienvenido!</h1>
        <p className="text-[var(--color-muted)] mt-1">Inicia sesión para continuar aprendiendo</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Email</label>
          <input
            type="email"
            className={`input ${errors.email ? 'border-alebrije-coral' : ''}`}
            placeholder="tu@email.com"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
          {errors.email && <p className="text-xs text-alebrije-coral mt-1">{errors.email}</p>}
        </div>

        {/* Contraseña */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Contraseña</label>
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              className={`input pr-12 ${errors.password ? 'border-alebrije-coral' : ''}`}
              placeholder="••••••••"
              value={form.password}
              onChange={(e) => setForm({ ...form, password: e.target.value })}
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
        </div>

        <div className="flex justify-end">
          <Link to="/forgot-password" className="text-sm text-alebrije-coral font-semibold hover:underline">
            ¿Olvidaste tu contraseña?
          </Link>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="btn-primary w-full text-base py-3.5"
        >
          {loading ? (
            <span className="flex items-center gap-2 justify-center">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Entrando...
            </span>
          ) : (
            <span className="flex items-center gap-2 justify-center">
              <LogIn size={18} />
              Iniciar sesión
            </span>
          )}
        </button>
      </form>

      <p className="text-center mt-6 text-sm text-[var(--color-muted)]">
        ¿No tienes cuenta?{' '}
        <Link to="/register" className="text-alebrije-coral font-bold hover:underline">
          Regístrate gratis
        </Link>
      </p>
    </div>
  )
}
