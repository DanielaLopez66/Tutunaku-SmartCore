// ============================================================
// TUTUNAKU — HomePage (Landing)
// ============================================================
import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { BookOpen, Trophy, Zap, Heart, Users, Globe, MapPin, Landmark, Palette, ScrollText } from 'lucide-react'
import MascotHeart from '@/components/ui/MascotHeart'

const features = [
  { icon: Zap,      color: 'text-alebrije-gold',    bg: 'bg-yellow-50 dark:bg-yellow-900/20',   title: 'Sistema de XP',        desc: 'Gana puntos de experiencia con cada ejercicio correcto y sube de nivel' },
  { icon: Heart,    color: 'text-alebrije-coral',   bg: 'bg-red-50 dark:bg-red-900/20',         title: 'Vidas / Corazones',    desc: 'Tienes 5 corazones. Los errores cuestan una vida ¡cuídalos!' },
  { icon: Trophy,   color: 'text-alebrije-violet',  bg: 'bg-violet-50 dark:bg-violet-900/20',   title: 'Insignias',            desc: 'Desbloquea más de 10 logros únicos mientras progresas' },
  { icon: BookOpen, color: 'text-alebrije-teal',    bg: 'bg-teal-50 dark:bg-teal-900/20',       title: 'Clases + Ejercicios',  desc: 'Aprende con contenido cultural antes de practicar' },
  { icon: Users,    color: 'text-alebrije-magenta', bg: 'bg-pink-50 dark:bg-pink-900/20',       title: 'Ranking Global',       desc: 'Compite con otros estudiantes en la tabla de posiciones' },
  { icon: Globe,    color: 'text-alebrije-sky',     bg: 'bg-sky-50 dark:bg-sky-900/20',         title: 'Mapa de Niveles',      desc: 'Navega por unidades temáticas como un videojuego de aventura' },
]

const cultureTags = [
  { label: 'Sierra Norte de Puebla', Icon: MapPin },
  { label: 'Cultura Totonaca', Icon: Landmark },
  { label: 'Diseño Alebrije', Icon: Palette },
  { label: 'Patrimonio Lingüístico', Icon: ScrollText },
]

const stats = [
  { value: '50+', label: 'Lecciones' },
  { value: '200+', label: 'Ejercicios' },
  { value: '4 tipos', label: 'Actividades' },
  { value: '10+', label: 'Insignias' },
]

export default function HomePage() {
  return (
    <div className="space-y-24 pb-16">

      {/* ── Hero ────────────────────────────────────────── */}
      <section className="relative pt-12 pb-8 overflow-hidden">
        {/* Fondo decorativo */}
        <div className="absolute inset-0 -z-10 overflow-hidden">
          <div className="absolute -top-20 -right-20 w-96 h-96 bg-alebrije-coral/10 rounded-full blur-3xl" />
          <div className="absolute -bottom-10 -left-10 w-80 h-80 bg-alebrije-teal/10 rounded-full blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-alebrije-violet/8 rounded-full blur-3xl" />
        </div>

        <div className="max-w-4xl mx-auto text-center px-4">
          {/* Mascota animada */}
          <motion.div
            initial={{ scale: 0, rotate: -10 }}
            animate={{ scale: 1, rotate: 0 }}
            transition={{ type: 'spring', stiffness: 200, damping: 15 }}
            className="flex justify-center mb-6"
          >
            <MascotHeart size={130} animated />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="font-display text-5xl md:text-7xl font-bold leading-tight"
          >
            Aprende{' '}
            <span className="gradient-text">Totonaco</span>
            <br />
            con alegría
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35 }}
            className="mt-6 text-xl md:text-2xl text-[var(--color-muted)] max-w-2xl mx-auto leading-relaxed"
          >
            Tutunaku es la plataforma educativa gamificada para preservar y aprender
            la <strong className="text-[var(--color-text)]">lengua totonaca</strong>,
            inspirada en la riqueza cultural de los alebrijes mexicanos.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="mt-10 flex flex-col sm:flex-row gap-4 justify-center"
          >
            <Link to="/register" className="btn-primary text-lg px-8 py-4">
              Comenzar gratis
            </Link>
            <Link to="/login" className="btn-secondary text-lg px-8 py-4">
              Ya tengo cuenta
            </Link>
          </motion.div>

          {/* Badges culturales */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.7 }}
            className="mt-8 flex flex-wrap gap-3 justify-center"
          >
            {cultureTags.map(({ label, Icon }) => (
              <span key={label}
                className="text-sm font-semibold px-4 py-2 rounded-full
                           bg-[var(--color-surface)] border border-[var(--color-border)]
                           text-[var(--color-muted)] flex items-center gap-1.5">
                <Icon size={14} /> {label}
              </span>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Stats ───────────────────────────────────────── */}
      <section className="max-w-4xl mx-auto px-4">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {stats.map(({ value, label }, i) => (
            <motion.div
              key={label}
              initial={{ opacity: 0, scale: 0.8 }}
              whileInView={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.1 }}
              viewport={{ once: true }}
              className="card p-6 text-center"
            >
              <div className="font-display text-4xl font-bold gradient-text">{value}</div>
              <div className="text-sm text-[var(--color-muted)] font-semibold mt-1">{label}</div>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── Features ────────────────────────────────────── */}
      <section className="max-w-5xl mx-auto px-4">
        <div className="text-center mb-12">
          <h2 className="font-display text-4xl font-bold">
            Todo lo que necesitas para aprender
          </h2>
          <p className="mt-3 text-[var(--color-muted)] text-lg">
            Una experiencia completa de aprendizaje gamificado
          </p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, color, bg, title, desc }, i) => (
            <motion.div
              key={title}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08 }}
              viewport={{ once: true }}
              className="card p-6 hover:-translate-y-1 transition-transform duration-200"
            >
              <div className={`w-12 h-12 rounded-2xl ${bg} flex items-center justify-center mb-4`}>
                <Icon className={color} size={24} />
              </div>
              <h3 className="font-display font-bold text-lg mb-2">{title}</h3>
              <p className="text-[var(--color-muted)] text-sm leading-relaxed">{desc}</p>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ── CTA final ───────────────────────────────────── */}
      <section className="max-w-2xl mx-auto px-4 text-center">
        <div className="card p-10 bg-alebrije-gradient text-white">
          <MascotHeart size={80} animated />
          <h2 className="font-display text-4xl font-bold mt-4 text-shadow">
            ¡Empieza hoy!
          </h2>
          <p className="mt-3 text-white/90 text-lg">
            Únete a la comunidad y preserva la lengua totonaca
          </p>
          <Link
            to="/register"
            className="mt-6 inline-flex items-center gap-2 bg-white text-alebrije-coral
                       font-bold px-8 py-3 rounded-2xl hover:bg-white/90 transition-colors
                       shadow-lg text-lg"
          >
            Crear mi cuenta gratis →
          </Link>
        </div>
      </section>
    </div>
  )
}
