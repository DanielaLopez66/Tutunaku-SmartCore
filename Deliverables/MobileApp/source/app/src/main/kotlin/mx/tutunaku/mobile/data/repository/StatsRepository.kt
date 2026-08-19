package mx.tutunaku.mobile.data.repository

import mx.tutunaku.mobile.data.model.UserStats

class StatsRepository(private val authRepository: AuthRepository) {
    suspend fun getStats(): Result<UserStats> =
        authRepository.withAuthRetry { it.getMyStats() }
}
