"""Cabeceras de seguridad HTTP (OWASP A05) y orígenes permitidos por CORS."""
import os

ORIGENES_POR_DEFECTO = (
    "https://taller-de-proyectos-software.vercel.app,"
    "http://localhost:5173,http://127.0.0.1:5173"
)
# Vistas previas de Vercel del mismo proyecto (taller-de-proyectos-software-xxxx.vercel.app)
REGEX_VISTAS_PREVIAS = r"https://taller-de-proyectos-software(-[a-z0-9-]+)?\.vercel\.app"

CABECERAS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "no-referrer",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
}
# La API solo devuelve JSON: se prohíbe cargar cualquier recurso, salvo en la documentación (Swagger)
CSP_API = "default-src 'none'; frame-ancestors 'none'"
RUTAS_DOCUMENTACION = ("/docs", "/redoc", "/openapi.json")


def origenes_permitidos() -> list:
    """CORS_ORIGINS en Render (separados por coma). '*' vuelve al comportamiento anterior."""
    return [o.strip() for o in os.getenv("CORS_ORIGINS", ORIGENES_POR_DEFECTO).split(",") if o.strip()]


def cabeceras_para(ruta: str) -> dict:
    cabeceras = dict(CABECERAS)
    if not ruta.startswith(RUTAS_DOCUMENTACION):
        cabeceras["Content-Security-Policy"] = CSP_API
    return cabeceras
