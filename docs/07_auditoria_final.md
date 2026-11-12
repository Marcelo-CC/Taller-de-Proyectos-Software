# 07 · Auditoría final integral — Green AI Municipal

| Dato | Valor |
|---|---|
| Entradas | `docs/03_auditoria_implementacion_furps.md`, `docs/06_auditoria_implementacion_owasp.md` y el estado actual de la rama `mejoras-semana13` |
| Rol | Agente 7 — Auditor principal de calidad y seguridad |
| Fecha | 12/11/2026 |

## 1. Resumen ejecutivo

Partiendo de un sistema funcional en producción, se aplicaron mejoras de calidad (FURPS+) y de seguridad (OWASP Top 10) en una rama aparte, sin cambiar ninguna ruta de la API ni el flujo de los vecinos y del personal municipal. El proyecto pasó de **0 a 55 pruebas automatizadas**, el puntaje FURPS+ subió de **69 a 77** y el score de seguridad de **56 a 77**.

Quedan dos acciones fuera del código que dependen del equipo: **revocar el token de DagsHub publicado** (crítico) y **revisar los permisos del rol público en Supabase**. Además, la rama todavía debe desplegarse y verificarse en producción.

## 2. Estado de calidad (FURPS+)

| Factor | Antes | Después |
|---|---|---|
| Functionality | 85 | 85 |
| Usability | 80 | 85 |
| Reliability | 62 | 75 |
| Performance | 65 | 65 |
| Supportability | 45 | 75 |
| **Global** | **69** | **77** |

**Dictamen de calidad: CUMPLE PARCIALMENTE FURPS+.** Se implementaron todas las mejoras críticas y altas (pruebas, validación de entradas, manejo de errores, arranque tolerante) y no quedan hallazgos críticos de calidad. Quedan pendientes, por decisión del plan, la paginación del listado, la exportación PDF/CSV, la limpieza de dependencias sin uso y un comando para dejar de versionar los archivos generados.

## 3. Estado de seguridad (OWASP Top 10)

| Categoría | Antes | Después |
|---|---|---|
| A01 Broken Access Control | 3 | 7 |
| A02 Cryptographic Failures | 2 | 4 |
| A03 Injection | 9 | 9 |
| A04 Insecure Design | 5 | 8 |
| A05 Security Misconfiguration | 5 | 8 |
| A06 Vulnerable Components | 6 | 7 |
| A07 Authentication Failures | 6 | 8 |
| A08 Integrity Failures | 5 | 8 |
| A09 Logging and Monitoring | 5 | 8 |
| A10 SSRF | 10 | 10 |
| **Score** | **56** | **77** |

**Dictamen de seguridad: CUMPLE PARCIALMENTE OWASP Top 10.** La API ya exige autenticación al personal, limita el abuso del registro público, restringe CORS, envía cabeceras de seguridad y deja bitácora. El único hallazgo crítico (A02-01) está corregido en el código, pero **no se considera mitigado hasta que el token publicado se revoque**.

## 4. Funcionalidad

**Dictamen: se preservó la funcionalidad existente; existen riesgos de regresión acotados, pendientes de verificar en producción.**

| Revisión | Resultado |
|---|---|
| Pruebas automatizadas | 53 pasadas y 2 omitidas en este entorno (las 2 omitidas requieren FastAPI y corren en GitHub Actions); 0 fallidas |
| Rutas y contratos de la API | Sin cambios |
| Registro, consulta con código, SIGEM y auditoría HITL | Sin cambios en su funcionamiento; cubiertos por pruebas o sin modificar |
| Riesgos de regresión | (1) CORS si el frontend usa otro dominio; (2) MLflow deja de registrar si Render no tiene `MLFLOW_TRACKING_PASSWORD`. Ambos se corrigen con variables de entorno, sin volver a desplegar |

## 5. Riesgo operativo

**Clasificación: MEDIO** mientras el token de DagsHub no se revoque y la rama no se verifique en producción. Pasa a **BAJO** al completar las acciones de la sección 6.

## 6. Riesgos pendientes

| # | Riesgo | Nivel | Acción | Responsable |
|---|---|---|---|---|
| 1 | Token de DagsHub publicado y vigente | Crítico | Revocarlo en DagsHub, crear uno nuevo y ponerlo en Render como `MLFLOW_TRACKING_PASSWORD` | Dueño de la cuenta de DagsHub |
| 2 | Permisos de `UPDATE` del rol `anon` en Supabase | Alto | Confirmar la clave del backend y ejecutar `backend/sql/seguridad_permisos.sql` | Equipo |
| 3 | Cambios sin desplegar | Medio | Unir la rama y hacer la verificación manual de la sección 7 | Equipo |
| 4 | Listado sin paginación y arranque en frío de Render | Medio | Próxima iteración / plan de hosting | Equipo |
| 5 | Archivos generados versionados | Bajo | `git rm --cached mlflow.db emissions.csv backend/emissions.csv` | Equipo |

## 7. Observaciones

1. Verificación manual obligatoria después de desplegar: registrar un reclamo desde el portal, consultarlo con su ticket y código, iniciar sesión en el SIGEM, cambiar un estado y auditar un reclamo retenido; abrir `/api/reclamos` sin sesión y comprobar que responde 401.
2. Los interruptores `AUTH_OBLIGATORIA`, `RATE_LIMIT_POR_MINUTO` y `CORS_ORIGINS` permiten desactivar un control en Render en segundos si algo falla.
3. La primera ejecución de GitHub Actions mostrará los reportes de `pip-audit` y `npm audit`; las vulnerabilidades altas que aparezcan deben revisarse.
4. Recomendación para el futuro: no volver a escribir claves en el código; usar siempre `backend/.env` (ignorado por Git) y las variables de Render.

## 8. Recomendación final

### **APTO PARA PRODUCCIÓN CON OBSERVACIONES**

Condiciones para el despliegue de la rama `mejoras-semana13`:

1. Revocar el token de DagsHub publicado **antes o al mismo tiempo** que el despliegue.
2. Confirmar en Render las variables `MLFLOW_TRACKING_PASSWORD` (token nuevo) y, si el frontend usa otro dominio, `CORS_ORIGINS`.
3. Ejecutar la verificación manual de la sección 7 y conservar las capturas como evidencia.
