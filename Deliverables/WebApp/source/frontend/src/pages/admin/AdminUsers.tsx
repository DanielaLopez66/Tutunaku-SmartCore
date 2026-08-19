// TUTUNAKU — AdminUsers
import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Search, ShieldCheck, ShieldOff, RefreshCw, UserCheck, Shield, User as UserIcon, Zap, Check, X, Users } from 'lucide-react'
import { adminApi } from '@/utils/api'
import type { User } from '@/types'
import toast from 'react-hot-toast'

export default function AdminUsers() {
  const qc = useQueryClient()
  const [search, setSearch] = useState('')

  const { data: users = [], isLoading } = useQuery<User[]>({
    queryKey: ['admin-users'],
    queryFn: () => adminApi.listUsers().then((r) => r.data),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: object }) => adminApi.updateUser(id, data),
    onSuccess: () => {
      toast.success('Usuario actualizado')
      qc.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => toast.error('Error al actualizar usuario'),
  })

  const resetMutation = useMutation({
    mutationFn: (id: string) => adminApi.resetProgress(id),
    onSuccess: () => {
      toast.success('Progreso reiniciado')
      qc.invalidateQueries({ queryKey: ['admin-users'] })
    },
    onError: () => toast.error('Error al reiniciar progreso'),
  })

  const filtered = users.filter(
    (u) =>
      u.username.toLowerCase().includes(search.toLowerCase()) ||
      u.email.toLowerCase().includes(search.toLowerCase())
  )

  return (
    <div className="space-y-6 animate-fade-in">
      <div className="flex items-center justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-3xl font-bold flex items-center gap-2">
            <Users className="text-alebrije-coral" /> Gestión de Usuarios
          </h1>
          <p className="text-[var(--color-muted)] mt-0.5">{users.length} usuarios registrados</p>
        </div>
      </div>

      {/* Buscador */}
      <div className="relative">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-[var(--color-muted)]" size={18} />
        <input
          type="text"
          className="input pl-11"
          placeholder="Buscar por username o email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      {/* Tabla */}
      <div className="card overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-[var(--color-muted)]">
            <div className="w-8 h-8 border-3 border-alebrije-coral/30 border-t-alebrije-coral
                            rounded-full animate-spin mx-auto mb-3" />
            Cargando usuarios...
          </div>
        ) : filtered.length === 0 ? (
          <div className="p-8 text-center text-[var(--color-muted)]">
            No se encontraron usuarios
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-[var(--color-border)] bg-gray-50 dark:bg-dark-muted">
                  <th className="text-left px-4 py-3 text-xs font-bold text-[var(--color-muted)] uppercase">
                    Usuario
                  </th>
                  <th className="text-left px-4 py-3 text-xs font-bold text-[var(--color-muted)] uppercase hidden md:table-cell">
                    Email
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-bold text-[var(--color-muted)] uppercase">
                    Nivel / XP
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-bold text-[var(--color-muted)] uppercase">
                    Rol
                  </th>
                  <th className="text-center px-4 py-3 text-xs font-bold text-[var(--color-muted)] uppercase">
                    Estado
                  </th>
                  <th className="text-right px-4 py-3 text-xs font-bold text-[var(--color-muted)] uppercase">
                    Acciones
                  </th>
                </tr>
              </thead>
              <tbody>
                {filtered.map((user) => (
                  <tr
                    key={user.id}
                    className="border-b border-[var(--color-border)] last:border-0
                               hover:bg-gray-50 dark:hover:bg-dark-muted transition-colors"
                  >
                    <td className="px-4 py-3">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-alebrije-gradient flex items-center
                                        justify-center text-white text-xs font-bold flex-shrink-0">
                          {user.username[0].toUpperCase()}
                        </div>
                        <div>
                          <p className="font-semibold text-sm">{user.username}</p>
                          <p className="text-xs text-[var(--color-muted)] md:hidden">{user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-4 py-3 text-sm text-[var(--color-muted)] hidden md:table-cell">
                      {user.email}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className="text-sm font-bold">Nv.{user.level}</span>
                      <span className="text-xs text-[var(--color-muted)] flex items-center justify-center gap-0.5">
                        <Zap size={11} />{user.xp_total}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`badge text-xs flex items-center gap-1 justify-center ${
                        user.role === 'admin'
                          ? 'bg-alebrije-violet/10 text-alebrije-violet'
                          : 'bg-alebrije-teal/10 text-alebrije-teal'
                      }`}>
                        {user.role === 'admin' ? <><Shield size={12} /> Admin</> : <><UserIcon size={12} /> Usuario</>}
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`badge text-xs flex items-center gap-1 justify-center ${
                        user.is_active
                          ? 'bg-green-50 dark:bg-green-900/20 text-green-600'
                          : 'bg-red-50 dark:bg-red-900/20 text-red-500'
                      }`}>
                        {user.is_active ? <><Check size={12} /> Activo</> : <><X size={12} /> Inactivo</>}
                      </span>
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-2">
                        {/* Toggle activo */}
                        <button
                          onClick={() =>
                            updateMutation.mutate({ id: user.id, data: { is_active: !user.is_active } })
                          }
                          title={user.is_active ? 'Desactivar' : 'Activar'}
                          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-muted
                                     transition-colors text-[var(--color-muted)]"
                        >
                          {user.is_active ? <ShieldOff size={16} /> : <ShieldCheck size={16} />}
                        </button>
                        {/* Toggle rol */}
                        <button
                          onClick={() =>
                            updateMutation.mutate({
                              id: user.id,
                              data: { role: user.role === 'admin' ? 'user' : 'admin' },
                            })
                          }
                          title="Cambiar rol"
                          className="p-1.5 rounded-lg hover:bg-gray-100 dark:hover:bg-dark-muted
                                     transition-colors text-alebrije-violet"
                        >
                          <UserCheck size={16} />
                        </button>
                        {/* Resetear progreso */}
                        <button
                          onClick={() => {
                            if (confirm(`¿Reiniciar progreso de ${user.username}?`)) {
                              resetMutation.mutate(user.id)
                            }
                          }}
                          title="Reiniciar progreso"
                          className="p-1.5 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/20
                                     transition-colors text-red-400"
                        >
                          <RefreshCw size={16} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  )
}
