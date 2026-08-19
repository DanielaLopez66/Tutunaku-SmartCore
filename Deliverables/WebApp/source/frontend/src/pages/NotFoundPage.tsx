// TUTUNAKU — NotFoundPage
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Home, ArrowLeft, Search } from 'lucide-react'
import MascotHeart from '@/components/ui/MascotHeart'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-[var(--color-bg)] alebrije-pattern">
      <div className="text-center max-w-lg">
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ duration: 0.5, type: 'spring' }}
        >
          <MascotHeart size={150} animated />
        </motion.div>
        
        <motion.div
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.2 }}
        >
          <h1 className="font-display text-8xl font-bold mt-6 gradient-text select-none">404</h1>
          <p className="font-display text-3xl font-bold mt-2">¡Página no encontrada!</p>
          <p className="text-[var(--color-muted)] mt-4 text-lg leading-relaxed">
            Parece que te has perdido en la selva de El Tajín. 
            Esta página no existe o fue movida.
          </p>
        </motion.div>

        <motion.div 
          className="flex flex-col sm:flex-row items-center justify-center gap-4 mt-10"
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{ delay: 0.4 }}
        >
          <Link to="/" className="btn-primary w-full sm:w-auto flex items-center justify-center gap-2">
            <Home size={18} />
            Volver al inicio
          </Link>
          <button 
            onClick={() => window.history.back()}
            className="btn-secondary w-full sm:w-auto flex items-center justify-center gap-2"
          >
            <ArrowLeft size={18} />
            Regresar
          </button>
        </motion.div>

        <motion.div
          className="mt-12 p-4 bg-white/5 rounded-2xl border border-white/10"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
        >
          <p className="text-sm text-[var(--color-muted)] flex items-center justify-center gap-2">
            <Search size={14} />
            ¿Buscabas algo específico? Revisa el <Link to="/sitemap" className="text-[var(--color-primary)] hover:underline">mapa del sitio</Link>.
          </p>
        </motion.div>
      </div>
    </div>
  )
}
