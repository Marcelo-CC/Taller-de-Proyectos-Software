# Evaluación de la calidad arquitectónica

> Fase 6 · Prompt 10 – Evaluación Arquitectónica. Escala: 1 (muy deficiente) a 5 (excelente).

## Calificaciones

| Atributo | Nota | Justificación técnica |
|---|---|---|
| **Cohesión** | **4** | Cada módulo tiene una responsabilidad clara: el servicio de confianza solo calcula la confianza, el repositorio solo persiste, los controles de seguridad están en `infrastructure/security/`. Resta un punto `GeminiAdapter` (267 líneas), que mezcla llamada al modelo, revisión de la corrección, restauración de texto, anonimización local y clasificación local. |
| **Acoplamiento** | **3** | La persistencia está desacoplada por un puerto (se prueba con un repositorio falso). Pero `RegistrarReclamoUseCase` importa `GeminiAdapter`, `mlflow` y `codecarbon`; `api_router` importa `supabase` desde `main`; y el frontend conoce el esquema de la tabla `reclamos` porque la consulta directamente. |
| **Escalabilidad** | **2** | Render gratuito (0,1 vCPU, 512 MB, arranque en frío ~60 s); el limitador de solicitudes está en memoria del proceso y no se comparte entre instancias; cada registro hace una llamada síncrona a Gemini de hasta 20 s por modelo. La base (Supabase) y el frontend (CDN de Vercel) sí escalan. |
| **Mantenibilidad** | **3** | Estructura por capas clara, nombres en español coherentes, pruebas y CI. En contra: restos sin uso (`backend/package.json` de Node, `axios`, `requests`, recursos gráficos), mensajes con `print`, reglas de negocio repartidas entre Python, JavaScript y SQL, y sin script de creación de la tabla. |
| **Testabilidad** | **4** | 74 pruebas en 16 archivos: dominio, casos de uso con dobles, adaptador de Gemini, DTO, seguridad y API; se ejecutan en el CI y bloquean el merge. No hay pruebas del frontend ni de los scripts SQL (función `consultar_reclamo` y trigger), y el caso de uso es difícil de probar sin parchear `GeminiAdapter`/`mlflow`. |
| **Seguridad** | **4** | Autenticación JWT en rutas internas, límite de solicitudes, validación de entradas, CORS restringido, cabeceras, errores genéricos, permisos por columna, hash del código, anonimización antes de la IA y auditoría de dependencias bloqueante. Resta un punto: el texto anonimizado se imprime en los logs, el limitador no es distribuido y `AUTH_OBLIGATORIA=false` desactiva toda la protección del SIGEM. |

**Promedio:** 3,3 / 5.

## Recomendaciones de mejora

| # | Recomendación | Atributos que mejora |
|---|---|---|
| 1 | Crear un puerto `ClasificadorReclamoPort` (y otro de telemetría) e inyectar `GeminiAdapter`, CodeCarbon y MLflow desde el router | Acoplamiento, testabilidad |
| 2 | Unificar el acceso del SIGEM en la API (o, al revés, documentar formalmente que Supabase es la capa de datos del SIGEM y retirar las rutas duplicadas) | Acoplamiento, mantenibilidad, seguridad |
| 3 | Dividir `GeminiAdapter` en cliente del modelo, revisor de corrección y clasificador local | Cohesión |
| 4 | Plan con instancia siempre activa o ping programado; procesar la llamada a Gemini en segundo plano si el volumen crece | Escalabilidad |
| 5 | Llevar el límite de solicitudes a un almacén compartido (Redis) o al proxy | Escalabilidad, seguridad |
| 6 | Eliminar `backend/package.json`, `axios`, `requests` y recursos sin uso | Mantenibilidad, seguridad |
| 7 | Sustituir `print` por `logging` y dejar de registrar texto del reclamo | Mantenibilidad, seguridad |
| 8 | Agregar `CREATE TABLE reclamos` y pruebas de los scripts SQL; pruebas de componentes React | Mantenibilidad, testabilidad |
| 9 | Modelar `Categoria` como objeto de valor del dominio | Cohesión |
