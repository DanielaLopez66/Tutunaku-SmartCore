import { Outlet, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import Navbar from './Navbar'
import Sidebar from './Sidebar'
import Breadcrumbs from '../ui/Breadcrumbs'
import { useAuthStore } from '@/store/authStore'

export default function MainLayout() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const location = useLocation()

  return (
    <div className="min-h-screen bg-[var(--color-bg)] alebrije-pattern">
      <Navbar />
      <div className="flex max-w-7xl mx-auto">
        {isAuthenticated && (
          <aside className="hidden lg:block w-72 shrink-0 border-r border-white/5 h-[calc(100vh-4.5rem)] sticky top-[4.5rem]">
            <Sidebar />
          </aside>
        )}
        <main className="flex-1 px-4 py-6 md:px-8 min-h-[calc(100vh-4rem)]">
          <Breadcrumbs />
          <AnimatePresence mode="wait">
            <motion.div
              key={location.pathname}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.2 }}
            >
              <Outlet />
            </motion.div>
          </AnimatePresence>
        </main>
      </div>
    </div>
  )
}
