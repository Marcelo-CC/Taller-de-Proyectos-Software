# Dependencias de infraestructura

> Fase 2 · Prompt 3 – Dependencias. Archivos analizados: `.github/workflows/calidad-seguridad.yml`, `.github/dependabot.yml`, `frontend/vercel.json`, `backend/sql/*.sql`, `README.md`.

## Plataformas y servicios

| Componente | Proveedor | Plan | Configuración en el repositorio | Criticidad |
|---|---|---|---|---|
| Backend | Render (servicio web Python) | Gratuito (512 MB RAM, 0,1 vCPU, se suspende sin uso) | Comando de inicio configurado en Render: `python -m uvicorn main:app --host 0.0.0.0 --port $PORT` | Crítica |
| Frontend | Vercel | Gratuito | `frontend/vercel.json` (cabeceras de seguridad) | Crítica |
| Base de datos y autenticación | Supabase (PostgreSQL + Auth) | Gratuito | `backend/sql/` (5 scripts) | Crítica |
| IA | Google Gemini API | Capa gratuita | `GEMINI_API_KEY` | Alta (hay respaldo local) |
| MLOps | DagsHub (MLflow) | Gratuito | `MLFLOW_TRACKING_PASSWORD` | Media (opcional) |
| Código y CI/CD | GitHub, GitHub Actions, Dependabot | Gratuito | `.github/` | Alta |

## Integración continua (`calidad-seguridad.yml`)

| Job | Entorno | Pasos | ¿Bloquea? |
|---|---|---|---|
| Backend · pruebas y dependencias | ubuntu-latest, Python 3.11 | `pip install -r requirements-dev.txt` → `pytest -v` → `pip-audit -r requirements.txt` | Sí |
| Frontend · build y dependencias | ubuntu-latest, Node 22 | `npm ci` → `npm run build` → `npm audit --omit=dev --audit-level=high` | Sí |

Se ejecuta en cada push a `main` y en cada pull request, con permisos mínimos (`contents: read`).

## Acciones de GitHub usadas (y versiones)

| Acción | Versión usada | Observación |
|---|---|---|
| actions/checkout | v4 | Dependabot propone v7 |
| actions/setup-python | v5 | Dependabot propone v7 |
| actions/setup-node | v4 | Dependabot propone v7 |

GitHub advierte en cada ejecución que estas versiones usan Node.js 20, que está deprecado en los ejecutores, y que la etiqueta `ubuntu-latest` migrará a Ubuntu 26.

## Dependabot (`dependabot.yml`)

Revisa cada lunes (America/Lima) `pip` en `/backend`, `npm` en `/frontend` (con las actualizaciones menores agrupadas) y mensualmente las acciones de GitHub. En su primera revisión abrió 9 pull requests (#5 a #13), todos con las verificaciones en verde.

## Base de datos (scripts SQL)

| Script | Objeto que crea | Propósito |
|---|---|---|
| `modulo_c_consulta.sql` | Columna `codigo_hash`, función `consultar_reclamo` (`SECURITY DEFINER`), permisos por columna | Consulta del vecino con ticket y código secreto |
| `hitl_auditoria.sql` | Columnas `confianza` y `requiere_auditoria`, función y trigger `proteger_auditoria_hitl` | Regla HITL dentro de la base |
| `seguridad_permisos.sql` | `REVOKE UPDATE ON reclamos FROM anon` (con reversión) | Control de acceso |
| `codigos_demo.sql`, `hitl_demo.sql` | Datos de demostración | Pruebas manuales |

## Observaciones

- No hay contenedores (`Dockerfile`, `docker-compose.yml`) ni infraestructura como código (Terraform, `render.yaml`): la configuración de Render, Vercel y Supabase vive en sus paneles web y no se puede reproducir solo desde el repositorio.
- La tabla `reclamos` no tiene un script de creación inicial (`CREATE TABLE`) en el repositorio; los scripts asumen que ya existe.
- El despliegue de Render se hace de forma manual tras cada merge (el despliegue automático no se disparó en las pruebas del 12/11/2026); Vercel sí despliega solo.
