import asyncio
import os
import json
import cloudinary
import cloudinary.uploader
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
from dotenv import load_dotenv

AUDIO_MAP_LESSONS = {
    "Hola.m4a": "Hola",
    "Buenos dias.m4a": "Buenos días",
    "Buenas Tardes.m4a": "Buenas tardes",
    "Buenas Noches.m4a": "Buenas noches",
    "como te llamas.m4a": "¿Cómo te llamas?",
    "Yo me llamo.m4a": "Yo me llamo...",
    "Mucho gusto.m4a": "Mucho gusto",
    "Hasta luego.m4a": "Hasta Luego",
    "Hasta mañana.m4a": "Hasta mañana",
    "Uno.m4a": "Uno (1)",
    "Dos.m4a": "Dos (2)",
    "Tres.m4a": "Tres (3)",
    "Cuatro.m4a": "Cuatro (4)",
    "Cinco.m4a": "Cinco (5)",
    "Seis.m4a": "Seis (6)",
    "Siete.m4a": "Siete (7)",
    "Ocho.m4a": "Ocho (8)",
    "Nueve.m4a": "Nueve (9)",
    "Diez.m4a": "Diez (10)",
    "Amarillo.m4a": "Amarillo",
    "Blanco.m4a": "Blanco",
    "Negro.m4a": "Negro",
    "Rojo.m4a": "Rojo",
    "Cabeza.m4a": "Cabeza",
    "Ojo.m4a": "Ojo",
    "Boca.m4a": "Boca",
    "Nariz.m4a": "Nariz",
    "Hombre.m4a": "Hombre",
    "Mujer o Esposa.m4a": "Mujer o Esposa",
    "Padre o Papá.m4a": "Padre o Papá",
    "Madre o Mamá.m4a": "Madre o Mamá",
    "Perro.m4a": "Perro",
    "Gato.m4a": "Gato",
    "Pollo.m4a": "Pollo"
}

AUDIO_MAP_EXERCISES = {
    "Hola.m4a": "¿Cómo se dice \"Hola\" en Totonaco?",
    "Buenos dias.m4a": "¿Cómo se dice \"Buenos días\"?",
    "Buenas Tardes.m4a": "¿Qué significa \"Kotanuma\"?",
    "Buenas Noches.m4a": "¿Cómo se dice \"Buenas noches\"?",
    "como te llamas.m4a": "¿Cómo se pregunta \"¿Cómo te llamas?\"",
    "Yo me llamo.m4a": "Traduce: \"Kit Kin Wanikan.\"",
    "Mucho gusto.m4a": "¿Cómo se dice \"Mucho gusto\"?",
    "Hasta luego.m4a": "¿Qué significa \"Anpuntsunaj\"?",
    "Hasta mañana.m4a": "¿Cómo se dice \"Hasta mañana\"?",
    "Uno.m4a": "¿Qué número es \"Aktin\"?",
    "Dos.m4a": "Traduce \"Dos\" a Totonaco",
    "Tres.m4a": "Identifica el número 3:",
    "Cinco.m4a": "¿Cómo se dice \"Cinco\"?",
    "Seis.m4a": "¿Cuál es el número 6 en Totonaco?",
    "Siete.m4a": "¿Qué número es \"Aktujun\"?",
    "Diez.m4a": "¿Cómo se dice \"Diez\"?"
}

UPLOADS_DIR = "uploads"

# 1. Configurar Cloudinary
cloudinary.config(
  cloud_name = "nctgkk5f",
  api_key = "336234965369988",
  api_secret = "c_Tv6maY7aBbwRz1mwvXp9YRhPc",
  secure = True
)

async def upload_and_update_db():
    load_dotenv()
    db_url = f"mysql+aiomysql://{os.getenv('MYSQL_USER')}:{os.getenv('MYSQL_PASSWORD')}@{os.getenv('MYSQL_HOST')}:{os.getenv('MYSQL_PORT')}/{os.getenv('MYSQL_DATABASE')}"
    engine = create_async_engine(db_url)
    
    file_to_url = {}

    print("--- 1. SUBIENDO AUDIOS A CLOUDINARY ---")
    if os.path.exists(UPLOADS_DIR):
        for filename in os.listdir(UPLOADS_DIR):
            if filename.endswith(".m4a"):
                file_path = os.path.join(UPLOADS_DIR, filename)
                print(f"Subiendo {filename}...")
                try:
                    res = cloudinary.uploader.upload(file_path, resource_type="auto", folder="tutunakun_audios")
                    secure_url = res.get("secure_url")
                    print(f" -> Éxito: {secure_url}")
                    file_to_url[filename] = secure_url
                    
                    os.remove(file_path)
                    print(f" -> Archivo local eliminado.")
                except Exception as e:
                    print(f" -> Error al subir {filename}: {e}")
    else:
        print(f"Directorio {UPLOADS_DIR} no encontrado.")

    print("\n--- 2. ACTUALIZANDO BASE DE DATOS ---")
    if not file_to_url:
        print("No hay archivos para actualizar.")
        return

    async with engine.connect() as conn:
        res = await conn.execute(text("SELECT id, content_data FROM lessons"))
        lessons = res.fetchall()
        for lesson in lessons:
            if lesson.content_data:
                content = json.loads(lesson.content_data) if isinstance(lesson.content_data, str) else lesson.content_data
                updated = False
                for block in content:
                    if block.get('type') == 'example' and 'caption' in block:
                        for filename, caption in AUDIO_MAP_LESSONS.items():
                            if block['caption'] == caption and filename in file_to_url:
                                block['audio_url'] = file_to_url[filename]
                                updated = True
                
                if updated:
                    await conn.execute(
                        text("UPDATE lessons SET content_data = :data WHERE id = :id"),
                        {"data": json.dumps(content), "id": lesson.id}
                    )
                    print(f"Lección actualizada: {lesson.id}")

        res = await conn.execute(text("SELECT id, question FROM exercises"))
        exercises = res.fetchall()
        for exercise in exercises:
            for filename, question in AUDIO_MAP_EXERCISES.items():
                if exercise.question == question and filename in file_to_url:
                    await conn.execute(
                        text("UPDATE exercises SET audio_url = :url WHERE id = :id"),
                        {"url": file_to_url[filename], "id": exercise.id}
                    )
                    print(f"Ejercicio actualizado: {exercise.id} con {filename}")
        
        await conn.commit()
    
    await engine.dispose()
    print("\n¡Proceso completado con éxito!")

if __name__ == "__main__":
    asyncio.run(upload_and_update_db())
