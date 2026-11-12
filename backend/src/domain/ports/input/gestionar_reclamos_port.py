from abc import ABC, abstractmethod

class GestionarReclamosPort(ABC):
    @abstractmethod
    def listar(self):
        pass

    @abstractmethod
    def listar_pagina(self, pagina: int, por_pagina: int):
        pass

    @abstractmethod
    def cambiar_estado(self, reclamo_id: int, estado: str):
        pass
