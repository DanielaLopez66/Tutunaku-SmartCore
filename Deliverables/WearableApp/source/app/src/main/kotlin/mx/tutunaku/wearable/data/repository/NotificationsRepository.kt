package mx.tutunaku.wearable.data.repository

import mx.tutunaku.wearable.data.model.NotificationDto

class NotificationsRepository(private val authRepository: AuthRepository) {

    suspend fun getNotifications(): Result<List<NotificationDto>> =
        authRepository.withAuthRetry { it.getNotifications() }

    suspend fun markRead(id: String): Result<Unit> =
        authRepository.withAuthRetry { it.markNotificationRead(id) }.map {}

    suspend fun markAllRead(): Result<Unit> =
        authRepository.withAuthRetry { it.markAllNotificationsRead() }.map {}
}
