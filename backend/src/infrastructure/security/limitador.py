"""Límite de solicitudes en memoria (OWASP A04): evita el abuso del registro público de reclamos.

Cuenta las solicitudes de la última ventana (60 s) por IP y en total. Es suficiente para una
sola instancia de Render; con varias instancias habría que usar un almacén compartido.
"""
import os
import threading
import time
from collections import defaultdict, deque


class LimitadorDeSolicitudes:
    def __init__(self, por_clave: int, total: int, ventana_segundos: float = 60.0, reloj=time.monotonic):
        self.por_clave = por_clave
        self.total = total
        self.ventana = ventana_segundos
        self.reloj = reloj
        self._por_clave = defaultdict(deque)
        self._todas = deque()
        self._candado = threading.Lock()  # las rutas síncronas de FastAPI corren en varios hilos

    def _limpiar(self, cola, ahora):
        while cola and ahora - cola[0] >= self.ventana:
            cola.popleft()

    def permitir(self, clave: str) -> bool:
        """True si la solicitud entra en el límite (y la cuenta); False si debe rechazarse."""
        if self.por_clave <= 0:  # 0 = límite desactivado
            return True
        with self._candado:
            ahora = self.reloj()
            cola = self._por_clave[clave]
            self._limpiar(cola, ahora)
            self._limpiar(self._todas, ahora)
            if len(cola) >= self.por_clave or (self.total > 0 and len(self._todas) >= self.total):
                return False
            cola.append(ahora)
            self._todas.append(ahora)
            if len(self._por_clave) > 10_000:  # evita que la memoria crezca sin límite
                for k in [k for k, c in self._por_clave.items() if not c]:
                    del self._por_clave[k]
            return True


def ip_del_cliente(cabecera_forwarded: str, ip_directa: str) -> str:
    """Render pone la IP real del cliente en X-Forwarded-For (la primera de la lista)."""
    if cabecera_forwarded:
        primera = cabecera_forwarded.split(",")[0].strip()
        if primera:
            return primera
    return ip_directa or "desconocida"


def desde_entorno() -> LimitadorDeSolicitudes:
    return LimitadorDeSolicitudes(
        por_clave=int(os.getenv("RATE_LIMIT_POR_MINUTO", "20")),
        total=int(os.getenv("RATE_LIMIT_TOTAL_POR_MINUTO", "120")),
    )
