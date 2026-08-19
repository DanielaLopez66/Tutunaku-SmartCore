// TUTUNAKUN — AchievementsPage
import { useQuery } from '@tanstack/react-query'
import { motion } from 'framer-motion'
import { Trophy, Zap, Lock } from 'lucide-react'
import { achievementApi } from '@/utils/api'
import { DynamicIcon } from '@/utils/icons'
import type { Achievement, UserAchievement } from '@/types'

export default function AchievementsPage() {
  const { data: all = [] } = useQuery<Achievement[]>({
    queryKey: ['achievements'],
    queryFn: () => achievementApi.list().then((r) => r.data),
  })
  const { data: mine = [] } = useQuery<UserAchievement[]>({
    queryKey: ['my-achievements'],
    queryFn: () => achievementApi.mine().then((r) => r.data),
  })

  const earnedIds = new Set(mine.map((ua) => ua.achievement.id))

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold flex items-center gap-2">
          <Trophy className="text-alebrije-gold" /> Logros
        </h1>
        <p className="text-[var(--color-muted)] mt-1">
          {mine.length} / {all.length} desbloqueados
        </p>
        <div className="mt-3 xp-bar h-3">
          <div
            className="xp-bar-fill"
            style={{ width: all.length ? `${(mine.length / all.length) * 100}%` : '0%' }}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        {all.map((ach, i) => {
          const earned = earnedIds.has(ach.id)
          return (
            <motion.div
              key={ach.id}
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.06 }}
              className={`card p-5 flex items-center gap-4 transition-all ${
                earned ? '' : 'opacity-50 grayscale'
              }`}
              style={{ borderLeft: earned ? `4px solid ${ach.badge_color}` : undefined }}
            >
              <div
                className="w-14 h-14 rounded-2xl flex items-center justify-center
                           flex-shrink-0"
                style={{ backgroundColor: `${ach.badge_color}20` }}
              >
                {earned ? (
                  <DynamicIcon name={ach.icon_emoji} fallback="trophy" size={26} style={{ color: ach.badge_color }} />
                ) : (
                  <Lock size={22} className="text-[var(--color-muted)]" />
                )}
              </div>
              <div>
                <p className="font-bold">{ach.title}</p>
                <p className="text-xs text-[var(--color-muted)] mt-0.5 line-clamp-2">
                  {ach.description}
                </p>
                <span className="text-xs font-bold text-yellow-600 flex items-center gap-1">
                  <Zap size={12} /> +{ach.xp_reward} XP
                </span>
              </div>
            </motion.div>
          )
        })}
      </div>
    </div>
  )
}
