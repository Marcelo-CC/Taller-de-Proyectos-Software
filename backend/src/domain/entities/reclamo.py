class Reclamo:
    def __init__(self, titulo: str, descripcion: str, categoria: str, estado: str = "PENDIENTE",
                 confianza: float = None, requiere_auditoria: bool = False):
        self.titulo = titulo
        self.descripcion = descripcion
        self.categoria = categoria
        self.estado = estado
        # HITL: confianza de la IA en la categoría (0.0–1.0) y si debe retenerse para revisión humana
        self.confianza = confianza
        self.requiere_auditoria = requiere_auditoria
