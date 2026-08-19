package mx.tutunaku.mobile.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.VolumeUp
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import coil.compose.AsyncImage
import mx.tutunaku.mobile.TutunakuMobileApp
import mx.tutunaku.mobile.data.model.ContentBlock
import mx.tutunaku.mobile.data.model.Lesson
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.theme.AlebrijeCoral
import mx.tutunaku.mobile.ui.theme.AlebrijeTeal

@Composable
fun LessonDetailScreen(
    lessonId: String,
    viewModel: MainViewModel,
    onStartExercises: () -> Unit,
    onBack: () -> Unit,
) {
    val app = LocalContext.current.applicationContext as TutunakuMobileApp
    var lesson by remember { mutableStateOf<Lesson?>(null) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(lessonId) {
        loading = true
        app.contentRepository.getLesson(lessonId)
            .onSuccess { lesson = it; error = null }
            .onFailure { error = "No se pudo cargar la lección." }
        loading = false
    }

    Column(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        Row(modifier = Modifier.padding(8.dp), verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = onBack) { Icon(Icons.Filled.ArrowBack, contentDescription = "Volver") }
            Text("Lección", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
        }

        when {
            loading -> Row(Modifier.fillMaxWidth().padding(32.dp)) { CircularProgressIndicator(color = AlebrijeTeal) }
            error != null -> Text(error ?: "", color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(20.dp))
            lesson != null -> {
                val current = lesson!!
                LazyColumn(
                    modifier = Modifier.weight(1f),
                    contentPadding = PaddingValues(20.dp),
                ) {
                    item {
                        Text(current.title, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                        if (current.description != null) {
                            Spacer(Modifier.height(4.dp))
                            Text(current.description, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Spacer(Modifier.height(6.dp))
                        Text(
                            "+${current.xp_reward} XP · ${current.exercises_count} ejercicios",
                            style = MaterialTheme.typography.labelMedium,
                            color = AlebrijeCoral,
                            fontWeight = FontWeight.Bold,
                        )
                        Spacer(Modifier.height(16.dp))
                    }
                    items(current.content_data ?: emptyList()) { block ->
                        ContentBlockItem(block = block, audioPlayer = app.audioPlayer)
                        Spacer(Modifier.height(12.dp))
                    }
                }

                val hasExercises = current.exercises_count > 0
                Column(modifier = Modifier.padding(horizontal = 20.dp, vertical = 8.dp)) {
                    Button(
                        onClick = onStartExercises,
                        modifier = Modifier.fillMaxWidth().height(52.dp),
                        shape = RoundedCornerShape(16.dp),
                        colors = ButtonDefaults.buttonColors(containerColor = AlebrijeCoral),
                        enabled = hasExercises,
                    ) {
                        Text(
                            if (hasExercises) "¡Comenzar ejercicios!" else "Sin ejercicios todavía",
                            fontWeight = FontWeight.Bold,
                        )
                    }
                    if (!hasExercises) {
                        Text(
                            "Esta lección aún no tiene ejercicios de práctica — vuelve a intentarlo más tarde.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier.padding(top = 8.dp),
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun ContentBlockItem(block: ContentBlock, audioPlayer: mx.tutunaku.mobile.data.audio.AudioPlayer) {
    val context = LocalContext.current
    when (block.type) {
        "example" -> {
            val isToto = block.language == "toto"
            val accent = if (isToto) AlebrijeCoral else AlebrijeTeal
            Card(
                shape = RoundedCornerShape(16.dp),
                colors = CardDefaults.cardColors(containerColor = accent.copy(alpha = 0.08f)),
                modifier = Modifier.fillMaxWidth(),
            ) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Column(modifier = Modifier.weight(1f)) {
                        Text(block.content, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = accent)
                        if (block.pronunciation != null) {
                            Text("[${block.pronunciation}]", style = MaterialTheme.typography.bodySmall, fontStyle = FontStyle.Italic)
                        }
                        if (block.example_sentence != null) {
                            Spacer(Modifier.height(4.dp))
                            Text(block.example_sentence, style = MaterialTheme.typography.bodyMedium)
                        }
                        if (block.caption != null) {
                            Text(block.caption, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                    }
                    if (isToto && block.audio_url != null) {
                        IconButton(onClick = { audioPlayer.play(block.audio_url) }) {
                            Icon(Icons.Filled.VolumeUp, contentDescription = "Reproducir pronunciación", tint = accent)
                        }
                    }
                }
            }
        }
        "image" -> {
            AsyncImage(
                model = block.content,
                contentDescription = block.caption,
                modifier = Modifier.fillMaxWidth().height(180.dp),
            )
        }
        "audio" -> {
            Card(shape = RoundedCornerShape(16.dp), modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier.fillMaxWidth().padding(14.dp).clickable { audioPlayer.play(block.content) },
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(Icons.Filled.PlayArrow, contentDescription = null, tint = AlebrijeTeal)
                    Spacer(Modifier.height(0.dp))
                    Text("Reproducir audio", modifier = Modifier.padding(start = 8.dp))
                }
            }
        }
        "video" -> {
            // Simplificación deliberada: sin WebView/YouTube SDK en el alcance,
            // se abre el enlace en el navegador del sistema.
            Card(shape = RoundedCornerShape(16.dp), modifier = Modifier.fillMaxWidth()) {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(14.dp)
                        .clickable {
                            context.startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(block.content)))
                        },
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Icon(Icons.Filled.PlayArrow, contentDescription = null, tint = AlebrijeCoral)
                    Text("Ver video", modifier = Modifier.padding(start = 8.dp))
                }
            }
        }
        else -> {
            Text(block.content, style = MaterialTheme.typography.bodyLarge)
        }
    }
}
