import os
import dagshub
import mlflow
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from supabase import create_client, Client

from src.infrastructure.adapters.input.api_router import router

load_dotenv()

# Obtener token e inyectarlo en la configuración global de DagsHub
DAGSHUB_TOKEN = os.getenv("MLFLOW_TRACKING_PASSWORD", "08a361eb762d8562daa67d9089d622d1e31bbc7a")

if DAGSHUB_TOKEN:
    dagshub.auth.add_app_token(DAGSHUB_TOKEN)

# Inicializar DagsHub MLflow sin parámetros no soportados
dagshub.init(
    repo_owner='Marcelo-CC',
    repo_name='Taller-de-Proyectos-Software',
    mlflow=True
)

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def home():
    return {"message": "API de Reclamos Vecinales activa y lista para recibir solicitudes."}