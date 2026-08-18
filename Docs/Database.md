# 🗄️ Tutunakun — Diagrama de Base de Datos MySQL

## Diagrama Lógico de Relaciones

```
┌─────────────────────────────────────────────────────────────────┐
│                      TUTUNAKUN DATABASE                         │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐       ┌──────────────────┐      ┌─────────────────┐
│    USERS     │       │    COURSES        │      │     UNITS       │
│──────────────│       │──────────────────│      │─────────────────│
│ id (PK)      │◄──┐   │ id (PK)          │◄──┐  │ id (PK)         │
│ email UNIQUE │   │   │ title            │   │  │ course_id (FK)  │◄─┐
│ username     │   │   │ description      │   │  │ title            │  │
│ role         │   │   │ difficulty       │   │  │ icon_emoji       │  │
│ xp_total     │   │   │ is_published     │   │  │ color_hex        │  │
│ level        │   │   │ order_index      │   │  │ order_index      │  │
│ hearts       │   │   │ created_by (FK)──┼───┘  │ is_locked        │  │
│ streak       │   │   └──────────────────┘      │ xp_reward        │  │
└──────────────┘   │                             └─────────────────┘  │
       │            │   ┌──────────────────┐               │           │
       │            │   │    LESSONS        │◄──────────────┘           │
       │            │   │──────────────────│      ┌───────────────┐    │
       │            │   │ id (PK)          │◄──┐  │   COURSES     │────┘
       │            │   │ unit_id (FK)─────┼───┘  └───────────────┘
       │            │   │ title            │
       │            │   │ content_type     │      ┌─────────────────┐
       │            │   │ content_data JSON│      │   EXERCISES     │
       │            │   │ xp_reward        │      │─────────────────│
       │            │   │ is_published     │◄─────│ id (PK)         │
       │            │   └──────────────────┘      │ lesson_id (FK)  │
       │            │                             │ type            │
       │            │   ┌──────────────────┐      │ question        │
       │            │   │  USER_PROGRESS   │      │ correct_answer  │
       │            │   │──────────────────│      │ options JSON    │
       ├────────────┼──►│ user_id (FK)     │      │ xp_reward       │
       │            │   │ lesson_id (FK)   │      └─────────────────┘
       │            │   │ is_completed     │              │
       │            │   │ completion_%     │      ┌─────────────────┐
       │            │   │ score            │      │ EXERCISE_ATTEMPTS│
       │            │   └──────────────────┘      │─────────────────│
       │            │                             │ id (PK)         │
       │            │   ┌──────────────────┐      │ user_id (FK)────┼──►USERS
       │            │   │  ACHIEVEMENTS    │      │ exercise_id (FK)┼──►EXERCISES
       │            │   │──────────────────│      │ user_answer     │
       │            │   │ id (PK)          │      │ is_correct      │
       │            │   │ title            │      │ xp_earned       │
       │            │   │ condition_type   │      └─────────────────┘
       │            │   │ condition_value  │
       │            │   └──────────────────┘
       │            │          │
       │            │   ┌──────────────────┐
       │            │   │USER_ACHIEVEMENTS │
       ├────────────┼──►│ user_id (FK)     │
       │            │   │ achievement_id(FK┼──►ACHIEVEMENTS
       │            │   │ earned_at        │
       │            │   └──────────────────┘
       │            │
       │            │   ┌──────────────────┐     ┌──────────────────┐
       │            │   │  REFRESH_TOKENS  │     │  NOTIFICATIONS   │
       ├────────────┼──►│ user_id (FK)     │  ┌─►│ user_id (FK)     │
       │            │   │ token UNIQUE     │  │  │ type             │
       │            │   │ is_revoked       │  │  │ title            │
       │            │   │ expires_at       │  │  │ is_read          │
       │            │   └──────────────────┘  │  └──────────────────┘
       │            │                         │
       │            │   ┌──────────────────┐  │  ┌──────────────────┐
       │            │   │  DAILY_STREAKS   │  │  │    REMINDERS     │
       ├────────────┼──►│ user_id (FK)     │  ├─►│ user_id (FK)     │
       │            │   │ streak_date      │  │  │ hour             │
       │            │   │ xp_today         │  │  │ minute           │
       │            │   └──────────────────┘  │  │ days_of_week JSON│
       │            │                         │  │ is_active        │
       │            │   ┌──────────────────┐  │  └──────────────────┘
       │            │   │ PASSWORD_RESETS  │  │
       ├────────────┼──►│ user_id (FK)     │  │  ┌──────────────────┐
       │            │   │ token UNIQUE     │  │  │EMAIL_VERIFICATION│
       │            │   │ is_used          │  └─►│ user_id (FK)     │
       └────────────┴──►│ expires_at       │     │ token UNIQUE     │
                        └──────────────────┘     │ is_used          │
                                                 └──────────────────┘
```

## Tablas: 16 en total

| # | Tabla | Propósito |
|---|-------|-----------|
| 1 | `users` | Usuarios del sistema con datos de gamificación |
| 2 | `courses` | Cursos educativos |
| 3 | `units` | Unidades temáticas dentro de cursos |
| 4 | `lessons` | Lecciones con contenido educativo JSON |
| 5 | `exercises` | Ejercicios con 4 tipos diferentes |
| 6 | `exercise_attempts` | Historial de respuestas |
| 7 | `user_progress` | Progreso por lección (UNIQUE user+lesson) |
| 8 | `achievements` | Catálogo de insignias/logros |
| 9 | `user_achievements` | Logros ganados por usuarios |
| 10 | `daily_streaks` | Registro de rachas diarias |
| 11 | `refresh_tokens` | Tokens JWT de sesión larga |
| 12 | `password_resets` | Tokens de recuperación de contraseña |
| 13 | `email_verifications` | Tokens de verificación de email |
| 14 | `notifications` | Notificaciones del sistema |
| 15 | `reminders` | Recordatorios de estudio configurados |
| 16 | Vista: `user_learning_summary` | Vista agregada para dashboards |

## Índices Clave

```sql
-- Búsqueda de usuarios
INDEX idx_users_role (role)
INDEX idx_users_active (is_active)
UNIQUE uq_users_email (email)
UNIQUE uq_users_username (username)

-- Consultas de contenido
INDEX idx_courses_published (is_published)
INDEX idx_units_course (course_id)
INDEX idx_lessons_unit (unit_id)
INDEX idx_exercises_lesson (lesson_id)

-- Gamificación
UNIQUE uq_user_lesson_progress (user_id, lesson_id)
UNIQUE uq_user_achievement (user_id, achievement_id)
UNIQUE uq_user_streak_date (user_id, streak_date)

-- Seguridad
UNIQUE uq_refresh_token (token)
INDEX idx_refresh_user (user_id)
INDEX idx_notif_user_unread (user_id, is_read)
INDEX idx_reminders_time (hour, minute, is_active)
```
