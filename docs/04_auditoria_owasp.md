# 04 · Auditoría de seguridad OWASP Top 10 — Green AI Municipal

| Dato | Valor |
|---|---|
| Alcance | Frontend, backend, API, autenticación, autorización, configuración, dependencias e infraestructura presente en el repositorio |
| Estado auditado | Rama `mejoras-semana13` después de la Fase 1 (calidad), comparada con `main` en producción |
| Rol | Agente 4 — Auditor de seguridad OWASP Top 10 (no se corrigió ni modificó nada) |
| Fecha | 12/11/2026 |

## 1. Resumen ejecutivo

El sistema tiene buenas bases: no guarda datos personales en claro, anonimiza antes de llamar a la IA, guarda solo el hash del código secreto, delega el inicio de sesión a Supabase Auth y no construye consultas SQL a mano.

Los problemas graves son dos. **(1)** El repositorio es público y contuvo un **token de DagsHub escrito en el código** (`backend/main.py`, línea 14 en `main`); aunque la Fase 1 lo quitó del código, sigue en el historial de Git y en la rama `main`, y no ha sido revocado. **(2)** El backend **no exige autenticación** en `GET /api/reclamos` ni en `PATCH /api/reclamos/{id}/estado`: cualquiera puede leer todos los reclamos y cambiar su estado.

**Score global de seguridad: 56 / 100 (nivel Medio-Bajo).**

## 2. Resultado por categoría

| # | Categoría OWASP | Estado | Severidad | Puntaje (0-10) |
|---|---|---|---|---|
| A01 | Broken Access Control | No cumple | **Alto** | 3 |
| A02 | Cryptographic Failures | No cumple | **Crítico** | 2 |
| A03 | Injection | Cumple | Bajo | 9 |
| A04 | Insecure Design | Cumple parcialmente | Medio | 5 |
| A05 | Security Misconfiguration | Cumple parcialmente | Medio | 5 |
| A06 | Vulnerable and Outdated Components | No verificable / parcial | Medio | 6 |
| A07 | Identification and Authentication Failures | Cumple parcialmente | Medio | 6 |
| A08 | Software and Data Integrity Failures | Cumple parcialmente | Medio | 5 |
| A09 | Security Logging and Monitoring Failures | Cumple parcialmente | Medio | 5 |
| A10 | Server-Side Request Forgery (SSRF) | Cumple (no aplica) | Bajo | 10 |
| | **Score global** | | | **56 / 100** |

Severidad = combinación de impacto y probabilidad: Crítico (impacto alto y explotación inmediata), Alto, Medio, Bajo.

## 3. Detalle por categoría

### A01 · Broken Access Control — Alto

| ID | Hallazgo | Evidencia | Impacto | Probabilidad |
|---|---|---|---|---|
| A01-01 | `GET /api/reclamos` devuelve los 1252 reclamos a cualquier visitante, sin iniciar sesión | `api_router.py` (ruta sin dependencia de autenticación); captura A06 (respuesta pública de 703 KB en producción) | Medio: los datos están anonimizados, pero expone ubicaciones, estados y el volumen de la gestión municipal | Alta |
| A01-02 | `PATCH /api/reclamos/{id}/estado` cambia el estado de cualquier reclamo sin autenticación (el operador del SIGEM sí inicia sesión, pero la API no lo comprueba) | `api_router.py`, ruta `cambiar_estado`; Swagger público sin botón *Authorize* (captura A04) | Alto: un tercero puede marcar reclamos como resueltos y alterar la atención | Alta |
| A01-03 | La base otorga `UPDATE (estado)` y `SELECT` al rol `anon`; la protección depende de políticas RLS que **no están en el repositorio** y no pudieron verificarse | `backend/sql/modulo_c_consulta.sql` líneas 12-14 | Alto si RLS no restringe | No verificable |

### A02 · Cryptographic Failures — Crítico

| ID | Hallazgo | Evidencia | Impacto | Probabilidad |
|---|---|---|---|---|
| A02-01 | Token de DagsHub publicado en un repositorio público (valor por defecto en `os.getenv`). Sigue visible en `main` y en el historial aunque la Fase 1 lo quitó del código | Captura A01 (valor oculto en el informe); `git log -p` | Alto: acceso a la cuenta de DagsHub/MLflow del proyecto (experimentos, métricas, posible borrado) | Alta: cualquier persona puede leerlo |
| A02-02 | El código secreto de consulta se guarda como SHA-256 sin sal ni clave secreta; si la columna `codigo_hash` se filtrara, los 30⁸ códigos posibles se pueden probar por fuerza bruta | `codigo_consulta.py`, `hashear()` | Medio | Baja: la columna no se expone por la API (`REVOKE` + función `SECURITY DEFINER`) |
| — | Transporte cifrado: Render, Vercel y Supabase sirven solo por HTTPS | URLs del despliegue | — | Cumple |

### A03 · Injection — Bajo (cumple)

| Revisión | Resultado | Evidencia |
|---|---|---|
| SQL | Sin SQL construido con texto: el backend usa el cliente de Supabase; las funciones SQL usan parámetros | `supabase_reclamo_repository.py`; `modulo_c_consulta.sql` |
| Filtros PostgREST del frontend | Los identificadores se codifican con `encodeURIComponent` | `api.js`, `actualizarReclamo` |
| XSS | React escapa la salida; no se usa `dangerouslySetInnerHTML` ni `eval` | Búsqueda en `frontend/src` sin resultados |
| Inyección de instrucciones a la IA | El texto del vecino va serializado con `json.dumps` y la categoría devuelta se valida contra una lista cerrada | `gemini_adapter.py`, `_normalizar_categoria` |

### A04 · Insecure Design — Medio

| ID | Hallazgo | Evidencia | Impacto | Probabilidad |
|---|---|---|---|---|
| A04-01 | `POST /api/reclamos` no tiene límite de solicitudes: cada llamada consume la cuota de Gemini, energía y espacio en la base | `api_router.py`, ruta `crear_reclamo` | Medio: costo, saturación y reclamos basura | Media |
| A04-02 | La regla HITL se protege con un trigger en la base (bien diseñado), pero el endpoint del backend permite intentar cambios de estado sin identidad del operador | `hitl_auditoria.sql`; `api_router.py` | Medio | Media |

### A05 · Security Misconfiguration — Medio

| ID | Hallazgo | Evidencia | Impacto | Probabilidad |
|---|---|---|---|---|
| A05-01 | CORS con `allow_origins=["*"]` junto con `allow_credentials=True` (cualquier sitio puede llamar a la API desde el navegador de un usuario) | `main.py`; captura A01 | Medio | Media |
| A05-02 | La API y el frontend no envían cabeceras de seguridad (`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Strict-Transport-Security`) | `main.py` sin middleware de cabeceras; no existe `vercel.json` | Bajo-Medio (clickjacking, *sniffing*) | Media |
| A05-03 | La documentación interactiva `/docs` es pública y permite probar todos los endpoints | Captura A04 | Bajo (agrava A01) | Alta |
| — | Los errores ya no exponen detalles internos (corregido en la Fase 1, M3) | `api_router.py`, `error_interno` | — | Cumple |

### A06 · Vulnerable and Outdated Components — Medio

| ID | Hallazgo | Evidencia |
|---|---|---|
| A06-01 | No hay análisis automático de vulnerabilidades (`npm audit`, `pip-audit`) en ningún flujo; en este entorno sin conexión no se pudo ejecutar, por lo que el estado real de CVE **no está verificado** | No existe `.github/workflows/` |
| A06-02 | Dependencias de Python con rangos de versión, sin archivo de bloqueo (cada despliegue puede instalar versiones distintas) | `backend/requirements.txt` |
| A06-03 | Dependencia sin uso (`axios`) que amplía la superficie de ataque | `frontend/package.json` |

### A07 · Identification and Authentication Failures — Medio

| Revisión | Resultado | Evidencia |
|---|---|---|
| Inicio de sesión | Delegado a Supabase Auth (contraseñas fuera del sistema, tokens JWT con expiración) | `api.js`, `iniciarSesion` |
| Mensajes de error | Genéricos ("Correo o contraseña incorrectos") | `api.js` |
| Sesión | Expira con el token; se guarda en `sessionStorage` (se borra al cerrar la pestaña) | `App.jsx`, `leerSesion` |
| **Brecha** | El backend no valida ningún token: la autenticación existe solo en el frontend y en Supabase | `api_router.py` (A01-02) |
| No verificable | Política de contraseñas y MFA de Supabase (configuración del panel, no del repositorio) | — |

### A08 · Software and Data Integrity Failures — Medio

| ID | Hallazgo | Evidencia |
|---|---|---|
| A08-01 | Render y Vercel despliegan automáticamente lo que llega a `main` sin ejecutar pruebas antes | No hay CI (`.github/workflows/` inexistente) |
| A08-02 | Sin archivo de bloqueo de Python (ver A06-02) | `requirements.txt` |

### A09 · Security Logging and Monitoring Failures — Medio

| ID | Hallazgo | Evidencia |
|---|---|---|
| A09-01 | No se registra quién cambia el estado de un reclamo, ni los accesos denegados | `api_router.py`; las actualizaciones del SIGEM van directo a Supabase sin bitácora |
| — | Desde la Fase 1 los errores se registran con `logging` y un código de incidente | `api_router.py`, `error_interno` |

### A10 · SSRF — Bajo (no aplica)

El backend solo llama a destinos fijos (Gemini, Supabase, DagsHub). Ningún endpoint recibe una URL del usuario. `api_router.py`, `gemini_adapter.py`, `main.py`.

## 4. Score global de seguridad

**56 / 100** — suma de los puntajes por categoría (10 categorías × 10 puntos). Las dos causas principales son A02-01 (token publicado) y A01 (API sin autenticación).

## 5. Evidencias (capturas)

| Captura | Muestra |
|---|---|
| A01 | `backend/main.py` en `main`: token de DagsHub escrito en el código (valor oculto) y CORS abierto |
| A03 | Rutas `GET` y `PATCH` sin autenticación |
| A04 | Swagger público en producción, sin botón *Authorize* |
| A06 | `GET /api/reclamos` en producción, accesible sin sesión |
