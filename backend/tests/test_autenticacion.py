"""OWASP A01/A07: solo el personal con un token válido de Supabase Auth usa las rutas internas."""
from types import SimpleNamespace

import pytest

from src.infrastructure.security import autenticacion as auth


class AuthFalso:
    def __init__(self, validos):
        self.validos = validos

    def get_user(self, token):
        if token not in self.validos:
            raise RuntimeError("invalid JWT")
        return SimpleNamespace(user=SimpleNamespace(email=self.validos[token], id="uuid-1"))


CLIENTE = SimpleNamespace(auth=AuthFalso({"token-bueno": "operador@municipalidad.com"}))


def test_token_valido_devuelve_el_correo_del_operador():
    assert auth.verificar_usuario(CLIENTE, "token-bueno") == "operador@municipalidad.com"


@pytest.mark.parametrize("token", [None, "", "   "])
def test_sin_token_se_rechaza(token):
    with pytest.raises(auth.NoAutorizado):
        auth.verificar_usuario(CLIENTE, token)


def test_token_invalido_o_vencido_se_rechaza():
    with pytest.raises(auth.NoAutorizado):
        auth.verificar_usuario(CLIENTE, "token-falsificado")


def test_respuesta_sin_usuario_se_rechaza():
    cliente = SimpleNamespace(auth=SimpleNamespace(get_user=lambda t: SimpleNamespace(user=None)))
    with pytest.raises(auth.NoAutorizado):
        auth.verificar_usuario(cliente, "token")


def test_interruptor_de_emergencia(monkeypatch):
    monkeypatch.delenv("AUTH_OBLIGATORIA", raising=False)
    assert auth.auth_obligatoria() is True
    monkeypatch.setenv("AUTH_OBLIGATORIA", "false")
    assert auth.auth_obligatoria() is False
