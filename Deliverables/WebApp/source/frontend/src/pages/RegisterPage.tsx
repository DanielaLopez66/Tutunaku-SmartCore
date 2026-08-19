// TUTUNAKU — RegisterPage
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, UserPlus } from 'lucide-react'
import { authApi } from '@/utils/api'
import toast from 'react-hot-toast'

export default function RegisterPage() {
  const navigate = useNavigate()
  const [form, setForm] = useState({ email: '', username: '', password: '', full_name: '' })
  const [showPass, setShowPass] = useState(false)
  const [loading, setLoading] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const validate = () => {
    const e: Record<string, string> = {}
    if (!form.email) e.email = 'Email obligatorio'
    else if (!/\S+@\S+\.\S+/.test(form.email)) e.email = 'Email inválido'
    if (!form.username) e.username = 'Nombre de usuario obligatorio'
    else if (form.username.length < 3) e.username = 'Mínimo 3 caracteres'
    else if (!/^[a-zA-Z0-9_]+$/.test(form.username)) e.username = 'Solo letras, números y _'
    if (!form.password) e.password = 'Contraseña obligatoria'
    else if (form.password.length < 8) e.password = 'Mínimo 8 caracteres'
    else if (!/[A-Z]/.test(form.password)) e.password = 'Debe contener mayúscula'
    else if (!/\d/.test(form.password)) e.password = 'Debe contener número'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const set = (k: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [k]: e.target.value }))

  const handleSubmit = async (ev: React.FormEvent) => {
    ev.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await authApi.register(form)
      toast.success('¡Registro exitoso! Revisa tu email para verificar tu cuenta')
      navigate('/login')
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || 'Error al registrarse'
      toast.error(msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="animate-fade-in">
      <div className="mb-8 text-center">
        <h1 className="font-display text-3xl font-bold">Crea tu cuenta</h1>
        <p className="text-[var(--color-muted)] mt-1">¡Empieza tu aventura totonaca hoy!</p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Nombre completo */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Nombre completo (opcional)</label>
          <input
            type="text"
            className="input"
            placeholder="Tu nombre"
            value={form.full_name}
            onChange={set('full_name')}
          />
        </div>

        {/* Email */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Email</label>
          <input
            type="email"
            className={`input ${errors.email ? 'border-alebrije-coral' : ''}`}
            placeholder="tu@email.com"
            value={form.email}
            onChange={set('email')}
          />
          {errors.email && <p className="text-xs text-alebrije-coral mt-1">{errors.email}</p>}
        </div>

        {/* Nombre de usuario */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Nombre de usuario</label>
          <input
            type="text"
            className={`input ${errors.username ? 'border-alebrije-coral' : ''}`}
            placeholder="totonaco_aprendiz"
            value={form.username}
            onChange={set('username')}
          />
          {errors.username && <p className="text-xs text-alebrije-coral mt-1">{errors.username}</p>}
        </div>

        <div>
          <label className="block text-sm font-bold mb-1.5">Contraseña</label>
          <div className="relative">
            <input
              type={showPass ? 'text' : 'password'}
              className={`input pr-12 ${errors.password ? 'border-alebrije-coral' : ''}`}
              placeholder="Mín. 8 chars, mayúscula y número"
              value={form.password}
              onChange={set('password')}
            />
            <button type="button" onClick={() => setShowPass(!showPass)}
              className="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]">
              {showPass ? <EyeOff size={18} /> : <Eye size={18} />}
            </button>
          </div>
          {errors.password && <p className="text-xs text-alebrije-coral mt-1">{errors.password}</p>}
        </div>

        {/* Indicador fortaleza */}
        {form.password && (
          <div className="space-y-1">
            <div className="xp-bar">
              <div className="xp-bar-fill" style={{ width: `${Math.min(100, form.password.length * 10)}%` }} />
            </div>
            <p className="text-xs text-[var(--color-muted)] flex items-center gap-1.5">
              <span className={`w-2 h-2 rounded-full ${
                form.password.length < 6 ? 'bg-red-500' : form.password.length < 10 ? 'bg-yellow-500' : 'bg-green-500'
              }`} />
              {form.password.length < 6 ? 'Débil' : form.password.length < 10 ? 'Media' : 'Fuerte'}
            </p>
          </div>
        )}

        <button type="submit" disabled={loading} className="btn-primary w-full text-base py-3.5 mt-2">
          {loading ? (
            <span className="flex items-center gap-2 justify-center">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Creando cuenta...
            </span>
          ) : (
            <span className="flex items-center gap-2 justify-center">
              <UserPlus size={18} />
              Crear cuenta gratis
            </span>
          )}
        </button>
      </form>

      <p className="text-center mt-6 text-sm text-[var(--color-muted)]">
        ¿Ya tienes cuenta?{' '}
        <Link to="/login" className="text-alebrije-coral font-bold hover:underline">
          Inicia sesión
        </Link>
      </p>
    </div>
  )
}
