package mx.tutunaku.mobile.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowForward
import androidx.compose.material.icons.filled.AutoStories
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.LocalFireDepartment
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.WorkspacePremium
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.shadow
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import coil.compose.AsyncImage
import mx.tutunaku.mobile.TutunakuMobileApp
import mx.tutunaku.mobile.data.model.Course
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.theme.AlebrijeCoral
import mx.tutunaku.mobile.ui.theme.AlebrijeGold
import mx.tutunaku.mobile.ui.theme.AlebrijeTeal
import mx.tutunaku.mobile.ui.theme.AlebrijeViolet
import mx.tutunaku.mobile.ui.theme.ErrorRed

@Composable
fun HomeScreen(viewModel: MainViewModel, onCourseClick: (String) -> Unit) {
    val app = androidx.compose.ui.platform.LocalContext.current.applicationContext as TutunakuMobileApp
    val stats by viewModel.stats.collectAsStateWithLifecycle()

    var courses by remember { mutableStateOf<List<Course>>(emptyList()) }
    var loading by remember { mutableStateOf(true) }
    var error by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(Unit) {
        loading = true
        app.contentRepository.getCourses()
            .onSuccess { courses = it; error = null }
            .onFailure { error = "No se pudieron cargar los cursos." }
        loading = false
    }

    LazyColumn(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background),
        contentPadding = PaddingValues(20.dp),
    ) {
        item {
            Text("¡Hola de nuevo! 👋", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(4.dp))
            Text(
                "Sigue aprendiendo totonaco hoy",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            Spacer(Modifier.height(20.dp))
        }

        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard(
                    icon = Icons.Filled.LocalFireDepartment,
                    color = AlebrijeCoral,
                    value = (stats?.current_streak ?: 0).toString(),
                    label = "Racha",
                    modifier = Modifier.weight(1f),
                )
                StatCard(
                    icon = Icons.Filled.WorkspacePremium,
                    color = AlebrijeViolet,
                    value = (stats?.level ?: 1).toString(),
                    label = "Nivel",
                    modifier = Modifier.weight(1f),
                )
            }
            Spacer(Modifier.height(10.dp))
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                StatCard(
                    icon = Icons.Filled.Star,
                    color = AlebrijeGold,
                    value = (stats?.xp_total ?: 0).toString(),
                    label = "XP",
                    modifier = Modifier.weight(1f),
                )
                StatCard(
                    icon = Icons.Filled.Favorite,
                    color = ErrorRed,
                    value = (stats?.hearts ?: 5).toString(),
                    label = "Vidas",
                    modifier = Modifier.weight(1f),
                )
            }
            Spacer(Modifier.height(24.dp))
            Text("Tus cursos", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))
        }

        if (loading) {
            item {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.Center) {
                    CircularProgressIndicator(color = AlebrijeTeal)
                }
            }
        } else if (error != null) {
            item { Text(error ?: "", color = MaterialTheme.colorScheme.error) }
        } else {
            items(courses) { course ->
                CourseCard(course = course, onClick = { onCourseClick(course.id) })
                Spacer(Modifier.height(12.dp))
            }
        }
    }
}

@Composable
private fun StatCard(
    icon: androidx.compose.ui.graphics.vector.ImageVector,
    color: androidx.compose.ui.graphics.Color,
    value: String,
    label: String,
    modifier: Modifier = Modifier,
) {
    Card(
        modifier = modifier,
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Icon(icon, contentDescription = label, tint = color)
            Spacer(Modifier.height(6.dp))
            Text(value, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold)
            Text(label, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

/** Gradiente de marca — igual que `alebrije-gradient` en frontend/tailwind.config.js. */
private val AlebrijeGradient = Brush.linearGradient(
    colors = listOf(AlebrijeCoral, AlebrijeTeal, AlebrijeViolet),
)

@Composable
private fun CourseCard(course: Course, onClick: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .shadow(elevation = 10.dp, shape = RoundedCornerShape(24.dp), spotColor = AlebrijeViolet, ambientColor = AlebrijeCoral)
            .clickable(onClick = onClick),
        shape = RoundedCornerShape(24.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
    ) {
        Column {
            Box(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(96.dp)
                    .background(AlebrijeGradient),
                contentAlignment = Alignment.Center,
            ) {
                if (course.cover_image_url != null) {
                    AsyncImage(
                        model = course.cover_image_url,
                        contentDescription = course.title,
                        modifier = Modifier.fillMaxSize(),
                    )
                } else {
                    Icon(
                        Icons.Filled.AutoStories,
                        contentDescription = null,
                        tint = Color.White.copy(alpha = 0.85f),
                        modifier = Modifier.size(44.dp),
                    )
                }
                if (course.difficulty != null) {
                    Surface(
                        shape = RoundedCornerShape(50),
                        color = Color.White.copy(alpha = 0.25f),
                        modifier = Modifier.align(Alignment.TopEnd).padding(10.dp),
                    ) {
                        Text(
                            course.difficulty,
                            style = MaterialTheme.typography.labelSmall,
                            fontWeight = FontWeight.Bold,
                            color = Color.White,
                            modifier = Modifier.padding(horizontal = 10.dp, vertical = 4.dp),
                        )
                    }
                }
            }
            Row(
                modifier = Modifier.fillMaxWidth().padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Column(modifier = Modifier.weight(1f)) {
                    Text(course.title, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    if (course.description != null) {
                        Text(
                            course.description,
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            maxLines = 2,
                        )
                    }
                    Spacer(Modifier.height(6.dp))
                    Text(
                        "Continuar camino",
                        style = MaterialTheme.typography.labelLarge,
                        color = AlebrijeTeal,
                        fontWeight = FontWeight.Bold,
                    )
                }
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .clip(CircleShape)
                        .background(AlebrijeTeal.copy(alpha = 0.12f)),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(Icons.Filled.ArrowForward, contentDescription = null, tint = AlebrijeTeal)
                }
            }
        }
    }
}
