import asyncio
from sqlalchemy import text
from app.core.database import get_session_factory, get_mysql_engine
from app.models.mysql_models import Course, Unit, Lesson, Exercise, ExerciseType, DifficultyLevel

async def seed_data():
    session_factory = get_session_factory()
    async with session_factory() as session:
        print("Limpiando base de datos...")
        await session.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
        await session.execute(text("TRUNCATE TABLE exercise_attempts;"))
        await session.execute(text("TRUNCATE TABLE exercises;"))
        await session.execute(text("TRUNCATE TABLE user_progress;"))
        await session.execute(text("TRUNCATE TABLE lessons;"))
        await session.execute(text("TRUNCATE TABLE units;"))
        await session.execute(text("TRUNCATE TABLE courses;"))
        await session.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
        await session.commit()

        print("Insertando curso base...")
        course = Course(
            id="course-1",
            title="Totonaco Básico",
            description="Curso introductorio de Totonaco",
            color_hex="#E879F9",
            difficulty=DifficultyLevel.beginner,
            is_published=True,
            order_index=1
        )
        session.add(course)

        print("Insertando unidades (categorías)...")
        units_data = [
            ("unit-1", "Fundamentos", "Aprende las bases del idioma", "book-open", "#8B5CF6", 1),
            ("unit-2", "Números", "Aprende a contar", "hash", "#10B981", 2),
            ("unit-3", "La Familia", "Miembros de la familia", "users", "#F59E0B", 3),
            ("unit-4", "Animales", "Fauna y mascotas", "paw-print", "#3B82F6", 4),
            ("unit-5", "Colores", "Identifica los colores", "palette", "#EC4899", 5),
            ("unit-6", "El Cuerpo", "Partes del cuerpo humano", "user", "#06B6D4", 6)
        ]
        for u in units_data:
            session.add(Unit(id=u[0], course_id="course-1", title=u[1], description=u[2], icon_emoji=u[3], color_hex=u[4], order_index=u[5], is_locked=False))

        print("Insertando lecciones...")
        lessons_data = [
            # Fundamentos
            ("lesson-1", "unit-1", "Saludos Básicos", 1),
            ("lesson-2", "unit-1", "Presentaciones", 2),
            ("lesson-3", "unit-1", "Despedidas", 3),
            # Numeros
            ("lesson-4", "unit-2", "Contando 1-5", 1),
            ("lesson-5", "unit-2", "Contando 6-10", 2),
            # Familia
            ("lesson-6", "unit-3", "Miembros principales", 1),
            # Animales
            ("lesson-7", "unit-4", "Mascotas", 1),
            # Colores
            ("lesson-8", "unit-5", "Colores Básicos", 1),
            # El Cuerpo
            ("lesson-9", "unit-6", "Partes de la Cara", 1)
        ]
        
        lesson_contents = {
            "lesson-1": [
                {"type": "example", "content": "Tlen", "caption": "Hola", "pronunciation": "Tlen", "example_sentence": "Tlen, ¿la tlan?", "language": "toto"},
                {"type": "example", "content": "Kuwinima", "caption": "Buenos días", "pronunciation": "Ku-wí-ni-ma", "example_sentence": "Kuwinima, Juan", "language": "toto"},
                {"type": "example", "content": "Kotanuma", "caption": "Buenas tardes", "pronunciation": "Ko-ta-nu-ma", "example_sentence": "Kotanuma, Kukc", "language": "toto"},
                {"type": "example", "content": "Tsishwama", "caption": "Buenas noches", "pronunciation": "Tsi-shwa-ma", "example_sentence": "Tsishwama, Pop", "language": "toto"}
            ],
            "lesson-2": [
                {"type": "example", "content": "¿Chi Wanikana?", "caption": "¿Cómo te llamas?", "pronunciation": "Chi wa-ni-ka-na", "example_sentence": "Tlen, ¿Chi Wanikana?", "language": "toto"},
                {"type": "example", "content": "Kit Kin Wanikan.", "caption": "Yo me llamo...", "pronunciation": "Kit Kin Wanikan", "example_sentence": "Kit Kin Wanikan, Pedro.", "language": "toto"},
                {"type": "example", "content": "Pashuwa ik laktsiman", "caption": "Mucho gusto", "pronunciation": "Pa-shu-wa ik lak-tsi-man", "example_sentence": "Pashuwa ik laktsiman, jose", "language": "toto"}
            ],
            "lesson-3": [
                {"type": "example", "content": "Anpuntsunaj", "caption": "Hasta Luego", "pronunciation": "An-pun-tsu-naj", "example_sentence": "Anpuntsunaj, Antonio", "language": "toto"},
                {"type": "example", "content": "La lacktsina lakali", "caption": "Hasta mañana", "pronunciation": "La lack-tsi-na la-ka-li", "example_sentence": "La lacktsina lakali, Maria", "language": "toto"}
            ],
            "lesson-4": [
                {"type": "example", "content": "Aktin", "caption": "Uno (1)", "pronunciation": "Ak-tin", "example_sentence": "Aktin Laxax", "language": "toto"},
                {"type": "example", "content": "Aktu", "caption": "Dos (2)", "pronunciation": "Ak-tu", "example_sentence": "Aktu Kahlwat", "language": "toto"},
                {"type": "example", "content": "Aktutun", "caption": "Tres (3)", "pronunciation": "Ak-tu-tun", "example_sentence": "Aktutun Skatan", "language": "toto"},
                {"type": "example", "content": "Aktati", "caption": "Cuatro (4)", "pronunciation": "Ak-ta-ti", "example_sentence": "Aktati Jaka", "language": "toto"},
                {"type": "example", "content": "Akkitsis", "caption": "Cinco (5)", "pronunciation": "Ak-kit-sis", "example_sentence": "Akkitsis Limaj", "language": "toto"}
            ],
            "lesson-5": [
                {"type": "example", "content": "Akchaxan", "caption": "Seis (6)", "pronunciation": "Ak-cha-xan", "example_sentence": "Akchaxan Segna", "language": "toto"},
                {"type": "example", "content": "Aktujun", "caption": "Siete (7)", "pronunciation": "Ak-tu-jun", "example_sentence": "Aktujun Akchikiwi", "language": "toto"},
                {"type": "example", "content": "Aktsallan", "caption": "Ocho (8)", "pronunciation": "Ak-tsal-lan", "example_sentence": "Aktsallan Shipa", "language": "toto"},
                {"type": "example", "content": "Akanajatsa", "caption": "Nueve (9)", "pronunciation": "A-ka-na-ja-tsa", "example_sentence": "Akanajatsa kukunu", "language": "toto"},
                {"type": "example", "content": "Akkaw", "caption": "Diez (10)", "pronunciation": "Ak-kaw", "example_sentence": "Akkaw Kukataj", "language": "toto"}
            ],
            "lesson-6": [
                {"type": "example", "content": "Puskat", "caption": "Mujer / Esposa", "pronunciation": "Pus-kat", "example_sentence": "Kinpúska", "language": "toto"},
                {"type": "example", "content": "Chixku", "caption": "Hombre / Esposo", "pronunciation": "Chíx-ku", "example_sentence": "Kinchíxku", "language": "toto"},
                {"type": "example", "content": "Tsit", "caption": "Madre", "pronunciation": "Tsi-t", "example_sentence": "Kintsit", "language": "toto"},
                {"type": "example", "content": "Tata", "caption": "Padre", "pronunciation": "Ta-ta", "example_sentence": "Kintata", "language": "toto"}
            ],
            "lesson-7": [
                {"type": "example", "content": "Chichi", "caption": "Perro", "pronunciation": "Chi-chi", "example_sentence": "Katla chichi", "language": "toto"},
                {"type": "example", "content": "Mistu", "caption": "Gato", "pronunciation": "Mí-tsu", "example_sentence": "Putsenke mistu", "language": "toto"},
                {"type": "example", "content": "Kashlilh", "caption": "Pollo", "pronunciation": "Kash-lilh", "example_sentence": "Kewanit Kashlilh", "language": "toto"}
            ],
            "lesson-8": [
                {"type": "example", "content": "Smukuku", "caption": "Amarillo", "pronunciation": "Smu-kú-ku", "example_sentence": "Smukuku staku", "language": "toto"},
                {"type": "example", "content": "Tsutsuku", "caption": "Rojo", "pronunciation": "Tsu-tsú-ku", "example_sentence": "Tsutsuku Xanat", "language": "toto"},
                {"type": "example", "content": "Stalanka", "caption": "Blanco", "pronunciation": "Sta-lan-ka", "example_sentence": "Stalanka Polhnu", "language": "toto"},
                {"type": "example", "content": "Putsenke", "caption": "Negro", "pronunciation": "Put-sen-ke", "example_sentence": "Putsenke chichi", "language": "toto"}
            ],
            "lesson-9": [
                {"type": "example", "content": "Akxak", "caption": "Cabeza", "pronunciation": "Ak-xak", "example_sentence": "Katsan Kin akxak", "language": "toto"},
                {"type": "example", "content": "Lakastapun", "caption": "Ojo", "pronunciation": "La-kas-tá-pun", "example_sentence": "Kin lakastapun", "language": "toto"},
                {"type": "example", "content": "Kini", "caption": "Nariz", "pronunciation": "Kí-ni", "example_sentence": "Kin kini ik li jaxanan", "language": "toto"},
                {"type": "example", "content": "Kilhni", "caption": "Boca", "pronunciation": "Kílh-ni", "example_sentence": "Kin kilhni ik li wallan", "language": "toto"}
            ]
        }

        for l in lessons_data:
            content = lesson_contents.get(l[0], [{"type": "text", "content": "Aprende estas palabras."}])
            session.add(Lesson(id=l[0], unit_id=l[1], title=l[2], order_index=l[3], xp_reward=20, is_published=True, content_type="mixed", content_data=content))

        await session.commit()

        print("Insertando ejercicios...")
        exercises_data = [
            # Lesson 1
            ("ex-1", "lesson-1", "multiple_choice", '¿Cómo se dice "Hola" en Totonaco?', "Tlen", ["Tlen", "Nak", "Kachin", "Xitit"], 1),
            ("ex-2", "lesson-1", "multiple_choice", '¿Cómo se dice "Buenos días"?', "Kuwinima", ["Kuwinima", "Kotanuma", "Tsishwama", "Tlen"], 2),
            ("ex-3", "lesson-1", "multiple_choice", '¿Qué significa "Kotanuma"?', "Buenas tardes", ["Buenos días", "Buenas tardes", "Hola", "Buenas noches"], 3),
            ("ex-4", "lesson-1", "multiple_choice", '¿Cómo se dice "Buenas noches"?', "Tsishwama", ["Kuwinima", "Kotanuma", "Tlen", "Tsishwama"], 4),
            # Lesson 2
            ("ex-5", "lesson-2", "multiple_choice", '¿Cómo se pregunta "¿Cómo te llamas?"', "¿Chi Wanikana?", ["¿Chi Wanikana?", "¿La tlan?", "¿Tlen?", "¿Kit nawan?"], 1),
            ("ex-6", "lesson-2", "multiple_choice", 'Traduce: "Kit Kin Wanikan."', "Yo me llamo...", ["¿Cómo te llamas?", "Hola", "Yo me llamo...", "Mucho gusto"], 2),
            ("ex-7", "lesson-2", "multiple_choice", '¿Cómo se dice "Mucho gusto"?', "Pashuwa ik laktsiman", ["Pashuwa ik laktsiman", "Tlen", "Anpuntsunaj", "Kotanuma"], 3),
            # Lesson 3
            ("ex-8", "lesson-3", "multiple_choice", '¿Qué significa "Anpuntsunaj"?', "Hasta Luego", ["Hola", "Buenas tardes", "Por favor", "Hasta Luego"], 1),
            ("ex-9", "lesson-3", "multiple_choice", '¿Cómo se dice "Hasta mañana"?', "La lacktsina lakali", ["Anpuntsunaj", "La lacktsina lakali", "Tlen", "Kuwinima"], 2),
            # Lesson 4
            ("ex-10", "lesson-4", "multiple_choice", '¿Qué número es "Aktin"?', "Uno (1)", ["Dos (2)", "Uno (1)", "Tres (3)", "Cinco (5)"], 1),
            ("ex-11", "lesson-4", "multiple_choice", 'Traduce "Dos" a Totonaco', "Aktu", ["Aktutun", "Aktin", "Aktu", "Aktati"], 2),
            ("ex-12", "lesson-4", "multiple_choice", 'Identifica el número 3:', "Aktutun", ["Aktu", "Aktati", "Aktutun", "Akkitsis"], 3),
            ("ex-13", "lesson-4", "multiple_choice", '¿Cómo se dice "Cinco"?', "Akkitsis", ["Akkitsis", "Aktin", "Aktati", "Aktu"], 4),
            # Lesson 5
            ("ex-14", "lesson-5", "multiple_choice", '¿Cuál es el número 6 en Totonaco?', "Akchaxan", ["Aktujun", "Aktsallan", "Akchaxan", "Akkaw"], 1),
            ("ex-15", "lesson-5", "multiple_choice", '¿Qué número es "Aktujun"?', "Siete (7)", ["Seis (6)", "Ocho (8)", "Siete (7)", "Nueve (9)"], 2),
            ("ex-16", "lesson-5", "multiple_choice", '¿Cómo se dice "Diez"?', "Akkaw", ["Aktsallan", "Akanajatsa", "Akchaxan", "Akkaw"], 3),
            # Lesson 6
            ("ex-17", "lesson-6", "multiple_choice", '¿Cómo se dice "Madre" en Totonaco?', "Tsit", ["Tata", "Tsit", "Puskat", "Chixku"], 1),
            ("ex-18", "lesson-6", "multiple_choice", 'Elige la palabra para "Padre":', "Tata", ["Tsit", "Tata", "Chixku", "Puskat"], 2),
            ("ex-19", "lesson-6", "multiple_choice", '¿Qué significa "Puskat"?', "Mujer / Esposa", ["Hombre / Esposo", "Niño", "Hermano", "Mujer / Esposa"], 3),
            # Lesson 7
            ("ex-20", "lesson-7", "multiple_choice", '¿Qué es un "Chichi"?', "Perro", ["Gato", "Pollo", "Pájaro", "Perro"], 1),
            ("ex-21", "lesson-7", "multiple_choice", '¿Cómo se le dice al "Gato"?', "Mistu", ["Kashlilh", "Mistu", "Chichi", "Luw"], 2),
            ("ex-22", "lesson-7", "multiple_choice", 'Identifica la palabra "Pollo"', "Kashlilh", ["Mistu", "Kashlilh", "Chichi", "Totol"], 3),
            # Lesson 8
            ("ex-23", "lesson-8", "multiple_choice", '¿Cómo se dice "Rojo" en Totonaco?', "Tsutsuku", ["Stalanka", "Tsutsuku", "Putsenke", "Smukuku"], 1),
            ("ex-24", "lesson-8", "multiple_choice", '¿Qué color es "Smukuku"?', "Amarillo", ["Blanco", "Negro", "Amarillo", "Rojo"], 2),
            ("ex-25", "lesson-8", "multiple_choice", 'Identifica el color "Putsenke"', "Negro", ["Negro", "Blanco", "Azul", "Rojo"], 3),
            ("ex-26", "lesson-8", "multiple_choice", '¿Cómo se dice "Blanco"?', "Stalanka", ["Putsenke", "Tsutsuku", "Stalanka", "Smukuku"], 4),
            # Lesson 9
            ("ex-27", "lesson-9", "multiple_choice", '¿Qué parte del cuerpo es "Lakastapun"?', "Ojo", ["Cabeza", "Ojo", "Nariz", "Boca"], 1),
            ("ex-28", "lesson-9", "multiple_choice", '¿Cómo se dice "Boca" en Totonaco?', "Kilhni", ["Kini", "Akxak", "Lakastapun", "Kilhni"], 2),
            ("ex-29", "lesson-9", "multiple_choice", 'Identifica la palabra "Cabeza"', "Akxak", ["Kilhni", "Lakastapun", "Akxak", "Kini"], 3),
            ("ex-30", "lesson-9", "multiple_choice", 'Traduce "Kini"', "Nariz", ["Ojo", "Nariz", "Boca", "Cabeza"], 4),
        ]
        
        for e in exercises_data:
            session.add(Exercise(id=e[0], lesson_id=e[1], type=ExerciseType.multiple_choice, question=e[3], correct_answer=e[4], options=e[5], order_index=e[6]))

        await session.commit()
        print("Base de datos recreada con éxito! (Usando SQLAlchemy)")

if __name__ == "__main__":
    asyncio.run(seed_data())
