"""OWASP A01/A04/A09 en las dependencias de la API (se ejecuta donde FastAPI está instalado)."""
import sys
import types
from types import SimpleNamespace

import pytest

pytest.importorskip("fastapi")

from fastapi import HTTPException  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials  # noqa: E402
from src.infrastructure.adapters.input import api_router  # noqa: E402


@pytest.fixture(autouse=True)
def supabase_falso(monkeypatch):
    auth = SimpleNamespace(get_user=lambda t: SimpleNamespace(user=SimpleNamespace(email="op@muni.pe"))
                           if t == "valido" else (_ for _ in ()).throw(RuntimeError("jwt invalido")))
    monkeypatch.setitem(sys.modules, "main", types.SimpleNamespace(supabase=SimpleNamespace(auth=auth)))
    monkeypatch.delenv("AUTH_OBLIGATORIA", raising=False)


def test_sin_token_responde_401():
    with pytest.raises(HTTPException) as e:
        api_router.usuario_autenticado(None)
    assert e.value.status_code == 401


def test_token_valido_identifica_al_operador():
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="valido")
    assert api_router.usuario_autenticado(cred) == "op@muni.pe"


def test_acceso_denegado_queda_en_la_bitacora(caplog):
    cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="robado")
    with pytest.raises(HTTPException):
        api_router.usuario_autenticado(cred)
    assert "Acceso denegado" in caplog.text


def test_el_registro_publico_responde_429_al_superar_el_limite(monkeypatch):
    from src.infrastructure.security.limitador import LimitadorDeSolicitudes
    monkeypatch.setattr(api_router, "limitador_registro", LimitadorDeSolicitudes(por_clave=1, total=10))
    peticion = SimpleNamespace(headers={"x-forwarded-for": "190.1.1.1"}, client=SimpleNamespace(host="10.0.0.1"))
    assert api_router.limitar_registro(peticion) == "190.1.1.1"
    with pytest.raises(HTTPException) as e:
        api_router.limitar_registro(peticion)
    assert e.value.status_code == 429
