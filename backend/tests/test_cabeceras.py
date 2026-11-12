"""OWASP A05: cabeceras de seguridad y orígenes permitidos por CORS."""
import re

from src.infrastructure.security import cabeceras


def test_cabeceras_basicas_en_la_api():
    h = cabeceras.cabeceras_para("/api/reclamos")
    assert h["X-Content-Type-Options"] == "nosniff"
    assert h["X-Frame-Options"] == "DENY"
    assert "max-age" in h["Strict-Transport-Security"]
    assert h["Content-Security-Policy"].startswith("default-src 'none'")


def test_swagger_no_recibe_csp_estricta_para_seguir_funcionando():
    assert "Content-Security-Policy" not in cabeceras.cabeceras_para("/docs")


def test_cors_por_defecto_solo_frontend_del_proyecto(monkeypatch):
    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    origenes = cabeceras.origenes_permitidos()
    assert "https://taller-de-proyectos-software.vercel.app" in origenes
    assert "*" not in origenes


def test_cors_configurable_desde_render(monkeypatch):
    monkeypatch.setenv("CORS_ORIGINS", "https://a.com, https://b.com")
    assert cabeceras.origenes_permitidos() == ["https://a.com", "https://b.com"]


def test_regex_acepta_vistas_previas_del_proyecto_y_no_otros_sitios():
    patron = re.compile(cabeceras.REGEX_VISTAS_PREVIAS)
    assert patron.fullmatch("https://taller-de-proyectos-software-git-dev-marcelo.vercel.app")
    assert not patron.fullmatch("https://sitio-malicioso.vercel.app")
    assert not patron.fullmatch("https://taller-de-proyectos-software.vercel.app.evil.com")
