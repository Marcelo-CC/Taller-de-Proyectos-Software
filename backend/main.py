import logging
import os
import dagshub
import mlflow
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client

from src.infrastructure.adapters.input.api_router import router
from src.infrastructure.security import cabeceras

load_dotenv()

# Registro (logging) estándar: los mensajes quedan en los logs de Render con fecha y nivel
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"),
                    format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("main")

# MLflow en DagsHub es opcional para que la API funcione: si no hay token o DagsHub no responde,
# la API arranca igual y solo se deja de registrar la telemetría en MLflow.
DAGSHUB_TOKEN = os.getenv("MLFLOW_TRACKING_PASSWORD")
if DAGSHUB_TOKEN:
    try:
        dagshub.auth.add_app_token(DAGSHUB_TOKEN)
        dagshub.init(
            repo_owner=os.getenv("DAGSHUB_REPO_OWNER", "Marcelo-CC"),
            repo_name=os.getenv("DAGSHUB_REPO_NAME", "Taller-de-Proyectos-Software"),
            mlflow=True
        )
    except Exception as e:
        logger.warning("No se pudo conectar con DagsHub/MLflow; la API sigue sin registrar en MLflow: %s", e)
else:
    logger.warning("MLFLOW_TRACKING_PASSWORD no está configurada: no se registrará en MLflow/DagsHub.")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Faltan las credenciales SUPABASE_URL o SUPABASE_KEY en el archivo .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI(
    title="API Reclamos Municipalidad Provincial de Huancayo",
    description="Backend para gestión de reclamos vecinales con telemetría Green AI",
    version="1.0.0"
)

# CORS (OWASP A05): solo el frontend del proyecto. Se ajusta sin redesplegar con CORS_ORIGINS en Render.
origenes = cabeceras.origenes_permitidos()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origenes,
    allow_origin_regex=None if "*" in origenes else cabeceras.REGEX_VISTAS_PREVIAS,
    allow_credentials=False,  # el frontend no usa cookies: la sesión viaja en la cabecera Authorization
    allow_methods=["GET", "POST", "PATCH", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


# Cabeceras de seguridad en todas las respuestas (OWASP A05)
@app.middleware("http")
async def agregar_cabeceras_de_seguridad(request, call_next):
    respuesta = await call_next(request)
    for nombre, valor in cabeceras.cabeceras_para(request.url.path).items():
        respuesta.headers.setdefault(nombre, valor)
    return respuesta

app.include_router(router)

@app.get("/")
def home():
    return {"message": "API de Reclamos Vecinales activa y lista para recibir solicitudes."}