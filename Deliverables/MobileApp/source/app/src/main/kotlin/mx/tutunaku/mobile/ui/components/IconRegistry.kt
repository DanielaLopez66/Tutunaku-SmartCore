package mx.tutunaku.mobile.ui.components

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowUpward
import androidx.compose.material.icons.filled.AutoAwesome
import androidx.compose.material.icons.filled.Bolt
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.Checkroom
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.Eco
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Group
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Inventory2
import androidx.compose.material.icons.filled.LocalFireDepartment
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.MenuBook
import androidx.compose.material.icons.filled.MilitaryTech
import androidx.compose.material.icons.filled.MusicNote
import androidx.compose.material.icons.filled.Notifications
import androidx.compose.material.icons.filled.Palette
import androidx.compose.material.icons.filled.Pets
import androidx.compose.material.icons.filled.Public
import androidx.compose.material.icons.filled.Restaurant
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.Tag
import androidx.compose.material.icons.filled.WbSunny
import androidx.compose.material.icons.filled.WorkspacePremium
import androidx.compose.material.icons.filled.GpsFixed
import androidx.compose.material.icons.filled.Person
import androidx.compose.ui.graphics.vector.ImageVector

/**
 * Espejo Kotlin de frontend/src/utils/icons.tsx: traduce las claves cortas
 * guardadas en icon_emoji (unidades, logros, notificaciones) a íconos
 * reales. El nombre del campo es engañoso — NO son emojis, son
 * identificadores de lucide-react (ej. "book-open", "paw-print").
 */
private val ICONS: Map<String, ImageVector> = mapOf(
    "book-open" to Icons.Filled.MenuBook,
    "hash" to Icons.Filled.Tag,
    "users" to Icons.Filled.Group,
    "paw-print" to Icons.Filled.Pets,
    "palette" to Icons.Filled.Palette,
    "user" to Icons.Filled.Person,
    "home" to Icons.Filled.Home,
    "globe" to Icons.Filled.Public,
    "utensils" to Icons.Filled.Restaurant,
    "music" to Icons.Filled.MusicNote,
    "calendar" to Icons.Filled.CalendarMonth,
    "map-pin" to Icons.Filled.LocationOn,
    "sun" to Icons.Filled.WbSunny,
    "moon" to Icons.Filled.DarkMode,
    "leaf" to Icons.Filled.Eco,
    "shirt" to Icons.Filled.Checkroom,
    "package" to Icons.Filled.Inventory2,
    "trophy" to Icons.Filled.EmojiEvents,
    "star" to Icons.Filled.Star,
    "medal" to Icons.Filled.MilitaryTech,
    "award" to Icons.Filled.WorkspacePremium,
    "flame" to Icons.Filled.LocalFireDepartment,
    "target" to Icons.Filled.GpsFixed,
    "zap" to Icons.Filled.Bolt,
    "heart" to Icons.Filled.Favorite,
    "bell" to Icons.Filled.Notifications,
    "clock" to Icons.Filled.Schedule,
    "arrow-up" to Icons.Filled.ArrowUpward,
    "sparkles" to Icons.Filled.AutoAwesome,
    "lock" to Icons.Filled.Lock,
)

/** Ícono correspondiente a una clave (icon_emoji); usa "sparkles" si la clave no existe. */
fun iconFor(name: String?): ImageVector =
    (name?.let { ICONS[it] }) ?: ICONS.getValue("sparkles")
