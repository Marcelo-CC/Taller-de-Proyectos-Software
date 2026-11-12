"""Ley N.° 29733: los datos personales se enmascaran antes de salir hacia Gemini."""
from src.application.useCases.registrar_reclamo_use_case import RegistrarReclamoUseCase
from src.infrastructure.adapters.output.gemini_adapter import GeminiAdapter


def test_enmascara_datos_del_formulario_repetidos_en_el_texto():
    datos = [("45678912", "[DNI_PROTEGIDO]"), ("Rosa Huamán", "[CIUDADANO_ANÓNIMO]")]
    texto = RegistrarReclamoUseCase._enmascarar("Soy rosa huamán, DNI 45678912, hay un bache.", datos)
    assert "45678912" not in texto and "huamán" not in texto.lower()
    assert "[DNI_PROTEGIDO]" in texto and "[CIUDADANO_ANÓNIMO]" in texto


def test_no_enmascara_valores_demasiado_cortos():
    # Un valor de menos de 3 caracteres taparía letras sueltas del texto
    assert RegistrarReclamoUseCase._enmascarar("Hay un bache", [("a", "[X]")]) == "Hay un bache"


def test_anonimizacion_local_de_dni_celular_y_correo():
    texto = GeminiAdapter._anonimizar_local("Mi DNI 45678912, celular 987 654 321 y correo vecino@mail.com")
    assert "45678912" not in texto and "987 654 321" not in texto and "vecino@mail.com" not in texto
    assert texto.count("[DATOS_PROTEGIDOS]") == 2 and "[DNI_PROTEGIDO]" in texto


def test_anonimizacion_local_de_nombre_y_domicilio():
    texto = GeminiAdapter._anonimizar_local("Me llamo Carlos Quispe y vivo en Jr. Lima 450, hay basura.")
    assert "Carlos" not in texto and "Jr. Lima 450" not in texto
    assert "[CIUDADANO_ANÓNIMO]" in texto and "[DATOS_PROTEGIDOS]" in texto
