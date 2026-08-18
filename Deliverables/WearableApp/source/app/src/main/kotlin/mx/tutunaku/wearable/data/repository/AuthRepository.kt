package mx.tutunaku.wearable.data.repository

import kotlinx.coroutines.flow.first
import mx.tutunaku.wearable.data.TokenStore
import mx.tutunaku.wearable.data.model.LoginRequest
import mx.tutunaku.wearable.data.model.RefreshRequest
import mx.tutunaku.wearable.data.network.ApiClient
import mx.tutunaku.wearable.data.network.ApiService
import retrofit2.HttpException

/**
 * Maneja login/logout/refresh y expone [withAuthRetry], usado por el resto
 * de los repositorios para reintentar UNA vez tras un 401 refrescando el
 * access_token (mismo patrón que el interceptor de respuesta de
 * `frontend/src/utils/api.ts`, adaptado a corrutinas de Kotlin).
 */
class AuthRepository(private val tokenStore: TokenStore) {

    private suspend fun plainApi(): ApiService = ApiClient.buildPlain(tokenStore.currentServerUrl())
    private suspend fun authedApi(): ApiService = ApiClient.buildAuthed(tokenStore.currentServerUrl(), tokenStore)

    suspend fun isLoggedIn(): Boolean = tokenStore.isLoggedIn()

    suspend fun login(email: String, password: String): Result<Unit> = runCatching {
        val tokens = plainApi().login(LoginRequest(email, password))
        tokenStore.saveTokens(tokens.access_token, tokens.refresh_token)
        tokenStore.saveCredentials(email, password)
    }

    /** Reintenta el login con las credenciales guardadas (sin pantalla de login). */
    suspend fun autoLogin(): Result<Unit> {
        val (email, password) = tokenStore.savedCredentials() ?: return Result.failure(IllegalStateException("no_credentials"))
        return login(email, password)
    }

    suspend fun logout() {
        tokenStore.clearTokens()
    }

    suspend fun refresh(): Boolean {
        val refreshToken = tokenStore.refreshToken.first() ?: return false
        return runCatching {
            val tokens = plainApi().refresh(RefreshRequest(refreshToken))
            tokenStore.saveTokens(tokens.access_token, tokens.refresh_token)
        }.isSuccess
    }

    /** Ejecuta [block] con la API autenticada; si responde 401, refresca una vez y reintenta. */
    suspend fun <T> withAuthRetry(block: suspend (ApiService) -> T): Result<T> = runCatching {
        val api = authedApi()
        try {
            block(api)
        } catch (e: HttpException) {
            if (e.code() == 401 && refresh()) {
                block(authedApi())
            } else {
                throw e
            }
        }
    }
}
