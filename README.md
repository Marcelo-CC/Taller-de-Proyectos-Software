# Sistema de Gestión de Reclamos - Municipalidad Provincial de Huancayo

Proyecto correspondiente a la **Unidad II (S6)** para la Municipalidad Provincial de Huancayo. La solución implementa un prototipo funcional (PMV) con **Arquitectura Hexagonal (Puertos y Adaptadores)**, persistencia en la nube mediante Supabase e integración con Inteligencia Artificial para el procesamiento de reclamos y telemetría de consumo energético (Green AI).

---

## 🏗️ Arquitectura del Sistema (Puertos y Adaptadores)

El sistema backend se encuentra desacoplado en tres capas principales dentro de `backend/src/` para garantizar la separación de responsabilidades, mantenibilidad y escalabilidad del código:

```text
backend/
└── src/
    ├── domain/                             # Capa de Dominio (Reglas de negocio puras)
    │   ├── entities/                       # Entidades (Reclamo.js)
    │   ├── valueObjects/                   # Objetos de Valor (EstadoReclamo.js)
    │   └── ports/                          # Puertos / Interfaces de Dominio
    │       ├── input/                      # Puerto de Entrada (RegistrarReclamoPort.js)
    │       └── output/                     # Puerto de Salida (ReclamoRepositoryPort.js)
    │
    ├── application/                        # Capa de Aplicación (Casos de Uso)
    │   ├── useCases/                       # Lógica de Negocio (RegistrarReclamoUseCase.js)
    │   └── services/                       # Servicios (ReclamoApplicationService.js)
    │
    └── infrastructure/                     # Capa de Infraestructura (Adaptadores)
        └── adapters/
            ├── input/                      # Adaptadores de Entrada (server.js)
            └── output/                     # Adaptadores de Salida (SupabaseReclamoRepository.js)

frontend/                                   # Interfaz de usuario construida en React + Vite
main.py                                     # Módulo de Green AI (Ollama + Telemetría CodeCarbon)
emissions.csv                               # Registro de impacto ambiental y huella de carbono
