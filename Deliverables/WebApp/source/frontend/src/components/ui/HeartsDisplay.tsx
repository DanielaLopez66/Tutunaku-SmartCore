// ============================================================
// TUTUNAKU — UI Micro-components
// ============================================================

import { Heart, Hourglass, Zap, Flame } from 'lucide-react'
import { useHeartTimer } from '@/hooks/useHeartTimer'

// ── HeartsDisplay ─────────────────────────────────────────
interface HeartsProps { hearts: number; compact?: boolean; lastHeartRefill?: string }
export function HeartsDisplay({ hearts, compact, lastHeartRefill }: HeartsProps) {
  const MAX = 5
  const timeLeft = useHeartTimer(hearts, lastHeartRefill)

  return (
    <div className="flex items-center gap-2">
      <div className="flex items-center gap-1">
        {compact ? (
          <span className="flex items-center gap-1 bg-red-50 dark:bg-red-900/20
                            text-red-500 px-2.5 py-1 rounded-full text-xs font-bold">
            <Heart size={12} fill="currentColor" /> {hearts}
          </span>
        ) : (
          Array.from({ length: MAX }).map((_, i) => (
            <Heart
              key={i}
              size={18}
              fill="currentColor"
              className={`text-red-500 transition-all duration-300 ${
                i < hearts ? 'opacity-100 scale-100' : 'opacity-30 grayscale scale-90'
              }`}
            />
          ))
        )}
      </div>
      {timeLeft && (
        <span className="flex items-center gap-1 text-xs font-bold text-red-400 bg-red-50 dark:bg-red-900/20 px-2 py-0.5 rounded-full whitespace-nowrap">
          <Hourglass size={11} /> {timeLeft}
        </span>
      )}
    </div>
  )
}

// ── XPBadge ───────────────────────────────────────────────
interface XPProps { xp: number; level: number; compact?: boolean }
export function XPBadge({ xp, level, compact }: XPProps) {
  return (
    <div className="flex items-center gap-2">
      <span className="flex items-center gap-1 bg-alebrije-gold/20 text-yellow-600
                        dark:text-alebrije-gold px-2.5 py-1 rounded-full text-xs font-bold">
        <Zap size={12} fill="currentColor" /> {compact ? xp : `${xp} XP`}
      </span>
      {!compact && (
        <span className="flex items-center gap-1 bg-alebrije-violet/20 text-alebrije-violet
                          px-2.5 py-1 rounded-full text-xs font-bold">
          Nv.{level}
        </span>
      )}
    </div>
  )
}

// ── StreakBadge ───────────────────────────────────────────
interface StreakProps { streak: number; compact?: boolean }
export function StreakBadge({ streak, compact }: StreakProps) {
  return (
    <span className="flex items-center gap-1 bg-orange-50 dark:bg-orange-900/20
                      text-orange-500 px-2.5 py-1 rounded-full text-xs font-bold">
      <Flame size={12} fill="currentColor" /> {streak}{!compact && ' días'}
    </span>
  )
}

// Re-exports default
export { HeartsDisplay as default }
