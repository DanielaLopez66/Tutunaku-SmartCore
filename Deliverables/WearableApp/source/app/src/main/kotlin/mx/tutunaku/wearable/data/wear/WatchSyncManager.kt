package mx.tutunaku.wearable.data.wear

import android.content.Context
import android.util.Log
import com.google.android.gms.wearable.CapabilityClient
import com.google.android.gms.wearable.CapabilityInfo
import com.google.android.gms.wearable.Wearable
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.tasks.await
import mx.tutunaku.wearable.R

/**
 * Emparejamiento reloj↔teléfono vía la Wearable Data Layer API — misma
 * capability compartida y mismos paths que
 * Deliverables/MobileApp/source/.../data/wear/WatchSyncManager.kt (no hay
 * módulo Gradle compartido entre los dos proyectos independientes, así que
 * los strings deben coincidir literal).
 */
class WatchSyncManager(private val context: Context) {

    private val capabilityName get() = context.getString(R.string.wear_capability)
    private val messageClient by lazy { Wearable.getMessageClient(context) }
    private val capabilityClient by lazy { Wearable.getCapabilityClient(context) }
    private val nodeClient by lazy { Wearable.getNodeClient(context) }

    private val _connectedPhoneNode = MutableStateFlow(false)
    val connectedPhoneNode: StateFlow<Boolean> = _connectedPhoneNode

    private val capabilityListener = CapabilityClient.OnCapabilityChangedListener { info ->
        updateConnectionState(info)
    }

    suspend fun registerCapability() {
        runCatching { capabilityClient.addLocalCapability(capabilityName).await() }
            .onFailure { Log.w(TAG, "No se pudo registrar la capability local", it) }
    }

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
            _connectedPhoneNode.value = info.nodes.any { it.id != local.id && it.isNearby }
        }.addOnFailureListener {
            _connectedPhoneNode.value = info.nodes.isNotEmpty()
        }
    }

    /** Avisa al teléfono que se ganó XP (ver ui/MainViewModel.kt, enganchado a onStatsUpdated). */
    suspend fun sendXpGained(xp: Int) {
        runCatching {
            val nodes = capabilityClient.getCapability(capabilityName, CapabilityClient.FILTER_REACHABLE).await().nodes
            val local = runCatching { nodeClient.localNode.await() }.getOrNull()
            nodes.filter { it.id != local?.id }.forEach { node ->
                messageClient.sendMessage(node.id, PATH_XP_GAINED, xp.toString().toByteArray()).await()
            }
        }.onFailure { Log.w(TAG, "No se pudo notificar XP al teléfono", it) }
    }

    companion object {
        private const val TAG = "WatchSyncManager"
        const val PATH_XP_GAINED = "/tutunaku/xp_gained"

        // Recibidos (no enviados) por PhoneAuthListenerService.kt — mismos
        // literales que Deliverables/MobileApp/source/.../WatchSyncManager.kt.
        const val PATH_AUTH = "/tutunaku/auth"
        const val KEY_ACCESS_TOKEN = "access_token"
        const val KEY_REFRESH_TOKEN = "refresh_token"
        const val KEY_USERNAME = "username"
    }
}
