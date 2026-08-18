package mx.tutunaku.wearable.data.network

import io.socket.client.IO
import io.socket.client.Socket
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.json.Json
import mx.tutunaku.wearable.data.model.NotificationDto
import mx.tutunaku.wearable.data.model.UserStatsUpdatedEvent
import org.json.JSONObject

/**
 * Cliente de Socket.IO hacia el mismo servidor que usa el dashboard web
 * (Deliverables/WebApp/source/backend/app/sockets/server.py). El backend
 * une cada conexión autenticada a una sala personal `user:<id>`, así que
 * aquí basta con enviar el token — nada de salas ni canales que configurar
 * desde el cliente.
 *
 * El envío de credenciales usa `IO.Options.auth`, el equivalente Java del
 * `auth` de socket.io-client JS que tuve que corregir en el frontend web
 * (`frontend/src/utils/socket.ts`): aquí no aplica el mismo bug porque la
 * librería Java expone `auth` como un mapa plano, no como una función con
 * callback — se asigna una sola vez antes de conectar.
 */
class SocketManager {
    private var socket: Socket? = null
    private val json = Json { ignoreUnknownKeys = true }

    private val _connected = MutableStateFlow(false)
    val connected: StateFlow<Boolean> = _connected

    var onStatsUpdated: ((UserStatsUpdatedEvent) -> Unit)? = null
    var onNewNotification: ((NotificationDto) -> Unit)? = null

    fun connect(serverUrl: String, token: String) {
        disconnect()

        val options = IO.Options()
        options.auth = mapOf("token" to token)
        options.reconnection = true
        options.reconnectionDelay = 1000
        options.reconnectionDelayMax = 10000

        val s = IO.socket(serverUrl, options)

        s.on(Socket.EVENT_CONNECT) { _ -> _connected.value = true }
        s.on(Socket.EVENT_DISCONNECT) { _ -> _connected.value = false }

        s.on("user_stats_updated") { args ->
            val payload = args.getOrNull(0) as? JSONObject ?: return@on
            runCatching {
                json.decodeFromString(UserStatsUpdatedEvent.serializer(), payload.toString())
            }.onSuccess { onStatsUpdated?.invoke(it) }
        }

        s.on("new_notification") { args ->
            val payload = args.getOrNull(0) as? JSONObject ?: return@on
            runCatching {
                json.decodeFromString(NotificationDto.serializer(), payload.toString())
            }.onSuccess { onNewNotification?.invoke(it) }
        }

        s.connect()
        socket = s
    }

    fun disconnect() {
        socket?.off()
        socket?.disconnect()
        socket = null
        _connected.value = false
    }
}
