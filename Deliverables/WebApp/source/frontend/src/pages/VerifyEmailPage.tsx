import { useEffect, useState } from 'react'
import { useSearchParams, Link } from 'react-router-dom'
import { authApi } from '@/utils/api'
import MascotHeart from '@/components/ui/MascotHeart'
import toast from 'react-hot-toast'

export default function VerifyEmailPage() {
  const [searchParams] = useSearchParams()
  const token = searchParams.get('token')
  
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading')
  const [message, setMessage] = useState('Verificando tu cuenta...')

  useEffect(() => {
    if (!token) {
      setStatus('error')
      setMessage('El enlace de verificación es inválido o no contiene un token.')
      return
    }

    const verify = async () => {
      try {
        await authApi.verifyEmail(token)
        setStatus('success')
        setMessage('¡Tu cuenta ha sido verificada con éxito!')
        toast.success('Cuenta verificada')
      } catch (err: any) {
        setStatus('error')
        setMessage(err.response?.data?.error?.message || 'Error al verificar la cuenta. El enlace puede haber expirado.')
      }
    }

    verify()
  }, [token])

  return (
    <div className="w-full max-w-md mx-auto text-center space-y-6 fade-in pt-10">
      <div className="flex justify-center mb-6">
        <MascotHeart size={100} animated={status === 'loading'} />
      </div>

      <h1 className="text-3xl font-display font-bold gradient-text">
        Verificación de Correo
      </h1>

      <div className="card p-6 shadow-xl bg-white dark:bg-dark-surface space-y-4">
        {status === 'loading' && (
          <div className="space-y-4">
            <div className="w-8 h-8 border-4 border-alebrije-teal border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-gray-600 dark:text-gray-300 font-medium">{message}</p>
          </div>
        )}

        {status === 'success' && (
          <div className="space-y-6">
            <div className="w-16 h-16 bg-green-100 text-green-500 rounded-full flex items-center justify-center mx-auto mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-gray-600 dark:text-gray-300 font-medium">{message}</p>
            <Link to="/login" className="btn-primary w-full inline-block text-center mt-4">
              Ir a Iniciar Sesión
            </Link>
          </div>
        )}

        {status === 'error' && (
          <div className="space-y-6">
            <div className="w-16 h-16 bg-red-100 text-red-500 rounded-full flex items-center justify-center mx-auto mb-2">
              <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
            <p className="text-red-500 font-medium">{message}</p>
            <Link to="/login" className="btn-secondary w-full inline-block text-center mt-4">
              Volver al inicio
            </Link>
          </div>
        )}
      </div>
    </div>
  )
}
