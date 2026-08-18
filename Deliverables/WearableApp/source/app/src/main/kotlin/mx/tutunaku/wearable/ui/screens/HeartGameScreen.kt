package mx.tutunaku.wearable.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavHostController
import androidx.wear.compose.material3.Button
import androidx.wear.compose.material3.CircularProgressIndicator
import androidx.wear.compose.material3.MaterialTheme
import androidx.wear.compose.material3.OutlinedButton
import androidx.wear.compose.material3.Text
import kotlinx.coroutines.delay
import mx.tutunaku.wearable.ui.MainViewModel
import kotlin.random.Random

private const val TOTAL_ROUNDS = 3
private const val HITS_NEEDED = 2
private const val GLOW_WINDOW_MS = 850L
private const val MIN_WAIT_MS = 500L
private const val MAX_WAIT_MS = 1500L
private const val MAX_HEARTS = 5

private enum class HeartPhase { DIM, GLOWING }
private enum class GameState { INTRO, PLAYING, SUBMITTING, DONE }

/**
 * Minijuego de reacción: el corazón se enciende brevemente TOTAL_ROUNDS
 * veces; tocarlo mientras brilla cuenta como acierto. Con HITS_NEEDED
 * aciertos se gana una vida (tope MAX_HEARTS, aplicado por el backend en
 * POST /users/me/hearts/earn). Se usa una sola posición fija en el centro a
 * propósito: en una pantalla redonda tan pequeña, mover el objetivo por el
 * espacio arriesga sacarlo del área tocable cerca del bisel.
 */
@Composable
fun HeartGameScreen(viewModel: MainViewModel, navController: NavHostController) {
    val stats by viewModel.stats.collectAsStateWithLifecycle()
    val heartsFull = (stats?.hearts ?: 0) >= MAX_HEARTS

    var state by remember { mutableStateOf(GameState.INTRO) }
    var round by remember { mutableStateOf(0) }
    var hits by remember { mutableStateOf(0) }
    var phase by remember { mutableStateOf(HeartPhase.DIM) }
    var resultText by remember { mutableStateOf<String?>(null) }
    var runId by remember { mutableStateOf(0) }

    // OJO: la key NO incluye `state`. Ese último tramo muta `state` mientras
    // espera a viewModel.earnHeart(); si `state` fuera parte de la key, ese
    // cambio cancelaría esta misma corrutina a mitad de la llamada de red
    // (síntoma real observado: IOException "Canceled" en logcat).
    LaunchedEffect(round, runId) {
        if (state != GameState.PLAYING) return@LaunchedEffect
        if (round >= TOTAL_ROUNDS) {
            if (hits >= HITS_NEEDED) {
                state = GameState.SUBMITTING
                val won = viewModel.earnHeart()
                resultText = if (won) "¡Ganaste una vida! ❤️" else "No se pudo otorgar la vida. Intenta más tarde."
            } else {
                resultText = "Casi… $hits/$TOTAL_ROUNDS. ¡Inténtalo de nuevo!"
            }
            state = GameState.DONE
            return@LaunchedEffect
        }
        phase = HeartPhase.DIM
        delay(Random.nextLong(MIN_WAIT_MS, MAX_WAIT_MS))
        phase = HeartPhase.GLOWING
        delay(GLOW_WINDOW_MS)
        if (phase == HeartPhase.GLOWING) {
            // no se tocó a tiempo: cuenta como ronda perdida
            phase = HeartPhase.DIM
            round += 1
        }
    }

    fun startGame() {
        round = 0
        hits = 0
        resultText = null
        runId += 1
        state = GameState.PLAYING
    }

    WearScreen {
        Column(
            modifier = Modifier.padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            when (state) {
                GameState.INTRO -> {
                    Text(
                        "💗 Juego del corazón",
                        style = MaterialTheme.typography.titleMedium,
                        textAlign = TextAlign.Center,
                    )
                    Spacer(Modifier.height(6.dp))
                    Text(
                        if (heartsFull) {
                            "Ya tienes el máximo de vidas"
                        } else {
                            "Toca el corazón cuando brille: $HITS_NEEDED de $TOTAL_ROUNDS para ganar una vida"
                        },
                        style = MaterialTheme.typography.labelSmall,
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                    Spacer(Modifier.height(10.dp))
                    Button(
                        onClick = { startGame() },
                        enabled = !heartsFull,
                        label = { Text("Jugar") },
                        modifier = Modifier.fillMaxWidth(),
                    )
                }

                GameState.PLAYING -> {
                    Text("Ronda ${round + 1}/$TOTAL_ROUNDS", style = MaterialTheme.typography.labelMedium)
                    Spacer(Modifier.height(10.dp))
                    HeartTarget(glowing = phase == HeartPhase.GLOWING) {
                        if (phase == HeartPhase.GLOWING) {
                            hits += 1
                            phase = HeartPhase.DIM
                            round += 1
                        }
                    }
                    Spacer(Modifier.height(10.dp))
                    Text("Aciertos: $hits", style = MaterialTheme.typography.labelSmall)
                }

                GameState.SUBMITTING -> {
                    CircularProgressIndicator(modifier = Modifier.size(32.dp))
                    Spacer(Modifier.height(6.dp))
                    Text("Calculando…", style = MaterialTheme.typography.labelSmall)
                }

                GameState.DONE -> {
                    Text(resultText ?: "", style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center)
                    Spacer(Modifier.height(10.dp))
                    Button(
                        onClick = { startGame() },
                        enabled = (stats?.hearts ?: 0) < MAX_HEARTS,
                        label = { Text("Reintentar") },
                        modifier = Modifier.fillMaxWidth(),
                    )
                    Spacer(Modifier.height(6.dp))
                    OutlinedButton(
                        onClick = { navController.popBackStack() },
                        modifier = Modifier.fillMaxWidth(),
                    ) { Text("Salir") }
                }
            }
        }
    }
}

@Composable
private fun HeartTarget(glowing: Boolean, onTap: () -> Unit) {
    val size = if (glowing) 64.dp else 44.dp
    Box(
        modifier = Modifier
            .size(size)
            .clip(CircleShape)
            .background(if (glowing) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.surfaceContainer)
            .clickable { onTap() },
        contentAlignment = Alignment.Center,
    ) {
        Text(if (glowing) "❤️" else "🤍", style = MaterialTheme.typography.titleLarge)
    }
}
