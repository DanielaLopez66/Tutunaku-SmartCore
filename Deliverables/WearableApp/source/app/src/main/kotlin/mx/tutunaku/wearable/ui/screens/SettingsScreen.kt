package mx.tutunaku.wearable.ui.screens

import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.wear.compose.foundation.lazy.rememberTransformingLazyColumnState
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.ButtonDefaults
import androidx.wear.compose.material3.ListHeader
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.Text
import kotlinx.coroutines.launch
import mx.tutunaku.wearable.TutunakuWearApp
import mx.tutunaku.wearable.ui.AuthState
import mx.tutunaku.wearable.ui.MainViewModel

@Composable
fun SettingsScreen(viewModel: MainViewModel) {
    val context = LocalContext.current
    val app = context.applicationContext as TutunakuWearApp
    val scope = rememberCoroutineScope()
    val listState = rememberTransformingLazyColumnState()

    val authState by viewModel.authState.collectAsStateWithLifecycle()
    val loginLoading by viewModel.loginLoading.collectAsStateWithLifecycle()
    val loginError by viewModel.loginError.collectAsStateWithLifecycle()
    val phoneConnected by viewModel.phoneConnected.collectAsStateWithLifecycle()

    DisposableEffect(Unit) {
        scope.launch { app.watchSyncManager.startObservingConnection() }
        onDispose { app.watchSyncManager.stopObservingConnection() }
    }

    var serverUrl by remember { mutableStateOf("") }
    var serverSaved by remember { mutableStateOf(false) }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        serverUrl = app.tokenStore.currentServerUrl()
    }

    LaunchedEffect(authState) {
        if (authState == AuthState.LOGGED_IN) {
            password = ""
        }
    }

    WearListScreen(state = listState) {
        item { ListHeader { Text("⚙️ Ajustes") } }

        item {
            Text(
                if (authState == AuthState.LOGGED_IN) "Cuenta conectada ✓" else "Cuenta sin configurar",
                style = MaterialTheme.typography.labelSmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }
        item {
            Text(
                if (phoneConnected) "Teléfono conectado ✓" else "Teléfono no conectado",
                style = MaterialTheme.typography.labelSmall,
                color = if (phoneConnected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
            )
        }

        item {
            WatchTextField(
                value = email,
                onValueChange = { email = it },
                placeholder = "Email",
                keyboardType = KeyboardType.Email,
            )
        }
        item {
            WatchTextField(
                value = password,
                onValueChange = { password = it },
                placeholder = "Contraseña",
                isPassword = true,
                keyboardType = KeyboardType.Password,
            )
        }
        item {
            Button(
                onClick = { viewModel.login(email.trim(), password) },
                enabled = !loginLoading && email.isNotBlank() && password.isNotBlank(),
                label = { Text(if (loginLoading) "…" else "Conectar") },
                modifier = Modifier.fillMaxWidth(),
            )
        }
        loginError?.let {
            item {
                Text(it, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.error)
            }
        }

        if (authState == AuthState.LOGGED_IN) {
            item {
                Button(
                    onClick = { viewModel.logout() },
                    label = { Text("Cerrar sesión") },
                    colors = ButtonDefaults.buttonColors(containerColor = MaterialTheme.colorScheme.error),
                    modifier = Modifier.fillMaxWidth(),
                )
            }
        }

        item { Spacer(Modifier.height(6.dp)) }

        item {
            Text("URL del backend", style = MaterialTheme.typography.labelSmall)
        }
        item {
            WatchTextField(
                value = serverUrl,
                onValueChange = { serverUrl = it; serverSaved = false },
                placeholder = "http://10.0.2.2:8000/",
            )
        }
        item {
            Button(
                onClick = {
                    scope.launch {
                        app.tokenStore.saveServerUrl(if (serverUrl.endsWith("/")) serverUrl else "$serverUrl/")
                        serverSaved = true
                    }
                },
                label = { Text(if (serverSaved) "Guardado ✓" else "Guardar URL") },
                colors = ButtonDefaults.filledTonalButtonColors(),
                modifier = Modifier.fillMaxWidth(),
            )
        }
    }
}
