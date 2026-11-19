# Inventario de archivos

> Fase 1 · Auditoría del proyecto. Fuente: repositorio `Marcelo-CC/Taller-de-Proyectos-Software`, rama `main` (commit `73a6f5e`, 19/11/2026).

## Resumen

| Carpeta | Archivos | Contenido |
|---|---|---|
| `.github` | 2 | Integración continua y Dependabot |
| `backend/src` | 17 | Backend FastAPI (dominio, aplicación, infraestructura) |
| `backend/tests` | 16 | Pruebas automatizadas |
| `backend/sql` | 5 | Scripts de Supabase (columnas, funciones, triggers, permisos) |
| `docs` | 9 | Auditorías FURPS+ y OWASP, guía de usuario |
| `frontend/src` | 20 | Aplicación React (portal, consulta, SIGEM) |
| `frontend/public` | 5 | Íconos y escudo |
| Raíz y configuración | 17 | .gitignore, README.md, backend/.env.example, backend/main.py, backend/package-lock.json, backend/package.json, backend/pytest.ini, backend/requirements-dev.txt, backend/requirements.txt, frontend/.gitignore, frontend/README.md, frontend/eslint.config.js, frontend/index.html, frontend/package-lock.json, frontend/package.json, frontend/vercel.json, frontend/vite.config.js |
| **Total versionado** | **91** | |

## Árbol de directorios

```
./.github/dependabot.yml
./.github/workflows/calidad-seguridad.yml
./.gitignore
./README.md
./backend/.env.example
./backend/main.py
./backend/package.json
./backend/pytest.ini
./backend/requirements-dev.txt
./backend/requirements.txt
./backend/sql/codigos_demo.sql
./backend/sql/hitl_auditoria.sql
./backend/sql/hitl_demo.sql
./backend/sql/modulo_c_consulta.sql
./backend/sql/seguridad_permisos.sql
./backend/src/application/useCases/gestionar_reclamos_use_case.py
./backend/src/application/useCases/registrar_reclamo_use_case.py
./backend/src/domain/entities/reclamo.py
./backend/src/domain/ports/input/gestionar_reclamos_port.py
./backend/src/domain/ports/input/registrar_reclamo_port.py
./backend/src/domain/ports/output/reclamo_repository_port.py
./backend/src/domain/services/evaluacion_confianza.py
./backend/src/domain/valueObjects/codigo_consulta.py
./backend/src/domain/valueObjects/estado_reclamo.py
./backend/src/infrastructure/adapters/input/api_router.py
./backend/src/infrastructure/adapters/input/dtos.py
./backend/src/infrastructure/adapters/output/gemini_adapter.py
./backend/src/infrastructure/adapters/output/supabase_reclamo_repository.py
./backend/src/infrastructure/security/__init__.py
./backend/src/infrastructure/security/autenticacion.py
./backend/src/infrastructure/security/cabeceras.py
./backend/src/infrastructure/security/limitador.py
./backend/tests/__init__.py
./backend/tests/conftest.py
./backend/tests/dobles.py
./backend/tests/test_anonimizacion.py
./backend/tests/test_api_errores.py
./backend/tests/test_api_seguridad.py
./backend/tests/test_autenticacion.py
./backend/tests/test_cabeceras.py
./backend/tests/test_clasificacion_local.py
./backend/tests/test_codigo_consulta.py
./backend/tests/test_dtos.py
./backend/tests/test_evaluacion_confianza.py
./backend/tests/test_gestionar_reclamos.py
./backend/tests/test_limitador.py
./backend/tests/test_registrar_reclamo.py
./backend/tests/test_revision_correccion.py
./docs/01_auditoria_furps.md
./docs/02_plan_furps.md
./docs/03_auditoria_implementacion_furps.md
./docs/04_auditoria_owasp.md
./docs/05_plan_owasp.md
./docs/06_auditoria_implementacion_owasp.md
./docs/07_auditoria_final.md
./docs/08_auditoria_final_cierre.md
./docs/GUIA_RAPIDA_USUARIO.md
./frontend/.gitignore
./frontend/README.md
./frontend/eslint.config.js
./frontend/index.html
./frontend/package.json
./frontend/public/apple-touch-icon.png
./frontend/public/escudo-huancayo.png
./frontend/public/favicon.png
./frontend/public/favicon.svg
./frontend/public/icons.svg
./frontend/src/App.css
./frontend/src/App.jsx
./frontend/src/assets/hero.png
./frontend/src/assets/react.svg
./frontend/src/assets/vite.svg
./frontend/src/components/Layout.jsx
./frontend/src/constantes.js
./frontend/src/index.css
./frontend/src/main.jsx
./frontend/src/pages/ConsultaTramite.jsx
./frontend/src/pages/GuiaUsuario.jsx
./frontend/src/pages/Inicio.jsx
./frontend/src/pages/LoginMunicipal.jsx
./frontend/src/pages/PortalCiudadano.jsx
./frontend/src/pages/Sigem.jsx
./frontend/src/pages/sigem/BusquedaFiltrado.jsx
./frontend/src/pages/sigem/DashboardGreenAI.jsx
./frontend/src/pages/sigem/TablaReclamos.jsx
./frontend/src/services/api.js
./frontend/src/services/exportar.js
./frontend/vercel.json
./frontend/vite.config.js
```

## Tamaño del código fuente (líneas)

| Componente | Archivos | Líneas |
|---|---|---|
| Backend (Python, src y main.py) | 18 | 1009 |
| Pruebas (pytest) | 16 | 704 |
| SQL de Supabase | 5 | 145 |
| Frontend (JSX/JS) | 15 | 1653 |
| Estilos (CSS) | 2 | 862 |
