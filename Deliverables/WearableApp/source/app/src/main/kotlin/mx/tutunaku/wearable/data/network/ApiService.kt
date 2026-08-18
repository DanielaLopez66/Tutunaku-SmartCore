package mx.tutunaku.wearable.data.network

import mx.tutunaku.wearable.data.model.LoginRequest
import mx.tutunaku.wearable.data.model.NotificationDto
import mx.tutunaku.wearable.data.model.RefreshRequest
import mx.tutunaku.wearable.data.model.StandardResponse
import mx.tutunaku.wearable.data.model.TokenResponse
import mx.tutunaku.wearable.data.model.UserStats
import mx.tutunaku.wearable.data.model.WordOfDay
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path

/**
 * Endpoints reutilizados TAL CUAL del backend de Tutunaku
 * (Deliverables/WebApp/source/backend/app/routes/{auth,users,notifications,exercises}.py).
 * No se creó ningún backend nuevo para el wearable.
 */
interface ApiService {

    @POST("api/v1/auth/login")
    suspend fun login(@Body body: LoginRequest): TokenResponse

    @POST("api/v1/auth/refresh")
    suspend fun refresh(@Body body: RefreshRequest): TokenResponse

    @GET("api/v1/users/me/stats")
    suspend fun getMyStats(): UserStats

    @GET("api/v1/notifications")
    suspend fun getNotifications(): List<NotificationDto>

    @PATCH("api/v1/notifications/{id}/read")
    suspend fun markNotificationRead(@Path("id") id: String): StandardResponse

    @PATCH("api/v1/notifications/read-all")
    suspend fun markAllNotificationsRead(): StandardResponse

    @GET("api/v1/exercises/word-of-day")
    suspend fun getWordOfDay(): WordOfDay

    @POST("api/v1/users/me/hearts/earn")
    suspend fun earnHeart(): UserStats
}
