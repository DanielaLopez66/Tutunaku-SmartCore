package mx.tutunaku.mobile.ui.theme

import androidx.compose.ui.graphics.Color

// Paleta Tutunaku — igual que frontend/tailwind.config.js (sección "alebrije")
// y Deliverables/WearableApp/source/.../ui/theme/Color.kt (mismos hex, esta
// vez con los acentos extra que solo usa la web, ya que el teléfono es una
// app completa como la web, no glanceable como el reloj).
val AlebrijeCoral = Color(0xFFFF6B6B)
val AlebrijeCoralDim = Color(0xFFE05353)
val AlebrijeTeal = Color(0xFF4ECDC4)
val AlebrijeTealDim = Color(0xFF39A8A1)
val AlebrijeSky = Color(0xFF45B7D1)
val AlebrijeMint = Color(0xFF96CEB4)
val AlebrijeViolet = Color(0xFFA29BFE)
val AlebrijeVioletDim = Color(0xFF8479E8)
val AlebrijeGold = Color(0xFFFFEAA7)
val AlebrijeMagenta = Color(0xFFFD79A8)
val AlebrijeLime = Color(0xFF55EFC4)
val AlebrijeOrange = Color(0xFFFDCB6E)
val AlebrijePurple = Color(0xFF6C5CE7)

val ErrorRed = Color(0xFFFF4757)
val ErrorRedDim = Color(0xFFD93B49)

// Superficies — valores exactos de frontend/src/index.css (light/.dark),
// no los de la app del reloj (esta es full light+dark, no solo-oscuro AMOLED).
val LightBg = Color(0xFFFAFAF8)
val LightSurface = Color(0xFFFFFFFF)
val LightText = Color(0xFF1A1A2E)
val LightMuted = Color(0xFF6B7280)
val LightBorder = Color(0xFFE5E7EB)

val DarkBg = Color(0xFF0F0F1A)
val DarkSurface = Color(0xFF1A1A2E)
val DarkText = Color(0xFFF0F0FF)
val DarkMuted = Color(0xFF9CA3AF)
val DarkBorder = Color(0xFF0F3460)
