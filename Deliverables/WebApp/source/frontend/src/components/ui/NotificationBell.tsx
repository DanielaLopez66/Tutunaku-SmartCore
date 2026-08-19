// TUTUNAKU — NotificationBell: campana de notificaciones real (antes decorativa)
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Bell, CheckCheck } from 'lucide-react'
import { notificationApi } from '@/utils/api'
import { DynamicIcon, NOTIFICATION_TYPE_FALLBACK } from '@/utils/icons'
import type { Notification } from '@/types'

function timeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime()
  const minutes = Math.floor(diffMs / 60_000)
  if (minutes < 1) return 'ahora'
  if (minutes < 60) return `hace ${minutes} min`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `hace ${hours} h`
  return `hace ${Math.floor(hours / 24)} d`
}

export default function NotificationBell() {
  const [open, setOpen] = useState(false)
  const qc = useQueryClient()

  const { data: notifications = [] } = useQuery<Notification[]>({
    queryKey: ['notifications'],
    queryFn: () => notificationApi.list().then((r) => r.data),
    refetchInterval: 30_000,
  })

  const unreadCount = notifications.filter((n) => !n.is_read).length

  const markReadMutation = useMutation({
    mutationFn: (id: string) => notificationApi.markRead(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  })

  const markAllReadMutation = useMutation({
    mutationFn: () => notificationApi.markAllRead(),
    onSuccess: () => qc.invalidateQueries({ queryKey: ['notifications'] }),
  })

  return (
    <div className="relative">
      <button
        onClick={() => setOpen((v) => !v)}
        className="btn-ghost p-2 rounded-xl relative"
        aria-label="Notificaciones"
      >
        <Bell size={20} />
        {unreadCount > 0 && (
          <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] px-1 flex items-center
                           justify-center bg-alebrije-coral rounded-full text-[10px] font-bold text-white">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && (
        <div className="absolute right-0 mt-2 w-80 max-w-[90vw] card shadow-xl py-2 z-50 animate-slide-down">
          <div className="flex items-center justify-between px-4 py-2">
            <p className="font-display font-bold text-sm">Notificaciones</p>
            {unreadCount > 0 && (
              <button
                onClick={() => markAllReadMutation.mutate()}
                className="text-xs font-semibold text-alebrije-teal flex items-center gap-1 hover:underline"
              >
                <CheckCheck size={14} /> Marcar todas
              </button>
            )}
          </div>
          <hr className="border-[var(--color-border)]" />

          <div className="max-h-96 overflow-y-auto">
            {notifications.length === 0 && (
              <p className="text-sm text-[var(--color-muted)] text-center py-6">
                No tienes notificaciones
              </p>
            )}
            {notifications.map((n) => {
              const content = (
                <div
                  className={`flex items-start gap-3 px-4 py-3 hover:bg-gray-50 dark:hover:bg-dark-muted
                             transition-colors ${!n.is_read ? 'bg-red-50/50 dark:bg-red-900/10' : ''}`}
                >
                  <DynamicIcon
                    name={n.icon_emoji}
                    fallback={NOTIFICATION_TYPE_FALLBACK[n.type] || 'bell'}
                    size={18}
                    className="flex-shrink-0 text-alebrije-coral mt-0.5"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold truncate">{n.title}</p>
                    {n.message && (
                      <p className="text-xs text-[var(--color-muted)] line-clamp-2">{n.message}</p>
                    )}
                    <p className="text-[10px] text-[var(--color-muted)] mt-1">{timeAgo(n.created_at)}</p>
                  </div>
                  {!n.is_read && (
                    <span className="w-2 h-2 rounded-full bg-alebrije-coral mt-1.5 flex-shrink-0" />
                  )}
                </div>
              )

              return n.action_url ? (
                <Link
                  key={n.id}
                  to={n.action_url}
                  onClick={() => {
                    if (!n.is_read) markReadMutation.mutate(n.id)
                    setOpen(false)
                  }}
                >
                  {content}
                </Link>
              ) : (
                <button
                  key={n.id}
                  onClick={() => !n.is_read && markReadMutation.mutate(n.id)}
                  className="w-full text-left"
                >
                  {content}
                </button>
              )
            })}
          </div>
        </div>
      )}
    </div>
  )
}
