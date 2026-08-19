package mx.tutunaku.wearable.data.network

import kotlinx.coroutines.runBlocking
import kotlinx.coroutines.flow.first
import kotlinx.serialization.json.Json
import mx.tutunaku.wearable.data.TokenStore
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.kotlinx.serialization.asConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Construye dos clientes Retrofit contra el MISMO backend:
 *  - [authed]: agrega el header Authorization en cada request (uso normal).
 *  - [plain]: sin header, usado únicamente para login/refresh (evita
 *    recursión: no tendría sentido adjuntar un token vencido para pedir uno
 *    nuevo). Mismo patrón que usa `frontend/src/utils/api.ts` con el
 *    `axios.post` directo en el interceptor de refresh.
 */
object ApiClient {

    private val json = Json {
        ignoreUnknownKeys = true
        coerceInputValues = true
        explicitNulls = false
    }

    fun buildAuthed(baseUrl: String, tokenStore: TokenStore): ApiService {
        val client = baseHttpClient()
            .addInterceptor { chain ->
                val token = runBlocking { tokenStore.accessToken.first() }
                val request = if (token != null) {
                    chain.request().newBuilder()
                        .addHeader("Authorization", "Bearer $token")
                        .build()
                } else {
                    chain.request()
                }
                chain.proceed(request)
            }
            .build()
        return retrofit(baseUrl, client)
    }

    fun buildPlain(baseUrl: String): ApiService {
        return retrofit(baseUrl, baseHttpClient().build())
    }

    private fun baseHttpClient(): OkHttpClient.Builder {
        val logging = HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BASIC
        }
        return OkHttpClient.Builder()
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .addInterceptor(logging)
    }

    private fun retrofit(baseUrl: String, client: OkHttpClient): ApiService {
        val contentType = "application/json".toMediaType()
        return Retrofit.Builder()
            .baseUrl(baseUrl)
            .client(client)
            .addConverterFactory(json.asConverterFactory(contentType))
            .build()
            .create(ApiService::class.java)
    }
}
