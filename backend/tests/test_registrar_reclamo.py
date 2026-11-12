"""Caso de uso de registro: protege los datos, clasifica, decide HITL, guarda solo el hash."""
import pytest

from src.application.useCases import registrar_reclamo_use_case as modulo
from src.application.useCases.registrar_reclamo_use_case import RegistrarReclamoUseCase
from src.domain.valueObjects import codigo_consulta
from tests.dobles import RepositorioFalso, GeminiFalso, TrackerFalso, MlflowFalso

DESCRIPCION = ("Soy Rosa Huamán con DNI 45678912. El poste de luz de la cuadra 5 del Jr. Cusco está "
               "apagado desde hace una semana y la calle queda totalmente oscura durante la noche.")


@pytest.fixture(autouse=True)
def sin_servicios_externos(monkeypatch):
    monkeypatch.setattr(modulo, "EmissionsTracker", TrackerFalso)
    monkeypatch.setattr(modulo, "mlflow", MlflowFalso(), raising=False)


def registrar(gemini, repo=None, **extra):
    repo = repo or RepositorioFalso()
    caso = RegistrarReclamoUseCase(repo, gemini_adapter=gemini)
    datos = dict(titulo="Poste sin luz", descripcion=DESCRIPCION, dni="45678912", nombre="Rosa Huamán",
                 direccion="Jr. Ancash 845", contacto="987654321", ubicacion="Jr. Cusco cuadra 5")
    datos.update(extra)
    return caso.ejecutar(**datos), repo


def test_los_datos_personales_no_llegan_a_gemini():
    gemini = GeminiFalso()
    registrar(gemini)
    enviado = " ".join(gemini.recibido)
    assert "45678912" not in enviado and "Rosa Huamán" not in enviado


def test_lo_guardado_no_contiene_datos_personales():
    _, repo = registrar(GeminiFalso())
    fila = repo.guardados[0]
    for dato in ("45678912", "Rosa Huamán", "Jr. Ancash 845", "987654321"):
        assert dato not in fila["titulo"] and dato not in fila["descripcion"]


def test_clasificacion_segura_va_directo_a_la_gerencia():
    resultado, _ = registrar(GeminiFalso(categoria="Alumbrado", probabilidades={"Alumbrado": 0.95}))
    assert resultado["categoria_detectada"] == "Alumbrado"
    assert resultado["requiere_auditoria"] is False


def test_clasificacion_dudosa_queda_retenida_para_revision_humana():
    gemini = GeminiFalso(categoria="Alumbrado", probabilidades={"Alumbrado": 0.5, "Vías Públicas": 0.5})
    resultado, repo = registrar(gemini)
    assert resultado["requiere_auditoria"] is True
    assert repo.guardados[0]["requiere_auditoria"] is True


def test_solo_se_guarda_el_hash_del_codigo_secreto():
    resultado, repo = registrar(GeminiFalso())
    fila = repo.guardados[0]
    assert resultado["codigo_consulta"] not in str(fila)
    assert fila["codigo_hash"] == codigo_consulta.hashear(resultado["codigo_consulta"])
    assert resultado["ticket"] == fila["id"]


def test_reporta_la_telemetria_green_ai():
    resultado, _ = registrar(GeminiFalso())
    assert resultado["consumo_kwh"] == 0.00005
    assert resultado["emisiones_gco2"] == pytest.approx(0.01)


def test_si_mlflow_falla_el_reclamo_se_guarda_igual(monkeypatch):
    class MlflowRoto:
        def start_run(self):
            raise ConnectionError("DagsHub no responde")
    monkeypatch.setattr(modulo, "mlflow", MlflowRoto(), raising=False)
    resultado, repo = registrar(GeminiFalso())
    assert len(repo.guardados) == 1 and resultado["ticket"] == 1
