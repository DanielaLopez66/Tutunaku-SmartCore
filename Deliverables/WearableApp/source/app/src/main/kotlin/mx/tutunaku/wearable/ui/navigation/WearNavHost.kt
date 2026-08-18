package mx.tutunaku.wearable.ui.navigation

import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.wear.compose.navigation.SwipeDismissableNavHost
import androidx.wear.compose.navigation.composable
import androidx.wear.compose.navigation.rememberSwipeDismissableNavController
import mx.tutunaku.wearable.ui.AuthState
import mx.tutunaku.wearable.ui.MainViewModel
import mx.tutunaku.wearable.ui.screens.CheckingScreen
import mx.tutunaku.wearable.ui.screens.HeartGameScreen
import mx.tutunaku.wearable.ui.screens.HomeScreen
import mx.tutunaku.wearable.ui.screens.NotificationsScreen
import mx.tutunaku.wearable.ui.screens.SettingsScreen
import mx.tutunaku.wearable.ui.screens.TutunakuAppScaffold
import mx.tutunaku.wearable.ui.screens.WordOfDayScreen

object Routes {
    const val CHECKING = "checking"
    const val HOME = "home"
    const val NOTIFICATIONS = "notifications"
    const val WORD_OF_DAY = "word_of_day"
    const val SETTINGS = "settings"
    const val HEART_GAME = "heart_game"
}

/**
 * Sin pantalla de login: el reloj siempre entra directo a Home en cuanto
 * termina de revisar/reintentar la sesión guardada. Si no hay cuenta
 * configurada, Home muestra un aviso para ir a Ajustes en vez de bloquear
 * la app entera con un formulario.
 */
@Composable
fun WearNavHost(viewModel: MainViewModel) {
    val navController = rememberSwipeDismissableNavController()
    val authState by viewModel.authState.collectAsStateWithLifecycle()

    LaunchedEffect(authState) {
        if (authState != AuthState.CHECKING) {
            navController.navigate(Routes.HOME) {
                popUpTo(0) { inclusive = true }
            }
        }
    }

    TutunakuAppScaffold {
        SwipeDismissableNavHost(
            navController = navController,
            startDestination = Routes.CHECKING,
        ) {
            composable(Routes.CHECKING) { CheckingScreen() }
            composable(Routes.HOME) { HomeScreen(viewModel, navController) }
            composable(Routes.NOTIFICATIONS) { NotificationsScreen(viewModel, navController) }
            composable(Routes.WORD_OF_DAY) { WordOfDayScreen(viewModel) }
            composable(Routes.SETTINGS) { SettingsScreen(viewModel) }
            composable(Routes.HEART_GAME) { HeartGameScreen(viewModel, navController) }
        }
    }
}
