package mx.tutunaku.wearable.data.wear

import com.google.android.gms.wearable.DataEventBuffer
import com.google.android.gms.wearable.DataMapItem
import com.google.android.gms.wearable.WearableListenerService
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import mx.tutunaku.wearable.TutunakuWearApp

/**
 * Recibe el traspaso de sesión desde el teléfono (ver
 * Deliverables/MobileApp/source/.../data/wear/WatchSyncManager.kt#pushAuthToWatch)
 * — evita tener que volver a pedir login en el reloj. Tokens vacíos en el
 * payload significan "el teléfono cerró sesión", así que también se
 * limpian aquí.
 */
class PhoneAuthListenerService : WearableListenerService() {

    override fun onDataChanged(events: DataEventBuffer) {
        val app = application as TutunakuWearApp
        for (event in events) {
            if (event.type != com.google.android.gms.wearable.DataEvent.TYPE_CHANGED) continue
            if (event.dataItem.uri.path != WatchSyncManager.PATH_AUTH) continue

            val map = DataMapItem.fromDataItem(event.dataItem).dataMap
            val accessToken = map.getString(WatchSyncManager.KEY_ACCESS_TOKEN).orEmpty()
            val refreshToken = map.getString(WatchSyncManager.KEY_REFRESH_TOKEN).orEmpty()

            CoroutineScope(Dispatchers.IO).launch {
                if (accessToken.isNotBlank() && refreshToken.isNotBlank()) {
                    app.tokenStore.saveTokens(accessToken, refreshToken)
                } else {
                    app.tokenStore.clearTokens()
                }
                app.authTokensUpdated.emit(Unit)
            }
        }
    }
}
