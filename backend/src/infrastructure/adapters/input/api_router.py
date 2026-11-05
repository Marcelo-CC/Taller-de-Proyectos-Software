from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.application.useCases.registrar_reclamo_use_case import RegistrarReclamoUseCase
from src.application.useCases.gestionar_reclamos_use_case import GestionarReclamosUseCase
from src.infrastructure.adapters.output.supabase_reclamo_repository import SupabaseReclamoRepository

router = APIRouter()

# Proveedores de dependencias para FastAPI
def get_repository() -> SupabaseReclamoRepository:
    from main import supabase
    return SupabaseReclamoRepository(supabase)

def get_use_case(repository: SupabaseReclamoRepository = Depends(get_repository)) -> RegistrarReclamoUseCase:
    return RegistrarReclamoUseCase(repository)

def get_gestion_use_case(repository: SupabaseReclamoRepository = Depends(get_repository)) -> GestionarReclamosUseCase:
    return GestionarReclamosUseCase(repository)


class ReclamoDTO(BaseModel):
    titulo: str
    descripcion: str
    categoria: Optional[str] = None  # Permite recibir valor nulo/ausente desde React sin arrojar 422
    ubicacion: Optional[str] = ""
    # Datos personales: se enmascaran en el backend y nunca se envían a Gemini
    dni: Optional[str] = ""
    nombre: Optional[str] = ""
    direccion: Optional[str] = ""
    contacto: Optional[str] = ""

class EstadoDTO(BaseModel):
    estado: str


# Módulo A: Portal Ciudadano
# def (no async): las llamadas a Gemini, MLflow y Supabase son bloqueantes
@router.post("/api/reclamos")
def crear_reclamo(
    dto: ReclamoDTO,
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
            "categoria_asignada": resultado.get("categoria_detectada"),
            "titulo_anonimizado": resultado["titulo_anonimizado"],
            "descripcion_anonimizada": resultado["descripcion_anonimizada"],
            "telemetria_green_ai": {
                "emisiones_gco2": round(resultado["emisiones_gco2"], 6),
                "consumo_kwh": round(resultado["consumo_kwh"], 8)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")


# Módulo B: Portal Operativo Interno (SIGEM)
@router.get("/api/reclamos")
def listar_reclamos(use_case: GestionarReclamosUseCase = Depends(get_gestion_use_case)):
    try:
        return {"status": "success", "data": use_case.listar()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")


@router.patch("/api/reclamos/{reclamo_id}/estado")
def cambiar_estado(
    reclamo_id: int,
    dto: EstadoDTO,
    use_case: GestionarReclamosUseCase = Depends(get_gestion_use_case)
):
    try:
        return {"status": "success", "data": use_case.cambiar_estado(reclamo_id, dto.estado)}
    except ValueError:
        raise HTTPException(status_code=422, detail="Estado inválido. Use PENDIENTE, EN_PROCESO o RESUELTO.")
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")
