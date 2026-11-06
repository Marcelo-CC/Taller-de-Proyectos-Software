"""Evaluación de confianza de la clasificación de la IA (Human-in-the-Loop, HITL).

La confianza es un número entre 0.0 y 1.0 que combina tres señales:

    confianza = certeza_llm × factor_ambigüedad × factor_claridad

  c) certeza_llm        Probabilidad (normalizada) que el modelo asignó a la categoría elegida.
                        Si el modelo reparte la probabilidad entre varias categorías, baja.
  a) factor_ambigüedad  Penaliza descripciones que mezclan varias problemáticas distintas.
  b) factor_claridad    Penaliza descripciones demasiado cortas para clasificar con certeza.

Regla de enrutamiento (umbral crítico = 70 %):
  - confianza >= 0.70 → enrutamiento directo a la gerencia de la categoría.
  - confianza <  0.70 → queda retenido como "Pendiente de auditoría HITL" hasta que un operador
                        confirme o corrija la categoría.
"""

UMBRAL_CONFIANZA = 0.70

# Sin la IA (clasificación local por palabras clave) la confianza nunca supera este tope:
# todo reclamo clasificado sin Gemini pasa por revisión humana.
TOPE_CLASIFICACION_LOCAL = 0.50

# Si el modelo no devolvió probabilidades válidas, no hay evidencia de certeza: se asume 50 %.
CERTEZA_SIN_SENAL = 0.50


def _certeza(probabilidades: dict, categoria: str) -> float:
    total = sum(max(float(p), 0.0) for p in (probabilidades or {}).values())
    if total <= 0:
        return CERTEZA_SIN_SENAL
    return max(float(probabilidades.get(categoria, 0.0)), 0.0) / total


def _factor_ambiguedad(problematicas: int) -> float:
    n = max(1, int(problematicas or 1))
    if n == 1:
        return 1.0
    if n == 2:
        return 0.80
    return 0.60


def _factor_claridad(texto: str) -> float:
    palabras = len((texto or "").split())
    if palabras < 8:
        return 0.60
    if palabras < 15:
        return 0.80
    if palabras < 25:
        return 0.90
    return 1.0


def evaluar(probabilidades: dict, categoria: str, problematicas: int, texto: str,
            clasificado_por_ia: bool = True) -> float:
    """Devuelve la confianza (0.0–1.0, 4 decimales) de haber asignado `categoria` al reclamo."""
    confianza = _certeza(probabilidades, categoria) * _factor_ambiguedad(problematicas) * _factor_claridad(texto)
    if not clasificado_por_ia:
        confianza = min(confianza, TOPE_CLASIFICACION_LOCAL)
    return round(min(max(confianza, 0.0), 1.0), 4)


def requiere_auditoria(confianza: float) -> bool:
    """True si el reclamo debe retenerse para revisión humana antes de derivarse."""
    return confianza < UMBRAL_CONFIANZA
