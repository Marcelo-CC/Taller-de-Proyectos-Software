"""Controles sobre el texto corregido por Gemini: no recortar el reclamo ni tapar palabras comunes."""
from src.infrastructure.adapters.output.gemini_adapter import GeminiAdapter

PREFIJO = ("Soy [CIUDADANO_ANÓNIMO] con DNI [DNI_PROTEGIDO], domiciliado en [DATOS_PROTEGIDOS]. "
           "Ubicación del problema: Parque Central. Detalle del problema: ")


def test_texto_recortado_por_la_ia_se_reemplaza_por_el_original():
    # Caso real del ticket N° 01254
    original = PREFIJO + ("en el parque ay un poste q esta medio caido y ademas los juegos de los niños "
                          "estan rotos y en la noche no ay luz, tambien se juntan personas a tomar")
    recortado = PREFIJO + "En el parque hay un poste que está medio caído y además los juegos de los niños."
    assert GeminiAdapter._revisar_correccion(original, recortado) == original


def test_correccion_completa_se_conserva():
    original = PREFIJO + ("en el parque ay un poste q esta medio caido y ademas los juegos de los niños "
                          "estan rotos y en la noche no ay luz, tambien se juntan personas a tomar")
    corregido = PREFIJO + ("En el parque hay un poste que está medio caído y además los juegos de los niños "
                           "están rotos; en la noche no hay luz y también se juntan personas a tomar.")
    assert GeminiAdapter._revisar_correccion(original, corregido) == corregido


def test_mi_casa_tapada_por_la_ia_se_restaura():
    # Caso real del ticket N° 01253
    original = PREFIJO + "Hace mas de una semana q nadie recoje la basura en la esquina de mi casa, ya hay olor"
    corregido = PREFIJO + "Hace más de una semana que nadie recoge la basura en la esquina de mi [DATOS_PROTEGIDOS], ya hay olor."
    resultado = GeminiAdapter._revisar_correccion(original, corregido)
    assert "esquina de mi casa" in resultado
    assert resultado.startswith(PREFIJO)  # el domicilio del formulario sigue protegido


def test_no_se_restaura_una_direccion_real():
    # "mi casa en Jr. Lima 450" ya llega enmascarado; solo se puede reponer la palabra "casa"
    original = GeminiAdapter._anonimizar_local("Hay basura frente a mi casa en Jr. Lima 450 desde ayer")
    corregido = "Hay basura frente a mi [DATOS_PROTEGIDOS] desde ayer."
    resultado = GeminiAdapter._revisar_correccion(original, corregido)
    assert "Lima 450" not in resultado


def test_si_la_ia_anonimiza_un_nombre_se_respeta_aunque_cambie_el_texto():
    # Privacidad primero: la IA detectó un nombre que la anonimización local no vio
    original = "El vecino Juan Pérez Rojas deja su basura en la vereda todos los días"
    corregido = "El vecino [CIUDADANO_ANÓNIMO] deja su basura en la vereda."
    assert GeminiAdapter._revisar_correccion(original, corregido) == corregido


def test_textos_cortos_no_se_revisan():
    assert GeminiAdapter._revisar_correccion("bache grande", "Bache grande.") == "Bache grande."
