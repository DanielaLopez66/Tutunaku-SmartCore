package mx.tutunaku.mobile.ui.util

import androidx.compose.ui.graphics.Color

/** Convierte un `color_hex` del backend ("#8B5CF6") a Color de Compose; null si viene vacío/mal formado. */
fun parseHexColor(hex: String?): Color? {
    if (hex.isNullOrBlank()) return null
    val clean = hex.removePrefix("#")
    val colorLong = clean.toLongOrNull(16) ?: return null
    return when (clean.length) {
        6 -> Color(0xFF000000 or colorLong)
        8 -> Color(colorLong)
        else -> null
    }
}
