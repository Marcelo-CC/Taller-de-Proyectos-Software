from abc import ABC, abstractmethod

class RegistrarReclamoPort(ABC):
    @abstractmethod
    def ejecutar(self, titulo: str, descripcion: str, categoria: str):
        pass