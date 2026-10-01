from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.application.useCases.registrar_reclamo_use_case import RegistrarReclamoUseCase
from src.infrastructure.adapters.output.supabase_reclamo_repository import SupabaseReclamoRepository

router = APIRouter()

# Proveedor de dependencias para FastAPI
def get_use_case() -> RegistrarReclamoUseCase:
    from main import supabase
    repository_adapter = SupabaseReclamoRepository(supabase)
    return RegistrarReclamoUseCase(repository_adapter)

class ReclamoDTO(BaseModel):
    titulo: str
    descripcion: str
    categoria: str

@router.post("/api/reclamos")
async def crear_reclamo(
    dto: ReclamoDTO, 
    use_case: RegistrarReclamoUseCase = Depends(get_use_case)
):
    try:
        resultado = use_case.ejecutar(
            titulo=dto.titulo,
            descripcion=dto.descripcion,
            categoria=dto.categoria
        )
        return {
            "status": "success",
            "message": "Reclamo registrado exitosamente.",
            "data": resultado["db_data"],
            "telemetria_green_ai": {
                "emisiones_gco2": round(resultado["emisiones_gco2"], 6),
                "consumo_kwh": round(resultado["consumo_kwh"], 8)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en el servidor: {str(e)}")