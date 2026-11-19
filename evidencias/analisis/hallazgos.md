# Matriz de hallazgos

> Fase 6 · Prompt 11 – Hallazgos (rol: Auditor de Software). Consolida auditoría, dependencias, configuración, ejecución e ingeniería inversa.
> Severidad: Crítica · Alta · Media · Baja. Prioridad: P1 (inmediata) · P2 (corto plazo) · P3 (mejora continua).

| ID | Hallazgo | Evidencia | Impacto | Severidad | Recomendación | Prioridad |
|---|---|---|---|---|---|---|
| H-01 | Arranque en frío del backend en Render (~60 s) | Pruebas en producción; plan gratuito | El primer vecino tras un periodo sin uso espera un minuto o abandona el registro | Alta | Instancia siempre activa o ping programado; aviso de espera en el frontend | P1 |
| H-02 | El caso de uso depende directamente de infraestructura (Gemini, MLflow, CodeCarbon) | Importaciones en `registrar_reclamo_use_case.py`; no existe puerto del clasificador | Cambiar de proveedor de IA obliga a modificar la capa de aplicación; pruebas más difíciles | Media | Crear `ClasificadorReclamoPort` y un puerto de telemetría; inyectarlos desde el router | P2 |
| H-03 | Doble ruta de acceso a datos en el SIGEM (API y Supabase directo) | `listarReclamos`, `cambiarEstado`, `auditarReclamo` en `api.js`; rutas equivalentes en `api_router.py` | Reglas y permisos duplicados entre la API y PostgreSQL; riesgo de divergencia | Media | Unificar en una sola vía y documentar la decisión | P2 |
| H-04 | Texto del reclamo en los logs del servidor | `print(f"Texto Anonimizado: …[:60]")` en el caso de uso | Exposición innecesaria de contenido ciudadano (aunque anonimizado) en Render | Media | Registrar solo métricas e ID del ticket | P1 |
| H-05 | Mensajes con `print` en lugar de `logging` | 4 puntos en `gemini_adapter.py` y el caso de uso | Sin niveles ni hora; `LOG_LEVEL` no los controla | Baja | Usar `logging.getLogger(__name__)` | P2 |
| H-06 | Limitador de solicitudes en memoria | `infrastructure/security/limitador.py` | Con varias instancias, cada una tiene su propio contador; se reinicia con cada despliegue | Media | Almacén compartido o límite en el proxy | P3 |
| H-07 | Restos de un backend Node sin uso | `backend/package.json` y lock con 121 paquetes (express, pg…), sin archivos `.js` | Confusión al instalar; alertas de Dependabot sin valor | Baja | Eliminar ambos archivos | P2 |
| H-08 | Dependencias declaradas sin uso | `axios` (frontend), `requests` (backend) | Superficie de ataque y mantenimiento innecesarios | Baja | Quitarlas | P2 |
| H-09 | Recursos gráficos sin referencia | `hero.png`, `react.svg`, `vite.svg`, `icons.svg`, `favicon.svg` | Peso y ruido en el repositorio | Baja | Eliminarlos | P3 |
| H-10 | Regla de categoría poco intuitiva | `categoria if (categoria and categoria != "Vías Públicas") else categoria_ia` | Un cliente externo puede imponer cualquier categoría (excepto Vías Públicas) y la IA se ignora | Media | Validar contra las 4 categorías y documentar cuándo prevalece la del cliente, o ignorarla | P2 |
| H-11 | No hay script de creación de la tabla `reclamos` | `backend/sql/` solo contiene `ALTER`/`GRANT` | El entorno no se puede reconstruir solo desde el repositorio | Media | Añadir `00_esquema.sql` con `CREATE TABLE` | P2 |
| H-12 | Configuración no documentada por completo | `.env.example` sin `AUTH_OBLIGATORIA`, `RATE_LIMIT_*`, `CORS_ORIGINS`; sin `frontend/.env.example` | Errores de despliegue; riesgo de dejar `AUTH_OBLIGATORIA=false` | Baja | Completar los ejemplos | P2 |
| H-13 | Pruebas de API omitidas si falta `fastapi` | `SKIPPED … could not import 'fastapi'` | Falsa sensación de cobertura en local | Baja | Instalar `requirements-dev.txt`; en el CI no ocurre | P3 |
| H-14 | Acciones de GitHub con Node.js 20 deprecado | Avisos en Actions; PR de Dependabot a `@v7` | El CI puede fallar cuando GitHub retire Node 20 | Baja | Aceptar los PR de Dependabot | P2 |
| H-15 | Sin pruebas del frontend ni de la lógica SQL | No hay pruebas para `consultar_reclamo`, el trigger ni componentes React | Regresiones no detectadas en reglas críticas (HITL, consulta) | Media | Pruebas SQL (pgTAP o scripts) y pruebas de componentes | P3 |
| H-16 | Despliegue manual de Render | Sin despliegue automático tras el merge | Producción puede quedar desactualizada respecto a `main` | Baja | Activar el auto-deploy o un *deploy hook* desde Actions | P3 |
| H-17 | Sin contenedores ni infraestructura como código | No hay `Dockerfile` ni `render.yaml` | Reproducción del entorno manual y propensa a errores | Baja | `Dockerfile` del backend y `render.yaml` | P3 |

## Fortalezas verificadas

| ID | Fortaleza | Evidencia |
|---|---|---|
| F-01 | Rutas internas protegidas con JWT | 401 en producción; `test_api_seguridad.py` |
| F-02 | Datos personales enmascarados antes de llegar a la IA y no almacenados | `_enmascarar`; columnas de `reclamos` |
| F-03 | Código de consulta guardado solo como hash y consulta mediante función `SECURITY DEFINER` | `codigo_consulta.py`, `modulo_c_consulta.sql` |
| F-04 | Regla HITL reforzada en la base con trigger | `hitl_auditoria.sql` |
| F-05 | CI bloqueante con pruebas, build y auditoría de dependencias; Dependabot; rama `main` protegida | `.github/` |
| F-06 | Tolerancia a fallas de Gemini y MLflow | Respaldo local; `test_si_mlflow_falla_el_reclamo_se_guarda_igual` |

## Resumen

| Severidad | Cantidad |
|---|---|
| Crítica | 0 |
| Alta | 1 |
| Media | 7 |
| Baja | 9 |
