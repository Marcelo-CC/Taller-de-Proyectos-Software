from abc import ABC, abstractmethod
from src.domain.entities.reclamo import Reclamo

class ReclamoRepositoryPort(ABC):
    @abstractmethod
    def guardar(self, reclamo: Reclamo, emisiones_gco2: float, consumo_kwh: float, codigo_hash: str):
        pass

    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def actualizar_estado(self, reclamo_id: int, estado: str):
        pass
