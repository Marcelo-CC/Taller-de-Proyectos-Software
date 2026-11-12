from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort
from src.domain.entities.reclamo import Reclamo

# Columnas públicas: codigo_hash nunca se lee por la API (la base no da permiso de lectura sobre ella)
COLUMNAS = ("id,created_at,titulo,descripcion,categoria,emisiones_gco2,consumo_kwh,estado,"
            "confianza,requiere_auditoria")

class SupabaseReclamoRepository(ReclamoRepositoryPort):
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def guardar(self, reclamo: Reclamo, emisiones_gco2: float, consumo_kwh: float, codigo_hash: str):
        response = self.supabase.table("reclamos").insert({
            "titulo": reclamo.titulo,
            "descripcion": reclamo.descripcion,
            "categoria": reclamo.categoria,
            "estado": reclamo.estado,
            "confianza": reclamo.confianza,
            "requiere_auditoria": reclamo.requiere_auditoria,
            "emisiones_gco2": emisiones_gco2,
            "consumo_kwh": consumo_kwh,
            "codigo_hash": codigo_hash
        }).select(COLUMNAS).execute()
        return response.data

    def listar(self):
        # Supabase devuelve como máximo 1000 filas por consulta: se pagina hasta traer todas
        filas, desde, lote = [], 0, 1000
        while True:
            response = (self.supabase.table("reclamos").select(COLUMNAS)
                        .order("id", desc=True).range(desde, desde + lote - 1).execute())
            filas.extend(response.data)
            if len(response.data) < lote:
                return filas
            desde += lote

    def listar_pagina(self, desde: int, cantidad: int):
        # Una sola consulta: la página pedida y el total de reclamos (count="exact")
        response = (self.supabase.table("reclamos").select(COLUMNAS, count="exact")
                    .order("id", desc=True).range(desde, desde + cantidad - 1).execute())
        return response.data, (response.count if response.count is not None else len(response.data))

    def actualizar_estado(self, reclamo_id: int, estado: str):
        response = (self.supabase.table("reclamos").update({"estado": estado})
                    .eq("id", reclamo_id).select(COLUMNAS).execute())
        return response.data[0] if response.data else None
