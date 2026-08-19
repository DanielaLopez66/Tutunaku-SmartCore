// TUTUNAKU — Navbar
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Moon, Sun, Menu, X, LogOut, User, Settings, Shield } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useThemeStore } from '@/store/themeStore'
import { authApi } from '@/utils/api'
import MascotHeart from '@/components/ui/MascotHeart'
import HeartsDisplay from '@/components/ui/HeartsDisplay'
import XPBadge from '@/components/ui/XPBadge'
import StreakBadge from '@/components/ui/StreakBadge'
import NotificationBell from '@/components/ui/NotificationBell'

export default function Navbar() {
  const { user, isAuthenticated, tokens, logout } = useAuthStore()
  const { isDark, toggle } = useThemeStore()
  const navigate = useNavigate()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [userMenuOpen, setUserMenuOpen] = useState(false)

  const handleLogout = async () => {
    try {
      if (tokens?.refresh_token) await authApi.logout(tokens.refresh_token)
    } finally {
      logout()
      navigate('/')
    }
  }

  return (
    <nav className="sticky top-0 z-50 h-16 bg-[var(--color-surface)]/90
                    backdrop-blur-md border-b border-[var(--color-border)]">
      <div className="max-w-7xl mx-auto h-full px-4 flex items-center justify-between">

        {/* Logo */}
        <Link to={isAuthenticated ? '/learn' : '/'} className="flex items-center gap-2.5">
          <MascotHeart size={36} animated={false} />
          <span className="font-display font-bold text-2xl gradient-text hidden sm:block">
            Tutunaku
          </span>
        </Link>

        {/* Centro: stats del usuario */}
        {isAuthenticated && user && (
          <div className="hidden md:flex items-center gap-3">
            <StreakBadge streak={user.current_streak} />
            <HeartsDisplay hearts={user.hearts} lastHeartRefill={user.last_heart_refill} />
            <XPBadge xp={user.xp_total} level={user.level} />
          </div>
        )}

        {/* Derecha */}
        <div className="flex items-center gap-2">
          {/* Toggle dark mode */}
          <button
            onClick={toggle}
            className="btn-ghost p-2 rounded-xl"
            aria-label="Cambiar tema"
          >
            {isDark ? <Sun size={20} className="text-alebrije-gold" /> : <Moon size={20} />}
          </button>

          {isAuthenticated ? (
            <>
              {/* Notificaciones */}
              <NotificationBell />

              {/* Avatar / menú usuario */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-2 p-1.5 rounded-xl hover:bg-gray-100
                             dark:hover:bg-dark-muted transition-colors"
                >
                  <div className="w-8 h-8 rounded-full bg-alebrije-gradient flex items-center
                                  justify-center text-white font-bold text-sm">
                    {user?.username?.[0]?.toUpperCase() || 'U'}
                  </div>
                  <span className="hidden sm:block font-semibold text-sm max-w-[100px] truncate">
                    {user?.username}
                  </span>
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-52 card shadow-xl py-2 z-50
                                  animate-slide-down">
                    <Link
                      to="/profile"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50
                                 dark:hover:bg-dark-muted transition-colors"
                    >
                      <User size={16} className="text-alebrije-coral" />
                      <span className="text-sm font-semibold">Mi Perfil</span>
                    </Link>
                    <Link
                      to="/settings"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50
                                 dark:hover:bg-dark-muted transition-colors"
                    >
                      <Settings size={16} className="text-alebrije-teal" />
                      <span className="text-sm font-semibold">Configuración</span>
                    </Link>
                    {user?.role === 'admin' && (
                      <Link
                        to="/admin"
                        onClick={() => setUserMenuOpen(false)}
                        className="flex items-center gap-3 px-4 py-2.5 hover:bg-gray-50
                                   dark:hover:bg-dark-muted transition-colors"
                      >
                        <Shield size={16} className="text-alebrije-violet" />
                        <span className="text-sm font-semibold">Panel Admin</span>
                      </Link>
                    )}
                    <hr className="my-1 border-[var(--color-border)]" />
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-2.5
                                 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors
                                 text-red-500"
                    >
                      <LogOut size={16} />
                      <span className="text-sm font-semibold">Cerrar sesión</span>
                    </button>
                  </div>
                )}
              </div>
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link to="/login" className="btn-ghost text-sm font-bold px-4 py-2">
                Entrar
              </Link>
              <Link to="/register" className="btn-primary text-sm px-4 py-2">
                Comenzar gratis
              </Link>
            </div>
          )}

          {/* Mobile menu button */}
          <button
            className="md:hidden btn-ghost p-2"
            onClick={() => setMobileOpen(!mobileOpen)}
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* Mobile stats bar */}
      {isAuthenticated && user && (
        <div className="md:hidden flex items-center justify-center gap-3 px-4 py-2
                        border-t border-[var(--color-border)] bg-[var(--color-surface)]">
          <StreakBadge streak={user.current_streak} compact />
          <HeartsDisplay hearts={user.hearts} lastHeartRefill={user.last_heart_refill} compact />
          <XPBadge xp={user.xp_total} level={user.level} compact />
        </div>
      )}
    </nav>
  )
}
