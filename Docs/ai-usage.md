# Uso responsable de IA generativa — Tutunaku

> Etapa 19 de la Guía de Apoyo para el Proyecto Integrador.
> "Todo contenido producido con IA deberá ser comprendido, probado, corregido y defendido por el equipo."

## Herramienta utilizada

- **Claude Code** (Anthropic), asistente de desarrollo en modo agente con acceso a
  terminal, sistema de archivos y ejecución de notebooks Jupyter, usado como
  copiloto para escalar el proyecto Tutunaku con la capa de Machine Learning,
  API inteligente, dashboard en tiempo real y el rebranding a "Tutunaku".

## Alcance de lo generado con asistencia de IA

| Área | Qué se generó | Validación aplicada |
|---|---|---|
| Simulación de datos | `simulation/generate_dataset.py` (6 escenarios, semilla 2026, reglas de negocio) | Ejecutado end-to-end; pruebas en `tests/simulation/` verifican reproducibilidad, rangos y coherencia de las reglas |
| ETL / Data Warehouse | `database/warehouse/build_warehouse.py` | Ejecutado end-to-end; reporte de calidad (`data/processed/etl_quality_report.json`); pruebas en `tests/etl/` |
| Notebooks de modelos | 6 notebooks (`notebooks/supervised`, `notebooks/unsupervised`) + 1 de EDA general | Cada notebook se **ejecutó realmente** (no solo se escribió) vía `jupyter nbconvert --execute`, verificando que ninguna celda quedara con error y que las métricas reportadas sean las calculadas, no inventadas |
| API inteligente | `app/ml/` (schemas, registro de modelos, servicio de inferencia) + `app/routes/ml.py` | Se probó la carga de los 6 modelos reales, inferencia end-to-end contra artefactos entrenados, y respuestas 401/403/422 esperadas; suite `test/test_ml.py` (16 casos) |
| Socket.IO / Dashboard | `app/sockets/server.py`, `AdminMLDashboard.tsx`, `socket.ts` | Se verificó el handshake de Socket.IO y que las rutas HTTP existentes siguen funcionando dentro de `socket_app`; `npm run type-check` y `npm run build` del frontend pasan sin errores |
| Rebrand "Tutunakun" → "Tutunaku" | Script de búsqueda y reemplazo con protección explícita de identificadores de infraestructura | Se listó cada archivo modificado y se verificó que el nombre real de la base de datos (`tutunakun_db`) y la carpeta de Cloudinary con audios ya subidos quedaran intactos |

## Decisiones tomadas por el equipo (no delegadas a la IA)

- **Qué se renombra y qué no** en el rebrand: se decidió explícitamente mantener
  el nombre físico de la base de datos (`tutunakun_db`) para no romper la
  conexión existente, documentando el paso de migración manual en `.env.example`.
- **Separar el Data Warehouse analítico** (SQLite local en
  `database/warehouse/tutunaku_dw.sqlite`) de la base de datos transaccional
  real (MySQL/MongoDB de la app), para que todo el trabajo de ML pudiera
  hacerse con **cero riesgo** sobre los datos y la funcionalidad en producción.
- **Qué endpoints requieren rol de usuario vs. administrador**: predict-time y
  predict-success (uso durante el juego) quedaron con `require_user`;
  detect-anomaly, segment-user, platform-load-forecast, analyze-navigation e
  inferences (uso operativo/monitoreo) quedaron con `require_admin`.

## Errores encontrados y corregidos durante la validación

- `pytest.ini` referenciaba `pytest.PytestRemovedIn9Warning`, una clase que ya
  no existe en la versión de pytest instalada (9.1.1) — bloqueaba **toda**
  ejecución de pruebas del backend. Se corrigió eliminando esa línea.
- Faltaba `src/vite-env.d.ts` en el frontend, por lo que `import.meta.env` no
  tenía tipos y `npm run type-check`/`npm run build` fallaban incluso antes de
  este proyecto. Se agregó el archivo estándar de Vite.
- El entorno virtual `backend/venv_run` apuntaba a una ruta de Python de otra
  máquina (`C:\Users\Brand\...`) y no era utilizable aquí; se conservó como
  `venv_run.broken_other_machine` y se creó uno nuevo y funcional.

## Limitaciones conocidas

- El modelo de regresión de tiempo de respuesta (S02) obtiene un R² bajo en
  el conjunto de prueba: la señal real (dificultad, conectividad, dispositivo)
  compite con una variabilidad aleatoria fuerte introducida deliberadamente en
  la simulación (ruido log-normal), documentado en el propio notebook en vez
  de ocultarse.
- No existe configuración de ESLint (`.eslintrc`) en el frontend original —
  gap preexistente detectado durante la verificación, fuera del alcance de
  este trabajo de ML/API/dashboard; se deja documentado para que el equipo lo
  resuelva por separado.
- Las pruebas de integración originales del backend (`test/test_auth.py`)
  requieren una instancia real de MySQL/MongoDB; no se pudieron ejecutar en
  este entorno por no contar con esa infraestructura, pero esto es
  independiente de los cambios de este proyecto.
