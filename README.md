## 🏗️ Arquitectura del Sistema (Puertos y Adaptadores - Hexagonal)

El sistema backend se encuentra desacoplado en tres capas principales dentro de `backend/src/` para garantizar la separación de responsabilidades, mantenibilidad y escalabilidad del código:

```text
backend/
├── src/
│   ├── application/
│   │   └── useCases/
│   │       ├── gestionar_reclamos_use_case.py   # Caso de Uso (Consulta y Gestión de Estado)
│   │       └── registrar_reclamo_use_case.py   # Caso de Uso (Anonimización PII + Categorización Green AI)
│   ├── domain/
│   │   ├── entities/
│   │   │   └── reclamo.py                       # Entidad Reclamo (Reglas de Negocio Core)
│   │   ├── ports/
│   │   │   ├── input/
│   │   │   │   ├── gestionar_reclamos_port.py   # Puerto de Entrada (Gestión/Consulta)
│   │   │   │   └── registrar_reclamo_port.py   # Puerto de Entrada (Registro)
│   │   │   └── output/
│   │   │       └── reclamo_repository_port.py  # Puerto de Salida (Persistencia de Datos)
│   │   └── valueObjects/
│   │       └── estado_reclamo.py               # Objeto de Valor (Enum: PENDIENTE, EN_PROCESO, RESUELTO)
│   └── infrastructure/
│       └── adapters/
│           ├── input/
│           │   └── api_router.py                # Adaptador de Entrada (Endpoints FastAPI)
│           └── output/
│               ├── gemini_adapter.py            # Adaptador de Salida (Inferencia SLM Gemini 2.5 Flash)
│               └── supabase_reclamo_repository.py # Adaptador de Salida (Persistencia Supabase PostgreSQL)
├── .env                                         # Variables de Entorno (API Keys)
├── emissions.csv                                # Registro de Huella de Carbono (CodeCarbon)
├── main.py                                      # Punto de Entrada FastAPI + DagsHub MLflow
├── package-lock.json
├── package.json
└── requirements.txt                             # Dependencias de Python