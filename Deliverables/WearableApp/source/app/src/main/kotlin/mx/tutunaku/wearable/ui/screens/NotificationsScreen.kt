package mx.tutunaku.wearable.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.wear.compose.foundation.lazy.items
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.ButtonDefaults
import androidx.wear.compose.material3.CircularProgressIndicator
import androidx.wear.compose.material3.ListHeader
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.OutlinedButton
import androidx.wear.compose.material3.Text
import mx.tutunaku.wearable.ui.MainViewModel

@Composable
fun NotificationsScreen(viewModel: MainViewModel, navController: NavHostController) {
    val notifications by viewModel.notifications.collectAsStateWithLifecycle()
    val notificationsState by viewModel.notificationsState.collectAsStateWithLifecycle()
    val listState = rememberTransformingLazyColumnState()

    WearListScreen(state = listState) {
        item {
            ListHeader { Text("🔔 Notificaciones") }
        }

        when {
            notifications.isEmpty() && notificationsState.loading -> {
                item {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.Center,
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        CircularProgressIndicator(modifier = Modifier.size(20.dp))
                        Spacer(Modifier.size(6.dp))
                        Text("Cargando…", style = MaterialTheme.typography.labelMedium)
                    }
                }
            }

            notifications.isEmpty() && notificationsState.error != null -> {
                item {
                    Text(
                        notificationsState.error ?: "",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                }
                item {
                    OutlinedButton(
                        onClick = { viewModel.refreshNotifications() },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("Reintentar") }
                }
            }

            notifications.isEmpty() -> {
                item {
                    Text(
                        "Sin notificaciones",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
            }
        }

        if (notifications.any { !it.is_read }) {
            item {
                Button(
                    onClick = { viewModel.markAllNotificationsRead() },
                    label = { Text("Marcar todas leídas") },
                    colors = ButtonDefaults.filledTonalButtonColors(),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }

        items(notifications, key = { it.id }) { notif ->
            Button(
                onClick = { viewModel.markNotificationRead(notif.id) },
                label = { Text(notif.title, maxLines = 2) },
                secondaryLabel = notif.message?.let { { Text(it, maxLines = 2) } },
                colors = if (notif.is_read) {
                    ButtonDefaults.filledTonalButtonColors()
                } else {
                    ButtonDefaults.buttonColors()
                },
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}
