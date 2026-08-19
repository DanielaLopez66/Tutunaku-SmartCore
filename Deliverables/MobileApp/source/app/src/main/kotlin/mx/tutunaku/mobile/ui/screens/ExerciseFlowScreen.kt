package mx.tutunaku.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.FavoriteBorder
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import kotlinx.coroutines.launch
import mx.tutunaku.mobile.TutunakuMobileApp
import mx.tutunaku.mobile.data.model.Exercise
import mx.tutunaku.mobile.data.model.ExerciseAttemptRequest
import mx.tutunaku.mobile.data.model.ExerciseAttemptResponse
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.theme.AlebrijeCoral
import mx.tutunaku.mobile.ui.theme.AlebrijeGold
import mx.tutunaku.mobile.ui.theme.AlebrijeTeal
import mx.tutunaku.mobile.ui.theme.ErrorRed

@Composable
fun ExerciseFlowScreen(lessonId: String, viewModel: MainViewModel, onFinished: () -> Unit) {
    val app = LocalContext.current.applicationContext as TutunakuMobileApp
    val scope = rememberCoroutineScope()

    var exercises by remember { mutableStateOf<List<Exercise>>(emptyList()) }
    var loading by remember { mutableStateOf(true) }
    var loadError by remember { mutableStateOf<String?>(null) }

    var currentIndex by remember { mutableIntStateOf(0) }
    var answer by remember { mutableStateOf("") }
    var result by remember { mutableStateOf<ExerciseAttemptResponse?>(null) }
    var submitting by remember { mutableStateOf(false) }
    var submitError by remember { mutableStateOf<String?>(null) }
    var hearts by remember { mutableIntStateOf(5) }
    var totalXp by remember { mutableIntStateOf(0) }
    var finished by remember { mutableStateOf(false) }
    var startedAt by remember { mutableStateOf(System.currentTimeMillis()) }

    LaunchedEffect(lessonId) {
        loading = true
        app.exerciseRepository.getExercises(lessonId)
            .onSuccess { exercises = it; loadError = null }
            .onFailure { loadError = "No se pudieron cargar los ejercicios." }
        loading = false
    }

    if (loading) {
        Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background), verticalArrangement = Arrangement.Center, horizontalAlignment = Alignment.CenterHorizontally) {
            CircularProgressIndicator(color = AlebrijeTeal)
        }
        return
    }
    if (loadError != null || exercises.isEmpty()) {
        Column(Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(20.dp)) {
            Text(loadError ?: "Esta lección no tiene ejercicios todavía.", color = MaterialTheme.colorScheme.error)
            Spacer(Modifier.height(16.dp))
            Button(onClick = onFinished) { Text("Volver") }
        }
        return
    }

    if (finished) {
        Column(
            Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background).padding(24.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("🎉", style = MaterialTheme.typography.displayMedium)
            Spacer(Modifier.height(12.dp))
            Text("¡Lección completada!", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text("+$totalXp XP ganados · $hearts vidas restantes", style = MaterialTheme.typography.bodyLarge, color = AlebrijeGold)
            Spacer(Modifier.height(24.dp))
            Button(
                onClick = onFinished,
                modifier = Modifier.fillMaxWidth().height(52.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = AlebrijeTeal),
            ) { Text("Volver al inicio", fontWeight = FontWeight.Bold) }
        }
        return
    }

    val exercise = exercises[currentIndex]
    val progress = (currentIndex + (if (result != null) 1 else 0)).toFloat() / exercises.size

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(
            modifier = Modifier.fillMaxWidth().padding(12.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            IconButton(onClick = onFinished) { Icon(Icons.Filled.Close, contentDescription = "Salir") }
            LinearProgressIndicator(
                progress = { progress.coerceIn(0f, 1f) },
                modifier = Modifier.weight(1f).padding(horizontal = 8.dp).height(8.dp),
                color = AlebrijeCoral,
            )
            Row {
                repeat(5) { i ->
                    Icon(
                        imageVector = if (i < hearts) Icons.Filled.Favorite else Icons.Filled.FavoriteBorder,
                        contentDescription = null,
                        tint = ErrorRed,
                        modifier = Modifier.height(18.dp),
                    )
                }
            }
        }

        Column(modifier = Modifier.weight(1f).padding(20.dp)) {
            Text(
                exerciseTypeLabel(exercise.type),
                style = MaterialTheme.typography.labelMedium,
                color = AlebrijeTeal,
                fontWeight = FontWeight.Bold,
            )
            Spacer(Modifier.height(8.dp))

            if (exercise.image_url != null) {
                AsyncImage(
                    model = exercise.image_url,
                    contentDescription = null,
                    modifier = Modifier.fillMaxWidth().height(160.dp),
                )
                Spacer(Modifier.height(12.dp))
            }

            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(exercise.question, style = MaterialTheme.typography.headlineSmall, fontWeight = FontWeight.Bold, modifier = Modifier.weight(1f))
                if (exercise.audio_url != null) {
                    IconButton(onClick = { app.audioPlayer.play(exercise.audio_url) }) {
                        Icon(Icons.Filled.VolumeUp, contentDescription = "Reproducir", tint = AlebrijeTeal)
                    }
                }
            }

            if (exercise.hint != null) {
                Spacer(Modifier.height(4.dp))
                Text("💡 ${exercise.hint}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }

            Spacer(Modifier.height(20.dp))

            if (exercise.type == "multiple_choice" && !exercise.options.isNullOrEmpty()) {
                exercise.options.forEach { option ->
                    val selected = answer == option
                    OutlinedButton(
                        onClick = { if (result == null) answer = option },
                        modifier = Modifier.fillMaxWidth().padding(bottom = 8.dp),
                        shape = RoundedCornerShape(14.dp),
                        colors = ButtonDefaults.outlinedButtonColors(
                            containerColor = if (selected) AlebrijeCoral.copy(alpha = 0.12f) else Color.Transparent,
                        ),
                    ) { Text(option) }
                }
            } else {
                OutlinedTextField(
                    value = answer,
                    onValueChange = { if (result == null) answer = it },
                    label = { Text("Tu respuesta") },
                    modifier = Modifier.fillMaxWidth(),
                    shape = RoundedCornerShape(14.dp),
                    enabled = result == null,
                )
            }

            if (submitError != null) {
                Spacer(Modifier.height(12.dp))
                Text(submitError ?: "", color = MaterialTheme.colorScheme.error)
            }

            result?.let { r ->
                Spacer(Modifier.height(16.dp))
                val accent = if (r.is_correct) AlebrijeTeal else ErrorRed
                Card(
                    shape = RoundedCornerShape(16.dp),
                    colors = CardDefaults.cardColors(containerColor = accent.copy(alpha = 0.1f)),
                    modifier = Modifier.fillMaxWidth(),
                ) {
                    Column(Modifier.padding(16.dp)) {
                        Text(
                            if (r.is_correct) "¡Correcto! 🎉" else "No es correcto",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            color = accent,
                        )
                        if (!r.is_correct && r.correct_answer != null) {
                            Spacer(Modifier.height(4.dp))
                            Text("Respuesta correcta: ${r.correct_answer}", style = MaterialTheme.typography.bodyMedium)
                        }
                        if (r.explanation != null) {
                            Spacer(Modifier.height(4.dp))
                            Text(r.explanation, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Spacer(Modifier.height(6.dp))
                        Text("+${r.xp_earned} XP", style = MaterialTheme.typography.labelLarge, color = AlebrijeGold, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }

        Button(
            onClick = {
                if (result == null) {
                    submitting = true
                    submitError = null
                    val elapsed = ((System.currentTimeMillis() - startedAt) / 1000).toInt()
                    scope.launch {
                        app.exerciseRepository.submitAttempt(
                            exercise.id,
                            ExerciseAttemptRequest(user_answer = answer, time_spent_seconds = elapsed),
                        ).onSuccess { response ->
                            result = response
                            hearts = response.hearts_remaining
                            totalXp += response.xp_earned
                            response.user_stats?.let {
                                viewModel.applyPartialStats(it.xp_total, it.level, it.current_streak, response.hearts_remaining)
                            }
                        }.onFailure {
                            submitError = if (hearts <= 0) "Sin vidas restantes. Vuelve más tarde." else "No se pudo enviar tu respuesta."
                        }
                        submitting = false
                    }
                } else {
                    if (currentIndex < exercises.size - 1) {
                        currentIndex += 1
                        answer = ""
                        result = null
                        startedAt = System.currentTimeMillis()
                    } else {
                        scope.launch {
                            app.exerciseRepository.completeLesson(lessonId)
                            finished = true
                        }
                    }
                }
            },
            enabled = !submitting && (result != null || answer.isNotBlank()) && hearts > 0,
            modifier = Modifier.fillMaxWidth().padding(20.dp).height(52.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.buttonColors(containerColor = AlebrijeCoral),
        ) {
            if (submitting) {
                CircularProgressIndicator(modifier = Modifier.height(22.dp), color = Color.White, strokeWidth = 2.dp)
            } else {
                Text(if (result == null) "Comprobar" else "Continuar", fontWeight = FontWeight.Bold)
            }
        }
    }
}

/** Mismas etiquetas que frontend/src/pages/ExercisePage.tsx para el tipo de ejercicio. */
private fun exerciseTypeLabel(type: String): String = when (type) {
    "translation" -> "Traducción"
    "multiple_choice" -> "Selección múltiple"
    "writing" -> "Escritura"
    else -> "Audio"
}
