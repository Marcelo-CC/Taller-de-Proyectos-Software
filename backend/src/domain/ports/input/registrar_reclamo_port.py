from abc import ABC, abstractmethod

class RegistrarReclamoPort(ABC):
    @abstractmethod
    def ejecutar(self, titulo: str, descripcion: str, categoria: str = None, dni: str = "",
                 nombre: str = "", direccion: str = "", contacto: str = "", ubicacion: str = ""):
        pass
