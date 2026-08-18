# WearableApp

## Qué es

La aplicación nativa para relojes **Wear OS** de Tutunaku, escrita en
**Kotlin + Wear Compose Material 3 Expressive** (el estándar de diseño
actual de Google para Wear OS). Sincroniza racha, XP, corazones,
notificaciones y la palabra del día en totonaco con la plataforma, en
tiempo real vía Socket.IO.

## Para qué sirve

- Da acceso rápido, sin sacar el celular, a: la palabra o frase del día en
  totonaco (con audio de pronunciación), las estadísticas del usuario,
  notificaciones, y un minijuego corto para recuperar corazones.
- Funciona **de forma independiente** (standalone): tiene su propia sesión
  y su propia conexión a la API, sin necesitar un celular cerca.
- Cuando está emparejada con la aplicación móvil (`MobileApp`), además
  recibe la sesión iniciada en el celular automáticamente (sin teclear
  usuario y contraseña en una pantalla tan pequeña) y le avisa al celular
  cuando el usuario gana XP desde el reloj.

## Estructura

```
WearableApp/
└── source/
    └── app/
        └── src/main/kotlin/mx/tutunaku/wearable/
            ├── MainActivity.kt, TutunakuWearApp.kt
            ├── data/
            │   ├── model/Models.kt
            │   ├── network/{ApiClient,ApiService,SocketManager}.kt
            │   ├── repository/{Auth,Stats,Notifications}Repository.kt
            │   ├── wear/{WatchSyncManager,PhoneAuthListenerService}.kt
            │   └── TokenStore.kt
            └── ui/
                ├── theme/, navigation/WearNavHost.kt, MainViewModel.kt
                └── screens/
                    ├── Splash, Home
                    ├── WordOfDay, Notifications
                    ├── HeartGame, Settings
                    └── WearScaffold, WatchTextField (componentes compartidos)
```

## Aspectos importantes

- **Wear Compose Material 3 Expressive**: usa `AppScaffold`/`ScreenScaffold`
  y `TransformingLazyColumn` (respetan solos el borde curvo de la pantalla
  circular, sin padding fijo calculado a mano) y `EdgeButton` para el botón
  principal de cada pantalla.
- **App standalone**: declara
  `com.google.android.wearable.standalone = true` — no depende de tener un
  celular emparejado para funcionar; el emparejamiento es un plus, no un
  requisito.
- **Sincronización con el celular vía Wearable Data Layer API**:
  `PhoneAuthListenerService` recibe la sesión que manda el celular, y
  `WatchSyncManager` le avisa al celular cuando sube el XP del usuario —
  enganchado al mismo evento en tiempo real que ya usa el resto de la app,
  no a una pantalla específica.
- **Ahorro de batería consciente**: un `ProcessLifecycleOwner` pausa la
  conexión de Socket.IO cuando la app pasa a segundo plano.
- Por defecto apunta a `http://10.0.2.2:8000/`, configurable desde la
  pantalla de Ajustes sin recompilar.

## Documentación completa

📄 [`DeployManual/WearableApp - Manual de Despliegue.pdf`](DeployManual/WearableApp%20-%20Manual%20de%20Despliegue.pdf) — arquitectura completa, cada pantalla explicada, la migración a Material 3 Expressive, la sincronización con el celular paso a paso, y cómo compilarla e instalarla.
