package mx.tutunaku.mobile.data.repository

import mx.tutunaku.mobile.data.model.Course
import mx.tutunaku.mobile.data.model.CourseUnit
import mx.tutunaku.mobile.data.model.Lesson

class ContentRepository(private val authRepository: AuthRepository) {
    suspend fun getCourses(): Result<List<Course>> =
        authRepository.withAuthRetry { it.getCourses() }

    suspend fun getUnits(courseId: String): Result<List<CourseUnit>> =
        authRepository.withAuthRetry { it.getUnits(courseId) }

    suspend fun getLessons(unitId: String): Result<List<Lesson>> =
        authRepository.withAuthRetry { it.getLessons(unitId) }

    suspend fun getLesson(lessonId: String): Result<Lesson> =
        authRepository.withAuthRetry { it.getLesson(lessonId) }
}
