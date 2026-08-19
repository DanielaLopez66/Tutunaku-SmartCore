package mx.tutunaku.wearable.ui.screens

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxScope
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.wear.compose.foundation.lazy.TransformingLazyColumn
import androidx.wear.compose.foundation.lazy.TransformingLazyColumnScope
import androidx.wear.compose.foundation.lazy.TransformingLazyColumnState
import androidx.wear.compose.material3.AppScaffold
import androidx.wear.compose.material3.ScreenScaffold
import androidx.wear.compose.material3.TimeText

/**
 * Anfitrión único de [AppScaffold] para toda la app: coordina la hora
 * compartida (se oculta al hacer scroll en cualquier pantalla) entre todas
 * las rutas de [mx.tutunaku.wearable.ui.navigation.WearNavHost].
 */
@Composable
fun TutunakuAppScaffold(content: @Composable BoxScope.() -> Unit) {
    AppScaffold(
        timeText = { TimeText() },
        content = content,
    )
}

/**
 * Pantalla con lista desplazable. [TransformingLazyColumn] reemplaza al
 * `ScalingLazyColumn` + `Vignette` de Material 2: cada fila se escala y
 * desvanece sola cerca del bisel, así que el contenido nunca queda
 * recortado por el borde circular sin necesidad de paddings fijos a mano.
 * [edgeButton], si se define, queda anclado al arco inferior y cambia de
 * forma con el scroll en vez de competir por espacio como un ítem más.
 */
@Composable
fun WearListScreen(
    state: TransformingLazyColumnState,
    modifier: Modifier = Modifier,
    edgeButton: (@Composable BoxScope.() -> Unit)? = null,
    content: TransformingLazyColumnScope.() -> Unit,
) {
    ScreenScaffold(
        scrollState = state,
        modifier = modifier,
        edgeButton = edgeButton ?: {},
    ) { contentPadding ->
        TransformingLazyColumn(
            state = state,
            contentPadding = contentPadding,
            content = content,
        )
    }
}

/** Pantalla simple sin scroll (contenido centrado): splash, palabra del día, minijuego. */
@Composable
fun WearScreen(modifier: Modifier = Modifier, content: @Composable () -> Unit) {
    ScreenScaffold(modifier = modifier) { contentPadding ->
        Box(
            modifier = Modifier.fillMaxSize().padding(contentPadding),
            contentAlignment = Alignment.Center,
        ) {
            content()
        }
    }
}
