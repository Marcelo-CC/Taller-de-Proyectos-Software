class Reclamo:
    def __init__(self, titulo: str, descripcion: str, categoria: str, estado: str = "PENDIENTE"):
        self.titulo = titulo
        self.descripcion = descripcion
        self.categoria = categoria
        self.estado = estado