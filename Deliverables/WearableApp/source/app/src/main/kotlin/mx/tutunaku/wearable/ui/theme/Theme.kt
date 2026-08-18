package mx.tutunaku.wearable.ui.theme

import androidx.compose.runtime.Composable
import androidx.wear.compose.material3.ColorScheme
import androidx.wear.compose.material3.MaterialTheme

/**
 * Esquema de color Material 3 Expressive con la paleta de marca "alebrije"
 * (igual que frontend/tailwind.config.js). Fondo y superficies casi negros a
 * propósito: en las pantallas AMOLED de los relojes, los píxeles negros no
 * consumen energía, y el alto contraste contra ellos es justo lo que hace
 * "glanceable" al texto.
 */
private val TutunakuColorScheme = ColorScheme(
    primary = AlebrijeCoral,
    primaryDim = AlebrijeCoralDim,
    primaryContainer = AlebrijeMagenta,
    onPrimary = BackgroundDark,
    onPrimaryContainer = OnDark,
    secondary = AlebrijeTeal,
    secondaryDim = AlebrijeTealDim,
    secondaryContainer = SurfaceDarkHigh,
    onSecondary = BackgroundDark,
    onSecondaryContainer = OnDark,
    tertiary = AlebrijeViolet,
    tertiaryDim = AlebrijeVioletDim,
    tertiaryContainer = SurfaceDarkHigh,
    onTertiary = BackgroundDark,
    onTertiaryContainer = OnDark,
    surfaceContainerLow = SurfaceDark,
    surfaceContainer = SurfaceDark,
    surfaceContainerHigh = SurfaceDarkHigh,
    onSurface = OnDark,
    onSurfaceVariant = OnDarkMuted,
    outline = OnDarkMuted,
    outlineVariant = SurfaceDarkHigh,
    background = BackgroundDark,
    onBackground = OnDark,
    error = ErrorRed,
    errorDim = ErrorRedDim,
    onError = BackgroundDark,
)

@Composable
fun TutunakuWearTheme(content: @Composable () -> Unit) {
    MaterialTheme(
        colorScheme = TutunakuColorScheme,
        content = content,
    )
}
