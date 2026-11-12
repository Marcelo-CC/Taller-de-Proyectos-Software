"""Autenticación del personal municipal en la API (OWASP A01/A07).

El SIGEM inicia sesión con Supabase Auth y recibe un token JWT. Las rutas internas de la API
exigen ese token en la cabecera `Authorization: Bearer <token>` y lo validan contra Supabase.
"""
import os


class NoAutorizado(Exception):
    """El token falta, es inválido o expiró."""


def auth_obligatoria() -> bool:
    """Interruptor de emergencia: AUTH_OBLIGATORIA=false desactiva la verificación sin redesplegar."""
    return os.getenv("AUTH_OBLIGATORIA", "true").strip().lower() not in ("false", "0", "no")


def verificar_usuario(cliente_supabase, token) -> str:
    """Devuelve el correo del usuario dueño del token o lanza NoAutorizado."""
    if not token or not str(token).strip():
        raise NoAutorizado("Falta el token de sesión")
    try:
        respuesta = cliente_supabase.auth.get_user(str(token).strip())
    except Exception as e:  # token vencido, firma inválida o Supabase no disponible
        raise NoAutorizado(f"Token rechazado por Supabase Auth: {type(e).__name__}") from e
    usuario = getattr(respuesta, "user", None)
    if usuario is None:
        raise NoAutorizado("Token sin usuario asociado")
    return getattr(usuario, "email", None) or getattr(usuario, "id", "usuario")
