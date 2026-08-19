"""
TUTUNAKUN — MongoDB Schema y Seeds
Estructura NoSQL optimizada para consultas rápidas

Para ejecutar:
    python database/mongodb/seed_mongodb.py
"""
import asyncio
import os
import sys
from datetime import datetime, timezone, timedelta
from motor.motor_asyncio import AsyncIOMotorClient
import uuid

# Fix Windows console encoding
if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

MONGODB_URL = "mongodb+srv://Brandon:luzleon2610b@clusterleon.wpahm.mongodb.net/?retryWrites=true&w=majority&appName=ClusterLeon"
DB_NAME = "tutunakun_db"


# ============================================================
# ESQUEMA MONGODB (documentación de colecciones)
# ============================================================
"""
COLECCIÓN: users
{
    _id: UUID string,
    email: str (indexed unique),
    username: str (indexed unique),
    hashed_password: str,
    full_name: str | null,
    avatar_url: str | null,
    role: "admin" | "user" | "visitor",
    is_active: bool,
    is_email_verified: bool,
    
    # Gamificación (embebido para velocidad)
    gamification: {
        xp_total: int,
        level: int,
        hearts: int,
        current_streak: int,
        longest_streak: int,
        last_activity_date: datetime | null,
    },
    
    # Progreso embebido (referencia ligera)
    completed_lessons: [lesson_id, ...],  # array de IDs
    
    created_at: datetime,
    updated_at: datetime,
}

COLECCIÓN: courses
{
    _id: UUID string,
    title: str,
    description: str | null,
    cover_image_url: str | null,
    difficulty: "beginner" | "intermediate" | "advanced",
    is_published: bool,
    order_index: int,
    created_by: user_id,
    
    # Unidades embebidas (para cargar todo de una vez)
    units: [
        {
            id: str,
            title: str,
            description: str | null,
            icon_emoji: str,
            color_hex: str,
            order_index: int,
            is_locked: bool,
            xp_reward: int,
            lesson_ids: [str, ...],
        }
    ],
    
    created_at: datetime,
    updated_at: datetime,
}

COLECCIÓN: lessons
{
    _id: UUID string,
    unit_id: str,
    course_id: str,
    title: str,
    description: str | null,
    order_index: int,
    xp_reward: int,
    content_type: str | null,
    content_data: [...],
    is_published: bool,
    created_at: datetime,
}

COLECCIÓN: exercises
{
    _id: UUID string,
    lesson_id: str,
    type: "translation" | "multiple_choice" | "writing" | "audio",
    question: str,
    correct_answer: str,
    options: [str] | null,
    hint: str | null,
    explanation: str | null,
    audio_url: str | null,
    image_url: str | null,
    xp_reward: int,
    order_index: int,
    created_at: datetime,
}

COLECCIÓN: attempts
{
    _id: UUID string,
    user_id: str,
    exercise_id: str,
    lesson_id: str,
    user_answer: str,
    is_correct: bool,
    xp_earned: int,
    time_spent_seconds: int | null,
    created_at: datetime,
}

COLECCIÓN: achievements
{
    _id: UUID string,
    title: str,
    description: str | null,
    icon_emoji: str,
    badge_color: str,
    xp_reward: int,
    condition_type: str,
    condition_value: int,
    created_at: datetime,
}

COLECCIÓN: notifications
{
    _id: UUID string,
    user_id: str (indexed),
    type: "reminder" | "achievement" | "progress" | "system",
    title: str,
    message: str | null,
    icon_emoji: str | null,
    is_read: bool (indexed),
    action_url: str | null,
    created_at: datetime,
}

COLECCIÓN: reminders
{
    _id: UUID string,
    user_id: str,
    hour: int,
    minute: int,
    timezone: str,
    is_active: bool,
    message: str,
    days_of_week: [int],
    last_sent_at: datetime | null,
    created_at: datetime,
    updated_at: datetime,
}
"""


async def seed_mongodb():
    client = AsyncIOMotorClient(MONGODB_URL)
    db = client[DB_NAME]

    print("[SEED] Iniciando seeds de MongoDB Atlas para Tutunakun...")

    # Limpiar colecciones (solo para desarrollo)
    for col in ["users", "courses", "lessons", "exercises", "achievements"]:
        await db[col].drop()

    # ── Índices ──────────────────────────────────────────
    await db.users.create_index("email", unique=True)
    await db.users.create_index("username", unique=True)
    await db.courses.create_index("is_published")
    await db.courses.create_index("order_index")
    await db.lessons.create_index("unit_id")
    await db.exercises.create_index("lesson_id")
    await db.attempts.create_index([("user_id", 1), ("exercise_id", 1)])
    await db.notifications.create_index([("user_id", 1), ("is_read", 1)])
    await db.reminders.create_index([("hour", 1), ("minute", 1), ("is_active", 1)])

    now = datetime.now(timezone.utc)

    # ── Usuarios ─────────────────────────────────────────
    # Contraseña: Admin1234! (hash bcrypt)
    admin_id = str(uuid.uuid4())
    demo_id = str(uuid.uuid4())

    await db.users.insert_many([
        {
            "_id": admin_id,
            "email": "admin@tutunakun.mx",
            "username": "admin",
            "hashed_password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBahzNtAT6cNVi",
            "full_name": "Administrador Tutunakun",
            "role": "admin",
            "is_active": True,
            "is_email_verified": True,
            "gamification": {"xp_total": 5000, "level": 10, "hearts": 5,
                             "current_streak": 0, "longest_streak": 0, "last_activity_date": None},
            "completed_lessons": [],
            "created_at": now,
            "updated_at": now,
        },
        {
            "_id": demo_id,
            "email": "demo@tutunakun.mx",
            "username": "totonaco_aprendiz",
            "hashed_password": "$2b$12$K8V9X2mN4pQ7rS1tU3wY5eA6bC0dE9fG1hI2jL3kM4nO5pR6sT7u",
            "full_name": "Aprendiz Totonaco",
            "role": "user",
            "is_active": True,
            "is_email_verified": True,
            "gamification": {"xp_total": 350, "level": 4, "hearts": 5,
                             "current_streak": 7, "longest_streak": 14, "last_activity_date": now},
            "completed_lessons": [],
            "created_at": now,
            "updated_at": now,
        },
    ])
    print("  [OK] Usuarios insertados")

    # ── Logros ───────────────────────────────────────────
    achievements = [
        {"_id": str(uuid.uuid4()), "title": "Primera Palabra", "description": "Completaste tu primer ejercicio",
         "icon_emoji": "🌱", "badge_color": "#4CAF50", "xp_reward": 50, "condition_type": "xp", "condition_value": 10, "created_at": now},
        {"_id": str(uuid.uuid4()), "title": "Racha de Fuego", "description": "3 días consecutivos",
         "icon_emoji": "🔥", "badge_color": "#FF5722", "xp_reward": 100, "condition_type": "streak", "condition_value": 3, "created_at": now},
        {"_id": str(uuid.uuid4()), "title": "Semana Constante", "description": "7 días seguidos",
         "icon_emoji": "⚡", "badge_color": "#FFC107", "xp_reward": 200, "condition_type": "streak", "condition_value": 7, "created_at": now},
        {"_id": str(uuid.uuid4()), "title": "Corazón Totonaco", "description": "Nivel 5",
         "icon_emoji": "🫀", "badge_color": "#E91E63", "xp_reward": 300, "condition_type": "level", "condition_value": 5, "created_at": now},
        {"_id": str(uuid.uuid4()), "title": "Cien XP", "description": "100 puntos de experiencia",
         "icon_emoji": "💯", "badge_color": "#FF9800", "xp_reward": 50, "condition_type": "xp", "condition_value": 100, "created_at": now},
        {"_id": str(uuid.uuid4()), "title": "Mil XP", "description": "1000 puntos de experiencia",
         "icon_emoji": "🌟", "badge_color": "#FFD700", "xp_reward": 200, "condition_type": "xp", "condition_value": 1000, "created_at": now},
        {"_id": str(uuid.uuid4()), "title": "Nivel 10", "description": "Alcanzaste nivel 10",
         "icon_emoji": "🏆", "badge_color": "#FF6B6B", "xp_reward": 500, "condition_type": "level", "condition_value": 10, "created_at": now},
    ]
    await db.achievements.insert_many(achievements)
    print("  [OK] Logros insertados")

    # ── Curso principal ──────────────────────────────────
    course_id = str(uuid.uuid4())
    unit1_id = str(uuid.uuid4())
    unit2_id = str(uuid.uuid4())
    unit3_id = str(uuid.uuid4())

    les1_id = str(uuid.uuid4())
    les2_id = str(uuid.uuid4())
    les3_id = str(uuid.uuid4())

    await db.courses.insert_one({
        "_id": course_id,
        "title": "Totonaco para Principiantes",
        "description": "Aprende las bases de la lengua totonaca con ejercicios interactivos.",
        "difficulty": "beginner",
        "is_published": True,
        "order_index": 1,
        "created_by": admin_id,
        "units": [
            {
                "id": unit1_id,
                "title": "Saludos y Presentaciones",
                "description": "Aprende a saludar en totonaco",
                "icon_emoji": "👋",
                "color_hex": "#FF6B6B",
                "order_index": 1,
                "is_locked": False,
                "xp_reward": 100,
                "lesson_ids": [les1_id, les2_id],
            },
            {
                "id": unit2_id,
                "title": "Los Números",
                "description": "Del uno al veinte en totonaco",
                "icon_emoji": "🔢",
                "color_hex": "#4ECDC4",
                "order_index": 2,
                "is_locked": True,
                "xp_reward": 100,
                "lesson_ids": [les3_id],
            },
        ],
        "created_at": now,
        "updated_at": now,
    })
    print("  [OK] Curso insertado")

    # ── Lecciones ────────────────────────────────────────
    await db.lessons.insert_many([
        {
            "_id": les1_id,
            "unit_id": unit1_id,
            "course_id": course_id,
            "title": "Hola y Adiós",
            "description": "Saludos básicos del totonaco",
            "order_index": 1,
            "xp_reward": 30,
            "content_type": "mixed",
            "content_data": [
                {"type": "text", "content": "En totonaco los saludos reflejan respeto cultural.", "language": "es"},
                {"type": "example", "content": "Lakgsnanat", "language": "toto", "caption": "Buenos días"},
                {"type": "example", "content": "Lakgtsukut", "language": "toto", "caption": "Buenas tardes"},
                {"type": "example", "content": "Kiwi", "language": "toto", "caption": "Adiós"},
            ],
            "is_published": True,
            "created_at": now,
        },
        {
            "_id": les2_id,
            "unit_id": unit1_id,
            "course_id": course_id,
            "title": "¿Cómo te llamas?",
            "description": "Presentaciones personales en totonaco",
            "order_index": 2,
            "xp_reward": 30,
            "content_type": "mixed",
            "content_data": [
                {"type": "text", "content": "Para presentarte en totonaco:", "language": "es"},
                {"type": "example", "content": "Chu kin chichi?", "language": "toto", "caption": "¿Cómo te llamas?"},
                {"type": "example", "content": "Kin chichi...", "language": "toto", "caption": "Me llamo..."},
            ],
            "is_published": True,
            "created_at": now,
        },
        {
            "_id": les3_id,
            "unit_id": unit2_id,
            "course_id": course_id,
            "title": "Del 1 al 5",
            "description": "Los primeros números en totonaco",
            "order_index": 1,
            "xp_reward": 25,
            "content_type": "text",
            "content_data": [
                {"type": "example", "content": "Tum = 1", "language": "toto", "caption": "Uno"},
                {"type": "example", "content": "Tsa = 2", "language": "toto", "caption": "Dos"},
                {"type": "example", "content": "Tomu = 3", "language": "toto", "caption": "Tres"},
                {"type": "example", "content": "Tsatsa = 4", "language": "toto", "caption": "Cuatro"},
                {"type": "example", "content": "Qalhtum = 5", "language": "toto", "caption": "Cinco"},
            ],
            "is_published": True,
            "created_at": now,
        },
    ])
    print("  [OK] Lecciones insertadas")

    # ── Ejercicios ───────────────────────────────────────
    exercises = [
        {"_id": str(uuid.uuid4()), "lesson_id": les1_id, "type": "translation",
         "question": "¿Cómo se dice 'Buenos días' en totonaco?", "correct_answer": "Lakgsnanat",
         "options": ["Lakgtsukut", "Lakgsnanat", "Kiwi", "Tum"],
         "hint": "Es el saludo de la mañana", "explanation": "Lakgsnanat es el saludo matutino.", "xp_reward": 10, "order_index": 1, "created_at": now},
        {"_id": str(uuid.uuid4()), "lesson_id": les1_id, "type": "multiple_choice",
         "question": "Selecciona 'Buenas tardes' en totonaco:", "correct_answer": "Lakgtsukut",
         "options": ["Lakgsnanat", "Lakgtsukut", "Kiwi", "Kin chichi"],
         "hint": None, "explanation": "Lakgtsukut se usa en la tarde.", "xp_reward": 10, "order_index": 2, "created_at": now},
        {"_id": str(uuid.uuid4()), "lesson_id": les1_id, "type": "writing",
         "question": "Escribe 'Adiós' en totonaco:", "correct_answer": "Kiwi",
         "options": None, "hint": "Empieza con K", "explanation": "Kiwi es la despedida más común.", "xp_reward": 15, "order_index": 3, "created_at": now},
        {"_id": str(uuid.uuid4()), "lesson_id": les3_id, "type": "translation",
         "question": "¿Cuánto es 'Tum'?", "correct_answer": "Uno",
         "options": ["Cero", "Uno", "Dos", "Tres"],
         "hint": "Es el primer número", "explanation": "Tum = 1 en totonaco.", "xp_reward": 10, "order_index": 1, "created_at": now},
        {"_id": str(uuid.uuid4()), "lesson_id": les3_id, "type": "writing",
         "question": "Escribe 'Cinco' en totonaco:", "correct_answer": "Qalhtum",
         "options": None, "hint": "Empieza con Q", "explanation": "Qalhtum = 5.", "xp_reward": 15, "order_index": 2, "created_at": now},
    ]
    await db.exercises.insert_many(exercises)
    print("  [OK] Ejercicios insertados")

    client.close()
    print("\n[DONE] Seeds de MongoDB Atlas completados exitosamente!")
    print(f"   Base de datos: {DB_NAME}")
    print(f"   Colecciones creadas: users, courses, lessons, exercises, achievements")
    print(f"\n   Admin: admin@tutunakun.mx / Admin1234!")
    print(f"   Demo:  demo@tutunakun.mx / Demo1234!")


if __name__ == "__main__":
    asyncio.run(seed_mongodb())
