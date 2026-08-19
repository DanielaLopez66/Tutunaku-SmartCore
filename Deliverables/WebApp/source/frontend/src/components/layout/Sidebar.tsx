// TUTUNAKU — Sidebar de navegación
import { NavLink } from 'react-router-dom'
import {
  Map, Trophy, Users, BarChart3,
  Settings, BookOpen, Heart, Brain, Plus
} from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import clsx from 'clsx'

const userNav = [
  { to: '/learn', icon: Map, label: 'Aprender' },
  { to: '/achievements', icon: Trophy, label: 'Logros' },
  { to: '/leaderboard', icon: Users, label: 'Ranking' },
  { to: '/profile', icon: Heart, label: 'Mi Perfil' },
  { to: '/settings', icon: Settings, label: 'Ajustes' },
]

const adminNav = [
  { to: '/admin', icon: BarChart3, label: 'Dashboard' },
  { to: '/admin/users', icon: Users, label: 'Usuarios' },
  { to: '/admin/courses', icon: BookOpen, label: 'Cursos' },
  { to: '/admin/units', icon: BookOpen, label: 'Unidades' },
  { to: '/admin/lessons', icon: Plus, label: 'Agregar Palabra' },
  { to: '/admin/ml', icon: Brain, label: 'IA / ML' },
]

export default function Sidebar() {
  const user = useAuthStore((s) => s.user)
  const isAdmin = user?.role === 'admin'
  const nav = isAdmin ? adminNav : userNav

  return (
    <div className="sticky top-20 p-4 space-y-1">
      {nav.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          end={to === '/admin'}
          className={({ isActive }) =>
            clsx(
              'flex items-center gap-3 px-4 py-3 rounded-2xl font-semibold text-sm',
              'transition-all duration-150',
              isActive
                ? 'bg-alebrije-coral text-white shadow-glow-coral'
                : 'hover:bg-gray-100 dark:hover:bg-dark-muted text-[var(--color-muted)]'
            )
          }
        >
          <Icon size={20} className="w-7" />
          {label}
        </NavLink>
      ))}
    </div>
  )
}
