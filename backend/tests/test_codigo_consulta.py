"""Código secreto del Módulo C: formato, alfabeto sin caracteres confusos y hash compatible con SQL."""
import hashlib
import re

from src.domain.valueObjects import codigo_consulta as cc


def test_formato_xxxx_xxxx_con_alfabeto_seguro():
    for _ in range(200):
        codigo = cc.generar()
        assert re.fullmatch(r"[23456789ABCDEFGHJKMNPQRSTVWXYZ]{4}-[23456789ABCDEFGHJKMNPQRSTVWXYZ]{4}", codigo)


def test_los_codigos_no_se_repiten():
    assert len({cc.generar() for _ in range(500)}) == 500


def test_hash_ignora_guion_espacios_y_minusculas():
    assert cc.hashear("ab2c-d3ef") == cc.hashear(" AB2CD3EF ")


def test_hash_es_sha256_del_codigo_normalizado():
    # Debe coincidir con encode(sha256(convert_to(upper(...)))) de la función SQL consultar_reclamo
    assert cc.hashear("AB2C-D3EF") == hashlib.sha256(b"AB2CD3EF").hexdigest()
