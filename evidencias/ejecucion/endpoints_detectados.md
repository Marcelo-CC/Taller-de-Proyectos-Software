# Endpoints detectados

> Fase 4 · Ejecución. Fuentes: `backend/main.py`, `backend/src/infrastructure/adapters/input/api_router.py`, `/docs` en producción y llamadas de `frontend/src/services/api.js`.

## API propia (FastAPI en Render)

| Método | Ruta | Acceso | Entrada | Respuesta | Controles |
|---|---|---|---|---|---|
| GET | `/` | Público | — | Mensaje de estado | — |
| POST | `/api/reclamos` | Público (vecino) | `ReclamoDTO`: título ≤200, descripción ≤2000, ubicación ≤300, nombre, DNI, dirección, contacto (≤200) y categoría opcional (el formulario web limita a 120 y 1500) | Ticket, código secreto (una sola vez), categoría asignada, confianza, `requiere_auditoria`, texto anonimizado, kWh y gCO₂e | Límite 20/min por IP y 120/min global (429); validación Pydantic (422) |
| GET | `/api/reclamos?pagina=&por_pagina=` | Personal (Bearer JWT) | Paginación opcional (`por_pagina` 1–100, por defecto 25) | Lista de reclamos y, si hay `pagina`, total y número de páginas | 401 sin token válido |
| PATCH | `/api/reclamos/{id}/estado` | Personal (Bearer JWT) | `EstadoDTO`: `PENDIENTE`, `EN_PROCESO` o `RESUELTO` | Reclamo actualizado | 401 sin token; 422 si el estado no es válido; 404 si el reclamo no existe; cada cambio queda en la bitácora `auditoria` con el usuario |
| GET | `/docs`, `/openapi.json` | Público | — | Documentación OpenAPI | Botón "Authorize" |

Todas las respuestas llevan cabeceras de seguridad (`X-Content-Type-Options`, `X-Frame-Options: DENY`, `Referrer-Policy`, `Strict-Transport-Security`, `Permissions-Policy`) y CORS restringido a Vercel y `localhost:5173`. Los errores internos devuelven 500 con un código de incidente, sin trazas.

## APIs de Supabase consumidas directamente por el frontend

| Método | Ruta | Uso | Credencial |
|---|---|---|---|
| POST | `/auth/v1/token?grant_type=password` | Login del personal | Clave pública |
| GET | `/rest/v1/reclamos?select=…&order=id.desc` | Listado del SIGEM | Clave pública + JWT del operador |
| PATCH | `/rest/v1/reclamos?id=eq.{id}` | Cambio de estado y auditoría HITL de la categoría | JWT del operador (rol `authenticated`) |
| POST | `/rest/v1/rpc/consultar_reclamo` | Consulta del vecino (Módulo C) | Clave pública (rol `anon`) |

## APIs externas consumidas por el backend

| Servicio | Operación |
|---|---|
| Gemini API | `models.generate_content` (modelo principal y de respaldo, tiempo límite 20 s) |
| Supabase | `table("reclamos").insert/select/update`, `auth.get_user(token)` |
| DagsHub / MLflow | `start_run`, `log_param`, `log_metric` |
