"""Dobles de prueba (fakes) de los puertos y servicios externos."""
from types import SimpleNamespace


class RepositorioFalso:
    """Implementa ReclamoRepositoryPort en memoria."""

    def __init__(self):
        self.guardados = []
        self.estados = {}

    def guardar(self, reclamo, emisiones_gco2, consumo_kwh, codigo_hash):
        fila = {"id": len(self.guardados) + 1, "titulo": reclamo.titulo, "descripcion": reclamo.descripcion,
                "categoria": reclamo.categoria, "estado": reclamo.estado, "confianza": reclamo.confianza,
                "requiere_auditoria": reclamo.requiere_auditoria, "codigo_hash": codigo_hash}
        self.guardados.append(fila)
        return [fila]

    def listar(self):
        return list(self.guardados)

    def actualizar_estado(self, reclamo_id, estado):
        for fila in self.guardados:
            if fila["id"] == reclamo_id:
                fila["estado"] = estado
                return fila
        return None


class GeminiFalso:
    """Responde como Gemini con una categoría y probabilidades fijas, y guarda lo que recibió."""

    def __init__(self, categoria="Alumbrado", probabilidades=None, problematicas=1, por_ia=True):
        self.categoria = categoria
        self.probabilidades = probabilidades or {categoria: 1.0}
        self.problematicas = problematicas
        self.por_ia = por_ia
        self.recibido = None

    def procesar_reclamo_con_ia(self, titulo, descripcion, ubicacion=""):
        self.recibido = (titulo, descripcion, ubicacion)
        senales = {"probabilidades": self.probabilidades, "problematicas": self.problematicas,
                   "clasificado_por_ia": self.por_ia}
        return titulo, ubicacion, descripcion, self.categoria, senales


class TrackerFalso:
    """Reemplaza a CodeCarbon: devuelve un consumo fijo sin medir el hardware."""

    def __init__(self, *args, **kwargs):
        self.final_emissions_data = SimpleNamespace(energy_consumed=0.00005)

    def start(self):
        pass

    def stop(self):
        return 0.00001  # kg de CO2e


class MlflowFalso:
    """Reemplaza a MLflow: acepta las llamadas sin conectarse a DagsHub."""

    def __init__(self):
        self.metricas = {}

    def start_run(self):
        return self

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def log_param(self, clave, valor):
        pass

    def log_metric(self, clave, valor):
        self.metricas[clave] = valor
