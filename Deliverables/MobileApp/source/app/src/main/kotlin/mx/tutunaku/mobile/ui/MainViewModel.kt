package mx.tutunaku.mobile.ui

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
import mx.tutunaku.mobile.TutunakuMobileApp
import mx.tutunaku.mobile.data.model.UserStats

enum class AuthState { CHECKING, LOGGED_OUT, LOGGED_IN }

/** Estado de una petición asíncrona para poder mostrar carga/error/datos en pantalla. */
data class LoadState(val loading: Boolean = false, val error: String? = null)

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private val app get() = getApplication<TutunakuMobileApp>()

    private val _authState = MutableStateFlow(AuthState.CHECKING)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    private val _loginError = MutableStateFlow<String?>(null)
    val loginError: StateFlow<String?> = _loginError.asStateFlow()
    private val _loginLoading = MutableStateFlow(false)
    val loginLoading: StateFlow<Boolean> = _loginLoading.asStateFlow()

    private val _registerError = MutableStateFlow<String?>(null)
    val registerError: StateFlow<String?> = _registerError.asStateFlow()
    private val _registerLoading = MutableStateFlow(false)
    val registerLoading: StateFlow<Boolean> = _registerLoading.asStateFlow()
    private val _registerSuccess = MutableStateFlow(false)
    val registerSuccess: StateFlow<Boolean> = _registerSuccess.asStateFlow()

    private val _stats = MutableStateFlow<UserStats?>(null)
    val stats: StateFlow<UserStats?> = _stats.asStateFlow()
    private val _statsState = MutableStateFlow(LoadState())
    val statsState: StateFlow<LoadState> = _statsState.asStateFlow()

    private var loggedInEmail: String? = null

    val socketConnected: StateFlow<Boolean> = app.socketManager.connected
    val watchConnected: StateFlow<Boolean> = app.watchSyncManager.connectedWatchNode

    private var socketJob: Job? = null

    /**
     * Desconecta el socket cuando la app entera pasa a segundo plano y lo
     * reconecta al volver a primer plano — mismo patrón que
     * Deliverables/WearableApp/source/.../ui/MainViewModel.kt, usando
     * ProcessLifecycleOwner en vez del ciclo de vida de una sola Activity.
     */
    private val lifecycleObserver = object : DefaultLifecycleObserver {
        override fun onStart(owner: LifecycleOwner) {
            if (_authState.value == AuthState.LOGGED_IN) {
                connectSocket()
                refreshStats()
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
        }
        ProcessLifecycleOwner.get().lifecycle.addObserver(lifecycleObserver)

        viewModelScope.launch { app.watchSyncManager.registerCapability() }

        viewModelScope.launch {
            if (app.authRepository.isLoggedIn()) {
                _authState.value = AuthState.LOGGED_IN
                onAuthenticated()
            } else {
                _authState.value = AuthState.LOGGED_OUT
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
                    loggedInEmail = email
                    _authState.value = AuthState.LOGGED_IN
                    onAuthenticated()
                }
                .onFailure {
                    _loginError.value = "No se pudo iniciar sesión. Revisa tu email y contraseña."
                }
            _loginLoading.value = false
        }
    }

    fun register(email: String, username: String, password: String, fullName: String?) {
        viewModelScope.launch {
            _registerLoading.value = true
            _registerError.value = null
            app.authRepository.register(email, username, password, fullName)
                .onSuccess { _registerSuccess.value = true }
                .onFailure {
                    _registerError.value = "No se pudo completar el registro. Revisa tus datos."
                }
            _registerLoading.value = false
        }
    }

    fun resetRegisterSuccess() {
        _registerSuccess.value = false
    }

    fun logout() {
        viewModelScope.launch {
            socketJob?.cancel()
            app.socketManager.disconnect()
            app.authRepository.logout()
            app.watchSyncManager.clearAuthOnWatch()
            _stats.value = null
            loggedInEmail = null
            _authState.value = AuthState.LOGGED_OUT
        }
    }

    private fun onAuthenticated() {
        refreshStats()
        connectSocket()
        viewModelScope.launch {
            val access = app.tokenStore.accessToken.first()
            val refresh = app.tokenStore.refreshToken.first()
            if (access != null && refresh != null) {
                // El email es lo único que tenemos a mano en este punto sin
                // una llamada extra de perfil — suficiente como identificador
                // legible en la pantalla de Ajustes del reloj.
                app.watchSyncManager.pushAuthToWatch(access, refresh, loggedInEmail ?: "")
            }
        }
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

    /** Actualiza el cache local de stats sin refetch, tras un intento de ejercicio exitoso. */
    fun applyPartialStats(xpTotal: Int, level: Int, currentStreak: Int, hearts: Int) {
        _stats.value = _stats.value?.copy(
            xp_total = xpTotal,
            level = level,
            current_streak = currentStreak,
            hearts = hearts,
        )
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
