package mx.tutunaku.mobile.data.network

import mx.tutunaku.mobile.data.model.Course
import mx.tutunaku.mobile.data.model.CourseUnit
import mx.tutunaku.mobile.data.model.Exercise
import mx.tutunaku.mobile.data.model.ExerciseAttemptRequest
import mx.tutunaku.mobile.data.model.ExerciseAttemptResponse
import mx.tutunaku.mobile.data.model.Lesson
import mx.tutunaku.mobile.data.model.LoginRequest
import mx.tutunaku.mobile.data.model.RefreshRequest
import mx.tutunaku.mobile.data.model.RegisterRequest
import mx.tutunaku.mobile.data.model.StandardResponse
import mx.tutunaku.mobile.data.model.TokenResponse
import mx.tutunaku.mobile.data.model.UserStats
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path

/**
 * Endpoints reutilizados TAL CUAL del backend de Tutunaku
 * (Deliverables/WebApp/source/backend/app/routes/{auth,users,courses,units,lessons,exercises}.py).
 * Mismo backend que ya prueban la web y el reloj — ningún endpoint nuevo.
 */
interface ApiService {

    @POST("api/v1/auth/register")
    suspend fun register(@Body body: RegisterRequest): StandardResponse

    @POST("api/v1/auth/login")
    suspend fun login(@Body body: LoginRequest): TokenResponse

    @POST("api/v1/auth/refresh")
    suspend fun refresh(@Body body: RefreshRequest): TokenResponse

    @GET("api/v1/users/me/stats")
    suspend fun getMyStats(): UserStats

    @GET("api/v1/courses")
    suspend fun getCourses(): List<Course>

    @GET("api/v1/units/course/{courseId}")
    suspend fun getUnits(@Path("courseId") courseId: String): List<CourseUnit>

    @GET("api/v1/lessons/unit/{unitId}")
    suspend fun getLessons(@Path("unitId") unitId: String): List<Lesson>

    @GET("api/v1/lessons/{lessonId}")
    suspend fun getLesson(@Path("lessonId") lessonId: String): Lesson

    @POST("api/v1/lessons/{lessonId}/complete")
    suspend fun completeLesson(@Path("lessonId") lessonId: String): StandardResponse

    @GET("api/v1/exercises/lesson/{lessonId}")
    suspend fun getExercises(@Path("lessonId") lessonId: String): List<Exercise>

    @POST("api/v1/exercises/{exerciseId}/attempt")
    suspend fun submitAttempt(
        @Path("exerciseId") exerciseId: String,
        @Body body: ExerciseAttemptRequest,
    ): ExerciseAttemptResponse
}
