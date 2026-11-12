"""Validación de entradas en el servidor (M2): mismos campos, ahora con límites de longitud."""
import pytest
from pydantic import ValidationError

from src.infrastructure.adapters.input.dtos import ReclamoDTO, EstadoDTO, MAX_DESCRIPCION


def test_acepta_un_reclamo_como_el_del_formulario_web():
    dto = ReclamoDTO(titulo="Poste sin luz", descripcion="x" * 1500, ubicacion="Jr. Cusco cuadra 5",
                     dni="45678912", nombre="Rosa Huamán", direccion="Jr. Ancash 845", contacto="987654321")
    assert dto.categoria is None


def test_acepta_los_campos_opcionales_ausentes():
    assert ReclamoDTO(titulo="Bache", descripcion="Hay un bache").dni == ""


def test_rechaza_una_descripcion_demasiado_larga():
    with pytest.raises(ValidationError):
        ReclamoDTO(titulo="Bache", descripcion="x" * (MAX_DESCRIPCION + 1))


def test_rechaza_titulo_vacio():
    with pytest.raises(ValidationError):
        ReclamoDTO(titulo="", descripcion="Hay un bache")


def test_estado_vacio_se_rechaza():
    with pytest.raises(ValidationError):
        EstadoDTO(estado="")
