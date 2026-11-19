# Casos de uso

> Fase 5 · Prompt 8 – Reconstrucción del Dominio (casos de uso). Fuente: `application/useCases`, `api_router.py`, `frontend/src/services/api.js`, `backend/sql/`.

## Diagrama de casos de uso (UML textual)

```plantuml
@startuml
left to right direction
actor Vecino
actor "Operador municipal" as Op
actor "Gemini API" as IA <<sistema>>
rectangle "Green AI Municipal" {
  usecase "CU-01 Registrar reclamo" as CU1
  usecase "CU-02 Consultar trámite" as CU2
  usecase "CU-03 Iniciar sesión" as CU3
  usecase "CU-04 Listar reclamos" as CU4
  usecase "CU-05 Cambiar estado" as CU5
  usecase "CU-06 Auditar categoría (HITL)" as CU6
  usecase "CU-07 Ver dashboard y exportar" as CU7
}
Vecino --> CU1
Vecino --> CU2
CU1 --> IA
Op --> CU3
Op --> CU4
Op --> CU5
Op --> CU6
Op --> CU7
CU4 ..> CU3 : <<include>>
CU5 ..> CU3 : <<include>>
CU6 ..> CU3 : <<include>>
@enduml
```

## Especificación

| ID | Caso de uso | Actor | Implementación | Precondición | Flujo principal | Resultado |
|---|---|---|---|---|---|---|
| CU-01 | Registrar reclamo | Vecino | `RegistrarReclamoUseCase` vía `POST /api/reclamos` | No superar 20 reclamos/min | Enmascarar datos → medir con CodeCarbon → Gemini (corrige, anonimiza, clasifica) → confianza → generar código → guardar → MLflow | Ticket, código secreto, categoría, confianza |
| CU-02 | Consultar trámite | Vecino | Función SQL `consultar_reclamo` (RPC) | Tener ticket y código | Comparar hash → devolver datos públicos | Estado del reclamo |
| CU-03 | Iniciar sesión | Operador | Supabase Auth (frontend) | Usuario creado en Supabase | Correo + contraseña → JWT | Acceso al SIGEM |
| CU-04 | Listar reclamos | Operador | `GestionarReclamosUseCase.listar/listar_pagina`; el frontend lee primero directo de Supabase | JWT válido | Consulta paginada | Bandeja de reclamos |
| CU-05 | Cambiar estado | Operador | `GestionarReclamosUseCase.cambiar_estado` vía API; el frontend actualiza directo en Supabase | JWT; reclamo no retenido por HITL | Validar estado → actualizar | Nuevo estado |
| CU-06 | Auditar categoría | Operador | `auditarReclamo` en `api.js` (PATCH directo a Supabase) | Reclamo con `requiere_auditoria` | Elegir categoría → `requiere_auditoria = false`, `estado = EN_PROCESO` (solo si seguía retenido) | Reclamo liberado a la gerencia |
| CU-07 | Dashboard y exportación | Operador | `DashboardGreenAI.jsx`, `services/exportar.js` | Sesión | Agregar kWh, gCO₂e y categorías | Gráficos, CSV y PDF |

## Diagrama de secuencia CU-01

```plantuml
@startuml
actor Vecino
participant "Portal (React)" as FE
participant "api_router" as API
participant "RegistrarReclamoUseCase" as UC
participant "GeminiAdapter" as G
participant "evaluacion_confianza" as EC
participant "SupabaseReclamoRepository" as R
participant "MLflow" as M
Vecino -> FE : completa el formulario
FE -> API : POST /api/reclamos
API -> API : límite por IP y validación Pydantic
API -> UC : ejecutar(...)
UC -> UC : enmascarar datos personales
UC -> G : procesar_reclamo_con_ia()
G --> UC : texto, categoría, señales
UC -> EC : evaluar() / requiere_auditoria()
UC -> R : guardar(reclamo, hash del código)
UC -> M : log_param / log_metric
UC --> API : resultado
API --> FE : ticket + código + categoría + confianza
@enduml
```

## Observación

CU-02, CU-03 y CU-06 no tienen caso de uso en la capa de aplicación del backend: se resuelven en el frontend contra Supabase. CU-04 y CU-05 existen en ambos lados (API y acceso directo), lo que duplica la lógica de acceso.
