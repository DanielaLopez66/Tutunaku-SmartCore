# MobileApp

## Qué es

La aplicación nativa de **Android** de Tutunaku, escrita en **Kotlin +
Jetpack Compose**. Consume la misma API que la web y comparte las mismas
cuentas de usuario — no es un sitio empaquetado, es una app 100% nativa.

## Para qué sirve

- Da acceso al mismo aprendizaje que la web (cursos, lecciones, ejercicios,
  XP, corazones, rachas) directamente desde el celular.
- Muestra el progreso como un **camino de niveles visual** (estilo
  Duolingo): un solo recorrido serpenteante por todas las lecciones de un
  curso, agrupadas por unidad, con el color y el ícono real de cada una.
- Se sincroniza con la aplicación de reloj (`WearableApp`) cuando ambas
  están emparejadas: comparte la sesión iniciada en el celular con el reloj,
  y recibe una notificación cuando el usuario gana XP desde el reloj.

## Estructura

```
MobileApp/
├── source/
│   ├── settings.gradle.kts, build.gradle.kts
│   └── app/
│       ├── build.gradle.kts
│       └── src/main/kotlin/mx/tutunaku/mobile/
│           ├── MainActivity.kt, TutunakuMobileApp.kt
│           ├── data/
│           │   ├── model/Models.kt                    # espejo de los esquemas del backend
│           │   ├── network/{ApiClient,ApiService,SocketManager}.kt
│           │   ├── repository/{Auth,Stats,Content,Exercise}Repository.kt
│           │   ├── wear/{WatchSyncManager,WatchMessageListenerService}.kt
│           │   ├── audio/AudioPlayer.kt
│           │   └── TokenStore.kt
│           └── ui/
│               ├── theme/, util/ColorUtils.kt, components/IconRegistry.kt
│               ├── navigation/MobileNavHost.kt, MainViewModel.kt
│               └── screens/
│                   ├── Splash, Login, Register
│                   ├── Home, LearningPathScreen (el camino de niveles)
│                   ├── LessonDetail, ExerciseFlow
│                   └── Profile
└── DeployManual/                                        # Manual de despliegue completo (.docx y .pdf)
```

## Aspectos importantes

- **Mismo backend que la web**: no tiene su propia base de datos ni lógica
  de negocio — todo vive en `WebApp/source/backend`. Por defecto apunta a
  `http://10.0.2.2:8000/` (el alias del emulador de Android hacia la
  máquina anfitriona); se puede cambiar sin recompilar.
- **Sin framework de inyección de dependencias** (ni Hilt ni Koin): un
  contenedor manual simple en `TutunakuMobileApp` — misma filosofía que
  `WearableApp`.
- **Sincronización con el reloj vía Wearable Data Layer API** — el
  mecanismo oficial de Android para esto, no un sustituto casero. Requiere
  que ambas apps estén emparejadas (con un reloj físico, o con el asistente
  "Wear Pairing" de Android Studio entre dos emuladores con Play Store
  habilitado).
- **Los contadores de lecciones/ejercicios** (`lessons_count`,
  `exercises_count`) dependen de que el backend los calcule correctamente
  — esto se encontró roto y se corrigió durante el desarrollo de esta app
  (ver el manual de despliegue).
- Sin ExoPlayer/Media3: los audios son clips cortos de pronunciación, así
  que basta con `android.media.MediaPlayer`.

## Documentación completa

📄 [`DeployManual/MobileApp - Manual de Despliegue.pdf`](DeployManual/MobileApp%20-%20Manual%20de%20Despliegue.pdf) — arquitectura completa, cada pantalla explicada, cómo funciona el camino de niveles, la sincronización con el reloj paso a paso, cómo compilarla e instalarla, y los problemas reales encontrados durante las pruebas.

## Equipo de Desarrollo

| Integrante | Contacto | Rol |
| --- | --- | --- |
| Ana Daniela López Neri | [@DanielaLopez66](https://github.com/DanielaLopez66) | Encargada de Documentación y Líder de Equipo |
| Brandon León Cabrera | [@bleon26](https://github.com/bleon26) | Encargado de Base de Datos |
| Tania Ibarra Salgado | [@ibarra-tania](https://github.com/ibarra-tania) | Encargada del Desarrollo |
