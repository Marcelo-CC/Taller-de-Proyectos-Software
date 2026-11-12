# 08 · Auditoría final integral (cierre) — Green AI Municipal

| Dato | Valor |
|---|---|
| Entradas | `docs/03_auditoria_implementacion_furps.md`, `docs/06_auditoria_implementacion_owasp.md`, `docs/07_auditoria_final.md` y el estado actual del proyecto en producción (rama `main`) |
| Rol | Agente 7 — Auditor principal de calidad y seguridad (segunda aplicación, sobre el sistema terminado) |
| Fecha | 12/11/2026 |
| Motivo | El documento 07 se emitió antes de desplegar y con acciones del equipo pendientes. Este documento repite el dictamen con el estado final, sin modificar los anteriores, para que se vea cómo inició y cómo quedó el proyecto. |

## 1. Resumen ejecutivo

Todas las acciones que el documento 07 dejó pendientes se completaron y verificaron en producción el 12/11/2026:

- El token de DagsHub publicado se **revocó** y se reemplazó por uno nuevo que solo existe en Render.
- Las mejoras se unieron a `main` mediante pull requests con las verificaciones automáticas en verde y se **desplegaron** en Render y Vercel.
- El backend pasó a la **clave secreta de Supabase** y se aplicó **R7**: el rol público ya no puede modificar reclamos.
- Se cerró el **Product Backlog**: exportación PDF/CSV, guía rápida de usuario, paginación de 25 reclamos y Dependabot con auditoría de dependencias bloqueante.
- En las pruebas en producción se detectaron y corrigieron dos fallas de la corrección automática de redacción: el texto del reclamo ya no se recorta y las palabras comunes como «mi casa» ya no se enmascaran.

| Indicador | Inicio (docs 01 y 04) | Documento 07 | Cierre (este documento) |
|---|---|---|---|
| Pruebas automatizadas | 0 | 55 | 70 (68 sin FastAPI + 2 de la API en GitHub Actions) |
| Nivel de apego de la matriz FURPS+ (Semana 13) | 60 % | 90 % | **100 %** |
| Score de seguridad OWASP Top 10 | 56 | 77 | **85** |
| Riesgo operativo | Alto | Medio | **Bajo** |

## 2. Estado de calidad (FURPS+)

Nivel de apego por factor según la matriz de la Semana 13 (SÍ = 5, PARCIAL = 3, NO = 1; apego = PO / PD × 100):

| Factor | Preguntas | Apego inicial | Apego al cierre |
|---|---|---|---|
| Functionality | 4 | 80,0 % | 100 % |
| Usability | 4 | 70,0 % | 100 % |
| Reliability | 4 | 50,0 % | 100 % |
| Performance | 3 | 86,7 % | 100 % |
| Supportability | 3 | 20,0 % | 100 % |
| + (restricciones) | 4 | 50,0 % | 100 % |
| + (OWASP Top 10) | 10 | 60,0 % | 100 % |
| **Total** | **32** | **60,0 %** | **100 %** |

Las cuatro preguntas que seguían sin cumplir en el documento 07 quedaron resueltas:

| Pregunta | Antes | Ahora | Evidencia |
|---|---|---|---|
| ¿Se pueden exportar reportes de sostenibilidad en PDF/CSV? | NO | SÍ | Dashboard Green AI: «Descargar CSV (Excel)» y «Reporte PDF» (`frontend/src/services/exportar.js`) |
| ¿Se cuenta con una guía rápida de usuario? | NO | SÍ | Página «¿Cómo usar?» (`#/guia`), botón «Guía» del SIGEM y `docs/GUIA_RAPIDA_USUARIO.md` |
| ¿El listado escala con el crecimiento de reclamos (paginación)? | PARCIAL | SÍ | SIGEM con 25 reclamos por página; `GET /api/reclamos?pagina=&por_pagina=` devuelve la página y el total |
| ¿Se tiene implementado A06 (componentes vulnerables)? | PARCIAL | SÍ | `.github/dependabot.yml` (revisión semanal) y `pip-audit` / `npm audit` bloqueantes en GitHub Actions |

**Dictamen de calidad: CUMPLE FURPS+.** Las 32 preguntas de la matriz están en SÍ CUMPLE y no quedan hallazgos de calidad abiertos.

## 3. Estado de seguridad (OWASP Top 10)

| Categoría | Inicio | Documento 07 | Cierre | Qué cambió después del documento 07 |
|---|---|---|---|---|
| A01 Broken Access Control | 3 | 7 | 9 | R7: el rol `anon` ya no tiene permiso de `UPDATE` sobre `reclamos` (verificado en Supabase) |
| A02 Cryptographic Failures | 2 | 4 | 8 | Token de DagsHub revocado; claves secretas solo en variables de Render |
| A03 Injection | 9 | 9 | 9 | — |
| A04 Insecure Design | 5 | 8 | 8 | — |
| A05 Security Misconfiguration | 5 | 8 | 8 | — |
| A06 Vulnerable Components | 6 | 7 | 9 | Dependabot y auditoría de dependencias bloqueante |
| A07 Authentication Failures | 6 | 8 | 8 | — |
| A08 Integrity Failures | 5 | 8 | 8 | — |
| A09 Logging and Monitoring | 5 | 8 | 8 | — |
| A10 SSRF | 10 | 10 | 10 | — |
| **Score** | **56** | **77** | **85** | |

**Dictamen de seguridad: CUMPLE OWASP Top 10.** Los 8 hallazgos de la auditoría OWASP están corregidos, incluido el crítico A02-01. Ninguna categoría queda por debajo de 8.

## 4. Funcionalidad

**Dictamen: se preservó la funcionalidad existente; no se detectaron regresiones en producción.**

| Verificación en producción (12/11/2026) | Resultado |
|---|---|
| Registrar un reclamo desde el portal | Correcto: ticket, código secreto, categoría, anonimización y sello Green AI |
| Consultar el trámite con ticket y código | Correcto |
| Iniciar sesión en el SIGEM y cambiar estados | Correcto, también después de aplicar R7 |
| Auditar un reclamo retenido (HITL) | Correcto: pasa a «En proceso» y baja el contador |
| `GET /api/reclamos` sin sesión | Rechazado: «Debe iniciar sesión como personal municipal» |
| Corrección de redacción con varios problemas en un reclamo | Correcto: el texto se conserva completo |
| Exportar CSV y PDF desde el Dashboard Green AI | Correcto: el CSV abre en columnas en Excel en español |
| Registro de métricas en MLflow (DagsHub) | Correcto con el token nuevo |
| GitHub Actions en `main` | Pruebas, build y auditoría de dependencias en verde |

## 5. Riesgo operativo

**Clasificación: BAJO.** No quedan riesgos críticos ni altos. Los controles nuevos se pueden desactivar con variables de entorno en Render (`AUTH_OBLIGATORIA`, `RATE_LIMIT_POR_MINUTO`, `CORS_ORIGINS`), y R7 tiene su script de reversión en `backend/sql/seguridad_permisos.sql`.

## 6. Riesgos pendientes

| # | Riesgo | Nivel | Acción sugerida |
|---|---|---|---|
| 1 | El plan gratuito de Render apaga el backend sin uso; la primera solicitud tarda hasta un minuto | Bajo | Plan de pago o un servicio que mantenga el backend activo en horario de atención |
| 2 | El despliegue de Render se hace a mano después de cada merge | Bajo | Revisar la conexión de Render con GitHub (Auto-Deploy «On Commit» ya está configurado) |
| 3 | La corrección de redacción y la clasificación dependen de la API de Gemini | Bajo | Ya mitigado: modelo de respaldo, clasificación local y revisión humana (HITL) cuando la confianza es baja |

## 7. Observaciones

1. Los documentos 01 a 07 se conservan sin cambios como registro del proceso: muestran el estado inicial, los planes y el avance de cada fase. Este documento 08 muestra el estado final.
2. La evidencia con capturas del antes y del después está en la guía de la Semana 13 (`Guia_FURPS_OWASP_Green_AI_Municipal.docx`, secciones 1 a 14).
3. Las claves (Supabase, Gemini, DagsHub) viven solo en las variables de entorno de Render y Vercel; el repositorio no contiene ninguna.
4. Dependabot abrirá pull requests de actualización de librerías; deben unirse solo con las verificaciones en verde.

## 8. Recomendación final

### **APTO PARA PRODUCCIÓN**
