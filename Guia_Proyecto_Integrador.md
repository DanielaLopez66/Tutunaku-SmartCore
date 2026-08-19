# Guía de Apoyo para el Proyecto Integrador

## Extracción de Conocimiento en Bases de Datos

**Programa educativo:** Ingeniería en Desarrollo y Gestión de Software  
**Cuatrimestre:** Noveno  
**Modalidad:** Proyecto colaborativo  
**Producto final:** Prototipo de sistema inteligente integrado mediante API, modelos de Machine Learning, visualización y consumo desde una aplicación web o wearable  

---

## 1. Propósito del proyecto

El Proyecto Integrador tiene como finalidad que cada equipo diseñe, implemente, evalúe e integre mecanismos de extracción de conocimiento a partir de datos, utilizando técnicas de análisis supervisado y no supervisado.

El proyecto deberá demostrar un proceso completo:

> **Problema → datos → simulación → ETL → EDA → entrenamiento → evaluación → selección de modelos → API inteligente → dashboard → integración → pruebas → documentación.**

El resultado final no deberá limitarse a ejecutar algoritmos en un Notebook. Los modelos seleccionados deberán integrarse a una API y ser consumidos desde un prototipo web o wearable desarrollado en las asignaturas que cursan de manera paralela.

---

## 2. Objetivo general del proyecto

Implementar una solución inteligente mediante la preparación, análisis y procesamiento de conjuntos de datos, la aplicación de modelos supervisados y no supervisados, y su integración en una arquitectura de software basada en API, para apoyar la toma de decisiones y ampliar las funcionalidades de un prototipo web o wearable.

---

## 3. Resultados esperados

Al finalizar el proyecto, el equipo deberá ser capaz de:

- Comprender un problema y convertirlo en una necesidad de análisis.
- Identificar fuentes, tipos y características de los datos.
- Diseñar y simular conjuntos de datos coherentes.
- Implementar un proceso ETL reproducible.
- Realizar análisis exploratorio de datos.
- Construir conjuntos de entrenamiento, validación y prueba.
- Implementar modelos supervisados.
- Implementar modelos no supervisados.
- Evaluar y comparar modelos.
- Seleccionar los modelos con mayor utilidad.
- Integrar modelos mediante endpoints inteligentes.
- Consumir los endpoints desde una aplicación web o wearable.
- Visualizar resultados mediante un dashboard.
- Actualizar información en tiempo real con Socket.IO.
- Diseñar y ejecutar pruebas técnicas y funcionales.
- Documentar el proyecto y trabajar colaborativamente con Git y GitHub.

---

## 4. Alcance obligatorio

Cada equipo deberá desarrollar, como mínimo:

1. Contexto y planteamiento del problema.
2. Metodología de análisis de datos.
3. Veinte propuestas de aplicación:
   - Diez de análisis supervisado.
   - Diez de análisis no supervisado.
4. Descripción de fuentes, entidades, atributos y tipos de datos.
5. Simulación estratégica del dataset.
6. Modelo de Data Warehouse o Data Mart.
7. Proceso ETL.
8. Análisis exploratorio de datos.
9. Implementación de modelos supervisados:
   - Clasificación.
   - Regresión o pronóstico.
10. Implementación de modelos no supervisados:
    - Agrupamiento.
    - Reducción de dimensionalidad.
11. Evaluación y optimización de modelos.
12. Selección de dos mecanismos para despliegue.
13. Dos endpoints inteligentes:
    - Uno supervisado.
    - Uno no supervisado.
14. Dashboard con actualización en tiempo real.
15. Consumo de endpoints desde un prototipo web o wearable.
16. Pruebas del dataset, ETL, modelos, API e integración.
17. Arquitectura de software.
18. Documentación técnica.
19. Evidencias de trabajo colaborativo.
20. Presentación y defensa.

---

# 5. Flujo general de trabajo

```text
Contexto del proyecto
        ↓
Problema y necesidades de información
        ↓
Metodología de análisis
        ↓
Fuentes, entidades y atributos
        ↓
Simulación estratégica
        ↓
Data Warehouse / Data Mart
        ↓
ETL y preparación
        ↓
EDA
        ↓
Modelos supervisados
        ↓
Modelos no supervisados
        ↓
Evaluación y optimización
        ↓
Selección de dos modelos
        ↓
Endpoints inteligentes
        ↓
Dashboard con Socket.IO
        ↓
Consumo web o wearable
        ↓
Pruebas
        ↓
Documentación y defensa
```

---

# 6. Etapas del proyecto

## Etapa 1. Contexto y planteamiento del problema

### Propósito

Definir el escenario de aplicación y explicar qué necesidad será atendida mediante análisis de datos y Machine Learning.

### Actividades

#### 1.1 Describir el contexto

Incluyan:

- Nombre del proyecto.
- Organización, empresa o escenario.
- Proceso principal.
- Usuarios involucrados.
- Problemática actual.
- Información disponible.
- Decisiones que se desean mejorar.
- Aplicación web o wearable con la que se integrará.

#### 1.2 Formular el problema

El problema debe ser específico y medible.

Ejemplos:

- Clasificar pacientes según su nivel de riesgo.
- Predecir demanda de medicamentos.
- Recomendar productos o servicios.
- Detectar comportamientos anómalos.
- Agrupar usuarios por patrones de uso.
- Reducir dimensiones para visualizar perfiles complejos.
- Pronosticar ventas, consumo o solicitudes.
- Identificar patrones de abandono.

#### 1.3 Identificar stakeholders

Ejemplos:

- Administrador.
- Médico.
- Paciente.
- Cliente.
- Usuario.
- Encargado de almacén.
- Analista.
- Responsable de operación.
- Desarrollador.
- Directivo.

#### 1.4 Formular preguntas de análisis

Definan entre cinco y diez preguntas.

Ejemplos:

- ¿Qué variables ayudan a clasificar el nivel de riesgo?
- ¿Qué grupos naturales existen en los datos?
- ¿Qué registros presentan comportamiento anómalo?
- ¿Qué variables influyen más en la predicción?
- ¿Qué algoritmo ofrece mejores resultados?
- ¿Qué nivel de confianza tiene una inferencia?
- ¿Cómo se consumirá el resultado desde el prototipo?

### Evidencias

- Documento de contexto.
- Planteamiento del problema.
- Usuarios involucrados.
- Preguntas de análisis.
- Objetivo general.
- Objetivos específicos.
- Alcances.
- Limitaciones.

### Errores que deben evitar

- Elegir un problema demasiado amplio.
- Seleccionar un algoritmo antes de entender el problema.
- Confundir la interfaz con el objetivo del proyecto.
- Formular preguntas que los datos no pueden responder.
- Describir únicamente la idea de la aplicación.

---

## Etapa 2. Metodología para el análisis de datos

### Propósito

Organizar el proyecto mediante una metodología reconocida.

### Metodología recomendada

Se recomienda utilizar **CRISP-DM**:

1. Comprensión del negocio.
2. Comprensión de los datos.
3. Preparación de los datos.
4. Modelado.
5. Evaluación.
6. Despliegue.

También pueden utilizar KDD, SEMMA u otra metodología, siempre que sea justificada.

### Actividades

- Seleccionar la metodología.
- Justificar su uso.
- Relacionar cada fase con los entregables.
- Elaborar un cronograma.
- Asignar responsables.
- Definir criterios de aceptación.
- Registrar avances y cambios.

### Evidencias

- Documento de metodología.
- Diagrama del proceso.
- Cronograma.
- Responsables.
- Relación entre fases y entregables.

### Errores que deben evitar

- Mencionar una metodología sin aplicarla.
- Cambiar de metodología durante el proyecto sin justificación.
- Confundir metodología de análisis con metodología de desarrollo de software.
- Trabajar sin planificación.

---

## Etapa 3. Veinte propuestas de aplicación

### Propósito

Analizar diferentes posibilidades de extracción de conocimiento antes de seleccionar los mecanismos que serán implementados.

### Cantidad requerida

- Diez propuestas supervisadas.
- Diez propuestas no supervisadas.

### Formato mínimo de cada propuesta

| Elemento | Descripción |
|---|---|
| Nombre | Título del mecanismo |
| Tipo | Supervisado o no supervisado |
| Problema | Necesidad que atiende |
| Usuario beneficiado | Quién utilizará el resultado |
| Datos necesarios | Fuentes y variables |
| Entradas | Datos recibidos por el modelo |
| Salida | Predicción, clasificación, grupo o representación |
| Algoritmo sugerido | Algoritmo inicial |
| Evaluación | Métricas posibles |
| Integración | Forma de consumirlo desde la API |
| Riesgos | Limitaciones, privacidad o sesgo |

### Ejemplos supervisados

1. Clasificación de riesgo.
2. Predicción de abandono.
3. Pronóstico de demanda.
4. Predicción de ventas.
5. Clasificación de solicitudes.
6. Estimación de tiempos.
7. Detección supervisada de fraude.
8. Predicción de satisfacción.
9. Clasificación de prioridad.
10. Estimación de costos.

### Ejemplos no supervisados

1. Segmentación de usuarios.
2. Agrupamiento de productos.
3. Detección de anomalías.
4. Asociación de productos.
5. Agrupamiento de pacientes.
6. Reducción de dimensionalidad.
7. Identificación de perfiles de consumo.
8. Agrupamiento geográfico.
9. Descubrimiento de patrones de sesiones.
10. Identificación de comportamientos atípicos.

### Evidencias

- Tabla de veinte propuestas.
- Clasificación correcta.
- Datos necesarios.
- Algoritmos sugeridos.
- Justificación.
- Viabilidad de integración.

### Errores que deben evitar

- Cambiar únicamente el nombre de la misma idea.
- Clasificar recomendación como un único tipo sin justificar.
- Proponer mecanismos sin datos suficientes.
- Confundir agrupamiento con clasificación.
- Usar “IA” como explicación técnica.

---

## Etapa 4. Fuentes, entidades, atributos y tipos de datos

### Propósito

Definir la estructura de información necesaria para el análisis.

### Actividades

#### 4.1 Identificar fuentes

Ejemplos:

- Base de datos relacional.
- MongoDB.
- Archivos CSV.
- JSON.
- APIs.
- Sensores.
- Wearables.
- Registros de aplicaciones.
- Datos web.
- Datos de transacciones.
- Datos biométricos.
- Datos simulados.

#### 4.2 Identificar entidades

Ejemplos:

- Usuarios.
- Pacientes.
- Productos.
- Sesiones.
- Pedidos.
- Mediciones.
- Eventos.
- Transacciones.
- Dispositivos.
- Ubicaciones.

#### 4.3 Definir atributos

Cada atributo deberá incluir:

- Nombre.
- Tipo.
- Descripción.
- Unidad.
- Rango.
- Fuente.
- Regla de validación.
- Uso en el análisis.

#### 4.4 Clasificar datos

- Cuantitativos.
- Cualitativos.
- Continuos.
- Discretos.
- Nominales.
- Ordinales.
- Binarios.
- Numéricos.
- Estructurados.
- Semiestructurados.
- No estructurados.

### Evidencias

- Descripción de fuentes.
- Modelo de datos.
- Diccionario de datos.
- Clasificación de atributos.
- Reglas de calidad.
- Justificación de variables.

### Errores que deben evitar

- Incluir atributos sin utilidad.
- Usar campos ambiguos.
- No documentar unidades.
- Exponer información sensible.
- Mezclar variables de entrada y salida sin explicación.

---

## Etapa 5. Simulación estratégica del dataset

### Propósito

Construir conjuntos de datos coherentes, reproducibles y adecuados para entrenamiento, evaluación e inferencia.

### Actividades

#### 5.1 Definir reglas de simulación

Incluyan:

- Distribuciones.
- Rangos.
- Relaciones.
- Frecuencias.
- Tendencias.
- Estacionalidad.
- Eventos especiales.
- Casos normales.
- Casos extremos.
- Casos faltantes.
- Casos anómalos.

#### 5.2 Evitar aleatoriedad total

La simulación deberá reflejar reglas del contexto.

Ejemplos:

- La edad puede influir en ciertos riesgos.
- Un usuario frecuente puede generar más sesiones.
- Una temporada puede aumentar la demanda.
- Una ubicación puede afectar el tiempo de respuesta.
- Un dispositivo puede producir lecturas dentro de rangos técnicos.

#### 5.3 Generar etiquetas supervisadas

Las etiquetas no deberán asignarse sin lógica.

Documenten:

- Regla de generación.
- Variables utilizadas.
- Umbrales.
- Probabilidades.
- Distribución de clases.
- Casos frontera.

#### 5.4 Crear datos para no supervisado

Los datos deberán permitir:

- Descubrir grupos.
- Identificar anomalías.
- Analizar asociaciones.
- Reducir dimensionalidad.
- Explorar patrones.

#### 5.5 Utilizar semilla

```python
import numpy as np

np.random.seed(2026)
```

### Evidencias

- Script generador.
- Reglas de simulación.
- Dataset original.
- Descripción estadística.
- Distribución de clases.
- Casos anómalos.
- Evidencia de reproducibilidad.

### Errores que deben evitar

- Generar un CSV completamente aleatorio.
- Crear etiquetas perfectas y fáciles de predecir.
- Generar clases totalmente balanceadas sin justificación.
- Copiar un dataset sin documentarlo.
- Entregar datos sin script generador.

---

## Etapa 6. Modelado de Data Warehouse o Data Mart

### Propósito

Diseñar un almacén de datos útil para análisis y extracción de conocimiento.

### Actividades

#### 6.1 Definir la granularidad

Ejemplos:

- Una fila por transacción.
- Una fila por sesión.
- Una fila por medición.
- Una fila por atención.
- Una fila por evento.
- Una fila por usuario y periodo.

#### 6.2 Diseñar tabla de hechos

Incluyan:

- Claves.
- Medidas.
- Fecha.
- Evento principal.
- Relaciones con dimensiones.

#### 6.3 Diseñar dimensiones

Ejemplos:

- Tiempo.
- Usuario.
- Producto.
- Ubicación.
- Dispositivo.
- Categoría.
- Servicio.
- Diagnóstico.
- Canal.

#### 6.4 Seleccionar esquema

- Estrella.
- Copo de nieve.
- Data Mart simplificado.

### Evidencias

- Diagrama.
- Tabla de hechos.
- Dimensiones.
- Medidas.
- Granularidad.
- Script de creación.
- Justificación.

### Errores que deben evitar

- Copiar el modelo transaccional.
- No definir granularidad.
- Crear dimensiones sin propósito.
- No documentar medidas.
- Omitir claves.

---

## Etapa 7. Proceso ETL

### Propósito

Extraer, transformar y cargar los datos de manera reproducible.

### Actividades

#### 7.1 Extracción

Registrar:

- Fuente.
- Formato.
- Fecha.
- Cantidad de registros.
- Campos.
- Problemas encontrados.

#### 7.2 Transformación

Aplicar:

- Limpieza.
- Eliminación de duplicados.
- Tratamiento de nulos.
- Corrección de tipos.
- Normalización.
- Estandarización.
- Codificación.
- Agregación.
- Suavizado.
- Construcción de atributos.
- Ingeniería de características.
- Anonimización.
- Integración de fuentes.

#### 7.3 Carga

Cargar en:

- Data Warehouse.
- Data Mart.
- Base de datos analítica.
- Archivos procesados.
- Repositorio de modelos.

#### 7.4 Validación

Verificar:

- Integridad.
- Rangos.
- Tipos.
- Totales.
- Relaciones.
- Pérdida de registros.
- Reproducibilidad.

### Evidencias

- Diagrama ETL.
- Código.
- Bitácora de transformaciones.
- Datos antes y después.
- Reporte de calidad.
- Scripts de carga.
- Pruebas.

### Errores que deben evitar

- Editar manualmente el dataset.
- Eliminar registros sin justificar.
- Mezclar ETL con entrenamiento.
- No guardar datos originales.
- No documentar transformaciones.

---

## Etapa 8. Análisis Exploratorio de Datos

### Propósito

Comprender la estructura, calidad y comportamiento del dataset antes del modelado.

### Actividades

#### 8.1 Calidad

Analizar:

- Nulos.
- Duplicados.
- Valores atípicos.
- Errores.
- Rangos.
- Balance de clases.
- Cobertura temporal.

#### 8.2 Análisis univariado

Incluir:

- Media.
- Mediana.
- Moda.
- Desviación estándar.
- Percentiles.
- Distribución.
- Frecuencia.

#### 8.3 Análisis bivariado

Ejemplos:

- Variable objetivo contra variables de entrada.
- Relación entre edad y riesgo.
- Sesiones y probabilidad de abandono.
- Precio y demanda.
- Uso y satisfacción.

#### 8.4 Análisis multivariado

Ejemplos:

- Correlaciones.
- Segmentos.
- Tendencias.
- Interacción entre variables.
- Comportamiento por grupo.

#### 8.5 Interpretar resultados

Cada gráfica deberá explicar:

1. Qué se observa.
2. Qué significa.
3. Qué posible causa existe.
4. Cómo afecta el modelado.
5. Qué decisión técnica se tomará.

### Evidencias

- Notebook EDA.
- Gráficas.
- Estadísticas.
- Interpretaciones.
- Hallazgos.
- Decisiones de preparación.

### Errores que deben evitar

- Generar gráficas sin explicación.
- Mostrar correlación como causalidad.
- Ignorar el desbalance.
- Usar gráficas inadecuadas.
- Entrenar antes de explorar.

---

## Etapa 9. Preparación de conjuntos de datos

### Propósito

Crear conjuntos adecuados para entrenamiento, validación, prueba e inferencia.

### Conjuntos requeridos

```text
data/
├── raw/
├── processed/
├── training/
├── validation/
├── test/
└── inference/
```

### Actividades

- Definir variable objetivo.
- Seleccionar características.
- Separar entrenamiento.
- Separar validación.
- Separar prueba.
- Crear casos nuevos para inferencia.
- Aplicar transformaciones sin fuga de información.
- Documentar proporciones.
- Mantener reproducibilidad.

### División sugerida

```text
Entrenamiento: 70 %
Validación: 15 %
Prueba: 15 %
```

La división puede cambiar según el problema.

### Datos temporales

En series de tiempo:

```text
Entrenamiento: periodo inicial
Validación: periodo intermedio
Prueba: periodo reciente
```

### Evidencias

- Scripts de división.
- Conjuntos generados.
- Justificación.
- Balance de clases.
- Validación de fuga de información.
- Semilla utilizada.

### Errores que deben evitar

- Usar el conjunto de prueba para entrenar.
- Normalizar antes de separar.
- Mezclar registros del futuro con el pasado.
- Utilizar variables que revelan el resultado.
- No documentar la división.

---

## Etapa 10. Modelos supervisados

### Propósito

Implementar modelos capaces de clasificar o predecir nuevas entradas.

### Modelos mínimos

#### Clasificación

Ejemplos:

- Regresión logística.
- Árbol de decisión.
- Random Forest.
- KNN.
- SVM.
- Naive Bayes.
- Red neuronal.

#### Regresión o pronóstico

Ejemplos:

- Regresión lineal.
- Árbol de regresión.
- Random Forest Regressor.
- Gradient Boosting.
- Series de tiempo.
- Red neuronal.

### Actividades

1. Seleccionar algoritmos.
2. Justificar su elección.
3. Preparar características.
4. Entrenar modelos.
5. Evaluar.
6. Ajustar hiperparámetros.
7. Comparar resultados.
8. Seleccionar el mejor modelo.
9. Serializar el modelo.
10. Documentar entradas y salidas.

### Métricas de clasificación

- Accuracy.
- Precision.
- Recall.
- F1-score.
- Matriz de confusión.
- ROC-AUC.

### Métricas de regresión o pronóstico

- MAE.
- MSE.
- RMSE.
- R².
- MAPE, cuando aplique.

### Evidencias

- Notebooks.
- Código.
- Modelos entrenados.
- Métricas.
- Comparación.
- Optimización.
- Modelo serializado.
- Justificación final.

### Errores que deben evitar

- Usar solo accuracy.
- No comparar modelos.
- Ajustar el modelo con datos de prueba.
- Elegir el modelo más complejo sin razón.
- Confundir predicción con certeza.

---

## Etapa 11. Modelos no supervisados

### Propósito

Descubrir estructuras, grupos o representaciones sin utilizar etiquetas.

### Modelos mínimos

#### Agrupamiento

Ejemplos:

- K-Means.
- DBSCAN.
- Clustering jerárquico.
- Gaussian Mixture.

#### Reducción de dimensionalidad

Ejemplos:

- PCA.
- t-SNE.
- UMAP.
- Autoencoder, como ampliación.

### Actividades

1. Seleccionar variables.
2. Escalar datos.
3. Probar algoritmos.
4. Seleccionar número de grupos.
5. Evaluar.
6. Interpretar clusters.
7. Aplicar reducción de dimensionalidad.
8. Comparar representaciones.
9. Documentar resultados.

### Métricas sugeridas

#### Agrupamiento

- Silhouette Score.
- Davies-Bouldin.
- Inercia.
- Interpretación de clusters.

#### Reducción

- Varianza explicada.
- Número de componentes.
- Conservación de información.
- Utilidad de visualización.

### Evidencias

- Código.
- Resultados.
- Métricas.
- Gráficas.
- Perfiles de grupos.
- Optimización.
- Interpretación.

### Errores que deben evitar

- Nombrar clusters sin analizarlos.
- Usar K-Means sin escalar.
- Seleccionar el número de grupos por intuición.
- Presentar una gráfica sin interpretación.
- Confundir reducción con selección de variables.

---

## Etapa 12. Evaluación, comparación y selección

### Propósito

Determinar qué modelos son útiles, precisos y adecuados para su despliegue.

### Actividades

- Comparar al menos dos configuraciones por mecanismo.
- Registrar hiperparámetros.
- Analizar métricas.
- Revisar sobreajuste.
- Revisar estabilidad.
- Revisar tiempo de respuesta.
- Analizar interpretabilidad.
- Identificar limitaciones.
- Seleccionar dos modelos para API.

### Selección final

Se desplegarán:

- Un modelo supervisado.
- Un modelo no supervisado.

### Criterios sugeridos

| Criterio | Pregunta |
|---|---|
| Utilidad | ¿Resuelve una necesidad real? |
| Calidad | ¿Obtiene métricas aceptables? |
| Estabilidad | ¿Mantiene resultados consistentes? |
| Integración | ¿Puede consumirse desde la API? |
| Velocidad | ¿Responde en tiempo adecuado? |
| Interpretación | ¿El resultado puede explicarse? |
| Riesgo | ¿Puede causar una decisión incorrecta? |

### Evidencias

- Tabla comparativa.
- Reporte de evaluación.
- Justificación de selección.
- Limitaciones.
- Riesgos.
- Modelos elegidos.

---

## Etapa 13. Adecuación de la API con endpoints inteligentes

### Propósito

Integrar los modelos seleccionados a una API funcional.

### Endpoints mínimos

1. Endpoint supervisado.
2. Endpoint no supervisado.

### Endpoints complementarios sugeridos

```text
POST /api/ml/supervised/predict
POST /api/ml/unsupervised/analyze
GET  /api/ml/models
GET  /api/ml/models/{id}/metrics
GET  /api/ml/inferences
GET  /api/ml/health
```

### Contrato mínimo

Cada endpoint deberá documentar:

- Propósito.
- Método HTTP.
- Ruta.
- Parámetros.
- Entrada.
- Validaciones.
- Modelo utilizado.
- Salida.
- Confianza.
- Errores.
- Ejemplos.
- Tiempo de respuesta.

### Ejemplo supervisado

```http
POST /api/ml/patients/classify-risk
```

```json
{
  "age": 57,
  "systolic_pressure": 145,
  "cholesterol": 230,
  "heart_rate": 92
}
```

```json
{
  "classification": "high_risk",
  "probability": 0.87,
  "model": "random_forest_v2",
  "inference_date": "2026-07-16T12:30:00"
}
```

### Ejemplo no supervisado

```http
POST /api/ml/users/segment
```

```json
{
  "purchase_frequency": 8,
  "average_amount": 560.50,
  "days_since_last_purchase": 12
}
```

```json
{
  "cluster": 2,
  "segment": "frequent_high_value",
  "distance_to_centroid": 0.42,
  "model": "kmeans_v3"
}
```

### Actividades

- Crear servicio de inferencia.
- Cargar modelo serializado.
- Validar entrada.
- Ejecutar transformación.
- Ejecutar inferencia.
- Formatear salida.
- Manejar errores.
- Registrar inferencia.
- Versionar modelos.
- Documentar con Swagger/OpenAPI.

### Evidencias

- Código fuente.
- Swagger.
- Pruebas.
- Modelos serializados.
- Ejemplos de consumo.
- Historial de inferencias.
- Documentación.

### Errores que deben evitar

- Entrenar el modelo en cada solicitud.
- No validar entradas.
- No controlar errores.
- Omitir versión del modelo.
- Enviar resultados sin contexto.
- Exponer credenciales.

---

## Etapa 14. Dashboard en tiempo real con Socket.IO

### Propósito

Visualizar resultados, métricas, inferencias y alertas sin recargar la página.

> Socket.IO permite transmitir información en tiempo real, pero no implica que el modelo aprenda en tiempo real.

### Eventos sugeridos

```text
new_inference
new_prediction
new_cluster_assignment
model_alert
dataset_update
processing_status
api_error
```

### Información posible

- Nuevas predicciones.
- Clasificaciones.
- Probabilidades.
- Clusters.
- Alertas.
- Métricas.
- Historial.
- Estado del servicio.
- Tiempo de respuesta.
- Número de inferencias.

### Actividades

- Diseñar dashboard.
- Definir eventos.
- Emitir datos desde backend.
- Escuchar eventos en frontend.
- Actualizar gráficas.
- Mostrar estado de conexión.
- Manejar desconexión.
- Registrar errores.
- Persistir resultados.

### Storytelling

El dashboard deberá responder:

- ¿Qué está ocurriendo?
- ¿Qué predijo o identificó el modelo?
- ¿Qué tan confiable es?
- ¿Qué patrón se encontró?
- ¿Qué acción se recomienda?
- ¿Qué limitaciones existen?

### Evidencias

- Dashboard funcional.
- Código de Socket.IO.
- Eventos documentados.
- Capturas.
- Video.
- Pruebas de conexión.
- Historial de resultados.

### Errores que deben evitar

- Mostrar números que cambian sin significado.
- Confundir actualización con reentrenamiento.
- No persistir inferencias.
- Saturar el dashboard.
- Omitir interpretación.

---

## Etapa 15. Consumo desde prototipos web o wearables

### Propósito

Integrar los endpoints inteligentes con un prototipo funcional.

### Opciones

- Aplicación web.
- Aplicación progresiva.
- Wearable.
- Panel administrativo.
- Aplicación móvil.
- Sistema de monitoreo.

### Actividades

- Definir caso de uso.
- Diseñar pantalla.
- Capturar datos.
- Validar datos.
- Consumir endpoint.
- Mostrar resultado.
- Mostrar confianza.
- Manejar errores.
- Registrar la consulta.
- Integrar actualización en tiempo real.

### Requisitos mínimos

- Interfaz comprensible.
- Validación.
- Consumo real de API.
- Respuesta visible.
- Mensajes de error.
- Evidencia de integración.
- Seguridad básica.
- No exponer secretos.

### Evidencias

- Prototipo.
- Código.
- Video.
- Capturas.
- Diagrama de integración.
- Ejemplos de consumo.
- Pruebas.

### Errores que deben evitar

- Simular la respuesta en frontend.
- Usar datos estáticos.
- No manejar fallas.
- Exponer URL o credenciales sensibles.
- Mostrar la predicción como decisión definitiva.

---

## Etapa 16. Pruebas

### Propósito

Comprobar que los datos, modelos, endpoints e integración funcionan correctamente.

### Tipos de pruebas

#### 16.1 Dataset

- Rangos.
- Nulos.
- Duplicados.
- Integridad.
- Distribución.
- Balance.
- Tipos.

#### 16.2 Simulación

- Reglas.
- Casos normales.
- Casos extremos.
- Coherencia.
- Reproducibilidad.

#### 16.3 ETL

- Extracción.
- Transformaciones.
- Carga.
- Totales.
- Repetición.
- Manejo de errores.

#### 16.4 Modelos

- Métricas.
- Generalización.
- Estabilidad.
- Sobreajuste.
- Casos frontera.
- Entradas inesperadas.

#### 16.5 API

- Solicitudes válidas.
- Campos faltantes.
- Tipos incorrectos.
- Valores fuera de rango.
- Latencia.
- Errores.
- Respuestas.
- Concurrencia básica.

#### 16.6 Integración

- Consumo web.
- Consumo wearable.
- Socket.IO.
- Persistencia.
- Desconexión.
- Reintento.
- Actualización de interfaz.

### Evidencias

- Plan de pruebas.
- Casos de prueba.
- Resultados.
- Capturas.
- Logs.
- Correcciones.
- Conclusiones.

### Errores que deben evitar

- Probar únicamente casos correctos.
- No registrar resultados.
- Cambiar datos para que las pruebas pasen.
- Omitir pruebas de error.
- No repetir pruebas después de corregir.

---

## Etapa 17. Arquitectura de software

### Propósito

Describir los componentes y la integración del sistema inteligente.

### Diagrama sugerido

```text
Fuentes de datos
        ↓
Proceso ETL
        ↓
Data Warehouse / Data Mart
        ↓
Entrenamiento y evaluación
        ↓
Repositorio de modelos
        ↓
API inteligente
        ↓
Socket.IO
        ↓
Dashboard / Web / Wearable
```

### Componentes mínimos

- Fuente de datos.
- Simulador.
- ETL.
- Almacén analítico.
- Módulo de entrenamiento.
- Modelo serializado.
- Servicio de inferencia.
- API.
- Socket.IO.
- Dashboard.
- Prototipo consumidor.
- Repositorio.

### Evidencias

- Diagrama de arquitectura.
- Descripción de componentes.
- Flujo de datos.
- Entradas y salidas.
- Requerimientos funcionales.
- Requerimientos no funcionales.
- Tecnologías.
- Justificación.

### Errores que deben evitar

- Dibujar componentes que no existen.
- No mostrar flujo de datos.
- Omitir almacenamiento.
- Confundir arquitectura con estructura de carpetas.
- No justificar tecnologías.

---

## Etapa 18. Ética, privacidad y sesgos

### Propósito

Analizar los riesgos asociados con el uso de datos y modelos.

### Actividades

- Identificar datos sensibles.
- Anonimizar.
- Reducir datos innecesarios.
- Analizar sesgos.
- Revisar distribución de clases.
- Identificar grupos afectados.
- Definir límites del modelo.
- Establecer intervención humana.
- Redactar advertencias.
- Documentar uso responsable.

### Preguntas obligatorias

- ¿Qué datos se utilizan?
- ¿Por qué son necesarios?
- ¿Qué sesgos podrían existir?
- ¿Qué usuarios podrían verse afectados?
- ¿Qué decisiones no deben automatizarse?
- ¿Cuándo debe intervenir una persona?
- ¿Qué limitaciones tiene el modelo?

### Evidencias

- Documento ético.
- Reglas de anonimización.
- Limitaciones.
- Riesgos.
- Medidas preventivas.
- Advertencias en interfaz.

---

## Etapa 19. Uso responsable de IA generativa

### Propósito

Utilizar IA como apoyo sin sustituir la comprensión ni la responsabilidad del equipo.

### Usos permitidos

- Explicación de conceptos.
- Generación de ejemplos.
- Revisión de código.
- Propuestas de arquitectura.
- Ayuda en pruebas.
- Mejora de documentación.
- Diseño de interfaz.
- Corrección de errores.

### Documento requerido

```text
docs/ai-usage.md
```

### Contenido

- Herramientas utilizadas.
- Prompts importantes.
- Código generado.
- Cambios realizados.
- Errores encontrados.
- Validaciones.
- Decisiones del equipo.
- Limitaciones.

### Regla principal

> Todo contenido producido con IA deberá ser comprendido, probado, corregido y defendido por el equipo.

### Errores que deben evitar

- Copiar código sin comprenderlo.
- Inventar resultados.
- Ocultar el uso de IA.
- Generar conclusiones sin verificar.
- Permitir que la IA seleccione el modelo sin evaluación.

---

## Etapa 20. Desarrollo colaborativo con Git y GitHub

### Propósito

Demostrar organización, colaboración y control de versiones.

### Ramas sugeridas

```text
main
develop
feature/data-simulation
feature/etl
feature/eda
feature/supervised-models
feature/unsupervised-models
feature/intelligent-api
feature/socket-dashboard
feature/web-integration
feature/wearable-integration
docs/readme
tests/integration
```

### Actividades

- Crear issues.
- Asignar responsables.
- Usar ramas.
- Crear pull requests.
- Revisar código.
- Resolver conflictos.
- Crear releases.
- Documentar avances.
- Mantener README actualizado.

### Commits sugeridos

```text
feat: agrega endpoint de clasificación
feat: integra modelo de agrupamiento
fix: corrige normalización de variables
test: agrega pruebas de entradas inválidas
docs: documenta contrato del endpoint
```

### Evidencias

- Commits.
- Ramas.
- Issues.
- Pull requests.
- Revisiones.
- Releases.
- Participación.
- Tablero.

### Errores que deben evitar

- Trabajar directamente en `main`.
- Realizar un solo commit.
- Subir archivos por mensajería al final.
- Crear commits artificiales.
- Dejar el proyecto a una sola persona.

---

## Etapa 21. Presentación y defensa

### Estructura sugerida

1. Contexto.
2. Problema.
3. Metodología.
4. Veinte propuestas.
5. Fuentes y datos.
6. Simulación.
7. Data Warehouse.
8. ETL.
9. EDA.
10. Modelos supervisados.
11. Modelos no supervisados.
12. Evaluación.
13. Endpoints.
14. Dashboard.
15. Integración.
16. Pruebas.
17. Resultados.
18. Limitaciones.
19. Conclusiones.
20. Demostración.

### Defensa individual

Cada integrante deberá explicar:

- El problema.
- Una fuente de datos.
- Una transformación ETL.
- Un modelo.
- Una métrica.
- Un endpoint.
- Una prueba.
- Su contribución.

### Evidencias

- Presentación.
- Demostración.
- Participación equilibrada.
- Respuestas.
- Video de respaldo.
- Evidencia individual.

---

# 7. Estructura sugerida del repositorio

```text
/
├── api/
│   ├── controllers/
│   ├── routes/
│   ├── services/
│   ├── middleware/
│   └── sockets/
├── data/
│   ├── raw/
│   ├── processed/
│   ├── training/
│   ├── validation/
│   ├── test/
│   └── inference/
├── database/
│   ├── ddl/
│   ├── etl/
│   ├── warehouse/
│   └── seeds/
├── docs/
│   ├── context.md
│   ├── methodology.md
│   ├── proposals.md
│   ├── data-sources.md
│   ├── data-dictionary.md
│   ├── simulation-rules.md
│   ├── data-warehouse.md
│   ├── etl-process.md
│   ├── model-evaluation.md
│   ├── api-contracts.md
│   ├── testing.md
│   ├── ethics.md
│   └── ai-usage.md
├── frontend/
│   ├── dashboard/
│   └── prototype/
├── models/
│   ├── supervised/
│   ├── unsupervised/
│   └── serialized/
├── notebooks/
│   ├── eda/
│   ├── supervised/
│   └── unsupervised/
├── simulation/
├── tests/
│   ├── data/
│   ├── etl/
│   ├── models/
│   ├── api/
│   └── integration/
├── .env.example
├── .gitignore
├── requirements.txt
├── package.json
├── README.md
└── LICENSE
```

---

# 8. Contenido mínimo del README del proyecto

- Nombre.
- Descripción.
- Problema.
- Objetivo.
- Integrantes.
- Metodología.
- Tecnologías.
- Arquitectura.
- Fuentes de datos.
- Modelos implementados.
- Endpoints.
- Instalación.
- Configuración.
- Ejecución.
- Pruebas.
- Dashboard.
- Integración web o wearable.
- Resultados.
- Limitaciones.
- Ética.
- Uso de IA.
- Licencia.
- Referencias.

---

# 9. Lista general de entregables

## Planeación

- [ ] Contexto.
- [ ] Problema.
- [ ] Objetivos.
- [ ] Stakeholders.
- [ ] Preguntas de análisis.
- [ ] Metodología.
- [ ] Cronograma.

## Propuestas

- [ ] Diez propuestas supervisadas.
- [ ] Diez propuestas no supervisadas.
- [ ] Justificación.
- [ ] Datos necesarios.
- [ ] Algoritmos sugeridos.
- [ ] Viabilidad de integración.

## Datos

- [ ] Fuentes.
- [ ] Entidades.
- [ ] Atributos.
- [ ] Diccionario.
- [ ] Reglas de calidad.
- [ ] Simulación.
- [ ] Script generador.
- [ ] Dataset original.
- [ ] Dataset procesado.

## Almacén y preparación

- [ ] Data Warehouse o Data Mart.
- [ ] Tabla de hechos.
- [ ] Dimensiones.
- [ ] ETL.
- [ ] Reporte de calidad.
- [ ] Conjuntos de entrenamiento.
- [ ] Conjunto de validación.
- [ ] Conjunto de prueba.
- [ ] Conjunto de inferencia.

## Análisis y modelos

- [ ] EDA.
- [ ] Clasificación.
- [ ] Regresión o pronóstico.
- [ ] Agrupamiento.
- [ ] Reducción de dimensionalidad.
- [ ] Evaluación.
- [ ] Optimización.
- [ ] Comparación.
- [ ] Selección de dos modelos.
- [ ] Modelos serializados.

## Integración

- [ ] Endpoint supervisado.
- [ ] Endpoint no supervisado.
- [ ] Swagger.
- [ ] Registro de inferencias.
- [ ] Dashboard.
- [ ] Socket.IO.
- [ ] Integración web o wearable.
- [ ] Manejo de errores.

## Calidad

- [ ] Pruebas del dataset.
- [ ] Pruebas de simulación.
- [ ] Pruebas ETL.
- [ ] Pruebas de modelos.
- [ ] Pruebas de API.
- [ ] Pruebas de integración.
- [ ] Pruebas de Socket.IO.

## Documentación

- [ ] Arquitectura.
- [ ] README.
- [ ] Manual de instalación.
- [ ] Manual de usuario.
- [ ] Ética y privacidad.
- [ ] Uso de IA.
- [ ] Evidencias de GitHub.
- [ ] Presentación.
- [ ] Video de respaldo.

---

# 10. Criterio general de calidad

Un proyecto completo deberá demostrar coherencia entre:

```text
Problema
   ↓
Datos
   ↓
Preparación
   ↓
Modelo
   ↓
Evaluación
   ↓
Endpoint
   ↓
Interfaz
   ↓
Decisión
```

El valor del proyecto no dependerá únicamente de obtener una métrica alta. También se evaluará:

- Utilidad del modelo.
- Calidad de los datos.
- Correcta selección de algoritmos.
- Interpretación de resultados.
- Reproducibilidad.
- Integración con software.
- Pruebas.
- Seguridad.
- Ética.
- Documentación.
- Trabajo colaborativo.

---

# 11. Regla final

> Un sistema inteligente no es únicamente un algoritmo. Es una solución completa en la que los datos, el modelo, la API, la interfaz, las pruebas y la interpretación trabajan juntos para resolver un problema real.
