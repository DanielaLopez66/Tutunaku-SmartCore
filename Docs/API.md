# Tutunakun API — Documentación de Endpoints

**Base URL:** `http://localhost:8000/api/v1`  
**Swagger UI:** `http://localhost:8000/docs`  
**ReDoc:** `http://localhost:8000/redoc`

---

##  Autenticación

Todos los endpoints protegidos requieren el header:
```
Authorization: Bearer <access_token>
```

---

## AUTH `/auth`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | ❌ | Registro de nuevo usuario |
| `POST` | `/auth/login` | ❌ | Inicio de sesión, retorna JWT |
| `POST` | `/auth/refresh` | ❌ | Renovar access token |
| `POST` | `/auth/logout` | ❌ | Invalidar refresh token |
| `POST` | `/auth/verify-email` | ❌ | Verificar email con token |
| `POST` | `/auth/forgot-password` | ❌ | Solicitar recuperación de contraseña |
| `POST` | `/auth/reset-password` | ❌ | Restablecer contraseña con token |

### POST `/auth/register`
```json
// Request
{
  "email": "usuario@ejemplo.com",
  "username": "mi_usuario",
  "password": "MiPass123",
  "full_name": "Mi Nombre"
}

// Response 201
{
  "success": true,
  "message": "Registro exitoso. Revisa tu email.",
  "data": { "user_id": "uuid" }
}
```

### POST `/auth/login`
```json
// Request
{ "email": "usuario@ejemplo.com", "password": "MiPass123" }

// Response 200
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

## Usuarios `/users`

| Método | Endpoint | Auth | Rol | Descripción |
|--------|----------|------|-----|-------------|
| `GET` | `/users/me` | ✅ | user | Perfil propio |
| `PATCH` | `/users/me` | ✅ | user | Actualizar perfil |
| `GET` | `/users/me/stats` | ✅ | user | Estadísticas de aprendizaje |

### GET `/users/me/stats`
```json
// Response 200
{
  "xp_total": 350,
  "level": 4,
  "hearts": 5,
  "current_streak": 7,
  "longest_streak": 14,
  "lessons_completed": 3,
  "exercises_correct": 45,
  "exercises_total": 55,
  "accuracy_percentage": 81.8,
  "achievements_count": 2
}
```

---

##  Cursos `/courses`

| Método | Endpoint | Auth | Rol | Descripción |
|--------|----------|------|-----|-------------|
| `GET` | `/courses` | ❌ | - | Listar cursos publicados |
| `GET` | `/courses/{id}` | ❌ | - | Obtener curso |
| `POST` | `/courses` | ✅ | admin | Crear curso |
| `PATCH` | `/courses/{id}` | ✅ | admin | Actualizar curso |
| `DELETE` | `/courses/{id}` | ✅ | admin | Eliminar curso |

---

##  Unidades `/units`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/units/course/{course_id}` | ❌ | Unidades de un curso |
| `POST` | `/units` | ✅ admin | Crear unidad |

---

## Lecciones `/lessons`

| Método | Endpoint | Auth | Rol | Descripción |
|--------|----------|------|-----|-------------|
| `GET` | `/lessons/unit/{unit_id}` | ❌ | - | Lecciones de una unidad |
| `GET` | `/lessons/{id}` | ❌ | - | Obtener lección (con contenido educativo) |
| `POST` | `/lessons` | ✅ | admin | Crear lección |
| `POST` | `/lessons/{id}/complete` | ✅ | user | Marcar lección como completada |

---

##  Ejercicios `/exercises`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/exercises/lesson/{lesson_id}` | ✅ | Ejercicios de una lección |
| `POST` | `/exercises/{id}/attempt` | ✅ | Enviar respuesta |

### POST `/exercises/{id}/attempt`
```json
// Request
{
  "user_answer": "Lakgsnanat",
  "time_spent_seconds": 8
}

// Response 200
{
  "is_correct": true,
  "correct_answer": "Lakgsnanat",
  "explanation": "Lakgsnanat es el saludo matutino en totonaco.",
  "xp_earned": 10,
  "hearts_remaining": 5,
  "user_stats": {
    "xp_total": 360,
    "level": 4,
    "current_streak": 7
  }
}
```

**Errores especiales:**
- `403 NO_HEARTS` — Sin corazones disponibles, esperar regeneración
- `404` — Ejercicio no encontrado

---

##  Logros `/achievements`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/achievements` | ❌ | Todos los logros disponibles |
| `GET` | `/achievements/me` | ✅ | Logros del usuario autenticado |

---

##  Notificaciones `/notifications`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/notifications` | ✅ | Mis notificaciones (últimas 50) |
| `PATCH` | `/notifications/{id}/read` | ✅ | Marcar como leída |
| `PATCH` | `/notifications/read-all` | ✅ | Marcar todas como leídas |

---

##  Recordatorios `/reminders`

| Método | Endpoint | Auth | Descripción |
|--------|----------|------|-------------|
| `GET` | `/reminders` | ✅ | Mis recordatorios |
| `POST` | `/reminders` | ✅ | Crear recordatorio (máx. 3) |
| `PATCH` | `/reminders/{id}` | ✅ | Actualizar recordatorio |
| `DELETE` | `/reminders/{id}` | ✅ | Eliminar recordatorio |

### POST `/reminders`
```json
// Request
{
  "hour": 8,
  "minute": 30,
  "timezone": "America/Mexico_City",
  "message": "¡Hora de aprender totonaco! ",
  "days_of_week": [0, 1, 2, 3, 4]
}

// Response 201
{
  "success": true,
  "message": "Recordatorio creado",
  "data": { "id": "uuid", "time": "08:30" }
}
```

---

##  Administración `/admin` (requiere rol admin)

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/admin/metrics` | Métricas globales del sistema |
| `GET` | `/admin/users` | Lista de todos los usuarios |
| `PATCH` | `/admin/users/{id}` | Actualizar rol/estado de usuario |
| `DELETE` | `/admin/users/{id}/progress` | Reiniciar progreso de usuario |
| `POST` | `/admin/achievements/{ach_id}/award/{user_id}` | Otorgar insignia manualmente |

---

##  Códigos de Error

| Código | Descripción |
|--------|-------------|
| `VALIDATION_ERROR` | Datos de entrada inválidos |
| `UNAUTHORIZED` | Token inválido o expirado |
| `FORBIDDEN` | Sin permisos suficientes |
| `NOT_FOUND` | Recurso no encontrado |
| `CONFLICT` | Email/username ya existe |
| `NO_HEARTS` | Sin corazones disponibles |
| `INTERNAL_ERROR` | Error interno del servidor |

### Formato de error estándar
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "Ejercicio no encontrado",
    "details": []
  }
}
```

---

## Seguridad

- **JWT HS256** con expiración de 30 minutos
- **Refresh tokens** rotativos (7 días)
- **bcrypt** para hashing de contraseñas
- **Rate limiting** 60 req/min por IP
- **CORS** configurado para frontend
- Validación estricta con **Pydantic v2**
