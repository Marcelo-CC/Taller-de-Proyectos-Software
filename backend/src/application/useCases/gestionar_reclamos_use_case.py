from src.domain.ports.input.gestionar_reclamos_port import GestionarReclamosPort
from src.domain.ports.output.reclamo_repository_port import ReclamoRepositoryPort
from src.domain.valueObjects.estado_reclamo import EstadoReclamo


class GestionarReclamosUseCase(GestionarReclamosPort):
    """Casos de uso del portal interno (SIGEM): listado y gestión de estados (HU-04)."""

    def __init__(self, repository: ReclamoRepositoryPort):
        self.repository = repository

    def listar(self):
        return self.repository.listar()

    def cambiar_estado(self, reclamo_id: int, estado: str):
        # Lanza ValueError si el estado no es PENDIENTE, EN_PROCESO o RESUELTO
        estado_valido = EstadoReclamo(estado).value
        actualizado = self.repository.actualizar_estado(reclamo_id, estado_valido)
        if not actualizado:
            raise LookupError(f"No existe el reclamo {reclamo_id}")
        return actualizado
