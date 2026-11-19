# Variables de entorno

> Fase 3 · Prompt 5 – Variables de Entorno. Archivos analizados: `backend/.env.example`, `backend/main.py`, `backend/src/**` (`os.getenv`), `frontend/src/**` (`import.meta.env`), `.gitignore`. No existen `config.py`, `settings.py` ni `docker-compose.yml`. Los valores de ejemplo son ficticios: los valores reales viven solo en Render y Vercel.

## Backend (Render)

| Variable | Obligatoria | Descripción | Valor de ejemplo | Tipo |
|---|---|---|---|---|
| `SUPABASE_URL` | Sí | URL del proyecto de Supabase. Sin ella la API no arranca (`ValueError` en `main.py`) | `https://xxxxxxxx.supabase.co` | Base de datos |
| `SUPABASE_KEY` | Sí | Clave del proyecto. En producción debe ser la **clave secreta** (`sb_secret_…`), porque el rol público no puede modificar reclamos | `sb_secret_…` | **Secreto** · Base de datos |
| `GEMINI_API_KEY` | Sí | Clave de la API de Gemini | `clave-de-gemini` | **Secreto** · API externa |
| `GEMINI_MODEL` | No | Modelo principal | `gemini-flash-lite-latest` | API externa |
| `GEMINI_MODEL_RESPALDO` | No | Modelo de respaldo si el principal no responde en 20 s | `gemini-flash-latest` | API externa |
| `MLFLOW_TRACKING_PASSWORD` | No | Token de DagsHub; sin él la API funciona pero no registra en MLflow | `token-de-dagshub` | **Token** · API externa |
| `DAGSHUB_REPO_OWNER` | No | Dueño del repositorio de DagsHub | `Marcelo-CC` | API externa |
| `DAGSHUB_REPO_NAME` | No | Nombre del repositorio de DagsHub | `Taller-de-Proyectos-Software` | API externa |
| `MLFLOW_TRACKING_URI`, `MLFLOW_TRACKING_USERNAME` | No | Configuradas en Render; el código no las lee directamente (las usa la librería MLflow) | `https://dagshub.com/…mlflow` | API externa |
| `LOG_LEVEL` | No | Nivel de registro | `INFO` | Operación |
| `AUTH_OBLIGATORIA` | No | `false` desactiva la verificación de sesión en el listado y el cambio de estado (por defecto `true`) | `true` | Seguridad |
| `RATE_LIMIT_POR_MINUTO` | No | Reclamos por minuto permitidos por IP (por defecto 20; 0 desactiva) | `20` | Seguridad |
| `RATE_LIMIT_TOTAL_POR_MINUTO` | No | Reclamos por minuto en total (por defecto 120) | `120` | Seguridad |
| `CORS_ORIGINS` | No | Orígenes permitidos separados por coma (por defecto Vercel y `localhost:5173`) | `https://taller-de-proyectos-software.vercel.app` | Seguridad |
| `PORT` | Sí (Render) | Puerto que asigna Render al proceso | `10000` | Plataforma |

## Frontend (Vercel)

| Variable | Obligatoria | Descripción | Valor de ejemplo | Tipo |
|---|---|---|---|---|
| `VITE_API_URL` | No | URL de la API; si falta, usa la de Render | `https://taller-de-proyectos-software.onrender.com` | API |
| `VITE_SUPABASE_URL` | Sí | URL de Supabase para el login, la lectura del SIGEM y la consulta del vecino | `https://xxxxxxxx.supabase.co` | Base de datos |
| `VITE_SUPABASE_PUBLISHABLE_KEY` | Sí | Clave **pública** de Supabase (`sb_publishable_…`). Es visible en el navegador por diseño; nunca debe ser la secreta | `sb_publishable_…` | Base de datos (pública) |

## Clasificación

### Secretos
`SUPABASE_KEY` (secreta) y `GEMINI_API_KEY`. Solo deben existir en las variables de Render.

### Tokens
`MLFLOW_TRACKING_PASSWORD` (token de DagsHub). El historial del proyecto registra que un token anterior estuvo escrito en el código y fue revocado; hoy solo se lee desde el entorno.

### Configuración de base de datos
`SUPABASE_URL`, `SUPABASE_KEY` (backend) y `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY` (frontend). Los permisos por rol se configuran con los scripts de `backend/sql/`.

### Configuración de APIs externas
Gemini (`GEMINI_*`), DagsHub/MLflow (`MLFLOW_*`, `DAGSHUB_*`) y la URL de la API propia (`VITE_API_URL`).

## Observaciones

| # | Observación | Severidad |
|---|---|---|
| 1 | `.env.example` no documenta `AUTH_OBLIGATORIA`, `RATE_LIMIT_POR_MINUTO`, `RATE_LIMIT_TOTAL_POR_MINUTO` ni `CORS_ORIGINS` (solo aparecen en el código) | Baja |
| 2 | No existe `frontend/.env.example`; las tres variables `VITE_*` solo se mencionan en el README | Baja |
| 3 | `.gitignore` excluye `.env` y `.env.*` (salvo `.env.example`): no hay secretos versionados en `main` | — (correcto) |
| 4 | `AUTH_OBLIGATORIA=false` desactiva la protección del SIGEM; debe quedar en `true` o sin definir en producción | Media (riesgo de configuración) |
