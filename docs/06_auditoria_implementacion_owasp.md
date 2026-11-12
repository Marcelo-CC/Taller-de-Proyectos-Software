# 06 · Auditoría de implementación OWASP — Green AI Municipal

| Dato | Valor |
|---|---|
| Entradas | `docs/04_auditoria_owasp.md`, `docs/05_plan_owasp.md` y el estado actual de la rama `mejoras-semana13` |
| Rol | Agente 6 — Auditor independiente de seguridad |
| Criterio | Ninguna vulnerabilidad se da por corregida sin evidencia (código, prueba ejecutada o captura) |

## 1. Estado de cada vulnerabilidad

| Hallazgo | Remediación | Estado | Evidencia |
|---|---|---|---|
| A02-01 Token de DagsHub publicado | R1 | **Parcialmente corregida** | El código ya no contiene el token y lo lee solo de `MLFLOW_TRACKING_PASSWORD` (captura D13: `git grep` sin resultados en `backend` y `frontend`). **Pendiente del equipo:** revocar el token publicado en DagsHub; mientras no se revoque sigue siendo válido porque está en el historial y en `main` |
| A01-01 Listado público | R2 | **Corregida (en la rama)** | `GET /api/reclamos` depende de `usuario_autenticado`; sin token responde 401 (captura D09; `test_sin_token_responde_401`) |
| A01-02 Cambio de estado sin autenticación | R2 | **Corregida (en la rama)** | `PATCH /api/reclamos/{id}/estado` exige token válido de Supabase Auth; 7 pruebas en `test_autenticacion.py` |
| A07 Backend sin verificación de identidad | R2 | **Corregida (en la rama)** | `verificar_usuario` valida el JWT con `supabase.auth.get_user`; Swagger mostrará el botón *Authorize* |
| A04-01 Sin límite de solicitudes | R3 | **Corregida** | `limitador.py`: 20 por minuto por IP y 120 en total, respuesta 429 (captura D10); 7 pruebas en `test_limitador.py`, incluida una que confirma que el script de carga secuencial no se bloquea |
| A05-01 CORS abierto con credenciales | R4 | **Corregida** | `main.py`: solo el dominio de Vercel del proyecto, sus vistas previas y `localhost`, sin `allow_credentials` (captura D11; `test_cabeceras.py`) |
| A05-02 Sin cabeceras de seguridad | R4 | **Corregida** | Middleware en `main.py` (`nosniff`, `DENY`, `no-referrer`, HSTS, `Permissions-Policy`, CSP en la API) y `frontend/vercel.json` |
| A09-01 Sin bitácora | R5 | **Corregida** | Registrador `auditoria`: cambios de estado con el correo del operador, accesos denegados y abusos del límite (captura D12; `test_acceso_denegado_queda_en_la_bitacora`) |
| A08-01 Despliegue sin pruebas / A06-01 sin análisis de dependencias | R6 | **Corregida en código, pendiente de primera ejecución** | `.github/workflows/calidad-seguridad.yml` (captura D14): `pytest` y `npm run build` bloquean; `pip-audit` y `npm audit` informan. Se ejecutará al subir la rama |
| A01-03 Permisos de `anon` en Supabase | R7 | **No corregida (condicionada)** | Script `backend/sql/seguridad_permisos.sql` listo, con verificación y reversión; se aplica solo tras confirmar qué clave usa el backend |
| A02-02 Hash sin sal / A05-03 `/docs` público / A06-02 sin archivo de bloqueo | — | Riesgo aceptado (plan) | Ver sección "Riesgos aceptados" del documento 05 |

Resultado de pruebas en este entorno: **53 pasadas y 2 omitidas** (las 2 omitidas prueban las dependencias de FastAPI, que no está instalado aquí; se ejecutan completas en GitHub Actions y en los equipos del grupo). Captura D08.

## 2. Búsqueda de nuevas vulnerabilidades y controles mal implementados

| Revisión | Resultado |
|---|---|
| El límite usa la primera IP de `X-Forwarded-For`, que un atacante puede falsificar para evadir el límite por IP | **Riesgo residual bajo:** el límite total de 120 por minuto sigue protegiendo la cuota de Gemini |
| El interruptor `AUTH_OBLIGATORIA=false` desactiva la autenticación | Control intencional para emergencias; debe quedar en `true` en Render y su cambio queda en el historial de Render |
| El límite vive en memoria | Se reinicia con cada despliegue; suficiente para una sola instancia de Render |
| CSP estricta en `/docs` | Se excluyó a propósito para no romper Swagger |
| Nuevos secretos en el código | Ninguno: `git grep` de claves y tokens sin resultados |

## 3. Regresiones funcionales derivadas de los cambios de seguridad

| Flujo | Resultado | Evidencia |
|---|---|---|
| Registro de reclamos del vecino (`POST`) | Sin cambios de contrato; solo se agrega el 429 por abuso | `test_registrar_reclamo.py`; `test_uso_normal_del_script_de_carga_no_se_bloquea` |
| Consulta de trámite (Módulo C) | Sin cambios: usa la función de Supabase, no la API | `ConsultaTramite.jsx` sin modificar |
| Listado del SIGEM | Sin cambios: sigue leyendo directo de Supabase; el respaldo por backend ahora envía el token de la sesión | `api.js`, `listarReclamos(token)`; `Sigem.jsx` |
| Cambio de estado y auditoría HITL | Sin cambios: el SIGEM ya actualizaba con el token del operador | `api.js`, `actualizarReclamo` sin modificar |
| Llamadas desde el frontend publicado | **Riesgo de regresión a verificar:** si el frontend usara un dominio distinto de `taller-de-proyectos-software.vercel.app`, CORS lo bloquearía. Se corrige sin desplegar con `CORS_ORIGINS` en Render | `cabeceras.py` |

## 4. Score de seguridad actualizado

| # | Categoría | Antes | Después (rama) | Con acciones pendientes del equipo |
|---|---|---|---|---|
| A01 | Broken Access Control | 3 | 7 | 9 (aplicar R7) |
| A02 | Cryptographic Failures | 2 | 4 | 8 (revocar el token) |
| A03 | Injection | 9 | 9 | 9 |
| A04 | Insecure Design | 5 | 8 | 8 |
| A05 | Security Misconfiguration | 5 | 8 | 8 |
| A06 | Vulnerable Components | 6 | 7 | 7 |
| A07 | Authentication Failures | 6 | 8 | 8 |
| A08 | Integrity Failures | 5 | 8 | 8 |
| A09 | Logging and Monitoring | 5 | 8 | 8 |
| A10 | SSRF | 10 | 10 | 10 |
| | **Score global** | **56** | **77** | **83** |

## 5. Riesgos residuales

| Riesgo | Nivel | Responsable |
|---|---|---|
| Token de DagsHub publicado y aún no revocado | **Crítico** hasta revocarlo | Equipo (Marcelo, dueño de la cuenta) |
| Permisos de `anon` en Supabase sin restringir (R7) | Alto, no verificado | Equipo, tras revisar la clave del backend |
| Cambios aún no desplegados ni verificados en producción | Medio | Equipo, al unir la rama |
| Evasión del límite por IP con `X-Forwarded-For` falso | Bajo | Aceptado |
| Hash sin sal del código secreto | Bajo | Aceptado |

## 6. Conclusión

Se corrigieron en la rama **6 de 8 hallazgos** del plan (A01-01, A01-02, A04-01, A05-01, A05-02, A09-01) y se implementaron los controles de A07 y A08/A06. Queda **parcialmente corregido el hallazgo crítico A02-01**, porque el token publicado solo deja de ser peligroso cuando el dueño de la cuenta lo revoca en DagsHub, y queda **pendiente R7**, que depende de una verificación en Supabase. No se encontraron regresiones en las pruebas; la verificación en producción se hará al desplegar la rama.

**El score de seguridad sube de 56 a 77 puntos (83 al completar las dos acciones del equipo).**
