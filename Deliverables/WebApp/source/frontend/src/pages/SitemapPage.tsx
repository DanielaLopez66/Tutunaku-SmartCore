// TUTUNAKU — SitemapPage
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Map, Book, Award, User, Settings, ShieldCheck, HelpCircle } from 'lucide-react'

const sections = [
  {
    title: 'General',
    icon: <HelpCircle className="text-blue-400" />,
    links: [
      { name: 'Inicio', path: '/' },
      { name: 'Aprender', path: '/learn' },
      { name: 'Clasificación', path: '/leaderboard' },
    ]
  },
  {
    title: 'Mi Cuenta',
    icon: <User className="text-purple-400" />,
    links: [
      { name: 'Perfil', path: '/profile' },
      { name: 'Logros', path: '/achievements' },
      { name: 'Configuración', path: '/settings' },
    ]
  },
  {
    title: 'Contenido',
    icon: <Book className="text-green-400" />,
    links: [
      { name: 'Explorar Cursos', path: '/learn' },
      { name: 'Continuar Lección', path: '/learn' },
    ]
  },
  {
    title: 'Administración',
    icon: <ShieldCheck className="text-red-400" />,
    links: [
      { name: 'Panel de Control', path: '/admin' },
      { name: 'Gestión de Usuarios', path: '/admin/users' },
      { name: 'Gestión de Cursos', path: '/admin/courses' },
    ]
  }
]

export default function SitemapPage() {
  return (
    <div className="max-w-4xl mx-auto py-12 px-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center mb-12"
      >
        <div className="inline-flex p-3 bg-white/5 rounded-2xl mb-4">
          <Map className="w-10 h-10 text-[var(--color-primary)]" />
        </div>
        <h1 className="text-4xl font-display font-bold gradient-text">Mapa del Sitio</h1>
        <p className="text-[var(--color-muted)] mt-2">Guía rápida de navegación para Tutunaku</p>
      </motion.div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {sections.map((section, idx) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, x: idx % 2 === 0 ? -20 : 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: idx * 0.1 }}
            className="bg-white/5 border border-white/10 rounded-2xl p-6 backdrop-blur-sm"
          >
            <div className="flex items-center gap-3 mb-6">
              {section.icon}
              <h2 className="text-xl font-display font-bold">{section.title}</h2>
            </div>
            <ul className="space-y-4">
              {section.links.map((link) => (
                <li key={link.path}>
                  <Link
                    to={link.path}
                    className="flex items-center text-[var(--color-muted)] hover:text-white transition-colors group"
                  >
                    <div className="w-1.5 h-1.5 rounded-full bg-[var(--color-primary)] mr-3 opacity-0 group-hover:opacity-100 transition-opacity" />
                    {link.name}
                  </Link>
                </li>
              ))}
            </ul>
          </motion.div>
        ))}
      </div>
    </div>
  )
}
