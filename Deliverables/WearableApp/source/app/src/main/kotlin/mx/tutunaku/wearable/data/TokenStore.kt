package mx.tutunaku.wearable.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "tutunaku_wearable")

/**
 * Persistencia local de tokens JWT y de la URL del backend. Espejo, en
 * espíritu, de `authStore.ts` (Zustand + persist) del frontend web — pero
 * el wearable no comparte proceso ni almacenamiento con la web, así que
 * necesita su propia copia.
 */
class TokenStore(private val context: Context) {

    private object Keys {
        val ACCESS_TOKEN = stringPreferencesKey("access_token")
        val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
        val SERVER_URL = stringPreferencesKey("server_url")
        val SAVED_EMAIL = stringPreferencesKey("saved_email")
        val SAVED_PASSWORD = stringPreferencesKey("saved_password")
    }

    val accessToken: Flow<String?> = context.dataStore.data.map { it[Keys.ACCESS_TOKEN] }
    val refreshToken: Flow<String?> = context.dataStore.data.map { it[Keys.REFRESH_TOKEN] }

    /**
     * 10.0.2.2 es el alias del emulador de Android hacia el "localhost" de
     * la máquina anfitriona, donde corre `uvicorn app.main:socket_app`
     * durante desarrollo. En un reloj físico, cámbiala desde Ajustes por la
     * IP LAN de tu backend (ej. http://192.168.1.50:8000/).
     */
    val serverUrl: Flow<String> = context.dataStore.data.map {
        it[Keys.SERVER_URL] ?: DEFAULT_SERVER_URL
    }

    suspend fun saveTokens(access: String, refresh: String) {
        context.dataStore.edit { prefs ->
            prefs[Keys.ACCESS_TOKEN] = access
            prefs[Keys.REFRESH_TOKEN] = refresh
        }
    }

    suspend fun saveServerUrl(url: String) {
        context.dataStore.edit { prefs -> prefs[Keys.SERVER_URL] = url }
    }

    suspend fun currentServerUrl(): String = serverUrl.first()

    suspend fun isLoggedIn(): Boolean = accessToken.first() != null

    /**
     * Credenciales guardadas para auto-conectar sin pantalla de login: el
     * reloj se configura UNA vez desde Ajustes y desde entonces siempre
     * reintenta la sesión solo, igual que un smartwatch se re-vincula solo a
     * su cuenta. Igual que los tokens, se guardan sin cifrar en DataStore:
     * aceptable en un reloj de un solo usuario, no para un backend multiusuario.
     */
    suspend fun saveCredentials(email: String, password: String) {
        context.dataStore.edit { prefs ->
            prefs[Keys.SAVED_EMAIL] = email
            prefs[Keys.SAVED_PASSWORD] = password
        }
    }

    suspend fun savedCredentials(): Pair<String, String>? {
        val prefs = context.dataStore.data.first()
        val email = prefs[Keys.SAVED_EMAIL]
        val password = prefs[Keys.SAVED_PASSWORD]
        return if (email != null && password != null) email to password else null
    }

    /** Cierra sesión y olvida las credenciales guardadas (para no auto-reconectar). */
    suspend fun clearTokens() {
        context.dataStore.edit { prefs ->
            prefs.remove(Keys.ACCESS_TOKEN)
            prefs.remove(Keys.REFRESH_TOKEN)
            prefs.remove(Keys.SAVED_EMAIL)
            prefs.remove(Keys.SAVED_PASSWORD)
        }
    }

    companion object {
        const val DEFAULT_SERVER_URL = "http://10.0.2.2:8000/"
    }
}
