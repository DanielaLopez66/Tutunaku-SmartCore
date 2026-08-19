package mx.tutunaku.wearable.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.wear.compose.material3.CircularProgressIndicator
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.OutlinedButton
import androidx.wear.compose.material3.Text
import mx.tutunaku.wearable.ui.MainViewModel

@Composable
fun WordOfDayScreen(viewModel: MainViewModel) {
    val word by viewModel.wordOfDay.collectAsStateWithLifecycle()
    val wordState by viewModel.wordOfDayState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) { viewModel.refreshWordOfDay() }

    WearScreen {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text("📖 Palabra del día", style = MaterialTheme.typography.labelMedium)
            Spacer(Modifier.height(8.dp))
            when {
                word != null -> {
                    Text(
                        word!!.word,
                        style = MaterialTheme.typography.titleLarge,
                        color = MaterialTheme.colorScheme.primary,
                        textAlign = TextAlign.Center,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        word!!.translation,
                        style = MaterialTheme.typography.bodyMedium,
                        textAlign = TextAlign.Center,
                    )
                    word!!.hint?.let {
                        Spacer(Modifier.height(6.dp))
                        Text(
                            "💡 $it",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant,
                            textAlign = TextAlign.Center,
                        )
                    }
                }

                wordState.error != null -> {
                    Text(
                        wordState.error ?: "",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.error,
                        textAlign = TextAlign.Center,
                    )
                    Spacer(Modifier.height(6.dp))
                    OutlinedButton(onClick = { viewModel.refreshWordOfDay() }) {
                        Text("Reintentar")
                    }
                }

                else -> {
                    CircularProgressIndicator(modifier = Modifier.size(24.dp))
                    Spacer(Modifier.height(6.dp))
                    Text("Cargando…", style = MaterialTheme.typography.labelSmall)
                }
            }
        }
    }
}
