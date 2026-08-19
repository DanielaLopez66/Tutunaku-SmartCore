package mx.tutunaku.mobile.data.wear

import android.Manifest
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.app.ActivityCompat
import androidx.core.app.NotificationCompat
import androidx.core.app.NotificationManagerCompat
import com.google.android.gms.wearable.MessageEvent
import com.google.android.gms.wearable.WearableListenerService
import mx.tutunaku.mobile.R

/**
 * Recibe mensajes del reloj vía la Wearable Data Layer API. Hoy solo
 * escucha "/tutunaku/xp_gained" (ver
 * Deliverables/WearableApp/source/.../ui/MainViewModel.kt, enganchado al
 * callback onStatsUpdated ya existente) y muestra una notificación local —
 * esto es un complemento de UX inmediata en el mismo dispositivo; los
 * datos "de verdad" ya llegan igual por el socket propio del teléfono en
 * cuanto hay conexión a internet.
 */
class WatchMessageListenerService : WearableListenerService() {

    override fun onMessageReceived(event: MessageEvent) {
        if (event.path != PATH_XP_GAINED) return
        val xp = String(event.data).toIntOrNull() ?: return
        showXpNotification(xp)
    }

    private fun showXpNotification(xp: Int) {
        ensureChannel()
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setContentTitle("¡Ganaste XP en el reloj!")
            .setContentText("+$xp XP — sigue así 🔥")
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .build()

        if (Build.VERSION.SDK_INT >= 33 &&
            ActivityCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED
        ) {
            return
        }
        NotificationManagerCompat.from(this).notify(NOTIFICATION_ID, notification)
    }

    private fun ensureChannel() {
        if (Build.VERSION.SDK_INT < 26) return
        val manager = getSystemService(NotificationManager::class.java)
        val channel = NotificationChannel(
            CHANNEL_ID,
            "Sincronización con el reloj",
            NotificationManager.IMPORTANCE_DEFAULT,
        )
        manager.createNotificationChannel(channel)
    }

    companion object {
        const val PATH_XP_GAINED = "/tutunaku/xp_gained"
        private const val CHANNEL_ID = "watch_sync"
        private const val NOTIFICATION_ID = 1001
    }
}
