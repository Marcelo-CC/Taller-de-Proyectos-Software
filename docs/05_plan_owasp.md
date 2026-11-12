# 05 · Plan de remediación OWASP Top 10 — Green AI Municipal

| Dato | Valor |
|---|---|
| Entrada | `docs/04_auditoria_owasp.md` |
| Rol | Agente 5 — Planificador OWASP Top 10 (Arquitecto de Seguridad) |
| Restricciones | No romper funcionalidad, no afectar procesos de negocio, mantener compatibilidad hacia atrás |

## 1. Remediaciones por vulnerabilidad

### R1 · Token de DagsHub expuesto (A02-01) — **Crítico**

| Campo | Detalle |
|---|---|
| Riesgo | Acceso de terceros a la cuenta de DagsHub/MLflow |
| Impacto | Alto |
| Componentes | `backend/main.py`, cuenta de DagsHub, variables de entorno de Render |
| Mitigación | 1) Código: el token se lee solo de `MLFLOW_TRACKING_PASSWORD` (hecho en la Fase 1). 2) **Revocar el token publicado** y crear uno nuevo en DagsHub. 3) Configurar el nuevo token solo en Render. 4) No reescribir el historial de Git (riesgoso para el equipo): el token viejo queda inutilizado al revocarlo |
| Validación | El token viejo deja de funcionar en DagsHub; Render registra de nuevo en MLflow; `git grep 08a361` en la rama no encuentra nada |
| Rollback | No aplica a la revocación (es irreversible por diseño). Si MLflow falla, la API sigue funcionando (M4) |

### R2 · API sin autenticación (A01-01, A01-02, A07) — **Alto**

| Campo | Detalle |
|---|---|
| Riesgo | Lectura masiva y cambios de estado por terceros |
| Impacto | Alto |
| Componentes | `api_router.py`, nuevo módulo `src/infrastructure/security/autenticacion.py`, `frontend/src/services/api.js`, `Sigem.jsx` |
| Mitigación | `GET /api/reclamos` y `PATCH /api/reclamos/{id}/estado` exigen el token JWT de Supabase Auth del personal municipal (`Authorization: Bearer`), validado con `supabase.auth.get_user`. `POST /api/reclamos` sigue siendo público (es el portal del vecino). El frontend envía el token de la sesión en sus lecturas |
| Compatibilidad | El SIGEM ya tiene el token de la sesión; el flujo principal de lectura va directo a Supabase y no depende del backend. Ningún cliente legítimo usa el `PATCH` del backend sin sesión |
| Validación | Pruebas: sin token → 401; token inválido → 401; token válido → acceso. En producción: `GET /api/reclamos` en el navegador devuelve 401 |
| Rollback | Variable `AUTH_OBLIGATORIA=false` en Render (desactiva la verificación sin volver a desplegar) o `git revert` |

### R3 · Sin límite de solicitudes (A04-01) — **Medio**

| Campo | Detalle |
|---|---|
| Riesgo | Abuso del endpoint público y consumo de cuota de Gemini |
| Impacto | Medio |
| Componentes | Nuevo módulo `src/infrastructure/security/limitador.py`, `api_router.py` |
| Mitigación | Límite en memoria de 20 reclamos por minuto por IP y 120 por minuto en total; al superarlo se responde 429 con un mensaje en español |
| Compatibilidad | Un vecino registra 1 reclamo cada varios minutos; el script de carga secuencial (1 cada 2-13 s) queda por debajo de 20 por minuto |
| Validación | Pruebas: la solicitud 21 de la misma IP en un minuto se rechaza, otra IP no se afecta, la ventana se libera al minuto |
| Rollback | `RATE_LIMIT_POR_MINUTO=0` en Render desactiva el límite |

### R4 · Configuración insegura (A05-01, A05-02) — **Medio**

| Campo | Detalle |
|---|---|
| Riesgo | Llamadas desde sitios ajenos, clickjacking, *sniffing* de contenido |
| Impacto | Medio |
| Componentes | `main.py`, nuevo `frontend/vercel.json` |
| Mitigación | CORS solo para el dominio de Vercel del proyecto (y sus vistas previas) y `localhost`, sin `allow_credentials`; cabeceras de seguridad en todas las respuestas de la API (`nosniff`, `DENY`, `no-referrer`, HSTS) y en el frontend (`vercel.json`), sin CSP estricta para no romper Swagger ni las fuentes |
| Validación | Prueba de las cabeceras; en producción, el frontend de Vercel sigue registrando reclamos |
| Rollback | `CORS_ORIGINS=*` en Render si otro dominio necesita acceso; borrar `vercel.json` |

### R5 · Bitácora de seguridad (A09-01) — **Medio**

| Campo | Detalle |
|---|---|
| Riesgo | No poder investigar cambios o abusos |
| Impacto | Medio |
| Componentes | `api_router.py` (registrador `auditoria`) |
| Mitigación | Registrar cada cambio de estado con el correo del operador, cada acceso denegado y cada solicitud rechazada por el límite |
| Validación | Prueba que verifica el mensaje de auditoría; revisión de los logs de Render |
| Rollback | `git revert` (solo agrega registros) |

### R6 · Integridad del despliegue y componentes (A08-01, A06-01) — **Medio**

| Campo | Detalle |
|---|---|
| Riesgo | Desplegar código roto o dependencias con vulnerabilidades conocidas |
| Impacto | Medio |
| Componentes | Nuevo `.github/workflows/calidad-seguridad.yml` |
| Mitigación | GitHub Actions ejecuta `pytest` en cada push y pull request; además ejecuta `pip-audit` y `npm audit` en modo informativo (no bloquean el primer día, se revisan sus reportes) |
| Validación | La pestaña *Actions* de GitHub muestra el flujo en verde |
| Rollback | Borrar el archivo del workflow |

### R7 · Permisos del rol `anon` en Supabase (A01-03) — **Alto, aplicación condicionada**

| Campo | Detalle |
|---|---|
| Riesgo | Que el rol público pueda cambiar estados directamente por PostgREST |
| Impacto | Alto si las políticas RLS no lo impiden |
| Componentes | Base de datos Supabase; script `backend/sql/seguridad_permisos.sql` |
| Mitigación | Quitar `UPDATE` al rol `anon` (el SIGEM siempre actualiza con el token del operador, rol `authenticated`) |
| Condición | Aplicar solo después de confirmar en Render que `SUPABASE_KEY` es la clave `service_role` o `secret`; si fuera la clave pública, el backend perdería permisos |
| Validación | Consulta de verificación incluida en el script; el SIGEM sigue cambiando estados |
| Rollback | `GRANT UPDATE (estado) ON reclamos TO anon;` (incluido en el script) |

### Riesgos aceptados y pospuestos

| Hallazgo | Decisión |
|---|---|
| A02-02 Hash sin sal del código secreto | Bajo: la columna no es legible por la API. Cambiar el algoritmo invalidaría los códigos ya entregados a los vecinos |
| A05-03 `/docs` público | Bajo una vez que R2 exige autenticación; se deja para facilitar la evaluación académica |
| A06-02 Archivo de bloqueo de Python | Se planifica con `pip-tools` en la siguiente iteración |
| Política de contraseñas y MFA en Supabase | Configuración del panel; se recomienda activarla |

## 2. Roadmap de remediación y orden recomendado

| Orden | Remediación | Prioridad | Motivo del orden |
|---|---|---|---|
| 1 | R1 Revocar el token | Crítico | Es explotable hoy y no depende de código |
| 2 | R2 Autenticación en la API | Alto | Cierra la principal brecha de acceso |
| 3 | R5 Bitácora | Medio | Se apoya en la identidad que obtiene R2 |
| 4 | R3 Límite de solicitudes | Medio | Independiente y con interruptor |
| 5 | R4 CORS y cabeceras | Medio | Se valida al final con el frontend real |
| 6 | R6 Integración continua | Medio | Protege los siguientes despliegues |
| 7 | R7 Permisos de Supabase | Alto (condicionado) | Requiere confirmar la clave del backend |

## 3. Riesgos de implementación

| Riesgo | Mitigación |
|---|---|
| El SIGEM deja de cargar si el backend exige token | El SIGEM lee directo de Supabase; el respaldo por backend ahora envía el token de la sesión |
| El límite bloquea pruebas de carga del equipo | Límite por IP de 20/min y variable para desactivarlo |
| CORS bloquea el dominio real del frontend | Se permite el dominio de Vercel del proyecto, sus vistas previas y `localhost`; variable `CORS_ORIGINS` para ajustar sin desplegar |
| R7 quita permisos al backend | Condición explícita y script de reversión |

## 4. Estrategia para preservar la funcionalidad

1. Todo se implementa en la rama `mejoras-semana13`, con pruebas para cada control.
2. Cada control nuevo tiene un **interruptor por variable de entorno** (`AUTH_OBLIGATORIA`, `RATE_LIMIT_POR_MINUTO`, `CORS_ORIGINS`) para desactivarlo en Render en segundos si algo falla, sin volver a desplegar.
3. El endpoint público del vecino (`POST /api/reclamos`) y la consulta con código (Módulo C) no cambian de contrato.
4. Prueba manual después del despliegue: registrar un reclamo, consultarlo con su código, iniciar sesión en el SIGEM, cambiar un estado y auditar un reclamo HITL.
