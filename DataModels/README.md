# DataModels

Esta carpeta documenta la capa de datos utilizada por **TUTUNAKU-SMARTCORE**. Su función es definir de dónde provienen los datos, cómo deben relacionarse, qué variables se pueden utilizar y qué reglas de calidad se deben cumplir antes de entrenar o ejecutar un modelo de Machine Learning.

No debe confundirse con una carpeta exclusiva de archivos de modelos entrenados. `DataModels` representa el puente entre la información generada por Tutunaku y los algoritmos supervisados o no supervisados.

## 1. Responsabilidad de la carpeta

- Describir las fuentes MySQL y MongoDB.
- Definir unidades de análisis y fechas de corte.
- Establecer variables reutilizables por escenario.
- Documentar etiquetas de modelos supervisados.
- Definir matrices de características para análisis no supervisados.
- Evitar fuga de información entre entrenamiento y evaluación.
- Mantener reglas de calidad, privacidad y versionado.
- Separar datos crudos, procesados y resultados de modelos.

## 2. Organización

```text
DataModels/
├── README.md
├── Supervised_LMs/
│   ├── README.md
│   └── translation_model_notes.md
└── Unsupervised_LMs/
    ├── README.md
    └── clustering_notes.md
```

| Carpeta | Contenido |
|---|---|
| [`Supervised_LMs/`](./Supervised_LMs/README.md) | Escenarios con etiqueta objetivo: clasificación, regresión y series temporales. |
| [`Unsupervised_LMs/`](./Unsupervised_LMs/README.md) | Escenarios sin etiqueta previa: clustering, asociaciones, anomalías y PCA. |

## 3. Fuentes principales

### 3.1 MySQL o MariaDB

MySQL funciona como fuente transaccional para la identidad y el estado de aprendizaje. Los nombres exactos pueden ajustarse al esquema implementado, pero el modelo lógico contempla:

| Tabla | Campos relevantes | Uso analítico |
|---|---|---|
| `users` | `user_id`, `hearts`, `xp_total`, `level`, `current_streak`, `longest_streak`, `last_activity_date`, `created_at` | Perfil de progreso, retención, compromiso y gamificación |
| `courses` | `course_id`, `name`, `is_published` | Contexto del curso |
| `units` | `unit_id`, `course_id`, `order_index` | Secuencia curricular |
| `lessons` | `lesson_id`, `unit_id`, `order_index`, `content_data`, `is_published` | Contenido y orden de lecciones |
| `exercises` | `exercise_id`, `lesson_id`, `type`, `difficulty`, `hint`, `explanation`, `audio_url`, `image_url` | Características del ejercicio |
| `exercise_attempts` | `user_id`, `exercise_id`, `is_correct`, `time_spent_seconds`, `xp_earned`, `created_at` | Entrenamiento y evaluación del desempeño |
| `user_progress` | `user_id`, `lesson_id`, `completion_percentage`, `score`, `attempts_count` | Avance y calificación |
| `achievements` | `achievement_id`, `condition_type`, `condition_value` | Definición de logros |
| `user_achievements` | `user_id`, `achievement_id`, `acquired_at` | Historial de logros obtenidos |
| `reminders` | `user_id`, `days_of_week`, `timezone`, `enabled` | Notificaciones y patrones temporales |

### 3.2 MongoDB

MongoDB almacena contenido y eventos con estructura flexible.

| Colección | Contenido | Uso analítico |
|---|---|---|
| `lessons` | Bloques de texto, audio, video, cultura y ejercicios embebidos | Modalidad y contenido flexible |
| `exercises` | Preguntas, respuestas, variantes y multimedia | Dificultad y análisis lingüístico |
| `attempts` | Interacciones de alta frecuencia y respuestas | Errores, tiempos y secuencias |
| `audio_attempts` | Audio, metadatos, palabra y evaluación | Pronunciación supervisada |
| `ui_events` | Rutas, clics, componentes y duración activa | Navegación y experiencia React |
| `game_experience_events` | Juegos, retos, torneos y experiencias | Éxito, vidas, XP y compromiso |
| `notifications` | Envío, apertura y respuesta | Evaluación de recordatorios |
| `technical_metrics` | Latencia, errores, peticiones y concurrencia | Predicción de carga y anomalías |

## 4. Identificador común

El proyecto utiliza un identificador global compatible entre MySQL y MongoDB. La recomendación es emplear UUID y mantener la misma referencia lógica en ambas bases.

```text
MySQL users.user_id  <---->  MongoDB user_id
```

Reglas:

- No utilizar correo o nombre como llave de unión analítica.
- Seudonimizar `user_id` cuando se exporten datasets.
- Validar que no existan identificadores huérfanos.
- Aplicar idempotencia mediante `event_id` en eventos.

## 5. Unidades de análisis

Cada escenario requiere una unidad definida. Mezclar unidades genera duplicidad y resultados incorrectos.

| Unidad | Ejemplo | Escenarios relacionados |
|---|---|---|
| Usuario-día | Actividad acumulada hasta una fecha | S01, U07 |
| Usuario-lección | Estado antes o después de una lección | S04, U02 |
| Intento | Una respuesta a un ejercicio | S02, S05 |
| Audio | Una pronunciación de palabra o frase | S03 |
| Usuario-actividad | Inicio de juego, reto o experiencia | S06 |
| Test de colocación | Respuestas de diagnóstico | S07 |
| Intervalo temporal | Métricas cada cinco minutos | S08 |
| Ejercicio-versión-nivel | Agregados de rendimiento | S09, U03 |
| Usuario-logro | Elegibilidad y obtención | S10 |
| Sesión | Secuencia de navegación o actividad | U04, U08, U10 |
| Palabra-variante | Término, audio y contexto | U06, U09 |

## 6. Contrato recomendado de eventos

Todo evento debe compartir una estructura mínima.

| Grupo | Campos |
|---|---|
| Identidad | `event_id`, `user_id`, `session_id`, `request_id` |
| Tiempo | `client_timestamp`, `server_timestamp`, `timezone`, `active_ms`, `network_wait_ms` |
| Contexto | `event_type`, `route_name`, `lesson_id`, `exercise_id`, `game_id`, `experience_id` |
| Gamificación | `level`, `hearts_before`, `hearts_after`, `xp_before`, `xp_after`, `streak` |
| Resultado | `completed`, `is_correct`, `score`, `quit_reason`, `error_category` |
| Trazabilidad | `content_version`, `app_version`, `experiment_id`, `model_version`, `consent_version` |

## 7. Capas de datos

Se recomienda separar físicamente o lógicamente las siguientes capas:

### 7.1 Datos crudos

Información registrada directamente por los sistemas de Tutunaku. Debe conservarse sin modificaciones destructivas y con permisos restringidos.

Ejemplos:

- Intentos individuales.
- Eventos de navegación.
- Estados de vidas y XP.
- Audios con consentimiento.
- Métricas técnicas.

### 7.2 Datos limpios

Registros con tipos corregidos, identificadores validados, duplicados eliminados y tiempos normalizados.

### 7.3 Variables o features

Tablas creadas para modelado con una fecha de corte explícita.

```text
user_daily_features
exercise_daily_features
user_lesson_features
content_sequences
technical_metrics_5m
```

### 7.4 Resultados

Predicciones, clusters, métricas y recomendaciones. Deben incluir versión del modelo y fecha de generación.

## 8. Reglas de calidad

Antes de utilizar un dataset se deben validar los siguientes puntos:

### Integridad

- `user_id`, `lesson_id` y `exercise_id` deben existir en su fuente principal.
- Los intentos deben pertenecer a un ejercicio y una versión válidos.
- Los valores de XP, nivel y vidas no pueden ser negativos.

### Unicidad

- `event_id` no debe repetirse.
- Un mismo evento de finalización no debe otorgar XP dos veces.
- Las uniones no deben multiplicar intentos accidentalmente.

### Consistencia temporal

- `completed_at` debe ser posterior a `started_at`.
- Las variables de entrenamiento solo pueden usar información disponible antes de la fecha de predicción.
- Los cambios de versión de contenido deben estar fechados.

### Rango

- `completion_percentage`: 0 a 100.
- `score`: de acuerdo con la escala oficial, preferiblemente 0 a 100.
- `time_spent_seconds`: positivo y dentro de límites razonables.
- `hearts`: dentro del máximo configurado por la plataforma.

### Completitud

- Medir porcentaje de nulos por campo.
- Diferenciar entre dato ausente, no aplicable y valor cero.
- No imputar audios o variantes lingüísticas como si fueran datos numéricos comunes.

## 9. Prevención de fuga de información

Existe fuga cuando el modelo recibe datos que no estarían disponibles al momento de producir la predicción.

Ejemplos que se deben evitar:

- Predecir abandono usando actividad ocurrida después de la fecha de corte.
- Predecir calificación incluyendo intentos de la misma lección después de iniciar.
- Predecir un logro utilizando su fecha de obtención.
- Clasificar dificultad mezclando versiones nuevas y anteriores del mismo ejercicio.
- Separar audios aleatoriamente y permitir que la misma persona aparezca en entrenamiento y prueba.

## 10. División de datasets

| Problema | División recomendada |
|---|---|
| Usuarios y progreso | Temporal y por usuario |
| Pronunciación | Por hablante, palabra, clase y variante |
| Contenido | Por versión y fecha de publicación |
| Series temporales | Backtesting con ventanas consecutivas |
| Clustering | Remuestreo para comprobar estabilidad |

Una división inicial puede ser 70% entrenamiento, 15% validación y 15% prueba, pero la fecha y la unidad tienen prioridad sobre el porcentaje exacto.

## 11. Privacidad y minimización

No deben incluirse en los datasets de modelado:

- Contraseñas o hashes de contraseña.
- Tokens de acceso, recuperación o verificación.
- Correos sin seudonimizar.
- Geolocalización precisa.
- Texto de pulsaciones o captura invasiva de pantalla.
- Audio sin consentimiento y regla de retención.

La región o variante lingüística solo debe utilizarse para inclusión y calidad cultural, no para castigar o limitar al estudiante.

## 12. Versionado

Todo dataset procesado debe incluir:

```yaml
dataset_name: user_daily_features
scenario_id: S01
version: 1.0.0
cutoff_date: 2026-08-13
source_schema_version: 1.0
rows: 0
created_by: data_pipeline
label_definition: churn_14d
```

Convención sugerida:

```text
{scenario_id}_{dataset_name}_{cutoff_date}_{version}.parquet
S01_user_daily_features_2026-08-13_v1.parquet
```

## 13. Estructura futura recomendada

Cuando comiencen las pruebas con datos y código, la carpeta puede crecer de forma controlada:

```text
DataModels/
├── schemas/
├── validation/
├── feature_definitions/
├── Supervised_LMs/
│   ├── configs/
│   ├── notebooks/
│   ├── src/
│   ├── tests/
│   └── artifacts/
└── Unsupervised_LMs/
    ├── configs/
    ├── notebooks/
    ├── src/
    ├── tests/
    └── artifacts/
```

No se deben subir datasets personales crudos ni modelos que incluyan datos sensibles al repositorio público.

## 14. Lista de verificación

- [ ] La unidad de análisis está definida.
- [ ] Existe una fecha de corte.
- [ ] La etiqueta no usa información futura.
- [ ] Los identificadores fueron validados y seudonimizados.
- [ ] Los duplicados fueron eliminados.
- [ ] Se documentaron nulos y exclusiones.
- [ ] El contenido y el dataset tienen versión.
- [ ] La división de evaluación respeta usuarios y tiempo.
- [ ] La información sensible tiene consentimiento y retención.
- [ ] El responsable de datos aprobó el dataset.

## 15. Navegación

- [Volver al README principal](../README.md)
- [Modelos supervisados](./Supervised_LMs/README.md)
- [Modelos no supervisados](./Unsupervised_LMs/README.md)
- [Documentación de base de datos](../Docs/Database.md)

