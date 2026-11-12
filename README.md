# Green AI Municipal — Clasificación ecoeficiente de reclamos vecinales

Sistema web de la Municipalidad Provincial de Huancayo que recibe reclamos vecinales, protege los datos personales (Ley N.° 29733), los clasifica con IA (Google Gemini Flash-Lite), retiene para revisión humana los casos dudosos (HITL) y mide la energía y las emisiones de cada inferencia (CodeCarbon + MLflow).

| Componente | Tecnología | Despliegue |
|---|---|---|
| Frontend | React + Vite | Vercel |
| Backend | FastAPI (Python) | Render |
| Base de datos y autenticación | Supabase (PostgreSQL + Auth) | Nube |
| IA | `gemini-flash-lite-latest`, con `gemini-flash-latest` de respaldo | API de Google |
| Telemetría | CodeCarbon y MLflow en DagsHub | Nube |

## 🏗️ Arquitectura del sistema (puertos y adaptadores — hexagonal)

```text
backend/
├── src/
│   ├── application/useCases/
│   │   ├── gestionar_reclamos_use_case.py   # Listado y cambio de estado (SIGEM)
│   │   └── registrar_reclamo_use_case.py    # Anonimización + clasificación Green AI
│   ├── domain/
│   │   ├── entities/reclamo.py              # Entidad Reclamo
│   │   ├── ports/input/                     # Puertos de entrada
│   │   ├── ports/output/                    # Puerto de salida (persistencia)
│   │   ├── services/evaluacion_confianza.py # Confianza de la IA y regla HITL (70 %)
│   │   └── valueObjects/                    # Estado del reclamo y código secreto de consulta
│   └── infrastructure/adapters/
│       ├── input/api_router.py              # Endpoints FastAPI
│       ├── input/dtos.py                    # Validación de entradas (Pydantic)
│       ├── output/gemini_adapter.py         # Inferencia con Gemini Flash-Lite
│       └── output/supabase_reclamo_repository.py
├── sql/                                     # Funciones y triggers de Supabase
├── tests/                                   # Pruebas automatizadas (pytest)
├── main.py                                  # Punto de entrada FastAPI
├── requirements.txt                         # Dependencias de producción
├── requirements-dev.txt                     # Dependencias de desarrollo y pruebas
└── .env.example                             # Plantilla de variables de entorno
```

## ▶️ Cómo ejecutar el backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate          # Windows  (en Linux/Mac: source .venv/bin/activate)
pip install -r requirements-dev.txt
copy .env.example .env          # en Linux/Mac: cp .env.example .env  — luego complete los valores
uvicorn main:app --reload
```

La API queda en `http://127.0.0.1:8000` y su documentación en `http://127.0.0.1:8000/docs`.

## ▶️ Cómo ejecutar el frontend

```bash
cd frontend
npm install
npm run dev
```

Variables del frontend (archivo `frontend/.env.local`): `VITE_API_URL`, `VITE_SUPABASE_URL`, `VITE_SUPABASE_PUBLISHABLE_KEY`.

## ✅ Pruebas automatizadas

```bash
cd backend
pytest
```

Las pruebas no necesitan internet ni credenciales: Gemini, Supabase, CodeCarbon y MLflow se reemplazan por dobles de prueba. Cubren la anonimización, la regla HITL, el código secreto de consulta, la clasificación local de respaldo, el registro de reclamos, el cambio de estado y la validación de entradas.

## 🔐 Variables de entorno del backend

Ver `backend/.env.example`. Las claves **nunca** se escriben en el código: se configuran en el archivo `.env` local (ignorado por Git) y en *Environment* de Render.

| Variable | Obligatoria | Uso |
|---|---|---|
| `SUPABASE_URL`, `SUPABASE_KEY` | Sí | Conexión a la base de datos |
| `GEMINI_API_KEY` | Sí | Clasificación con IA |
| `GEMINI_MODEL`, `GEMINI_MODEL_RESPALDO` | No | Modelos de Gemini |
| `MLFLOW_TRACKING_PASSWORD` | No | Token de DagsHub; sin él la API funciona pero no registra en MLflow |
| `LOG_LEVEL` | No | Nivel de registro (por defecto `INFO`) |

## 📄 Documentación de calidad y seguridad

La carpeta `docs/` contiene la auditoría FURPS+, la auditoría OWASP Top 10, sus planes de mejora y las verificaciones de implementación.
