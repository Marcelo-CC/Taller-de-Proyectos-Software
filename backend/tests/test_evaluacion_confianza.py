"""Regla HITL: confianza = certeza × ambigüedad × claridad, umbral del 70 %."""
from src.domain.services import evaluacion_confianza as ec

TEXTO_CLARO = " ".join(["palabra"] * 30)  # 30 palabras: factor de claridad 1.0


def test_reclamo_claro_y_seguro_no_requiere_auditoria():
    confianza = ec.evaluar({"Alumbrado": 0.95, "Vías Públicas": 0.05}, "Alumbrado", 1, TEXTO_CLARO)
    assert confianza == 0.95
    assert ec.requiere_auditoria(confianza) is False


def test_reclamo_con_dos_problemas_baja_la_confianza():
    confianza = ec.evaluar({"Alumbrado": 0.9, "Limpieza Pública": 0.1}, "Alumbrado", 2, TEXTO_CLARO)
    assert confianza == 0.72  # 0.9 × 0.80


def test_texto_corto_se_retiene_para_revision_humana():
    confianza = ec.evaluar({"Alumbrado": 1.0}, "Alumbrado", 1, "poste apagado")
    assert confianza == 0.6  # menos de 8 palabras: factor 0.60
    assert ec.requiere_auditoria(confianza) is True


def test_sin_ia_la_confianza_nunca_supera_el_tope_local():
    confianza = ec.evaluar({"Alumbrado": 1.0}, "Alumbrado", 1, TEXTO_CLARO, clasificado_por_ia=False)
    assert confianza == ec.TOPE_CLASIFICACION_LOCAL
    assert ec.requiere_auditoria(confianza) is True


def test_sin_probabilidades_validas_se_asume_certeza_media():
    assert ec.evaluar({}, "Alumbrado", 1, TEXTO_CLARO) == ec.CERTEZA_SIN_SENAL


def test_umbral_exacto_de_70_por_ciento_no_se_retiene():
    assert ec.requiere_auditoria(0.70) is False
    assert ec.requiere_auditoria(0.6999) is True
