package mx.tutunaku.mobile.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = AlebrijeCoral,
    onPrimary = LightSurface,
    secondary = AlebrijeTeal,
    onSecondary = LightSurface,
    tertiary = AlebrijeViolet,
    onTertiary = LightSurface,
    error = ErrorRed,
    background = LightBg,
    onBackground = LightText,
    surface = LightSurface,
    onSurface = LightText,
    surfaceVariant = LightSurface,
    onSurfaceVariant = LightMuted,
    outline = LightBorder,
)

private val DarkColors = darkColorScheme(
    primary = AlebrijeCoral,
    onPrimary = DarkText,
    secondary = AlebrijeTeal,
    onSecondary = DarkText,
    tertiary = AlebrijeViolet,
    onTertiary = DarkText,
    error = ErrorRed,
    background = DarkBg,
    onBackground = DarkText,
    surface = DarkSurface,
    onSurface = DarkText,
    surfaceVariant = DarkSurface,
    onSurfaceVariant = DarkMuted,
    outline = DarkBorder,
)

/**
 * Sigue el tema del sistema (claro/oscuro), igual que la app completa del
 * frontend web. `dynamicColor` queda deliberadamente desactivado: la
 * paleta de marca "alebrije" siempre gana sobre Material You.
 */
@Composable
fun TutunakuMobileTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val colorScheme = if (darkTheme) DarkColors else LightColors
    MaterialTheme(
        colorScheme = colorScheme,
        typography = TutunakuTypography,
        content = content,
    )
}
