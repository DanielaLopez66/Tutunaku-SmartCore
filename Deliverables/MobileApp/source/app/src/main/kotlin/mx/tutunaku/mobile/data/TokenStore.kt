package mx.tutunaku.mobile.data

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore(name = "tutunaku_mobile")

/**
 * Persistencia local de tokens JWT y de la URL del backend. Mismo patrón
 * que Deliverables/WearableApp/source/.../data/TokenStore.kt, pero SIN
 * guardar credenciales en texto plano: aquello era un hack solo para un
 * reloj sin teclado que necesita auto-reconectar; el teléfono tiene una
 * pantalla de login real y no debe replicar ese atajo.
 */
class TokenStore(private val context: Context) {

    private object Keys {
        val ACCESS_TOKEN = stringPreferencesKey("access_token")
        val REFRESH_TOKEN = stringPreferencesKey("refresh_token")
        val SERVER_URL = stringPreferencesKey("server_url")
    }

    val accessToken: Flow<String?> = context.dataStore.data.map { it[Keys.ACCESS_TOKEN] }
    val refreshToken: Flow<String?> = context.dataStore.data.map { it[Keys.REFRESH_TOKEN] }

    /**
     * 10.0.2.2 es el alias del emulador de Android hacia el "localhost" de
     * la máquina anfitriona. En un teléfono físico, cámbiala desde la
     * pantalla de Perfil por la IP LAN de tu backend o la URL del túnel
     * (ej. https://tu-tunel.trycloudflare.com/).
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

    suspend fun clearTokens() {
        context.dataStore.edit { prefs ->
            prefs.remove(Keys.ACCESS_TOKEN)
            prefs.remove(Keys.REFRESH_TOKEN)
        }
    }

    companion object {
        const val DEFAULT_SERVER_URL = "http://10.0.2.2:8000/"
    }
}
