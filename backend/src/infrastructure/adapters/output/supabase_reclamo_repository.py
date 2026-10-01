from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort
from src.domain.entities.reclamo import Reclamo

class SupabaseReclamoRepository(ReclamoRepositoryPort):
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def guardar(self, reclamo: Reclamo, emisiones_gco2: float, consumo_kwh: float):
        response = self.supabase.table("reclamos").insert({
            "titulo": reclamo.titulo,
            "descripcion": reclamo.descripcion,
            "categoria": reclamo.categoria,
            "estado": reclamo.estado,
            "emisiones_gco2": emisiones_gco2,
            "consumo_kwh": consumo_kwh
        }).execute()
        return response.data