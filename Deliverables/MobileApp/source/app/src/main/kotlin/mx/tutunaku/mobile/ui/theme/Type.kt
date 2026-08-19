package mx.tutunaku.mobile.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.googlefonts.Font
import androidx.compose.ui.text.googlefonts.GoogleFont
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.sp
import mx.tutunaku.mobile.R

/**
 * Mismo split tipográfico que frontend/tailwind.config.js: "Baloo 2" para
 * títulos/display, "Nunito" para cuerpo. Se descargan vía el proveedor de
 * Google Fonts (sin empaquetar .ttf) — si no hay Play Store/internet,
 * Compose cae solo a la tipografía del sistema, sin crash.
 */
private val fontProvider = GoogleFont.Provider(
    providerAuthority = "com.google.android.gms.fonts",
    providerPackage = "com.android.vending",
    certificates = R.array.com_google_android_gms_fonts_certs,
)

private val BalooFont = GoogleFont("Baloo 2")
private val NunitoFont = GoogleFont("Nunito")

val DisplayFontFamily = FontFamily(
    Font(googleFont = BalooFont, fontProvider = fontProvider, weight = FontWeight.Normal),
    Font(googleFont = BalooFont, fontProvider = fontProvider, weight = FontWeight.SemiBold),
    Font(googleFont = BalooFont, fontProvider = fontProvider, weight = FontWeight.Bold),
)

val BodyFontFamily = FontFamily(
    Font(googleFont = NunitoFont, fontProvider = fontProvider, weight = FontWeight.Normal),
    Font(googleFont = NunitoFont, fontProvider = fontProvider, weight = FontWeight.Medium),
    Font(googleFont = NunitoFont, fontProvider = fontProvider, weight = FontWeight.SemiBold),
    Font(googleFont = NunitoFont, fontProvider = fontProvider, weight = FontWeight.Bold),
)

val TutunakuTypography = Typography(
    displayLarge = TextStyle(fontFamily = DisplayFontFamily, fontWeight = FontWeight.Bold, fontSize = 36.sp),
    displayMedium = TextStyle(fontFamily = DisplayFontFamily, fontWeight = FontWeight.Bold, fontSize = 30.sp),
    headlineLarge = TextStyle(fontFamily = DisplayFontFamily, fontWeight = FontWeight.Bold, fontSize = 26.sp),
    headlineMedium = TextStyle(fontFamily = DisplayFontFamily, fontWeight = FontWeight.SemiBold, fontSize = 22.sp),
    titleLarge = TextStyle(fontFamily = DisplayFontFamily, fontWeight = FontWeight.SemiBold, fontSize = 20.sp),
    titleMedium = TextStyle(fontFamily = DisplayFontFamily, fontWeight = FontWeight.SemiBold, fontSize = 17.sp),
    bodyLarge = TextStyle(fontFamily = BodyFontFamily, fontWeight = FontWeight.Normal, fontSize = 16.sp),
    bodyMedium = TextStyle(fontFamily = BodyFontFamily, fontWeight = FontWeight.Normal, fontSize = 14.sp),
    bodySmall = TextStyle(fontFamily = BodyFontFamily, fontWeight = FontWeight.Normal, fontSize = 12.sp),
    labelLarge = TextStyle(fontFamily = BodyFontFamily, fontWeight = FontWeight.SemiBold, fontSize = 14.sp),
    labelMedium = TextStyle(fontFamily = BodyFontFamily, fontWeight = FontWeight.SemiBold, fontSize = 12.sp),
    labelSmall = TextStyle(fontFamily = BodyFontFamily, fontWeight = FontWeight.Medium, fontSize = 11.sp),
)
