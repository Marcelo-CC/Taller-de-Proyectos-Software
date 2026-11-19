# Logs del backend y análisis

> Fase 4 · Prompt 6 – Análisis de Logs (rol: Ingeniero de Soporte Nivel 3). Fuentes: ejecución local de `pytest` sobre `main` (commit `73a6f5e`, 19/11/2026), pruebas en producción contra Render (12/11/2026 y 19/11/2026), registros de GitHub Actions y revisión de las instrucciones de registro (`logging`, `print`) del código.

## 1. Logs obtenidos

### 1.1 Pruebas automatizadas (entorno local sin `fastapi` instalado)

```text
collecting ... collected 68 items / 2 skipped
...
SKIPPED [1] tests/test_api_errores.py:4: could not import 'fastapi': No module named 'fastapi'
SKIPPED [1] tests/test_api_seguridad.py:8: could not import 'fastapi': No module named 'fastapi'
======================== 68 passed, 2 skipped in 0.15s =========================
```

En GitHub Actions (con `requirements-dev.txt` completo) se ejecutan también esos 2 módulos y el job termina en verde.

### 1.2 Producción (Render, plan gratuito)

```text
GET https://taller-de-proyectos-software.onrender.com/     → espera ~60 s ("Service waking up") → 200
GET /api/reclamos (sin token)                               → 401 "Debe iniciar sesión como personal municipal…"
GET /docs                                                   → Swagger con botón "Authorize" y candados en rutas del SIGEM
POST /api/reclamos (reclamo de prueba)                      → 200, ticket + código XXXX-XXXX, categoría y confianza
21 POST seguidos desde la misma IP                          → 429 "Se recibieron demasiados reclamos seguidos…"
```

### 1.3 Mensajes que emite el backend

| Origen | Mensaje | Mecanismo |
|---|---|---|
| `gemini_adapter.py:132` | `⚠️ Error al procesar reclamo con Gemini API (modelo): …` | `print` |
| `gemini_adapter.py:135` | `⚠️ Gemini no disponible. Se aplica anonimización y clasificación local.` | `print` |
| `gemini_adapter.py:152` | `⚠️ La corrección de Gemini omitió parte del reclamo…` | `print` |
| `registrar_reclamo_use_case.py:90-96` | Bloque `TELEMETRIA GREEN AI (CODECARBON) - RESUMEN` con texto anonimizado, CO₂e, kWh y confianza | `print` |
| `api_router.py` | `Incidente XXXXXXXX en …` (con traza) | `logging` (`api.reclamos`) |
| `api_router.py` | `Acceso denegado a la API interna`, `Límite de solicitudes superado…` | `logging` (`auditoria`) |
| `main.py` | Aviso si DagsHub no se inicializa | `logging` |

### 1.4 GitHub Actions

```text
Node.js 20 actions are deprecated … actions/checkout@v4, actions/setup-python@v5, actions/setup-node@v4
The ubuntu-latest label will migrate to Ubuntu 26 …
```

## 2. Clasificación de hallazgos

| Tipo | Hallazgo | Evidencia |
|---|---|---|
| Errores | No se observaron errores en las pruebas ni en las respuestas de producción | 68 aprobadas; respuestas 200/401/429 esperadas |
| Advertencias | Acciones de GitHub sobre Node.js 20 deprecado | Registro de Actions |
| Excepciones | Las excepciones de Gemini, MLflow y Supabase se capturan; el cliente recibe un mensaje genérico con código de incidente | `error_interno()` en `api_router.py`; prueba `test_si_mlflow_falla_el_reclamo_se_guarda_igual` |
| Dependencias faltantes | En un entorno sin `fastapi`, 2 módulos de pruebas (6 pruebas de API y seguridad) se omiten en silencio | `SKIPPED … could not import 'fastapi'` |
| Configuración | Sin `SUPABASE_URL`/`SUPABASE_KEY` la API no arranca (`ValueError`); sin token de DagsHub solo se omite MLflow | `main.py` |
| Red | Arranque en frío de Render (~60 s) en el primer acceso tras inactividad; Gemini con tiempo límite de 20 s y respaldo | Pruebas en producción; `gemini_adapter.py` |
| Autenticación | Las rutas internas responden 401 sin token y registran el intento en la bitácora `auditoria` | Prueba en producción; `test_api_seguridad.py` |

## 3. Matriz de hallazgos

| ID | Hallazgo | Categoría | Severidad | Recomendación |
|---|---|---|---|---|
| LOG-01 | Arranque en frío de Render de ~60 s: el primer vecino del día espera o cree que el sistema está caído | Red / disponibilidad | **Alto** | Plan pagado o ping periódico; mostrar en el frontend un aviso de "despertando el servidor" |
| LOG-02 | Mensajes operativos con `print()` en lugar de `logging`: no tienen nivel, hora ni nombre del módulo y no se filtran con `LOG_LEVEL` | Configuración / observabilidad | **Medio** | Sustituir por `logger.warning/info` |
| LOG-03 | El resumen de telemetría imprime los primeros 60 caracteres del texto anonimizado en los logs de Render | Seguridad / privacidad | **Medio** | Registrar solo métricas (kWh, gCO₂e, confianza) y el ID del ticket |
| LOG-04 | Pruebas de API omitidas sin aviso cuando falta `fastapi` en el entorno local | Dependencias | **Bajo** | Instalar siempre con `requirements-dev.txt` o hacer que la omisión falle en el CI |
| LOG-05 | Acciones de GitHub con Node.js 20 deprecado | Configuración CI | **Bajo** | Aceptar los PR de Dependabot que suben a `@v7` |
| LOG-06 | Si Gemini falla, la caída a clasificación local solo deja un `print`; no hay métrica de cuántas veces ocurre | Observabilidad | **Bajo** | Registrar en MLflow un indicador `clasificado_por_ia` |

No se identificaron hallazgos **críticos**: la aplicación responde, protege las rutas internas y maneja las fallas de los servicios externos sin exponer detalles técnicos.
