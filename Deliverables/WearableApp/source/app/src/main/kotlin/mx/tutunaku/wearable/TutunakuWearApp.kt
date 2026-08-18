package mx.tutunaku.wearable

import android.app.Application
import kotlinx.coroutines.flow.MutableSharedFlow
import mx.tutunaku.wearable.data.TokenStore
import mx.tutunaku.wearable.data.network.SocketManager
import mx.tutunaku.wearable.data.repository.AuthRepository
import mx.tutunaku.wearable.data.repository.NotificationsRepository
import mx.tutunaku.wearable.data.repository.StatsRepository
import mx.tutunaku.wearable.data.wear.WatchSyncManager

/**
 * Contenedor de dependencias manual y simple (sin Hilt/Dagger a propósito,
 * para minimizar piezas móviles en un proyecto nuevo). Todo se construye una
 * sola vez y se reutiliza durante la vida de la app.
 */
class TutunakuWearApp : Application() {

    lateinit var tokenStore: TokenStore
        private set
    lateinit var authRepository: AuthRepository
        private set
    lateinit var statsRepository: StatsRepository
        private set
    lateinit var notificationsRepository: NotificationsRepository
        private set
    lateinit var socketManager: SocketManager
        private set
    lateinit var watchSyncManager: WatchSyncManager
        private set

    /** Emite cuando PhoneAuthListenerService recibe una sesión nueva (o su limpieza) del teléfono. */
    val authTokensUpdated = MutableSharedFlow<Unit>(extraBufferCapacity = 1)

    override fun onCreate() {
        super.onCreate()
        tokenStore = TokenStore(this)
        authRepository = AuthRepository(tokenStore)
        statsRepository = StatsRepository(authRepository)
        notificationsRepository = NotificationsRepository(authRepository)
        socketManager = SocketManager()
        watchSyncManager = WatchSyncManager(this)
    }
}
