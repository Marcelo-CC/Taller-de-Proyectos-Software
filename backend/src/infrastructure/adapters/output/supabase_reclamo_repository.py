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

    def listar(self):
        # Supabase devuelve como máximo 1000 filas por consulta: se pagina hasta traer todas
        filas, desde, lote = [], 0, 1000
        while True:
            response = (self.supabase.table("reclamos").select("*")
                        .order("id", desc=True).range(desde, desde + lote - 1).execute())
            filas.extend(response.data)
            if len(response.data) < lote:
                return filas
            desde += lote

    def actualizar_estado(self, reclamo_id: int, estado: str):
        response = (self.supabase.table("reclamos").update({"estado": estado})
                    .eq("id", reclamo_id).execute())
        return response.data[0] if response.data else None
