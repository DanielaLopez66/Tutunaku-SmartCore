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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Watch
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import kotlinx.coroutines.launch
import mx.tutunaku.mobile.TutunakuMobileApp
import mx.tutunaku.mobile.ui.MainViewModel
import mx.tutunaku.mobile.ui.theme.AlebrijeCoral
import mx.tutunaku.mobile.ui.theme.AlebrijeGold
import mx.tutunaku.mobile.ui.theme.AlebrijeTeal
import mx.tutunaku.mobile.ui.theme.AlebrijeViolet
import mx.tutunaku.mobile.ui.theme.ErrorRed

@Composable
fun ProfileScreen(viewModel: MainViewModel) {
    val app = LocalContext.current.applicationContext as TutunakuMobileApp
    val scope = rememberCoroutineScope()
    val stats by viewModel.stats.collectAsStateWithLifecycle()
    val watchConnected by viewModel.watchConnected.collectAsStateWithLifecycle()

    // Observa la conexión con el reloj solo mientras esta pantalla está
    // visible (CapabilityClient vía Deliverables/MobileApp/.../data/wear/WatchSyncManager.kt).
    DisposableEffect(Unit) {
        scope.launch { app.watchSyncManager.startObservingConnection() }
        onDispose { app.watchSyncManager.stopObservingConnection() }
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
    ) {
        Text("Perfil", style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(20.dp))

        Card(shape = RoundedCornerShape(20.dp), modifier = Modifier.fillMaxWidth()) {
            Column(Modifier.padding(20.dp)) {
                Text("Estadísticas", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                Spacer(Modifier.height(12.dp))
                StatRow("XP total", "${stats?.xp_total ?: 0}", AlebrijeGold)
                StatRow("Nivel", "${stats?.level ?: 1}", AlebrijeViolet)
                StatRow("Vidas", "${stats?.hearts ?: 5}", ErrorRed)
                StatRow("Racha actual", "${stats?.current_streak ?: 0} días", AlebrijeCoral)
                StatRow("Racha más larga", "${stats?.longest_streak ?: 0} días", AlebrijeCoral)
                StatRow("Lecciones completadas", "${stats?.lessons_completed ?: 0}", AlebrijeTeal)
                StatRow("Precisión", "${"%.1f".format(stats?.accuracy_percentage ?: 0.0)}%", AlebrijeTeal)
                StatRow("Logros", "${stats?.achievements_count ?: 0}", AlebrijeGold)
            }
        }

        Spacer(Modifier.height(16.dp))

        Card(shape = RoundedCornerShape(20.dp), modifier = Modifier.fillMaxWidth()) {
            Row(
                modifier = Modifier.fillMaxWidth().padding(20.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(Icons.Filled.Watch, contentDescription = null, tint = if (watchConnected) AlebrijeTeal else MaterialTheme.colorScheme.onSurfaceVariant)
                Spacer(Modifier.height(0.dp))
                Column(modifier = Modifier.weight(1f).padding(start = 12.dp)) {
                    Text("Reloj", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold)
                    Text(
                        if (watchConnected) "Conectado ✓" else "No conectado",
                        style = MaterialTheme.typography.bodyMedium,
                        color = if (watchConnected) AlebrijeTeal else MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                if (watchConnected) {
                    Icon(Icons.Filled.CheckCircle, contentDescription = null, tint = AlebrijeTeal)
                }
            }
        }

        Spacer(Modifier.height(24.dp))

        OutlinedButton(
            onClick = { viewModel.logout() },
            modifier = Modifier.fillMaxWidth().height(52.dp),
            shape = RoundedCornerShape(16.dp),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = ErrorRed),
        ) {
            Text("Cerrar sesión", fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun StatRow(label: String, value: String, color: androidx.compose.ui.graphics.Color) {
    Row(
        modifier = Modifier.fillMaxWidth().padding(vertical = 6.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold, color = color)
    }
}
