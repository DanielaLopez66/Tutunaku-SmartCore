# Arquitectura Wearable

**Tecnología**: Kotlin + Jetpack Compose para Wear OS (proyecto nativo de Android Studio).
**Propósito**: Mostrar racha, XP, vidas, notificaciones y la palabra del día en Totonaco,
sincronizados en tiempo real con el backend de Tutunaku vía REST + Socket.IO.

## Por qué Kotlin nativo (y no React Native/Expo, como decía la versión anterior de este documento)

Se decidió construir la app como proyecto Kotlin nativo para Wear OS en vez de
React Native/Expo. No se creó un backend nuevo para el wearable: reutiliza
exactamente los mismos endpoints que ya consume la app web
(`Deliverables/WebApp/source/backend`).

## Estructura

```text
Deliverables/WearableApp/source/
├── settings.gradle.kts, build.gradle.kts, gradle.properties, local.properties
├── gradlew, gradlew.bat, gradle/wrapper/      # wrapper de Gradle real
└── app/                                        # módulo de la app (Android Studio)
    ├── build.gradle.kts
    └── src/main/
        ├── AndroidManifest.xml
        ├── res/                                # tema, ícono adaptativo, network security config
        └── kotlin/mx/tutunaku/wearable/
            ├── MainActivity.kt, TutunakuWearApp.kt
            ├── data/                            # modelos, Retrofit, Socket.IO, DataStore
            └── ui/                              # ViewModel, navegación y pantallas Compose
```

## Backend reutilizado (sin endpoints nuevos, salvo lo indicado)

- `POST /api/v1/auth/login`, `POST /api/v1/auth/refresh` — mismo JWT que la web.
- `GET /api/v1/users/me/stats` — XP, nivel, vidas, racha actual y récord.
- `GET/PATCH /api/v1/notifications` — notificaciones (incluye recordatorios,
  que ahora sí se disparan: ver `app/sockets/server.py`).
- `GET /api/v1/exercises/word-of-day` — **nuevo**, palabra del día en totonaco
  (elegida de forma determinista por fecha), retoma el propósito original de
  este documento.
- Socket.IO (`app/sockets/server.py`): el backend une cada conexión
  autenticada a una sala personal `user:<id>` y emite `user_stats_updated` y
  `new_notification` — el wearable y la web reciben ambos los mismos eventos
  en tiempo real sin lógica adicional en el cliente.

## Cómo correrlo

1. Abrir esta carpeta (`Deliverables/WearableApp/source`) directamente en
   Android Studio como proyecto existente.
2. Levantar el backend con `uvicorn app.main:socket_app --reload --port 8000`
   (ver README del backend).
3. En un emulador de Wear OS, `10.0.2.2:8000` ya apunta al backend local por
   defecto (configurado en Ajustes de la app). En un reloj físico, cambia la
   URL en Ajustes por la IP LAN de tu backend.

## Equipo de Desarrollo

| Integrante | Contacto | Rol |
| --- | --- | --- |
| Ana Daniela López Neri | [@DanielaLopez66](https://github.com/DanielaLopez66) | Encargada de Documentación y Líder de Equipo |
| Brandon León Cabrera | [@bleon26](https://github.com/bleon26) | Encargado de Base de Datos |
| Tania Ibarra Salgado | [@ibarra-tania](https://github.com/ibarra-tania) | Encargada del Desarrollo |
