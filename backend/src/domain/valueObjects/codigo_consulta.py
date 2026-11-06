import hashlib
import re
import secrets

# Sin 0/O, 1/I/L ni U para que el vecino no confunda caracteres al copiarlo
ALFABETO = "23456789ABCDEFGHJKMNPQRSTVWXYZ"
LONGITUD = 8


def generar() -> str:
    """Código secreto que se muestra una sola vez al vecino, con formato XXXX-XXXX."""
    codigo = "".join(secrets.choice(ALFABETO) for _ in range(LONGITUD))
    return f"{codigo[:4]}-{codigo[4:]}"


def hashear(codigo: str) -> str:
    """En la base solo se guarda este hash. Debe coincidir con la función SQL consultar_reclamo."""
    normalizado = re.sub(r"[^A-Za-z0-9]", "", codigo or "").upper()
    return hashlib.sha256(normalizado.encode("utf-8")).hexdigest()
