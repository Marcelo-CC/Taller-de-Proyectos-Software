"""Caso de uso del SIGEM: listar y cambiar estados válidos (HU-04)."""
import pytest

from src.application.useCases.gestionar_reclamos_use_case import GestionarReclamosUseCase
from src.domain.entities.reclamo import Reclamo
from tests.dobles import RepositorioFalso


@pytest.fixture
def caso():
    repo = RepositorioFalso()
    repo.guardar(Reclamo("Bache", "Hay un bache", "Vías Públicas"), 0.0, 0.0, "hash")
    return GestionarReclamosUseCase(repo)


def test_lista_los_reclamos(caso):
    assert len(caso.listar()) == 1


def test_cambia_a_un_estado_valido(caso):
    assert caso.cambiar_estado(1, "RESUELTO")["estado"] == "RESUELTO"


def test_rechaza_un_estado_inexistente(caso):
    with pytest.raises(ValueError):
        caso.cambiar_estado(1, "BORRADO")


def test_avisa_si_el_reclamo_no_existe(caso):
    with pytest.raises(LookupError):
        caso.cambiar_estado(999, "RESUELTO")
