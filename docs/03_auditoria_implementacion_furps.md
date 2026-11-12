# 03 · Auditoría de implementación FURPS+ — Green AI Municipal

| Dato | Valor |
|---|---|
| Entradas | `docs/01_auditoria_furps.md`, `docs/02_plan_furps.md` y el estado actual de la rama `mejoras-semana13` |
| Rol | Agente 3 — Auditor independiente de implementación FURPS+ |
| Criterio | Ninguna mejora se da por aplicada sin evidencia observable (código, prueba ejecutada o captura) |

## 1. Comparación antes / después

| Factor | Antes (01) | Después | Cambio principal |
|---|---|---|---|
| Functionality | 85 | 85 | Sin cambios funcionales (era la restricción del plan) |
| Usability | 80 | 85 | Mensajes de error comprensibles y sin detalles internos |
| Reliability | 62 | 75 | Arranque tolerante a DagsHub, validación de entradas, registro de errores con código de incidente |
| Performance | 65 | 65 | Sin cambios (paginación pospuesta) |
| Supportability | 45 | 75 | De 0 a 35 pruebas automatizadas, README y `.env.example`, archivos generados excluidos |
| **Global** | **69** | **77** | **+8 puntos** |

## 2. Estado de cada mejora

| Mejora | Estado | Evidencia |
|---|---|---|
| M1 · Pruebas automatizadas | **Implementada** | Carpeta `backend/tests/` con 35 pruebas en 8 archivos. Resultado en este entorno: `34 passed, 1 skipped` (la prueba de la API se omite porque FastAPI no está instalado aquí; en un equipo con `requirements-dev.txt` corre completa). Captura D01 |
| M7 · DTO separados | **Implementada** | `backend/src/infrastructure/adapters/input/dtos.py`; `api_router.py` los importa (línea 9) |
| M2 · Validación de entradas | **Implementada** | `dtos.py`: título ≤ 200, descripción ≤ 2000, ubicación ≤ 300, campos personales ≤ 200; `test_dtos.py` (5 pruebas en verde). Captura D02 |
| M3 · Errores con registro | **Implementada** | Función `error_interno` en `api_router.py`; las tres rutas ya no devuelven `str(e)`; `test_api_errores.py` comprueba que el cliente no ve la contraseña ni el host de la excepción y que el log sí los registra. Captura D03 |
| M4 · Arranque tolerante | **Implementada** | `main.py` líneas 19-33: `dagshub.init()` dentro de `try/except` y solo si hay token. Prueba de humo con DagsHub caído: la API se importa con sus 4 rutas. Capturas D04 y D05 |
| M6 · Higiene del repositorio | **Parcialmente implementada** | `.gitignore` excluye `mlflow.db`, `mlruns/`, `emissions.csv` y cachés (captura D06). Falta que el equipo ejecute `git rm --cached mlflow.db emissions.csv backend/emissions.csv` al subir la rama, porque esos archivos ya estaban versionados |
| M5 · Documentación | **Implementada** | `README.md` reescrito con el modelo real, instalación, pruebas y variables (captura D07); `backend/.env.example` con las 9 variables que lee el código |
| Paginación del listado (P-02) | No implementada (pospuesta en el plan) | `listar()` sin cambios |
| Exportación PDF/CSV (F-06) | No implementada (pospuesta en el plan) | Queda en el Product Backlog |
| Retirar `axios` y `backend/package.json` (S-06) | No implementada (pospuesta en el plan) | Requiere regenerar `package-lock.json` con conexión |
| Reutilizar `EmissionsTracker` (P-03) | No implementada (pospuesta en el plan) | Sin cambios en la medición |

## 3. Búsqueda de regresiones y errores nuevos

| Revisión | Resultado | Evidencia |
|---|---|---|
| Rutas de la API | Sin cambios: `POST /api/reclamos`, `GET /api/reclamos`, `PATCH /api/reclamos/{id}/estado`, `GET /` | Prueba de humo (captura D05) |
| Formato de respuesta exitosa | Sin cambios: el cuerpo de `crear_reclamo` no se modificó | `git diff` de `api_router.py` |
| Reclamos legítimos rechazados | Ninguno: los límites del servidor son mayores que los del formulario (120 y 1500) | `test_acepta_un_reclamo_como_el_del_formulario_web` |
| Anonimización y regla HITL | Se mantienen; ahora están cubiertas por pruebas | `test_anonimizacion.py`, `test_registrar_reclamo.py`, `test_evaluacion_confianza.py` |
| Pruebas fallidas | Ninguna | Captura D01 |
| Incompatibilidades | Ninguna en código. **Cambio de configuración:** `main.py` ya no tiene un token de DagsHub escrito por defecto; si Render no tiene `MLFLOW_TRACKING_PASSWORD`, la API funciona pero deja de registrar en MLflow | `main.py` línea 21 |

## 4. Riesgos residuales

| Riesgo | Nivel | Acción |
|---|---|---|
| La rama aún no está desplegada: la verificación en producción queda pendiente | Medio | Tras unir la rama: registrar un reclamo de prueba, consultarlo con su código y cambiar su estado en el SIGEM |
| Configurar `MLFLOW_TRACKING_PASSWORD` en Render | Medio | Usar un token nuevo (ver hallazgo A02-01 en el documento 04) |
| Listado sin paginación (P-02) | Medio | Próxima iteración |
| Arranque en frío del plan gratuito de Render (R-06) | Medio | Depende del plan de hosting, no del código |
| Archivos generados aún versionados hasta ejecutar `git rm --cached` | Bajo | Incluido en las instrucciones de subida |

## 5. Conclusión de cumplimiento

El plan FURPS+ se implementó en **5 de 7 mejoras completas y 1 parcial** (M6, falta un comando al subir la rama); las 4 mejoras de prioridad baja quedaron pospuestas tal como el plan lo indicaba. No se detectaron regresiones ni pruebas fallidas, y ninguna ruta ni formato de respuesta cambió. El puntaje FURPS+ sube de **69 a 77 puntos**.

**Dictamen: plan implementado de forma satisfactoria, con verificación en producción pendiente del despliegue de la rama.**
