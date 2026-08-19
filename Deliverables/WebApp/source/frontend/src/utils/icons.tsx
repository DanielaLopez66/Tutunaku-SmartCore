// TUTUNAKU — Registro de íconos
// Traduce las claves cortas guardadas en icon_emoji (unidades, logros,
// notificaciones) a componentes de lucide-react. Reemplaza el uso previo
// de emojis como valor de icon_emoji.
import type { CSSProperties } from 'react'
import {
  BookOpen, Hash, Users, PawPrint, Palette, User,
  Home, Globe, Utensils, Music, Calendar, MapPin, Sun, Moon, Leaf, Shirt,
  Trophy, Star, Medal, Award, Flame, Target, Zap, Heart,
  Bell, Clock, ArrowUp, Sparkles, Lock, Package,
  type LucideIcon,
} from 'lucide-react'

export const ICONS = {
  'book-open': BookOpen,
  hash: Hash,
  users: Users,
  'paw-print': PawPrint,
  palette: Palette,
  user: User,
  home: Home,
  globe: Globe,
  utensils: Utensils,
  music: Music,
  calendar: Calendar,
  'map-pin': MapPin,
  sun: Sun,
  moon: Moon,
  leaf: Leaf,
  shirt: Shirt,
  package: Package,
  trophy: Trophy,
  star: Star,
  medal: Medal,
  award: Award,
  flame: Flame,
  target: Target,
  zap: Zap,
  heart: Heart,
  bell: Bell,
  clock: Clock,
  'arrow-up': ArrowUp,
  sparkles: Sparkles,
  lock: Lock,
} satisfies Record<string, LucideIcon>

export type IconKey = keyof typeof ICONS

/** Íconos ofrecidos en el selector de unidades (categorías temáticas del curso). */
export const UNIT_ICON_OPTIONS: IconKey[] = [
  'book-open', 'hash', 'users', 'paw-print', 'palette', 'user',
  'home', 'globe', 'utensils', 'music', 'calendar', 'map-pin',
  'sun', 'moon', 'leaf', 'shirt',
]

/** Íconos ofrecidos en el selector de logros/insignias. */
export const ACHIEVEMENT_ICON_OPTIONS: IconKey[] = [
  'trophy', 'star', 'medal', 'award', 'flame', 'target', 'zap', 'heart',
]

/** Nombres legibles para mostrar en los selectores de ícono. */
export const ICON_LABELS: Record<IconKey, string> = {
  'book-open': 'Libro',
  hash: 'Números',
  users: 'Familia',
  'paw-print': 'Animales',
  palette: 'Colores',
  user: 'Persona',
  home: 'Casa',
  globe: 'Mundo',
  utensils: 'Comida',
  music: 'Música',
  calendar: 'Calendario',
  'map-pin': 'Lugar',
  sun: 'Sol',
  moon: 'Luna',
  leaf: 'Naturaleza',
  shirt: 'Ropa',
  package: 'Paquete',
  trophy: 'Trofeo',
  star: 'Estrella',
  medal: 'Medalla',
  award: 'Premio',
  flame: 'Racha',
  target: 'Objetivo',
  zap: 'Rayo',
  heart: 'Corazón',
  bell: 'Campana',
  clock: 'Reloj',
  'arrow-up': 'Subida de nivel',
  sparkles: 'Destellos',
  lock: 'Bloqueado',
}

/** Ícono de respaldo según el tipo de notificación, cuando no trae icon_emoji. */
export const NOTIFICATION_TYPE_FALLBACK: Record<string, IconKey> = {
  reminder: 'clock',
  achievement: 'trophy',
  progress: 'arrow-up',
  system: 'bell',
}

interface DynamicIconProps {
  name?: string | null
  fallback?: IconKey
  size?: number
  className?: string
  style?: CSSProperties
}

/** Renderiza el ícono correspondiente a una clave (icon_emoji); usa un ícono de respaldo si la clave no existe. */
export function DynamicIcon({ name, fallback = 'sparkles', size = 20, className, style }: DynamicIconProps) {
  const Icon = (name && ICONS[name as IconKey]) || ICONS[fallback]
  return <Icon size={size} className={className} style={style} />
}
