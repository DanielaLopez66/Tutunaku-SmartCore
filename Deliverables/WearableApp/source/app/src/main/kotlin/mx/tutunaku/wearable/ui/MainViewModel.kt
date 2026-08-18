package mx.tutunaku.wearable.ui

import android.app.Application
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.DefaultLifecycleObserver
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.ProcessLifecycleOwner
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import mx.tutunaku.wearable.TutunakuWearApp
import mx.tutunaku.wearable.data.model.NotificationDto
import mx.tutunaku.wearable.data.model.UserStats
import mx.tutunaku.wearable.data.model.WordOfDay

enum class AuthState { CHECKING, LOGGED_OUT, LOGGED_IN }

/** Estado de una petición asíncrona para poder mostrar carga/error/datos en pantalla. */
data class LoadState(val loading: Boolean = false, val error: String? = null)

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val app get() = getApplication<TutunakuWearApp>()

    private val _authState = MutableStateFlow(AuthState.CHECKING)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    private val _loginError = MutableStateFlow<String?>(null)
    val loginError: StateFlow<String?> = _loginError.asStateFlow()

    private val _loginLoading = MutableStateFlow(false)
    val loginLoading: StateFlow<Boolean> = _loginLoading.asStateFlow()

    private val _stats = MutableStateFlow<UserStats?>(null)
    val stats: StateFlow<UserStats?> = _stats.asStateFlow()
    private val _statsState = MutableStateFlow(LoadState())
    val statsState: StateFlow<LoadState> = _statsState.asStateFlow()

    private val _notifications = MutableStateFlow<List<NotificationDto>>(emptyList())
    val notifications: StateFlow<List<NotificationDto>> = _notifications.asStateFlow()
    private val _notificationsState = MutableStateFlow(LoadState())
    val notificationsState: StateFlow<LoadState> = _notificationsState.asStateFlow()

    private val _wordOfDay = MutableStateFlow<WordOfDay?>(null)
    val wordOfDay: StateFlow<WordOfDay?> = _wordOfDay.asStateFlow()
    private val _wordOfDayState = MutableStateFlow(LoadState())
    val wordOfDayState: StateFlow<LoadState> = _wordOfDayState.asStateFlow()

    val socketConnected: StateFlow<Boolean> = app.socketManager.connected
    val phoneConnected: StateFlow<Boolean> = app.watchSyncManager.connectedPhoneNode

    private var socketJob: Job? = null
    private var lastKnownXp: Int? = null

    /**
     * Desconecta el socket cuando la app entera pasa a segundo plano y lo
     * reconecta (+ refresca datos, por si algo llegó mientras tanto) al
     * volver a primer plano. Usa [ProcessLifecycleOwner] en vez del ciclo de
     * vida de [mx.tutunaku.wearable.MainActivity] porque solo debe reaccionar
     * a que la app deje de ser visible, no a la navegación interna entre
     * pantallas (cada `composable()` no es una Activity separada).
     */
    private val lifecycleObserver = object : DefaultLifecycleObserver {
        override fun onStart(owner: LifecycleOwner) {
            if (_authState.value == AuthState.LOGGED_IN) {
                connectSocket()
                refreshStats()
                refreshNotifications()
            }
        }

        override fun onStop(owner: LifecycleOwner) {
            socketJob?.cancel()
            app.socketManager.disconnect()
        }
    }

    init {
        app.socketManager.onStatsUpdated = { event ->
            _stats.value = _stats.value?.copy(
                xp_total = event.xp_total,
                level = event.level,
                hearts = event.hearts,
                current_streak = event.current_streak,
                longest_streak = event.longest_streak,
            ) ?: UserStats(
                xp_total = event.xp_total,
                level = event.level,
                hearts = event.hearts,
                current_streak = event.current_streak,
                longest_streak = event.longest_streak,
            )
            // Avisa al teléfono (Data Layer) cuando el XP sube — cubre el
            // minijuego del corazón actual y cualquier flujo de ejercicios
            // futuro en el reloj, sin acoplarse a una pantalla específica.
            val previous = lastKnownXp
            lastKnownXp = event.xp_total
            if (previous != null && event.xp_total > previous) {
                viewModelScope.launch {
                    app.watchSyncManager.sendXpGained(event.xp_total - previous)
                }
            }
        }
        app.socketManager.onNewNotification = { notif ->
            _notifications.value = listOf(notif) + _notifications.value
        }
        ProcessLifecycleOwner.get().lifecycle.addObserver(lifecycleObserver)

        viewModelScope.launch { app.watchSyncManager.registerCapability() }

        // Traspaso de sesión desde el teléfono (ver
        // data/wear/PhoneAuthListenerService.kt) — llega en cualquier
        // momento, no solo al arrancar, así que se colecciona igual que un
        // login normal en vez de consultarse una sola vez.
        viewModelScope.launch {
            app.authTokensUpdated.collect {
                if (app.authRepository.isLoggedIn()) {
                    _authState.value = AuthState.LOGGED_IN
                    onAuthenticated()
                } else {
                    socketJob?.cancel()
                    app.socketManager.disconnect()
                    _stats.value = null
                    _authState.value = AuthState.LOGGED_OUT
                }
            }
        }

        viewModelScope.launch {
            if (app.authRepository.isLoggedIn()) {
                _authState.value = AuthState.LOGGED_IN
                onAuthenticated()
            } else {
                // Sin pantalla de login: si ya se configuró una cuenta antes
                // desde Ajustes, el reloj se reconecta solo.
                app.authRepository.autoLogin()
                    .onSuccess {
                        _authState.value = AuthState.LOGGED_IN
                        onAuthenticated()
                    }
                    .onFailure {
                        _authState.value = AuthState.LOGGED_OUT
                    }
            }
        }
    }

    override fun onCleared() {
        ProcessLifecycleOwner.get().lifecycle.removeObserver(lifecycleObserver)
        super.onCleared()
    }

    fun login(email: String, password: String) {
        viewModelScope.launch {
            _loginLoading.value = true
            _loginError.value = null
            app.authRepository.login(email, password)
                .onSuccess {
                    _authState.value = AuthState.LOGGED_IN
                    onAuthenticated()
                }
                .onFailure {
                    _loginError.value = "No se pudo iniciar sesión. Revisa tus datos."
                }
            _loginLoading.value = false
        }
    }

    fun logout() {
        viewModelScope.launch {
            socketJob?.cancel()
            app.socketManager.disconnect()
            app.authRepository.logout()
            _stats.value = null
            _notifications.value = emptyList()
            _authState.value = AuthState.LOGGED_OUT
        }
    }

    private fun onAuthenticated() {
        refreshStats()
        refreshNotifications()
        refreshWordOfDay()
        connectSocket()
    }

    fun refreshStats() {
        viewModelScope.launch {
            _statsState.value = LoadState(loading = true)
            app.statsRepository.getStats()
                .onSuccess {
                    _stats.value = it
                    _statsState.value = LoadState()
                }
                .onFailure {
                    _statsState.value = LoadState(error = "No se pudieron cargar tus estadísticas.")
                }
        }
    }

    fun refreshNotifications() {
        viewModelScope.launch {
            _notificationsState.value = LoadState(loading = true)
            app.notificationsRepository.getNotifications()
                .onSuccess {
                    _notifications.value = it
                    _notificationsState.value = LoadState()
                }
                .onFailure {
                    _notificationsState.value = LoadState(error = "No se pudieron cargar tus notificaciones.")
                }
        }
    }

    fun refreshWordOfDay() {
        viewModelScope.launch {
            _wordOfDayState.value = LoadState(loading = true)
            app.statsRepository.getWordOfDay()
                .onSuccess {
                    _wordOfDay.value = it
                    _wordOfDayState.value = LoadState()
                }
                .onFailure {
                    _wordOfDayState.value = LoadState(error = "No se pudo cargar la palabra del día.")
                }
        }
    }

    fun markNotificationRead(id: String) {
        viewModelScope.launch {
            app.notificationsRepository.markRead(id).onSuccess {
                _notifications.value = _notifications.value.map {
                    if (it.id == id) it.copy(is_read = true) else it
                }
            }
        }
    }

    fun markAllNotificationsRead() {
        viewModelScope.launch {
            app.notificationsRepository.markAllRead().onSuccess {
                _notifications.value = _notifications.value.map { it.copy(is_read = true) }
            }
        }
    }

    /** Llamado por el minijuego del corazón al ganar. Devuelve true si el backend otorgó la vida. */
    suspend fun earnHeart(): Boolean {
        val result = app.statsRepository.earnHeart()
        result.onSuccess { _stats.value = it }
        return result.isSuccess
    }

    private fun connectSocket() {
        socketJob?.cancel()
        socketJob = viewModelScope.launch {
            val serverUrl = app.tokenStore.currentServerUrl()
            val accessToken = app.tokenStore.accessToken.first()
            if (accessToken != null) {
                app.socketManager.connect(serverUrl, accessToken)
            }
        }
    }
}
