// TUTUNAKU — Theme Store (dark mode)
import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface ThemeState {
  isDark: boolean
  toggle: () => void
  setDark: (dark: boolean) => void
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      isDark: false,
      toggle: () =>
        set((s) => {
          const next = !s.isDark
          document.documentElement.classList.toggle('dark', next)
          return { isDark: next }
        }),
      setDark: (dark) => {
        document.documentElement.classList.toggle('dark', dark)
        set({ isDark: dark })
      },
    }),
    { name: 'tutunaku-theme' }
  )
)
