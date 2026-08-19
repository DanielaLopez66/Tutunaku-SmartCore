// TUTUNAKU — AuthLayout
import { Outlet, Link } from 'react-router-dom'
import { Bird, Flower2, Feather, Sparkles, Wind, Leaf, Gamepad2, Flame, Trophy, Compass } from 'lucide-react'
import MascotHeart from '@/components/ui/MascotHeart'

const DECORATIONS = [Bird, Flower2, Feather, Sparkles, Wind, Leaf]
const FEATURES = [
  { label: 'Gamificado', Icon: Gamepad2 },
  { label: 'Rachas', Icon: Flame },
  { label: 'Logros', Icon: Trophy },
  { label: 'Aventura', Icon: Compass },
]

export default function AuthLayout() {
  return (
    <div className="min-h-screen flex alebrije-pattern">
      {/* Panel izquierdo — decorativo */}
      <div className="hidden lg:flex flex-col items-center justify-center w-1/2
                      bg-gradient-to-br from-alebrije-coral via-alebrije-orange to-alebrije-violet
                      relative overflow-hidden">
        {/* Decoración de fondo */}
        <div className="absolute inset-0 opacity-10">
          {DECORATIONS.map((Icon, i) => (
            <Icon
              key={i}
              size={64}
              className="absolute"
              style={{
                top: `${10 + i * 14}%`,
                left: `${5 + (i % 3) * 30}%`,
                transform: `rotate(${i * 45}deg)`,
              }}
            />
          ))}
        </div>

        <div className="relative z-10 text-center text-white px-8">
          <MascotHeart size={120} animated />
          <h1 className="font-display text-5xl font-bold mt-6 text-shadow">
            Tutunaku
          </h1>
          <p className="mt-3 text-xl opacity-90 font-body">
            Aprende totonaco de forma<br />divertida y gamificada
          </p>
          <div className="mt-8 flex gap-4 justify-center flex-wrap">
            {FEATURES.map(({ label, Icon }) => (
              <span key={label} className="bg-white/20 backdrop-blur-sm px-4 py-2
                                        rounded-full text-sm font-semibold flex items-center gap-1.5">
                <Icon size={14} /> {label}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Panel derecho — formulario */}
      <div className="flex-1 flex flex-col items-center justify-center p-8">
        {/* Logo mobile */}
        <Link to="/" className="lg:hidden flex items-center gap-3 mb-8">
          <MascotHeart size={48} />
          <span className="font-display text-3xl font-bold gradient-text">Tutunaku</span>
        </Link>

        <div className="w-full max-w-md">
          <Outlet />
        </div>
      </div>
    </div>
  )
}
