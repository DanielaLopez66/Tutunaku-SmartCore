// TUTUNAKU — Breadcrumbs Component
import { Link, useLocation } from 'react-router-dom'
import { ChevronRight, Home } from 'lucide-react'
import { motion } from 'framer-motion'

const BREADCRUMB_NAMES: Record<string, string> = {
  learn: 'Aprender',
  lesson: 'Lección',
  exercise: 'Ejercicio',
  profile: 'Perfil',
  achievements: 'Logros',
  leaderboard: 'Clasificación',
  settings: 'Configuración',
  admin: 'Administración',
  users: 'Usuarios',
  courses: 'Cursos',
  units: 'Unidades',
  lessons: 'Lecciones',
}

export default function Breadcrumbs() {
  const location = useLocation()
  const pathnames = location.pathname.split('/').filter((x) => x)

  if (pathnames.length === 0) return null

  return (
    <motion.nav 
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex items-center space-x-2 text-sm text-[var(--color-muted)] mb-6 overflow-x-auto no-scrollbar py-1"
      aria-label="Breadcrumb"
    >
      <Link
        to="/"
        className="flex items-center hover:text-white transition-colors duration-200"
      >
        <Home size={14} className="mr-1" />
        <span className="hidden sm:inline">Inicio</span>
      </Link>

      {pathnames.map((value, index) => {
        const last = index === pathnames.length - 1
        const to = `/${pathnames.slice(0, index + 1).join('/')}`
        const name = BREADCRUMB_NAMES[value] || value

        // Skip IDs in breadcrumbs if possible, or handle them
        const isId = /^[0-9a-fA-F]{24}$/.test(value) || /^\d+$/.test(value)
        if (isId && last) return null

        return (
          <div key={to} className="flex items-center space-x-2">
            <ChevronRight size={14} className="shrink-0 text-gray-600" />
            {last ? (
              <span className="font-semibold text-[var(--color-primary)] truncate max-w-[150px]">
                {name}
              </span>
            ) : (
              <Link
                to={to}
                className="hover:text-white transition-colors duration-200 truncate max-w-[150px]"
              >
                {name}
              </Link>
            )}
          </div>
        )
      })}
    </motion.nav>
  )
}
