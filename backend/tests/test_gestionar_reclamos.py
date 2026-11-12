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


@pytest.fixture
def con_60_reclamos():
    repo = RepositorioFalso()
    for n in range(60):
        repo.guardar(Reclamo(f"Reclamo {n + 1}", "texto", "Vías Públicas"), 0.0, 0.0, "hash")
    return GestionarReclamosUseCase(repo)


def test_primera_pagina_trae_25_reclamos_mas_recientes(con_60_reclamos):
    r = con_60_reclamos.listar_pagina(1, 25)
    assert len(r["data"]) == 25 and r["data"][0]["id"] == 60
    assert r["paginacion"] == {"pagina": 1, "por_pagina": 25, "total": 60, "total_paginas": 3}


def test_ultima_pagina_trae_el_resto(con_60_reclamos):
    r = con_60_reclamos.listar_pagina(3, 25)
    assert [f["id"] for f in r["data"]] == list(range(10, 0, -1))


def test_pagina_fuera_de_rango_devuelve_lista_vacia(con_60_reclamos):
    assert con_60_reclamos.listar_pagina(9, 25)["data"] == []


@pytest.mark.parametrize("pagina,por_pagina", [(0, 25), (1, 0), (1, 101)])
def test_rechaza_parametros_invalidos(con_60_reclamos, pagina, por_pagina):
    with pytest.raises(ValueError):
        con_60_reclamos.listar_pagina(pagina, por_pagina)
