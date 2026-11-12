"""Manejo de errores de la API (M3): el cliente recibe un mensaje genérico con código de incidente."""
import pytest

pytest.importorskip("fastapi")

from fastapi import HTTPException  # noqa: E402
from src.infrastructure.adapters.input import api_router  # noqa: E402
from src.infrastructure.adapters.input.dtos import ReclamoDTO  # noqa: E402


class CasoQueFalla:
    def ejecutar(self, **kwargs):
        raise RuntimeError("password=secreta host=db.interna:5432")

    def listar(self):
        raise RuntimeError("password=secreta host=db.interna:5432")


def test_error_interno_no_expone_detalles_tecnicos(caplog):
    with pytest.raises(HTTPException) as error:
        api_router.crear_reclamo(ReclamoDTO(titulo="Bache", descripcion="Hay un bache"), CasoQueFalla())
    assert error.value.status_code == 500
    assert "secreta" not in error.value.detail and "db.interna" not in error.value.detail
    assert "código de incidente" in error.value.detail
    # El detalle técnico sí queda en el log del servidor para poder investigarlo
    assert "db.interna" in caplog.text
