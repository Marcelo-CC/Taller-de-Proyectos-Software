import logging
import uuid
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.application.useCases.registrar_reclamo_use_case import RegistrarReclamoUseCase
from src.application.useCases.gestionar_reclamos_use_case import GestionarReclamosUseCase
from src.infrastructure.adapters.output.supabase_reclamo_repository import SupabaseReclamoRepository
from src.infrastructure.adapters.input.dtos import ReclamoDTO, EstadoDTO
from src.infrastructure.security import autenticacion, limitador

logger = logging.getLogger("api.reclamos")
# Bitácora de seguridad (OWASP A09): accesos denegados, abusos y cambios hechos por el personal
auditoria = logging.getLogger("auditoria")


def error_interno(operacion: str, error: Exception) -> HTTPException:
    """Registra el detalle técnico en el servidor y devuelve al cliente solo un mensaje genérico
    con un código de incidente para poder rastrearlo en los logs de Render."""
    incidente = uuid.uuid4().hex[:8].upper()
    logger.error("Incidente %s en %s: %s", incidente, operacion, error, exc_info=error)
    return HTTPException(
        status_code=500,
        detail=f"No se pudo completar la operación. Intente nuevamente (código de incidente {incidente}).",
    )


router = APIRouter()

# Proveedores de dependencias para FastAPI
def get_repository() -> SupabaseReclamoRepository:
    from main import supabase
    return SupabaseReclamoRepository(supabase)

def get_use_case(repository: SupabaseReclamoRepository = Depends(get_repository)) -> RegistrarReclamoUseCase:
    return RegistrarReclamoUseCase(repository)

def get_gestion_use_case(repository: SupabaseReclamoRepository = Depends(get_repository)) -> GestionarReclamosUseCase:
    return GestionarReclamosUseCase(repository)


# Seguridad (OWASP A01/A07): las rutas del SIGEM exigen el token de Supabase Auth del operador.
# auto_error=False para responder con un mensaje propio en español; Swagger muestra el botón "Authorize".
esquema_bearer = HTTPBearer(auto_error=False)


def usuario_autenticado(
    credenciales: Optional[HTTPAuthorizationCredentials] = Depends(esquema_bearer),
) -> str:
    if not autenticacion.auth_obligatoria():
        return "sin-verificacion"
    from main import supabase
    try:
        return autenticacion.verificar_usuario(supabase, credenciales.credentials if credenciales else None)
    except autenticacion.NoAutorizado as e:
        auditoria.warning("Acceso denegado a la API interna: %s", e)
        raise HTTPException(
            status_code=401,
            detail="Debe iniciar sesión como personal municipal para usar esta función.",
            headers={"WWW-Authenticate": "Bearer"},
        )


# Seguridad (OWASP A04): límite de registros por minuto para el endpoint público
limitador_registro = limitador.desde_entorno()


def limitar_registro(request: Request) -> str:
    ip = limitador.ip_del_cliente(request.headers.get("x-forwarded-for", ""),
                                  request.client.host if request.client else "")
    if not limitador_registro.permitir(ip):
        auditoria.warning("Límite de solicitudes superado al registrar reclamos desde %s", ip)
        raise HTTPException(
            status_code=429,
            detail="Se recibieron demasiados reclamos seguidos desde su conexión. Espere un minuto e intente nuevamente.",
        )
    return ip


# Módulo A: Portal Ciudadano
# def (no async): las llamadas a Gemini, MLflow y Supabase son bloqueantes
@router.post("/api/reclamos")
def crear_reclamo(
    dto: ReclamoDTO,
    ip: str = Depends(limitar_registro),
    use_case: RegistrarReclamoUseCase = Depends(get_use_case)
):
    try:
        resultado = use_case.ejecutar(
            titulo=dto.titulo,
            descripcion=dto.descripcion,
            categoria=dto.categoria,
            dni=dto.dni,
            nombre=dto.nombre,
            direccion=dto.direccion,
            contacto=dto.contacto,
            ubicacion=dto.ubicacion
        )
        return {
            "status": "success",
            "message": "Reclamo registrado exitosamente.",
            "data": resultado["db_data"],
            "ticket": resultado["ticket"],
            "codigo_consulta": resultado["codigo_consulta"],
            "categoria_asignada": resultado.get("categoria_detectada"),
            # HITL: confianza (0.0–1.0) y si el reclamo quedó retenido para revisión humana
            "confianza": resultado["confianza"],
            "requiere_auditoria": resultado["requiere_auditoria"],
            "titulo_anonimizado": resultado["titulo_anonimizado"],
            "descripcion_anonimizada": resultado["descripcion_anonimizada"],
            "telemetria_green_ai": {
                "emisiones_gco2": round(resultado["emisiones_gco2"], 6),
                "consumo_kwh": round(resultado["consumo_kwh"], 8)
            }
        }
    except Exception as e:
        raise error_interno("registrar reclamo", e)


# Módulo B: Portal Operativo Interno (SIGEM)
@router.get("/api/reclamos")
def listar_reclamos(
    usuario: str = Depends(usuario_autenticado),
    use_case: GestionarReclamosUseCase = Depends(get_gestion_use_case)
):
    try:
        return {"status": "success", "data": use_case.listar()}
    except Exception as e:
        raise error_interno("listar reclamos", e)


@router.patch("/api/reclamos/{reclamo_id}/estado")
def cambiar_estado(
    reclamo_id: int,
    dto: EstadoDTO,
    usuario: str = Depends(usuario_autenticado),
    use_case: GestionarReclamosUseCase = Depends(get_gestion_use_case)
):
    try:
        actualizado = use_case.cambiar_estado(reclamo_id, dto.estado)
        auditoria.info("Reclamo %s cambiado a %s por %s", reclamo_id, dto.estado, usuario)
        return {"status": "success", "data": actualizado}
    except ValueError:
        raise HTTPException(status_code=422, detail="Estado inválido. Use PENDIENTE, EN_PROCESO o RESUELTO.")
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise error_interno("cambiar estado", e)
