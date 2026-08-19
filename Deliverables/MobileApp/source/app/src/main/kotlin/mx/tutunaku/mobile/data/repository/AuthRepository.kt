package mx.tutunaku.mobile.data.repository

import kotlinx.coroutines.flow.first
import mx.tutunaku.mobile.data.TokenStore
import mx.tutunaku.mobile.data.model.LoginRequest
import mx.tutunaku.mobile.data.model.RefreshRequest
import mx.tutunaku.mobile.data.model.RegisterRequest
import mx.tutunaku.mobile.data.network.ApiClient
import mx.tutunaku.mobile.data.network.ApiService
import retrofit2.HttpException

/**
 * Maneja login/registro/logout/refresh y expone [withAuthRetry], usado por
 * el resto de los repositorios para reintentar UNA vez tras un 401
 * refrescando el access_token. Mismo patrón, verbatim, que
 * Deliverables/WearableApp/source/.../data/repository/AuthRepository.kt
 * (ya probado en esta sesión contra el mismo backend).
 */
class AuthRepository(private val tokenStore: TokenStore) {

    private suspend fun plainApi(): ApiService = ApiClient.buildPlain(tokenStore.currentServerUrl())
    private suspend fun authedApi(): ApiService = ApiClient.buildAuthed(tokenStore.currentServerUrl(), tokenStore)

    suspend fun isLoggedIn(): Boolean = tokenStore.isLoggedIn()

    suspend fun register(email: String, username: String, password: String, fullName: String?): Result<Unit> =
        runCatching {
            plainApi().register(RegisterRequest(email, username, password, fullName))
            Unit
        }

    suspend fun login(email: String, password: String): Result<Unit> = runCatching {
        val tokens = plainApi().login(LoginRequest(email, password))
        tokenStore.saveTokens(tokens.access_token, tokens.refresh_token)
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
