// TUTUNAKU — ForgotPasswordPage con CAPTCHA visual
// Envía un enlace de recuperación por email al resolver el CAPTCHA correctamente
import { useState, useEffect, useCallback } from 'react'
import { Link } from 'react-router-dom'
import { Mail, RefreshCw, ShieldCheck, ArrowLeft, Loader2, MailCheck, Lock } from 'lucide-react'
import { authApi } from '@/utils/api'
import toast from 'react-hot-toast'

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('')
  const [captchaId, setCaptchaId] = useState('')
  const [captchaImage, setCaptchaImage] = useState('')
  const [captchaAnswer, setCaptchaAnswer] = useState('')
  const [loading, setLoading] = useState(false)
  const [loadingCaptcha, setLoadingCaptcha] = useState(false)
  const [sent, setSent] = useState(false)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const fetchCaptcha = useCallback(async () => {
    setLoadingCaptcha(true)
    setCaptchaAnswer('')
    try {
      const { data } = await authApi.getCaptcha()
      setCaptchaId(data.captcha_id)
      setCaptchaImage(data.image)
    } catch {
      toast.error('Error al generar el CAPTCHA')
    } finally {
      setLoadingCaptcha(false)
    }
  }, [])

  useEffect(() => {
    fetchCaptcha()
  }, [fetchCaptcha])

  const validate = () => {
    const e: Record<string, string> = {}
    if (!email) e.email = 'El email es obligatorio'
    else if (!/\S+@\S+\.\S+/.test(email)) e.email = 'Email inválido'
    if (!captchaAnswer) e.captcha = 'Escribe el texto del CAPTCHA'
    setErrors(e)
    return Object.keys(e).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return
    setLoading(true)
    try {
      await authApi.forgotPassword({
        email,
        captcha_id: captchaId,
        captcha_answer: captchaAnswer,
      })
      setSent(true)
    } catch (err: any) {
      const msg = err?.response?.data?.error?.message || err?.response?.data?.detail || 'Error al procesar la solicitud'
      toast.error(msg)
      // Regenerar CAPTCHA en caso de error
      fetchCaptcha()
    } finally {
      setLoading(false)
    }
  }

  // ── Vista de éxito: pedir que revise su correo ──
  if (sent) {
    return (
      <div className="animate-fade-in text-center">
        <div className="w-20 h-20 rounded-full bg-alebrije-teal/10 flex items-center justify-center mx-auto mb-6
                        animate-[pulse_2s_ease-in-out_1]">
          <MailCheck size={40} className="text-alebrije-teal" />
        </div>
        <h1 className="font-display text-3xl font-bold mb-3">Revisa tu correo</h1>
        <p className="text-[var(--color-muted)] mb-2">
          Si existe una cuenta con el email <strong className="text-[var(--color-text)]">{email}</strong>,
          te enviamos un enlace para crear una nueva contraseña.
        </p>
        <p className="text-sm text-[var(--color-muted)] mb-6">
          El enlace expira en 30 minutos. Revisa también tu carpeta de spam si no lo ves.
        </p>

        <Link
          to="/login"
          className="btn-primary w-full text-base py-3.5 flex items-center gap-2 justify-center"
        >
          <ArrowLeft size={18} />
          Ir a iniciar sesión
        </Link>
      </div>
    )
  }

  // ── Formulario principal ──
  return (
    <div className="animate-fade-in">
      <div className="mb-8 text-center">
        <div className="w-16 h-16 rounded-full bg-alebrije-coral/10 flex items-center justify-center mx-auto mb-4">
          <ShieldCheck size={32} className="text-alebrije-coral" />
        </div>
        <h1 className="font-display text-3xl font-bold">Recuperar contraseña</h1>
        <p className="text-[var(--color-muted)] mt-2">
          Ingresa tu email y resuelve el CAPTCHA para recibir un enlace de recuperación
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Email */}
        <div>
          <label className="block text-sm font-bold mb-1.5">Email</label>
          <div className="relative">
            <Mail size={18} className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" />
            <input
              type="email"
              className={`input pl-11 ${errors.email ? 'border-alebrije-coral' : ''}`}
              placeholder="tu@email.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          {errors.email && <p className="text-xs text-alebrije-coral mt-1">{errors.email}</p>}
        </div>

        {/* CAPTCHA */}
        <div>
          <label className="block text-sm font-bold mb-2 flex items-center gap-1.5">
            <Lock size={14} /> Verificación CAPTCHA
          </label>
          <div className="rounded-2xl border-2 border-[var(--color-border)] overflow-hidden bg-gray-50 dark:bg-[#1A1A2E]">
            {/* Imagen CAPTCHA */}
            <div className="relative flex items-center justify-center p-4 min-h-[100px]">
              {loadingCaptcha ? (
                <div className="flex items-center gap-2 text-[var(--color-muted)]">
                  <Loader2 size={20} className="animate-spin" />
                  <span className="text-sm">Generando CAPTCHA...</span>
                </div>
              ) : captchaImage ? (
                <img
                  src={captchaImage}
                  alt="CAPTCHA"
                  className="rounded-xl shadow-lg max-h-[90px] select-none pointer-events-none"
                  draggable={false}
                  style={{ imageRendering: 'crisp-edges' }}
                />
              ) : null}
              {/* Botón refrescar */}
              <button
                type="button"
                onClick={fetchCaptcha}
                disabled={loadingCaptcha}
                className="absolute top-3 right-3 p-2 rounded-xl
                           bg-white/80 dark:bg-[#0F0F1A]/80 backdrop-blur-sm
                           hover:bg-alebrije-coral/10 transition-all duration-200
                           text-[var(--color-muted)] hover:text-alebrije-coral
                           disabled:opacity-50"
                title="Generar nuevo CAPTCHA"
              >
                <RefreshCw size={16} className={loadingCaptcha ? 'animate-spin' : ''} />
              </button>
            </div>

            {/* Input CAPTCHA */}
            <div className="px-4 pb-4">
              <input
                type="text"
                className={`input text-center text-lg tracking-[0.3em] font-bold uppercase ${
                  errors.captcha ? 'border-alebrije-coral' : ''
                }`}
                placeholder="Escribe el texto de la imagen"
                value={captchaAnswer}
                onChange={(e) => setCaptchaAnswer(e.target.value.toUpperCase())}
                maxLength={8}
                autoComplete="off"
                spellCheck={false}
              />
              {errors.captcha && (
                <p className="text-xs text-alebrije-coral mt-1 text-center">{errors.captcha}</p>
              )}
            </div>
          </div>
          <p className="text-xs text-[var(--color-muted)] mt-2 text-center">
            Escribe los caracteres que ves en la imagen. Haz clic en el botón de recarga para obtener uno nuevo.
          </p>
        </div>

        <button
          type="submit"
          disabled={loading || loadingCaptcha}
          className="btn-primary w-full text-base py-3.5"
        >
          {loading ? (
            <span className="flex items-center gap-2 justify-center">
              <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              Verificando...
            </span>
          ) : (
            <span className="flex items-center gap-2 justify-center">
              <ShieldCheck size={18} />
              Enviar enlace de recuperación
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
