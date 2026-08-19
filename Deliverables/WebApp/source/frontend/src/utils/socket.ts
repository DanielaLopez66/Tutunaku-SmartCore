// ============================================================
// TUTUNAKU — Cliente Socket.IO (Dashboard en tiempo real)
// Singleton autenticado con el JWT actual; conecta bajo demanda.
// ============================================================
import { io, type Socket } from 'socket.io-client'
import { useAuthStore } from '@/store/authStore'
import { ROOT_URL } from './api'

let socket: Socket | null = null

export function getSocket(): Socket {
  if (socket) return socket

  socket = io(ROOT_URL, {
    autoConnect: false,
    reconnection: true,
    reconnectionAttempts: Infinity,
    reconnectionDelay: 1_000,
    reconnectionDelayMax: 10_000,
    auth: (cb) => {
      // socket.io-client requiere invocar el callback recibido; retornar un
      // valor directamente (sin llamarlo) deja el paquete CONNECT sin enviar
      // y el socket queda atascado en "conectando" para siempre.
      cb({ token: useAuthStore.getState().tokens?.access_token ?? null })
    },
  })

  return socket
}

export function connectSocket(): Socket {
  const s = getSocket()
  if (!s.connected) s.connect()
  return s
}

export function disconnectSocket(): void {
  socket?.disconnect()
}
