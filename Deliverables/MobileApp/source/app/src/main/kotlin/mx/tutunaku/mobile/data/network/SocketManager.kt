package mx.tutunaku.mobile.data.network

import io.socket.client.IO
import io.socket.client.Socket
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.serialization.json.Json
import mx.tutunaku.mobile.data.model.UserStatsUpdatedEvent
import org.json.JSONObject

/**
 * Cliente de Socket.IO hacia el mismo servidor que usa el dashboard web y
 * el reloj (Deliverables/WebApp/source/backend/app/sockets/server.py) —
 * mismo patrón, verbatim, que
 * Deliverables/WearableApp/source/.../data/network/SocketManager.kt.
 */
class SocketManager {
    private var socket: Socket? = null
    private val json = Json { ignoreUnknownKeys = true }

    private val _connected = MutableStateFlow(false)
    val connected: StateFlow<Boolean> = _connected

    var onStatsUpdated: ((UserStatsUpdatedEvent) -> Unit)? = null

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
