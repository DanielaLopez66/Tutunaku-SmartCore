package mx.tutunaku.wearable.data.model

import kotlinx.serialization.Serializable

/**
 * Espejo de los esquemas Pydantic del backend
 * (Deliverables/WebApp/source/backend/app/schemas/schemas.py), mismos
 * nombres de campo para evitar cualquier ambigüedad de mapeo.
 */

@Serializable
data class LoginRequest(val email: String, val password: String)

@Serializable
data class RefreshRequest(val refresh_token: String)

@Serializable
data class TokenResponse(
    val access_token: String,
    val refresh_token: String,
    val token_type: String = "bearer",
    val expires_in: Int = 0,
)

@Serializable
data class UserStats(
    val xp_total: Int = 0,
    val level: Int = 1,
    val hearts: Int = 5,
    val current_streak: Int = 0,
    val longest_streak: Int = 0,
    val lessons_completed: Int = 0,
    val exercises_correct: Int = 0,
    val exercises_total: Int = 0,
    val accuracy_percentage: Double = 0.0,
    val achievements_count: Int = 0,
    val last_heart_refill: String? = null,
)

@Serializable
data class NotificationDto(
    val id: String,
    val type: String,
    val title: String,
    val message: String? = null,
    val icon_emoji: String? = null,
    val is_read: Boolean = false,
    val action_url: String? = null,
    val created_at: String,
)

@Serializable
data class WordOfDay(
    val word: String,
    val translation: String,
    val hint: String? = null,
    val audio_url: String? = null,
    val date: String,
)

@Serializable
data class StandardResponse(
    val success: Boolean = true,
    val message: String? = null,
)

/** Evento en vivo `user_stats_updated` recibido por Socket.IO. */
@Serializable
data class UserStatsUpdatedEvent(
    val xp_total: Int,
    val level: Int,
    val hearts: Int,
    val current_streak: Int,
    val longest_streak: Int,
    val timestamp: String,
)
