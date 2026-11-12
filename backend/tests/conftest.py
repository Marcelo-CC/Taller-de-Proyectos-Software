"""Configuración común de las pruebas.

Las pruebas no usan internet ni credenciales: Gemini, Supabase, CodeCarbon y MLflow se
reemplazan por dobles de prueba. Si alguna librería externa no está instalada en la máquina
(por ejemplo, en un entorno de CI mínimo), se registra un módulo vacío para poder importar el código.
"""
import os
import sys
import types
import importlib.util

RAIZ_BACKEND = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if RAIZ_BACKEND not in sys.path:
    sys.path.insert(0, RAIZ_BACKEND)


def _modulo_vacio(nombre):
    modulo = types.ModuleType(nombre)
    sys.modules[nombre] = modulo
    return modulo


if importlib.util.find_spec("codecarbon") is None:
    _modulo_vacio("codecarbon").EmissionsTracker = object

if importlib.util.find_spec("mlflow") is None:
    _modulo_vacio("mlflow")

try:
    from google import genai  # noqa: F401
    from google.genai import types as _tipos  # noqa: F401
except ImportError:
    try:
        import google
    except ImportError:
        google = _modulo_vacio("google")
    genai = _modulo_vacio("google.genai")
    genai.types = _modulo_vacio("google.genai.types")
    google.genai = genai

# El adaptador de Gemini exige la clave al crearse; en las pruebas nunca se llama a la API real
os.environ.setdefault("GEMINI_API_KEY", "clave-de-prueba")
