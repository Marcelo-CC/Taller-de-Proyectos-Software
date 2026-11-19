# Servicios externos requeridos

> Fase 3 · Prompt 4 – Reconstrucción del Entorno (servicios y bases de datos). Fuente: código, variables de entorno y scripts SQL del repositorio.

## Servicios

| Servicio | Para qué se usa | Cómo se configura | ¿Obligatorio? | Qué pasa si falla |
|---|---|---|---|---|
| **Supabase · PostgreSQL** | Tabla `reclamos` (texto anonimizado, categoría, estado, confianza, energía, emisiones, hash del código) | Crear el proyecto y ejecutar `backend/sql/modulo_c_consulta.sql`, `hitl_auditoria.sql` y `seguridad_permisos.sql` | Sí | La API no arranca o no guarda; el SIGEM no lista |
| **Supabase · Auth** | Login del personal municipal (correo y contraseña) y validación del token en la API | Authentication → Users: crear los usuarios operadores | Sí (SIGEM) | El personal no puede ingresar |
| **Supabase · RPC** | `consultar_reclamo(ticket, código)` para el Módulo C | Script `modulo_c_consulta.sql` | Sí (consulta) | El vecino no puede consultar su trámite |
| **Google Gemini API** | Corrige la redacción, anonimiza el texto libre y clasifica | Clave en `GEMINI_API_KEY` | Recomendado | Se usa la clasificación local por palabras clave con confianza ≤ 50 % (el reclamo va a revisión HITL) |
| **DagsHub · MLflow** | Registro de cada inferencia (categoría, confianza, kWh, gCO₂e) | `MLFLOW_TRACKING_PASSWORD` y `DAGSHUB_*` | No | La API sigue funcionando y solo deja de registrar en MLflow |
| **Render** | Ejecuta el backend | Servicio web Python, raíz `backend/`, inicio con Uvicorn y variables de entorno | Sí (producción) | No hay registro de reclamos |
| **Vercel** | Publica el frontend | Proyecto con raíz `frontend/`, build `npm run build`, variables `VITE_*` | Sí (producción) | No hay interfaz |
| **GitHub Actions / Dependabot** | Pruebas, build y auditoría de dependencias en cada cambio | `.github/` | No (calidad) | Los cambios no se verifican automáticamente |

## Base de datos requerida

**Motor:** PostgreSQL (Supabase). **Tabla principal:** `reclamos`.

| Columna | Tipo | Origen |
|---|---|---|
| `id` | bigint (identidad) | Número de ticket |
| `created_at` | timestamptz | Fecha de registro |
| `titulo`, `descripcion` | text | Texto ya anonimizado |
| `categoria` | text | Vías Públicas, Limpieza Pública, Parques y Jardines o Alumbrado |
| `estado` | text | `PENDIENTE`, `EN_PROCESO` o `RESUELTO` |
| `confianza` | double precision | Confianza de la IA (0–1) |
| `requiere_auditoria` | boolean | Retenido para revisión humana (HITL) |
| `emisiones_gco2`, `consumo_kwh` | double precision | Telemetría de CodeCarbon |
| `codigo_hash` | text | SHA-256 del código secreto (no legible por la API pública) |

El repositorio no contiene el `CREATE TABLE reclamos`; la estructura anterior se reconstruyó a partir de las columnas que usan el repositorio (`COLUMNAS` en `supabase_reclamo_repository.py`) y los scripts `ALTER TABLE`.

## Roles y permisos de la base

| Rol | Lectura | Modificación |
|---|---|---|
| `anon` (clave pública) | Columnas públicas de `reclamos` (sin `codigo_hash`) y `consultar_reclamo` | Ninguna (tras `seguridad_permisos.sql`) |
| `authenticated` (operador con sesión) | Columnas públicas | `estado`, `categoria`, `requiere_auditoria` |
| `service_role` (backend con clave secreta) | Todo | Todo |
