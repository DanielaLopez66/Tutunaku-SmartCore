package mx.tutunaku.wearable.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.ButtonDefaults
import androidx.wear.compose.material3.CircularProgressIndicator
import androidx.wear.compose.material3.EdgeButton
import androidx.wear.compose.material3.ListHeader
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.OutlinedButton
import androidx.wear.compose.material3.Text
import mx.tutunaku.wearable.ui.AuthState
import mx.tutunaku.wearable.ui.MainViewModel
import mx.tutunaku.wearable.ui.navigation.Routes

@Composable
fun HomeScreen(viewModel: MainViewModel, navController: NavHostController) {
    val authState by viewModel.authState.collectAsStateWithLifecycle()
    val stats by viewModel.stats.collectAsStateWithLifecycle()
    val statsState by viewModel.statsState.collectAsStateWithLifecycle()
    val connected by viewModel.socketConnected.collectAsStateWithLifecycle()
    val notifications by viewModel.notifications.collectAsStateWithLifecycle()
    val unread = notifications.count { !it.is_read }

    val listState = rememberTransformingLazyColumnState()

    WearListScreen(
        state = listState,
        edgeButton = if (authState == AuthState.LOGGED_IN) {
            { EdgeButton(onClick = { viewModel.refreshStats() }) { Text("🔄 Actualizar") } }
        } else {
            null
        },
    ) {
        item {
            ListHeader {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Text("🫀 Tutunaku")
                    if (connected) {
                        Spacer(Modifier.width(6.dp))
                        LiveDot()
                    }
                }
            }
        }

        if (authState == AuthState.LOGGED_OUT) {
            item {
                Text(
                    "Configura tu cuenta en Ajustes para sincronizar racha, XP y vidas.",
                    style = MaterialTheme.typography.bodySmall,
                    textAlign = TextAlign.Center,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
            item {
                Button(
                    onClick = { navController.navigate(Routes.SETTINGS) },
                    label = { Text("⚙️ Ir a Ajustes") },
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        } else {
            item {
                when {
                    stats == null && statsState.loading -> {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.Center,
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            CircularProgressIndicator(modifier = Modifier.size(20.dp))
                            Spacer(Modifier.width(6.dp))
                            Text("Cargando…", style = MaterialTheme.typography.labelMedium)
                        }
                    }

                    stats == null && statsState.error != null -> {
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text(
                                statsState.error ?: "",
                                style = MaterialTheme.typography.labelSmall,
                                color = MaterialTheme.colorScheme.error,
                                textAlign = TextAlign.Center,
                            )
                            Spacer(Modifier.height(4.dp))
                            OutlinedButton(onClick = { viewModel.refreshStats() }) {
                                Text("Reintentar")
                            }
                        }
                    }

                    else -> {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceEvenly,
                        ) {
                            StatPill(emoji = "⚡", value = "${stats?.xp_total ?: 0}", label = "XP")
                            StatPill(emoji = "🔥", value = "${stats?.current_streak ?: 0}", label = "racha")
                            StatPill(
                                emoji = "❤️",
                                value = "${stats?.hearts ?: 0}",
                                label = "vidas · toca",
                                onClick = { navController.navigate(Routes.HEART_GAME) },
                            )
                        }
                    }
                }
            }

            item {
                Text(
                    "Nivel ${stats?.level ?: 1}",
                    style = MaterialTheme.typography.labelMedium,
                    color = MaterialTheme.colorScheme.secondary,
                )
            }

            item {
                Button(
                    onClick = { navController.navigate(Routes.NOTIFICATIONS) },
                    label = { Text(if (unread > 0) "🔔 Notificaciones ($unread)" else "🔔 Notificaciones") },
                    colors = if (unread > 0) {
                        ButtonDefaults.buttonColors()
                    } else {
                        ButtonDefaults.filledTonalButtonColors()
                    },
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }

        item {
            Button(
                onClick = { navController.navigate(Routes.WORD_OF_DAY) },
                label = { Text("📖 Palabra del día") },
                colors = ButtonDefaults.filledTonalButtonColors(),
                modifier = Modifier.fillMaxWidth(),
            )
        }

        item {
            Button(
                onClick = { navController.navigate(Routes.SETTINGS) },
                label = { Text("⚙️ Ajustes") },
                colors = ButtonDefaults.filledTonalButtonColors(),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}

@Composable
private fun LiveDot() {
    Box(
        modifier = Modifier
            .size(6.dp)
            .clip(CircleShape)
            .background(MaterialTheme.colorScheme.primary),
    )
}

@Composable
private fun StatPill(emoji: String, value: String, label: String, onClick: (() -> Unit)? = null) {
    Column(
        horizontalAlignment = Alignment.CenterHorizontally,
        modifier = if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier,
    ) {
        Text("$emoji $value", style = MaterialTheme.typography.titleMedium)
        Text(
            label,
            style = MaterialTheme.typography.labelSmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}
