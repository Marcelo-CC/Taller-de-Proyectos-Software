# Stack tecnológico

> Fase 1 · Prompt 1 – Descubrimiento Tecnológico. Fuente: repositorio `Marcelo-CC/Taller-de-Proyectos-Software`, rama `main` (commit `73a6f5e`). Se identificó cada tecnología a partir de los archivos del proyecto, sin suponer el lenguaje ni el framework.

## Tabla de tecnologías

| Categoría | Tecnología | Evidencia | Confianza |
|---|---|---|---|
| Lenguaje | Python 3.11 | `backend/**/*.py`; `python-version: "3.11"` en `.github/workflows/calidad-seguridad.yml` | Alta |
| Lenguaje | JavaScript (ES módulos) y JSX | `frontend/src/**/*.jsx`, `"type": "module"` en `frontend/package.json` | Alta |
| Lenguaje | SQL (PostgreSQL / PL/pgSQL) | `backend/sql/*.sql` (`CREATE FUNCTION … LANGUAGE plpgsql`, `CREATE TRIGGER`) | Alta |
| Lenguaje | CSS | `frontend/src/App.css`, `frontend/src/index.css` | Alta |
| Framework backend | FastAPI | `from fastapi import FastAPI` en `backend/main.py`; `fastapi>=0.115.0` en `requirements.txt` | Alta |
| Servidor ASGI | Uvicorn | `uvicorn>=0.30.0` en `requirements.txt`; comando `uvicorn main:app` en el README | Alta |
| Validación de datos | Pydantic 2 | `Field(min_length=…, max_length=…)` en `adapters/input/dtos.py` | Alta |
| Framework frontend | React 19 | `"react": "^19.2.8"` en `frontend/package.json`; `main.jsx` | Alta |
| Herramienta de build | Vite 8 | `"vite": "^8.3.0"`, `vite.config.js` | Alta |
| Gráficos | Recharts 3 | `import … from 'recharts'` en `pages/sigem/DashboardGreenAI.jsx` | Alta |
| Base de datos | PostgreSQL gestionado por Supabase | `supabase.table("reclamos")` en `supabase_reclamo_repository.py`; scripts `backend/sql/` | Alta |
| Cliente de base de datos | supabase-py y API REST de Supabase (PostgREST) | `create_client` en `main.py`; `fetch(${SUPABASE_URL}/rest/v1/reclamos…)` en `frontend/src/services/api.js` | Alta |
| Inteligencia artificial | Google Gemini (`gemini-flash-lite-latest`, respaldo `gemini-flash-latest`) con el SDK `google-genai` | `gemini_adapter.py`; `google-genai>=1.50.0` | Alta |
| Telemetría ambiental | CodeCarbon | `EmissionsTracker` en `registrar_reclamo_use_case.py` | Alta |
| MLOps | MLflow sobre DagsHub | `mlflow.start_run()`, `dagshub.init(...)` en `main.py` | Alta |
| Autenticación | Supabase Auth (JWT) | `/auth/v1/token?grant_type=password` en `api.js`; `verificar_usuario` en `security/autenticacion.py`; `HTTPBearer` en `api_router.py` | Alta |
| Autorización en la base | Permisos por columna, RLS y función `SECURITY DEFINER` | `GRANT/REVOKE` y `consultar_reclamo` en `backend/sql/modulo_c_consulta.sql` | Alta |
| Pruebas | pytest | `pytest.ini`, `requirements-dev.txt`, `backend/tests/` | Alta |
| Calidad frontend | ESLint | `eslint.config.js`, script `npm run lint` | Alta |
| DevOps · Integración continua | GitHub Actions | `.github/workflows/calidad-seguridad.yml` (pytest, build, `pip-audit`, `npm audit`) | Alta |
| DevOps · Dependencias | Dependabot | `.github/dependabot.yml` (pip, npm, github-actions) | Alta |
| Despliegue backend | Render (servicio web) | URL por defecto `https://taller-de-proyectos-software.onrender.com` en `api.js`; README | Alta |
| Despliegue frontend | Vercel | `frontend/vercel.json`; regex de orígenes `*.vercel.app` en `security/cabeceras.py` | Alta |
| Experimentación | Google Colab (prueba de concepto) | Enlace en el informe y el README; no hay notebook en el repositorio | Media |
| Tecnología residual | Node.js + Express + `pg` | `backend/package.json` y `backend/package-lock.json`; no hay ningún archivo `.js` en `backend/` | Alta (no se usa) |

## Servicios externos

| Servicio | Uso | Evidencia |
|---|---|---|
| Supabase | Base de datos PostgreSQL, API REST y autenticación | `SUPABASE_URL`, `SUPABASE_KEY`, `VITE_SUPABASE_*` |
| Google AI Studio (Gemini API) | Corrección, anonimización y clasificación del reclamo | `GEMINI_API_KEY` |
| DagsHub | Servidor MLflow para registrar cada inferencia | `MLFLOW_TRACKING_PASSWORD`, `DAGSHUB_REPO_*` |
| Render | Alojamiento del backend | URL de la API |
| Vercel | Alojamiento del frontend | `vercel.json` |
| GitHub | Código, Actions y Dependabot | `.github/` |

## Conclusión técnica

El sistema es una aplicación web de dos capas desplegadas por separado: un **backend en Python con FastAPI** (Render) y un **frontend en React con Vite** (Vercel), que comparten una base **PostgreSQL en Supabase**, la cual además resuelve la autenticación del personal (Supabase Auth). La inteligencia artificial no se ejecuta localmente: se consume como servicio (**Gemini API**) y cada inferencia se mide con **CodeCarbon** y se registra en **MLflow (DagsHub)**. El proyecto cuenta con integración continua en **GitHub Actions** y vigilancia de dependencias con **Dependabot**. El único elemento ajeno a la arquitectura actual es el `package.json` de Node/Express dentro de `backend/`, resto de una versión anterior que no tiene código asociado.
