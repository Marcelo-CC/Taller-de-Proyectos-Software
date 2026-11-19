# Arquitectura detectada

> Fase 1 · Prompt 2 – Detección Arquitectónica. Fuente: estructura de carpetas, módulos e importaciones del repositorio (rama `main`, commit `73a6f5e`).

## Evaluación por estilo arquitectónico

### 1. Arquitectura Hexagonal (puertos y adaptadores) — **presente**

- **Evidencias:**
  - Puertos de entrada abstractos (`ABC`): `RegistrarReclamoPort`, `GestionarReclamosPort`.
  - Puerto de salida abstracto: `ReclamoRepositoryPort` (`guardar`, `listar`, `listar_pagina`, `actualizar_estado`).
  - Adaptador de entrada: `api_router.py` (FastAPI) traduce HTTP a casos de uso.
  - Adaptadores de salida: `SupabaseReclamoRepository` implementa el puerto; `GeminiAdapter` encapsula la IA.
  - Las pruebas reemplazan el repositorio por un doble (`tests/dobles.py: RepositorioFalso`), lo que demuestra que el núcleo no depende de Supabase.
- **Carpetas involucradas:** `backend/src/domain/ports/{input,output}`, `backend/src/application/useCases`, `backend/src/infrastructure/adapters/{input,output}`.
- **Nivel de confianza:** Alto.
- **Justificación técnica:** la separación por puertos está declarada en código (clases abstractas) y respetada para la persistencia. Hay una desviación: `RegistrarReclamoUseCase` importa directamente `GeminiAdapter`, `mlflow` y `codecarbon`, por lo que el servicio de IA y la telemetría no están detrás de un puerto.

### 2. Clean Architecture — **parcial**

- **Evidencias:** capas `domain` → `application` → `infrastructure` con dependencias hacia el centro para la persistencia; entidad `Reclamo`, objetos de valor y servicio de dominio sin dependencias externas.
- **Carpetas:** `backend/src/domain`, `backend/src/application`, `backend/src/infrastructure`.
- **Nivel de confianza:** Medio.
- **Justificación técnica:** cumple la regla de dependencia en el dominio, pero la capa de aplicación conoce detalles de infraestructura (Gemini, MLflow, CodeCarbon), y la inyección de dependencias se arma en el router (`get_repository` importa `supabase` desde `main`).

### 3. Arquitectura por capas — **presente**

- **Evidencias:** cuatro capas identificables: presentación (`frontend/`), aplicación (`application/useCases`), dominio (`domain/`) e infraestructura (`infrastructure/`, `backend/sql`).
- **Nivel de confianza:** Alto.
- **Justificación técnica:** cada carpeta corresponde a una responsabilidad; es la vista en capas de la arquitectura hexagonal.

### 4. MVC — **no aplica**

- **Evidencias:** no hay controladores ni vistas en el backend (es una API JSON). En el frontend, React organiza la interfaz por componentes y páginas (`pages/`, `components/`) con una capa de servicios (`services/api.js`), no por modelo-vista-controlador.
- **Nivel de confianza:** Alto (de que no se usa).

### 5. Microservicios — **no**

- **Evidencias:** un solo servicio backend (`main.py`) con un único despliegue en Render; no hay comunicación entre servicios, colas ni API gateway.
- **Nivel de confianza:** Alto (de que no se usa).
- **Justificación técnica:** el sistema se reparte entre servicios gestionados (Supabase, Gemini, DagsHub), pero eso es integración con terceros, no una arquitectura de microservicios propia.

### 6. Monolito modular — **presente (backend)**

- **Evidencias:** el backend es un único proceso desplegable organizado en módulos internos con límites claros (dominio, casos de uso, adaptadores, seguridad).
- **Carpetas:** `backend/src/**`.
- **Nivel de confianza:** Medio-alto.

### 7. Arquitectura orientada a eventos — **no**

- **Evidencias:** no hay broker de mensajes ni publicación de eventos. El único comportamiento reactivo es el trigger `trg_proteger_auditoria_hitl` en PostgreSQL, que es una regla de integridad, no un bus de eventos.
- **Nivel de confianza:** Alto (de que no se usa).

## Patrones complementarios detectados

| Patrón | Dónde | Evidencia |
|---|---|---|
| Repositorio | `supabase_reclamo_repository.py` | Encapsula `insert`, `select`, `update` de la tabla `reclamos` |
| Estrategia / cadena de respaldo | `gemini_adapter.py` | Lista `self.modelos` (Flash-Lite → Flash) y clasificación local si ambos fallan |
| Inyección de dependencias | `api_router.py` | `Depends(get_repository)`, `Depends(usuario_autenticado)` |
| Objeto de valor | `domain/valueObjects/` | `EstadoReclamo` (enum), `codigo_consulta` (generación y hash) |
| Servicio de dominio | `domain/services/evaluacion_confianza.py` | Regla HITL (umbral 0,70) |
| BFF parcial / acceso directo a BaaS | `frontend/src/services/api.js` | El frontend lee y actualiza `reclamos` directamente en Supabase con el token del operador |

## Conclusión

La arquitectura predominante del backend es **hexagonal (puertos y adaptadores)**, implementada como un **monolito modular** y vista en **cuatro capas** (presentación, aplicación, dominio e infraestructura). El sistema completo es una **arquitectura cliente-servidor sobre servicios gestionados** (Backend as a Service con Supabase y IA como servicio con Gemini). La adherencia al estilo hexagonal es alta en persistencia y parcial en la integración con la IA y la telemetría, que no están detrás de un puerto.
