from enum import Enum

class EstadoReclamo(str, Enum):
    PENDIENTE = "PENDIENTE"
    EN_PROCESO = "EN_PROCESO"
    RESUELTO = "RESUELTO"