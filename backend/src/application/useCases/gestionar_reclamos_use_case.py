from src.domain.ports.input.gestionar_reclamos_port import GestionarReclamosPort
from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort
from src.domain.valueObjects.estado_reclamo import EstadoReclamo


class GestionarReclamosUseCase(GestionarReclamosPort):
    """Casos de uso del portal interno (SIGEM): listado y gestión de estados (HU-04)."""

    def __init__(self, repository: ReclamoRepositoryPort):
        self.repository = repository

    def listar(self):
        return self.repository.listar()

    POR_PAGINA_MAXIMO = 100

    def listar_pagina(self, pagina: int, por_pagina: int = 25):
        """Paginación del listado (FURPS+ Performance): evita enviar todos los reclamos en cada consulta."""
        if pagina < 1 or not 1 <= por_pagina <= self.POR_PAGINA_MAXIMO:
            raise ValueError(f"pagina debe ser ≥ 1 y por_pagina entre 1 y {self.POR_PAGINA_MAXIMO}")
        filas, total = self.repository.listar_pagina((pagina - 1) * por_pagina, por_pagina)
        return {
            "data": filas,
            "paginacion": {
                "pagina": pagina,
                "por_pagina": por_pagina,
                "total": total,
                "total_paginas": max(1, -(-total // por_pagina)),
            },
        }

    def cambiar_estado(self, reclamo_id: int, estado: str):
        # Lanza ValueError si el estado no es PENDIENTE, EN_PROCESO o RESUELTO
        estado_valido = EstadoReclamo(estado).value
        actualizado = self.repository.actualizar_estado(reclamo_id, estado_valido)
        if not actualizado:
            raise LookupError(f"No existe el reclamo {reclamo_id}")
        return actualizado
