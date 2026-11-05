# Sistema de Gestión de Reclamos - Municipalidad Provincial de Huancayo

Proyecto correspondiente a la **Unidad II (S6)** para la Municipalidad Provincial de Huancayo. La solución implementa un prototipo funcional (PMV) con **Arquitectura Hexagonal (Puertos y Adaptadores)**, persistencia en la nube mediante Supabase e integración con Inteligencia Artificial para el procesamiento de reclamos y telemetría de consumo energético (Green AI).

---

## 🏗️ Arquitectura del Sistema (Puertos y Adaptadores)

El sistema backend se encuentra desacoplado en tres capas principales dentro de `backend/src/` para garantizar la separación de responsabilidades, mantenibilidad y escalabilidad del código:

```text
backend/
├── src/
│   ├── application/
│   │   └── useCases/
│   │       └── registrar_reclamo_use_case.py       # Casos de Uso (Anonimización PII + Green AI)
│   ├── domain/
│   │   ├── entities/
│   │   │   └── reclamo.py                          # Entidad Reclamo
│   │   ├── ports/
│   │   │   ├── input/
│   │   │   │   └── registrar_reclamo_port.py       # Puerto de Entrada
│   │   │   └── output/
│   │   │       └── reclamo_repository_port.py     # Puerto de Salida
│   │   └── valueObjects/
│   │       └── estado_reclamo.py                   # Objetos de Valor
│   └── infrastructure/
│       └── adapters/
│           ├── input/
│           │   └── api_router.py                   # Adaptador Entrada (Endpoints FastAPI)
│           └── output/
│               └── supabase_reclamo_repository.py  # Adaptador Salida (Persistencia Supabase)
├── .env                                            # Variables de Entorno (API Keys)
├── emissions.csv                                   # Registro de Huella de Carbono
├── main.py                                         # Punto de Entrada FastAPI + DagsHub MLflow
├── package-lock.json
├── package.json
└── requirements.txt                                # Dependencias de Python
