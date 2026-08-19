package mx.tutunaku.mobile.data.wear

import android.content.Context
import android.util.Log
import com.google.android.gms.wearable.CapabilityClient
import com.google.android.gms.wearable.CapabilityInfo
import com.google.android.gms.wearable.PutDataMapRequest
import com.google.android.gms.wearable.Wearable
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.tasks.await
import mx.tutunaku.mobile.R

/**
 * Emparejamiento teléfono↔reloj vía la Wearable Data Layer API de Google
 * (com.google.android.gms:play-services-wearable) — el mecanismo oficial
 * para esto, no un sustituto indirecto por el backend.
 *
 * Ambas apps (teléfono y reloj) se anuncian bajo la MISMA capability
 * ("tutunaku_wear_app", ver res/values/wear.xml en ambos proyectos —
 * no hay módulo Gradle compartido entre los dos, así que el nombre debe
 * coincidir literal). "Conectado" significa: existe un nodo alcanzable con
 * esa capability que NO es este mismo dispositivo.
 *
 * Paths usados en la Data Layer (deben coincidir con
 * Deliverables/WearableApp/source/.../data/wear/):
 *  - "/tutunaku/auth"       (teléfono -> reloj): traspaso de sesión.
 *  - "/tutunaku/xp_gained"  (reloj -> teléfono): notificación de XP ganado.
 */
class WatchSyncManager(private val context: Context) {

    private val capabilityName get() = context.getString(R.string.wear_capability)
    private val dataClient by lazy { Wearable.getDataClient(context) }
    private val messageClient by lazy { Wearable.getMessageClient(context) }
    private val capabilityClient by lazy { Wearable.getCapabilityClient(context) }
    private val nodeClient by lazy { Wearable.getNodeClient(context) }

    private val _connectedWatchNode = MutableStateFlow(false)
    val connectedWatchNode: StateFlow<Boolean> = _connectedWatchNode

    private val capabilityListener = CapabilityClient.OnCapabilityChangedListener { info ->
        updateConnectionState(info)
    }

    /** Anuncia este dispositivo bajo la capability compartida. Llamar una vez al iniciar la app. */
    suspend fun registerCapability() {
        runCatching { capabilityClient.addLocalCapability(capabilityName).await() }
            .onFailure { Log.w(TAG, "No se pudo registrar la capability local", it) }
    }

    /** Empieza a observar si hay un reloj emparejado alcanzable. Llamar desde un DisposableEffect. */
    suspend fun startObservingConnection() {
        capabilityClient.addListener(capabilityListener, capabilityName)
        runCatching {
            val info = capabilityClient.getCapability(capabilityName, CapabilityClient.FILTER_REACHABLE).await()
            updateConnectionState(info)
        }.onFailure { Log.w(TAG, "No se pudo consultar la capability", it) }
    }

    fun stopObservingConnection() {
        capabilityClient.removeListener(capabilityListener, capabilityName)
    }

    private fun updateConnectionState(info: CapabilityInfo) {
        nodeClient.localNode.addOnSuccessListener { local ->
            _connectedWatchNode.value = info.nodes.any { it.id != local.id && it.isNearby }
        }.addOnFailureListener {
            _connectedWatchNode.value = info.nodes.isNotEmpty()
        }
    }

    /** Traspasa la sesión activa al reloj: no necesita volver a pedir login ahí. */
    suspend fun pushAuthToWatch(accessToken: String, refreshToken: String, username: String) {
        val request = PutDataMapRequest.create(PATH_AUTH).apply {
            dataMap.putString(KEY_ACCESS_TOKEN, accessToken)
            dataMap.putString(KEY_REFRESH_TOKEN, refreshToken)
            dataMap.putString(KEY_USERNAME, username)
            dataMap.putLong(KEY_PUSHED_AT, System.currentTimeMillis())
        }.asPutDataRequest().setUrgent()
        runCatching { dataClient.putDataItem(request).await() }
            .onFailure { Log.w(TAG, "No se pudo enviar la sesión al reloj", it) }
    }

    /** Cierra la sesión también en el reloj (tokens vacíos = señal de logout). */
    suspend fun clearAuthOnWatch() {
        val request = PutDataMapRequest.create(PATH_AUTH).apply {
            dataMap.putString(KEY_ACCESS_TOKEN, "")
            dataMap.putString(KEY_REFRESH_TOKEN, "")
            dataMap.putString(KEY_USERNAME, "")
            dataMap.putLong(KEY_PUSHED_AT, System.currentTimeMillis())
        }.asPutDataRequest().setUrgent()
        runCatching { dataClient.putDataItem(request).await() }
            .onFailure { Log.w(TAG, "No se pudo limpiar la sesión en el reloj", it) }
    }

    companion object {
        private const val TAG = "WatchSyncManager"
        const val PATH_AUTH = "/tutunaku/auth"
        const val KEY_ACCESS_TOKEN = "access_token"
        const val KEY_REFRESH_TOKEN = "refresh_token"
        const val KEY_USERNAME = "username"
        const val KEY_PUSHED_AT = "pushed_at"
    }
}
