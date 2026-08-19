package mx.tutunaku.mobile.data.model

import kotlinx.serialization.Serializable

/**
 * Espejo de los esquemas Pydantic del backend
 * (Deliverables/WebApp/source/backend/app/schemas/schemas.py), mismos
 * nombres de campo para evitar cualquier ambigüedad de mapeo. Los tipos
 * de auth/stats son idénticos a los ya probados en
 * Deliverables/WearableApp/source/.../data/model/Models.kt.
 */

@Serializable
data class LoginRequest(val email: String, val password: String)

@Serializable
data class RegisterRequest(
    val email: String,
    val username: String,
    val password: String,
    val full_name: String? = null,
)

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
data class StandardResponse(
    val success: Boolean = true,
    val message: String? = null,
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

@Serializable
data class Course(
    val id: String,
    val title: String,
    val description: String? = null,
    val cover_image_url: String? = null,
    val color_hex: String? = null,
    val difficulty: String? = null,
    val is_published: Boolean = true,
    val order_index: Int = 0,
    val units_count: Int = 0,
)

/**
 * El backend llama a este recurso "Unit", pero esa palabra choca con
 * `kotlin.Unit` — se renombra a CourseUnit únicamente del lado Kotlin.
 */
@Serializable
data class CourseUnit(
    val id: String,
    val course_id: String,
    val title: String,
    val description: String? = null,
    val icon_emoji: String? = null,
    val color_hex: String? = null,
    val order_index: Int = 0,
    val is_locked: Boolean = false,
    val xp_reward: Int = 0,
    val lessons_count: Int = 0,
)

@Serializable
data class ContentBlock(
    val type: String,
    val content: String,
    val language: String? = null,
    val caption: String? = null,
    val pronunciation: String? = null,
    val example_sentence: String? = null,
    val audio_url: String? = null,
)

@Serializable
data class Lesson(
    val id: String,
    val unit_id: String,
    val title: String,
    val description: String? = null,
    val order_index: Int = 0,
    val xp_reward: Int = 0,
    val content_type: String? = null,
    val content_data: List<ContentBlock>? = null,
    val is_published: Boolean = true,
    val exercises_count: Int = 0,
)

@Serializable
data class Exercise(
    val id: String,
    val lesson_id: String,
    val type: String,
    val question: String,
    val options: List<String>? = null,
    val hint: String? = null,
    val image_url: String? = null,
    val audio_url: String? = null,
    val xp_reward: Int = 0,
    val order_index: Int = 0,
)

@Serializable
data class ExerciseAttemptRequest(
    val user_answer: String,
    val time_spent_seconds: Int? = null,
)

/** Sub-objeto parcial que manda el backend junto al resultado del intento. */
@Serializable
data class ExerciseUserStatsPartial(
    val xp_total: Int,
    val level: Int,
    val current_streak: Int,
)

@Serializable
data class ExerciseAttemptResponse(
    val is_correct: Boolean,
    val correct_answer: String? = null,
    val explanation: String? = null,
    val xp_earned: Int = 0,
    val hearts_remaining: Int = 0,
    val user_stats: ExerciseUserStatsPartial? = null,
)
