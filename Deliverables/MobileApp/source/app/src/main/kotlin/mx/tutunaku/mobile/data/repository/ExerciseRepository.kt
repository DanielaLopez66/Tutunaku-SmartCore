package mx.tutunaku.mobile.data.repository

import mx.tutunaku.mobile.data.model.Exercise
import mx.tutunaku.mobile.data.model.ExerciseAttemptRequest
import mx.tutunaku.mobile.data.model.ExerciseAttemptResponse
import mx.tutunaku.mobile.data.model.StandardResponse

class ExerciseRepository(private val authRepository: AuthRepository) {
    suspend fun getExercises(lessonId: String): Result<List<Exercise>> =
        authRepository.withAuthRetry { it.getExercises(lessonId) }

    suspend fun submitAttempt(exerciseId: String, request: ExerciseAttemptRequest): Result<ExerciseAttemptResponse> =
        authRepository.withAuthRetry { it.submitAttempt(exerciseId, request) }

    suspend fun completeLesson(lessonId: String): Result<StandardResponse> =
        authRepository.withAuthRetry { it.completeLesson(lessonId) }
}
