# Unsupervised_LMs

Esta carpeta reúne la documentación de los escenarios de **Machine Learning no supervisado** de Tutunaku. Estos métodos no requieren una etiqueta objetivo previamente conocida. Su función es descubrir grupos, relaciones, componentes, rutas y comportamientos atípicos que no son evidentes al revisar los registros individualmente.

Los resultados no supervisados no deben interpretarse automáticamente como categorías pedagógicas verdaderas. Un cluster es una agrupación matemática que necesita estabilidad, descripción y validación humana antes de convertirse en una decisión de producto.

## 1. Objetivo

- Descubrir patrones de uso y aprendizaje.
- Agrupar ejercicios con comportamientos similares.
- Identificar rutas frecuentes entre contenidos.
- Detectar anomalías para revisión.
- Simplificar métricas complejas.
- Organizar vocabulario y variantes con apoyo de especialistas.
- Mejorar experiencia de usuario, notificaciones y contenido.

## 2. Archivos actuales

```text
Unsupervised_LMs/
├── README.md
└── clustering_notes.md
```

### `clustering_notes.md`

Documento de trabajo para registrar experimentos de clustering: variables, escalado, número de clusters, métodos comparados, métricas, perfiles encontrados, gráficos y revisión pedagógica.

Debe indicar claramente si los nombres de los clusters son provisionales y evitar etiquetas que juzguen a las personas.

## 3. Escenarios no supervisados

### U01. Segmentación por preferencias de interacción

**Pregunta:** ¿qué patrones aparecen según el uso de audio, lectura, juegos, repetición y experiencias?

| Elemento | Definición |
|---|---|
| Unidad | Usuario en una ventana de 28 días |
| Variables | Proporciones de modalidad, tiempo activo, repetición, juegos, finalización y XP |
| Algoritmos | K-means o Gaussian Mixture Models |
| Métricas | Silhouette, Davies-Bouldin y estabilidad por remuestreo |
| Acción | Variar formato y orden de recomendaciones |

Control: hablar de preferencias observadas, no de estilos de aprendizaje permanentes. El usuario debe conservar acceso a todas las modalidades.

### U02. Descubrimiento de rutas temáticas

**Pregunta:** ¿qué lecciones, palabras, juegos o experiencias aparecen juntas o en una secuencia frecuente?

| Elemento | Definición |
|---|---|
| Unidad | Secuencia por sesión o semana |
| Variables | Contenidos vistos/completados, errores, abandonos y orden |
| Algoritmos | Apriori, FP-Growth o PrefixSpan |
| Métricas | Soporte, confianza, lift y estabilidad temporal |
| Acción | Proponer prerrequisitos y rutas de repaso |

Control: una asociación no demuestra causalidad y el contenido menos frecuente no debe desaparecer.

### U03. Agrupación de ejercicios por patrones de fallo

**Pregunta:** ¿qué ejercicios comparten tasas de error, abandono, tiempo o intentos similares?

| Elemento | Definición |
|---|---|
| Unidad | Ejercicio-versión-nivel |
| Variables | Fallos, abandono, p50/p90 de tiempo, pistas, intentos y vidas perdidas |
| Algoritmos | K-means, DBSCAN o clustering jerárquico |
| Métricas | Silhouette, ARI por bootstrap y casos confirmados |
| Acción | Priorizar revisión y rediseño |

Control: un outlier puede ser contenido avanzado, un audio defectuoso o una pregunta ambigua. Requiere diagnóstico humano.

### U04. Detección de anomalías y comportamiento sospechoso

**Pregunta:** ¿qué sesiones presentan velocidad, XP o secuencias inusuales?

| Elemento | Definición |
|---|---|
| Unidad | Sesión o usuario-día |
| Variables | XP/minuto, ejercicios/minuto, repetición, intervalos, sesiones simultáneas y errores |
| Algoritmos | Isolation Forest, One-Class SVM o DBSCAN |
| Métricas | Precision@k mediante revisión y falsos positivos |
| Acción | Abrir caso de auditoría o corregir duplicidad |

Control: nunca sancionar automáticamente. La conectividad o el uso intensivo legítimo pueden generar anomalías.

### U05. Reducción de dimensiones del progreso

**Pregunta:** ¿qué combinaciones explican la variación de progreso, constancia y participación?

| Elemento | Definición |
|---|---|
| Unidad | Usuario por periodo |
| Variables | XP, nivel, racha, precisión, lecciones, tiempo, juegos, logros y vidas |
| Algoritmo | PCA; UMAP solo como exploración visual adicional |
| Métricas | Varianza explicada, estabilidad de cargas y error de reconstrucción |
| Acción | Crear visualización y simplificar tableros |

Control: los componentes no son calificaciones ni conceptos pedagógicos automáticos.

### U06. Agrupación semántica y fonética de vocabulario

**Pregunta:** ¿qué palabras forman familias de significado, sonido o confusión?

| Elemento | Definición |
|---|---|
| Unidad | Palabra, sentido y variante |
| Variables | Traducción, definición, ejemplo, fonemas, audio, errores y coocurrencia |
| Algoritmos | Embeddings + K-means o clustering jerárquico |
| Métricas | Coherencia, precision@k y aceptación de especialistas |
| Acción | Crear unidades temáticas y ejercicios de contraste |

Control: separar semejanza semántica de semejanza fonética y permitir corrección por parte de la comunidad.

### U07. Segmentación por compromiso

**Pregunta:** ¿qué grupos aparecen al combinar recencia, frecuencia y valor educativo?

| Elemento | Definición |
|---|---|
| Unidad | Usuario-semana |
| Variables | Días desde acceso, sesiones, minutos, lecciones, XP, racha y experiencias |
| Algoritmos | RFM clustering, K-means o jerárquico |
| Métricas | Silhouette, estabilidad y transición entre segmentos |
| Acción | Adaptar bienvenida, continuidad, regreso y retos |

Control: no mostrar nombres ofensivos como “usuarios fantasma” y no discriminar conectividad intermitente.

### U08. Navegación e interacción en React

**Pregunta:** ¿cómo se desplazan los usuarios entre inicio, lecciones, juegos, vidas, niveles, logros y experiencias?

| Elemento | Definición |
|---|---|
| Unidad | Secuencia por sesión |
| Variables | Ruta, componente, evento, tiempo activo, dispositivo y salida |
| Algoritmos | Cadena de Markov y clustering de secuencias |
| Métricas | Cobertura, estabilidad, fuga y tiempo a completar |
| Acción | Reducir pasos y mejorar la interfaz mobile-first |

Control: no capturar teclas, texto privado ni grabaciones invasivas de pantalla.

### U09. Comunidades y variantes lingüísticas

**Pregunta:** ¿qué comunidades comparten vocabulario, pronunciación o respuestas aceptadas?

| Elemento | Definición |
|---|---|
| Unidad | Comunidad/variante y término |
| Variables | Vocabulario, fonética, respuestas, audios y evaluación experta |
| Algoritmos | Clustering jerárquico con distancia Gower o combinada |
| Métricas | Estabilidad, bootstrap y concordancia con especialistas |
| Acción | Aceptar formas válidas y localizar contenido |

Control: no inferir ubicación individual ni declarar una variante como la única correcta. Requiere gobernanza comunitaria.

### U10. Patrones temporales de estudio

**Pregunta:** ¿qué horarios y duraciones predominan en las sesiones de aprendizaje?

| Elemento | Definición |
|---|---|
| Unidad | Sesión o usuario-semana |
| Variables | Hora local, día, duración, actividad, respuesta y zona horaria |
| Algoritmos | K-means con variables cíclicas o DBSCAN |
| Métricas | Silhouette, estabilidad y respuesta a notificaciones |
| Acción | Programar recordatorios, retos y mantenimiento |

Control: respetar descanso y preferencias; no inferir ocupación o hábitos fuera de la aplicación.

## 4. Preparación de variables

Los algoritmos de distancia son sensibles a la escala. Antes de agrupar se debe:

1. Definir la unidad y la ventana temporal.
2. Eliminar duplicados técnicos.
3. Separar datos insuficientes de valores cero.
4. Transformar conteos sesgados con `log1p` cuando corresponda.
5. Escalar variables con StandardScaler o RobustScaler.
6. Revisar correlación y variables dominantes.
7. Comparar resultados con distintas semillas y muestras.
8. Describir los grupos con sus variables, no con suposiciones personales.

Ejemplo:

```python
features = [
    "days_since_last_activity",
    "sessions_28d",
    "active_minutes_28d",
    "lessons_completed_28d",
    "games_completed_28d",
    "xp_earned_28d"
]
```

## 5. Selección del número de clusters

No debe elegirse `k` únicamente porque produce una gráfica atractiva.

Se deben comparar:

- Método del codo o WCSS.
- Silhouette score.
- Davies-Bouldin.
- Tamaño mínimo de cada cluster.
- Estabilidad ante remuestreo.
- Interpretación y utilidad para una decisión real.

Un cluster pequeño puede ser ruido, pero también puede representar una variante o necesidad importante. Nunca debe eliminarse sin análisis.

## 6. Reglas de asociación

Para U02 se utilizan:

```text
support(A,B) = ocurrencias(A y B) / total_transacciones
confidence(A -> B) = support(A,B) / support(A)
lift(A -> B) = confidence(A -> B) / support(B)
```

Umbrales iniciales de exploración:

- Soporte mayor o igual a 0.03.
- Confianza mayor o igual a 0.50.
- Lift mayor o igual a 1.20.

Estos valores deben ajustarse al volumen real y validarse en otro periodo.

## 7. Estructura recomendada por escenario

```text
Unsupervised_LMs/
└── U07_engagement_segments/
    ├── README.md
    ├── config.yaml
    ├── build_features.py
    ├── cluster.py
    ├── profile_clusters.py
    ├── evaluate_stability.py
    ├── tests/
    └── artifacts/
        ├── metrics.json
        ├── centroids.csv
        └── model_card.md
```

## 8. Salida recomendada

```json
{
  "analysis_id": "uuid",
  "scenario_id": "U07",
  "generated_at": "2026-08-13T20:00:00Z",
  "entity_id": "user_uuid",
  "cluster_id": 2,
  "cluster_name": "regreso_suave",
  "membership_score": 0.74,
  "top_characteristics": [
    "high_recency",
    "low_frequency",
    "previous_progress"
  ],
  "recommended_action": "optional_short_activity",
  "model_version": "1.0.0",
  "expires_at": "2026-08-20T20:00:00Z"
}
```

## 9. Validación mínima

- Comparar más de un algoritmo o parametrización.
- Repetir con distintas semillas y remuestreo.
- Medir estabilidad de los grupos.
- Describir centroides o variables dominantes.
- Revisar tamaño y cobertura.
- Validar interpretación con responsables pedagógicos.
- Probar la decisión mediante experimento antes de automatizarla.
- Recalcular periódicamente; los usuarios pueden cambiar de comportamiento.

## 10. Errores que se deben evitar

- Asumir que los clusters son categorías naturales o permanentes.
- Asignar nombres negativos a grupos de usuarios.
- Utilizar variables sin escalar en K-means.
- Elegir `k` únicamente por el método del codo.
- Considerar causal una regla de asociación.
- Sancionar automáticamente a una anomalía.
- Publicar agrupaciones lingüísticas sin revisión comunitaria.
- Utilizar UMAP o t-SNE como prueba definitiva de separación.

## 11. Navegación

- [Volver a DataModels](../README.md)
- [Volver al README principal](../../README.md)
- [Notas de clustering](./clustering_notes.md)
- [Documentación de base de datos](../../Docs/Database.md)

