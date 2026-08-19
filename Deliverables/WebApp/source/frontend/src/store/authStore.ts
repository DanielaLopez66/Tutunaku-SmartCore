// ============================================================
// TUTUNAKU — Auth Store (Zustand)
// Estado global de autenticación con cookie de sesión de 5 min
// ============================================================
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { User, AuthTokens } from '@/types'

// ── Cookie utilities ─────────────────────────────────
const SESSION_COOKIE_NAME = 'tutunaku_session'
const SESSION_COOKIE_MINUTES = 5

function setSessionCookie() {
  const expires = new Date(Date.now() + SESSION_COOKIE_MINUTES * 60 * 1000)
  document.cookie = `${SESSION_COOKIE_NAME}=active; expires=${expires.toUTCString()}; path=/; SameSite=Strict`
}

function getSessionCookie(): boolean {
  return document.cookie.split(';').some((c) => c.trim().startsWith(`${SESSION_COOKIE_NAME}=`))
}

function deleteSessionCookie() {
  document.cookie = `${SESSION_COOKIE_NAME}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/; SameSite=Strict`
}

// ── Auth State Interface ─────────────────────────────
interface AuthState {
  user: User | null
  tokens: AuthTokens | null
  isAuthenticated: boolean
  isLoading: boolean
  sessionExpiredAt: number | null

  // Actions
  setUser: (user: User) => void
  setTokens: (tokens: AuthTokens) => void
  logout: () => void
  updateUser: (partial: Partial<User>) => void
  refreshSession: () => void
  checkSession: () => boolean
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      tokens: null,
      isAuthenticated: false,
      isLoading: false,
      sessionExpiredAt: null,

      setUser: (user) => {
        setSessionCookie()
        set({
          user,
          isAuthenticated: true,
          sessionExpiredAt: Date.now() + SESSION_COOKIE_MINUTES * 60 * 1000,
        })
      },

      setTokens: (tokens) => {
        setSessionCookie()
        set({
          tokens,
          sessionExpiredAt: Date.now() + SESSION_COOKIE_MINUTES * 60 * 1000,
        })
      },

      logout: () => {
        deleteSessionCookie()
        set({
          user: null,
          tokens: null,
          isAuthenticated: false,
          sessionExpiredAt: null,
        })
      },

      updateUser: (partial) =>
        set((state) => ({
          user: state.user ? { ...state.user, ...partial } : null,
        })),

      refreshSession: () => {
        const state = get()
        if (state.isAuthenticated) {
          setSessionCookie()
          set({ sessionExpiredAt: Date.now() + SESSION_COOKIE_MINUTES * 60 * 1000 })
        }
      },

      checkSession: () => {
        const state = get()
        if (!state.isAuthenticated) return false

        // Check if cookie still exists
        if (!getSessionCookie()) {
          // Session expired — auto-logout
          deleteSessionCookie()
          set({
            user: null,
            tokens: null,
            isAuthenticated: false,
            sessionExpiredAt: null,
          })
          return false
        }
        return true
      },
    }),
    {
      name: 'tutunaku-auth',
      partialize: (state) => ({
        tokens: state.tokens,
        user: state.user,
        sessionExpiredAt: state.sessionExpiredAt,
      }),
    }
  )
)
