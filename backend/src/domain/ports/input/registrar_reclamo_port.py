from abc import ABC, abstractmethod

class RegistrarReclamoPort(ABC):
    @abstractmethod
    def ejecutar(self, titulo: str, descripcion: str, categoria: str,
                 dni: str = None, nombre: str = None, direccion: str = None, ubicacion: str = None):
        pass