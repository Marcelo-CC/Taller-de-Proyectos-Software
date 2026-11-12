# 01 · Auditoría FURPS+ — Green AI Municipal

| Dato | Valor |
|---|---|
| Proyecto | Sistema Ecoeficiente de Clasificación Automática de Reclamos Vecinales (Green AI Municipal) |
| Repositorio | `Marcelo-CC/Taller-de-Proyectos-Software`, rama `main`, commit `c04b1a8` |
| Despliegue observado | Backend FastAPI en Render · Frontend React/Vite en Vercel · Base de datos Supabase |
| Fecha de la auditoría | 12/11/2026 |
| Rol | Agente 1 — Auditor FURPS+ (solo lectura: no se modificó ningún archivo) |

## 1. Resumen ejecutivo

El sistema cumple sus procesos de negocio principales: registro de reclamos con anonimización, clasificación con IA, código secreto de consulta, consola SIGEM con auditoría humana (HITL) y dashboard Green AI. La arquitectura hexagonal está bien aplicada y el dominio es legible.

Las brechas más importantes están en **Supportability** (no existe ninguna prueba automatizada, la documentación está desactualizada y hay archivos de trabajo versionados) y en **Reliability/Performance**: el arranque depende de un servicio externo (DagsHub), los errores internos se devuelven al cliente, el listado devuelve todos los reclamos en una sola respuesta (703 KB) y el servidor gratuito tarda más de un minuto en despertar.

**Puntaje global: 69/100 (nivel aceptable con brechas).**

## 2. Puntaje por categoría

| Factor | Puntaje | Nivel |
|---|---|---|
| Functionality (F) | 85 / 100 | Bueno |
| Usability (U) | 80 / 100 | Bueno |
| Reliability (R) | 62 / 100 | Regular |
| Performance (P) | 65 / 100 | Regular |
| Supportability (S) | 45 / 100 | Deficiente |
| **Global (promedio)** | **69 / 100** | **Aceptable con brechas** |

Escala: 90–100 excelente · 75–89 bueno · 60–74 regular · menos de 60 deficiente. El factor "+" (seguridad) se evalúa por separado con OWASP Top 10 (documento 04).

## 3. Hallazgos y evidencias

### Functionality (F)

| ID | Hallazgo | Estado | Evidencia |
|---|---|---|---|
| F-01 | Registro de reclamos con anonimización de DNI, nombre, domicilio y contacto antes de llamar a la IA | Implementado | `backend/src/application/useCases/registrar_reclamo_use_case.py` (pasos 1 a 8) |
| F-02 | Clasificación en 4 categorías con Gemini y respaldo local por palabras clave si la IA no responde | Implementado | `backend/src/infrastructure/adapters/output/gemini_adapter.py` (`procesar_reclamo_con_ia`, `_clasificar_local`) |
| F-03 | Confianza de la IA y retención HITL por debajo del 70 % | Implementado | `backend/src/domain/services/evaluacion_confianza.py`; trigger `backend/sql/hitl_auditoria.sql` |
| F-04 | Consulta de trámite con ticket y código secreto (hash SHA-256) | Implementado | `backend/src/domain/valueObjects/codigo_consulta.py`; `backend/sql/modulo_c_consulta.sql`; `frontend/src/pages/ConsultaTramite.jsx` |
| F-05 | SIGEM: listado, búsqueda, cambio de estado, auditoría HITL y dashboard Green AI | Implementado | `frontend/src/pages/Sigem.jsx` y `frontend/src/pages/sigem/*` |
| F-06 | Exportación de reportes de sostenibilidad en PDF/CSV (recomendada por la experta) | Ausente | No existe código de exportación en `frontend/src` ni en el backend |
| F-07 | El endpoint `PATCH /api/reclamos/{id}/estado` del backend duplica la ruta que usa el frontend (que actualiza directo en Supabase) | Parcial | `api_router.py` líneas 86-99 frente a `frontend/src/services/api.js` (`actualizarReclamo`) |

**Cobertura de procesos de negocio:** los tres módulos (A Portal Ciudadano, B SIGEM, C Consulta) están operativos en producción. Falta solo la exportación de reportes (F-06).

### Usability (U)

| ID | Hallazgo | Estado | Evidencia |
|---|---|---|---|
| U-01 | Validaciones de formulario completas en el cliente (DNI de 8 dígitos, celular o correo, longitudes mínimas y máximas) | Cumple | `PortalCiudadano.jsx`, función `validar` |
| U-02 | Retroalimentación al usuario: mensajes de error por campo, aviso de espera, ticket y código copiable | Cumple | `PortalCiudadano.jsx`; `Sigem.jsx` (avisos tras actualizar) |
| U-03 | Accesibilidad: 40 atributos `aria-*`/`role` en las vistas; estados con ícono y texto, no solo color | Cumple | `grep aria-/role` en `frontend/src` (40 coincidencias); `constantes.js` (`ESTADOS`) |
| U-04 | Navegación por URL (`#/ciudadano`, `#/sigem`) compatible con el botón Atrás | Cumple | `App.jsx` |
| U-05 | Los errores del servidor muestran al usuario detalles técnicos internos (`Error en el servidor: <excepción>`) | No cumple | `api_router.py` líneas 74, 83 y 99 |
| U-06 | La primera solicitud tras inactividad puede tardar más de un minuto (arranque en frío de Render); el formulario lo advierte, pero el SIGEM no | Parcial | Captura A05; `PortalCiudadano.jsx` (`nota-centrada`) |

### Reliability (R)

| ID | Hallazgo | Estado | Evidencia |
|---|---|---|---|
| R-01 | Respaldo ante caída de Gemini: 2 modelos con 20 s de timeout y clasificación local | Cumple | `gemini_adapter.py` (`self.modelos`, bucle `for modelo`) |
| R-02 | Si MLflow/DagsHub falla al registrar, el reclamo se guarda igual | Cumple | `registrar_reclamo_use_case.py`, paso 6 (`try/except`) |
| R-03 | El arranque del servidor llama a `dagshub.init()` sin protección: si DagsHub no responde, la API completa no inicia | No cumple | `backend/main.py` líneas 16-24 |
| R-04 | Los errores se devuelven con `str(e)`, sin registro estructurado ni identificador de incidente para rastrearlos | No cumple | `api_router.py` líneas 74, 83, 99; solo `print` en todo el backend |
| R-05 | El backend no valida longitudes en el servidor: un cliente que no use el formulario puede enviar textos de cualquier tamaño | No cumple | `api_router.py`, `ReclamoDTO` (líneas 23-32), captura A02 |
| R-06 | Disponibilidad: el plan gratuito de Render apaga el servicio; el despertar observado tomó unos 90 s | Riesgo | Captura A05 (20:03:24 → 20:04:35 y reintento) |

### Performance (P)

| ID | Hallazgo | Estado | Evidencia |
|---|---|---|---|
| P-01 | Latencia de clasificación de 1,8 a 2,1 s y energía de 0,0000721 kWh por inferencia, dentro de las metas | Cumple | Informe final, sección 8.2.4; tabla `reclamos` de Supabase |
| P-02 | `GET /api/reclamos` devuelve **todos** los reclamos en una sola respuesta (703 039 caracteres con 1252 registros), sin paginación | No cumple | `supabase_reclamo_repository.py`, `listar()`; captura A06 |
| P-03 | Se crea un `EmissionsTracker` nuevo en cada solicitud (sobrecarga de inicialización de CodeCarbon) | Riesgo | `registrar_reclamo_use_case.py` línea 41 |
| P-04 | El frontend divide el SIGEM en un paquete aparte (`lazy`) para no cargar los gráficos al vecino | Cumple | `App.jsx` (`lazy(() => import('./pages/Sigem'))`) |

### Supportability (S)

| ID | Hallazgo | Estado | Evidencia |
|---|---|---|---|
| S-01 | Arquitectura hexagonal con dominio, puertos y adaptadores separados | Cumple | Árbol `backend/src/` |
| S-02 | **No existe ninguna prueba automatizada** (0 archivos de prueba, sin `pytest` ni scripts de test) | No cumple | Búsqueda de `*test*` sin resultados; `backend/package.json`: `"test": "echo \"Error: no test specified\""` |
| S-03 | README desactualizado: dice "Gemini 2.5 Flash" (el código usa `gemini-flash-lite-latest`), lista un `.env` que no está en el repositorio y no explica cómo ejecutar el proyecto | No cumple | `README.md` líneas 28 y 30 |
| S-04 | No hay plantilla `.env.example` con las variables que necesita el backend | No cumple | Variables leídas en `main.py` y `gemini_adapter.py` sin documentar |
| S-05 | Archivos de trabajo versionados: `mlflow.db` (954 KB) y dos `emissions.csv` | No cumple | Raíz del repositorio; `.gitignore` no los excluye |
| S-06 | Dependencias que no se usan: `axios` en el frontend y un `backend/package.json` de Node (express, pg) en un backend Python | No cumple | `frontend/package.json` línea 13 (ningún `import axios`); `backend/package.json` |
| S-07 | Los DTO están definidos dentro del adaptador FastAPI, lo que impide probarlos sin levantar el servidor | Riesgo | `api_router.py` líneas 23-35 |

## 4. Brechas identificadas

1. Ausencia total de pruebas automatizadas (S-02).
2. Robustez del arranque y del manejo de errores (R-03, R-04, U-05).
3. Falta de validación de entradas en el servidor (R-05).
4. Documentación de instalación y configuración (S-03, S-04).
5. Higiene del repositorio y dependencias sin uso (S-05, S-06).
6. Listado sin paginación (P-02) y exportación de reportes ausente (F-06).

## 5. Riesgos detectados

| Riesgo | Probabilidad | Impacto |
|---|---|---|
| Un cambio futuro rompe la anonimización o la regla HITL sin que nadie lo note, por falta de pruebas | Alta | Alto |
| La API no inicia si DagsHub está caído | Media | Alto |
| Mensajes técnicos internos visibles para el vecino | Alta | Medio |
| Solicitudes con textos enormes elevan el costo y la latencia de Gemini | Media | Medio |
| El listado crece sin límite y vuelve lento el SIGEM | Media | Medio |
| Un nuevo integrante no puede ejecutar el proyecto por falta de documentación | Alta | Medio |

## 6. Recomendaciones de alto nivel

- Incorporar pruebas automatizadas del dominio y de los casos de uso.
- Hacer tolerante a fallos el arranque y estandarizar el manejo de errores con registro (logging).
- Validar longitudes y campos obligatorios también en el servidor.
- Actualizar la documentación y agregar `.env.example`.
- Excluir de Git los archivos generados y retirar dependencias sin uso.
- Planificar paginación del listado y la exportación de reportes como mejoras futuras.

## 7. Evidencias (capturas)

| Captura | Muestra |
|---|---|
| A01 | `backend/main.py` en GitHub: arranque con `dagshub.init()` sin protección y configuración de CORS |
| A02 | `ReclamoDTO` sin límites de longitud |
| A03 | Endpoints que devuelven `str(e)` al cliente |
| A05 | Arranque en frío de Render |
| A06 | `GET /api/reclamos` devuelve todos los registros en una respuesta |
| A07 | Repositorio sin carpeta ni archivos de pruebas, con `mlflow.db` y `emissions.csv` versionados |
| A08 | README desactualizado |
