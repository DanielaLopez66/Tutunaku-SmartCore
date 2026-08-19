package mx.tutunaku.mobile

import android.app.Application
import mx.tutunaku.mobile.data.TokenStore
import mx.tutunaku.mobile.data.audio.AudioPlayer
import mx.tutunaku.mobile.data.network.SocketManager
import mx.tutunaku.mobile.data.repository.AuthRepository
import mx.tutunaku.mobile.data.repository.ContentRepository
import mx.tutunaku.mobile.data.repository.ExerciseRepository
import mx.tutunaku.mobile.data.repository.StatsRepository
import mx.tutunaku.mobile.data.wear.WatchSyncManager

/**
 * Contenedor de dependencias manual y simple (sin Hilt/Dagger a propósito,
 * mismo criterio que Deliverables/WearableApp/source/.../TutunakuWearApp.kt).
 * Todo se construye una sola vez y se reutiliza durante la vida de la app.
 */
class TutunakuMobileApp : Application() {

    lateinit var tokenStore: TokenStore
        private set
    lateinit var authRepository: AuthRepository
        private set
    lateinit var statsRepository: StatsRepository
        private set
    lateinit var contentRepository: ContentRepository
        private set
    lateinit var exerciseRepository: ExerciseRepository
        private set
    lateinit var socketManager: SocketManager
        private set
    lateinit var watchSyncManager: WatchSyncManager
        private set
    lateinit var audioPlayer: AudioPlayer
        private set

    override fun onCreate() {
        super.onCreate()
        tokenStore = TokenStore(this)
        authRepository = AuthRepository(tokenStore)
        statsRepository = StatsRepository(authRepository)
        contentRepository = ContentRepository(authRepository)
        exerciseRepository = ExerciseRepository(authRepository)
        socketManager = SocketManager()
        watchSyncManager = WatchSyncManager(this)
        audioPlayer = AudioPlayer()
    }
}
