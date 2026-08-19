// TUTUNAKU — LeaderboardPage
import { useQuery } from '@tanstack/react-query'
import { Trophy, Crown, Medal, Flame, Zap, Users } from 'lucide-react'
import { userApi } from '@/utils/api'
import type { LeaderboardEntry } from '@/types'

export default function LeaderboardPage() {
  const { data: entries = [], isLoading } = useQuery<LeaderboardEntry[]>({
    queryKey: ['leaderboard'],
    queryFn: () => userApi.getLeaderboard().then((r) => r.data),
  })

  return (
    <div className="max-w-2xl mx-auto animate-fade-in">
      <div className="mb-8">
        <h1 className="font-display text-3xl font-bold flex items-center gap-2">
          <Trophy className="text-alebrije-gold" /> Tabla de posiciones
        </h1>
        <p className="text-[var(--color-muted)] mt-1">Los mejores estudiantes de totonaco</p>
      </div>

      {isLoading ? (
        <div className="p-8 text-center text-[var(--color-muted)]">
          <div className="w-8 h-8 border-3 border-alebrije-coral/30 border-t-alebrije-coral
                          rounded-full animate-spin mx-auto mb-3" />
          Cargando ranking...
        </div>
      ) : entries.length === 0 ? (
        <div className="text-center py-16 card">
          <Users size={48} className="mx-auto text-[var(--color-muted)] mb-4" />
          <p className="font-display text-xl font-bold">Aún no hay estudiantes en el ranking</p>
          <p className="text-[var(--color-muted)] mt-2">Sé el primero en ganar XP</p>
        </div>
      ) : (
        <div className="space-y-3">
          {entries.map((u, i) => (
            <div
              key={u.id}
              className={`card p-4 flex items-center gap-4 ${
                i < 3 ? 'border-l-4' : ''
              } ${u.is_me ? 'ring-2 ring-alebrije-coral' : ''}`}
              style={{
                borderLeftColor: i === 0 ? '#FFD700' : i === 1 ? '#C0C0C0' : i === 2 ? '#CD7F32' : undefined
              }}
            >
              <span className="w-10 flex items-center justify-center">
                {i === 0 ? (
                  <Crown size={22} className="text-yellow-500" fill="currentColor" />
                ) : i < 3 ? (
                  <Medal size={22} className={i === 1 ? 'text-gray-400' : 'text-amber-700'} />
                ) : (
                  <span className="text-lg font-bold text-[var(--color-muted)]">#{u.rank}</span>
                )}
              </span>
              <div className="w-10 h-10 rounded-full bg-alebrije-gradient flex items-center
                              justify-center text-white font-bold text-sm flex-shrink-0">
                {u.username[0].toUpperCase()}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-bold truncate">
                  {u.username} {u.is_me && <span className="text-alebrije-coral font-semibold">(tú)</span>}
                </p>
                <p className="text-xs text-[var(--color-muted)] flex items-center gap-1">
                  Nivel {u.level} · <Flame size={12} className="text-orange-500" /> {u.current_streak} días
                </p>
              </div>
              <span className="font-display font-bold text-lg text-alebrije-coral flex items-center gap-1 flex-shrink-0">
                <Zap size={16} /> {u.xp_total.toLocaleString()}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
