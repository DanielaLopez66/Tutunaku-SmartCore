package mx.tutunaku.wearable.data.repository

import mx.tutunaku.wearable.data.model.UserStats
import mx.tutunaku.wearable.data.model.WordOfDay

class StatsRepository(private val authRepository: AuthRepository) {

    suspend fun getStats(): Result<UserStats> =
        authRepository.withAuthRetry { it.getMyStats() }

    suspend fun getWordOfDay(): Result<WordOfDay> =
        authRepository.withAuthRetry { it.getWordOfDay() }

    suspend fun earnHeart(): Result<UserStats> =
        authRepository.withAuthRetry { it.earnHeart() }
}
