"""Respaldo cuando Gemini no responde: clasificación por palabras clave y categorías oficiales."""
from src.infrastructure.adapters.output.gemini_adapter import GeminiAdapter, CATEGORIAS_VALIDAS


def test_clasifica_por_palabras_clave():
    assert GeminiAdapter._clasificar_local("el poste de luz está apagado") == "Alumbrado"
    assert GeminiAdapter._clasificar_local("acumulación de basura y ratas") == "Limpieza Pública"
    assert GeminiAdapter._clasificar_local("el parque no tiene riego") == "Parques y Jardines"


def test_sin_palabras_clave_se_asigna_vias_publicas():
    assert GeminiAdapter._clasificar_local("hay un hueco en la pista") == "Vías Públicas"


def test_normaliza_nombres_de_categoria_devueltos_por_la_ia():
    assert GeminiAdapter._normalizar_categoria("Alumbrado") == "Alumbrado"
    assert GeminiAdapter._normalizar_categoria("Categoría: Limpieza Pública") == "Limpieza Pública"
    assert GeminiAdapter._normalizar_categoria("Seguridad Ciudadana") is None


def test_ignora_probabilidades_de_categorias_inexistentes_o_no_numericas():
    leidas = GeminiAdapter._leer_probabilidades({"Alumbrado": "0.8", "Otra": 0.5, "Vías Públicas": "x"})
    assert leidas == {"Alumbrado": 0.8}
    assert set(leidas) <= set(CATEGORIAS_VALIDAS)
