from abc import ABC, abstractmethod
from src.domain.entities.reclamo import Reclamo

class ReclamoRepositoryPort(ABC):
    @abstractmethod
    def guardar(self, reclamo: Reclamo, emisiones_gco2: float, consumo_kwh: float):
        pass