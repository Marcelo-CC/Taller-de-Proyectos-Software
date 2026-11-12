"""OWASP A04: límite de reclamos por minuto en el endpoint público."""
from src.infrastructure.security.limitador import LimitadorDeSolicitudes, ip_del_cliente


class Reloj:
    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t


def test_permite_hasta_el_limite_y_rechaza_el_siguiente():
    lim = LimitadorDeSolicitudes(por_clave=20, total=120, reloj=Reloj())
    assert all(lim.permitir("1.1.1.1") for _ in range(20))
    assert lim.permitir("1.1.1.1") is False


def test_otra_ip_no_se_ve_afectada():
    lim = LimitadorDeSolicitudes(por_clave=2, total=120, reloj=Reloj())
    lim.permitir("1.1.1.1"); lim.permitir("1.1.1.1")
    assert lim.permitir("1.1.1.1") is False
    assert lim.permitir("2.2.2.2") is True


def test_la_ventana_se_libera_despues_de_un_minuto():
    reloj = Reloj()
    lim = LimitadorDeSolicitudes(por_clave=1, total=120, reloj=reloj)
    assert lim.permitir("1.1.1.1") is True
    assert lim.permitir("1.1.1.1") is False
    reloj.t = 60.0
    assert lim.permitir("1.1.1.1") is True


def test_limite_total_protege_ante_muchas_ips():
    lim = LimitadorDeSolicitudes(por_clave=20, total=3, reloj=Reloj())
    assert [lim.permitir(f"10.0.0.{i}") for i in range(4)] == [True, True, True, False]


def test_cero_desactiva_el_limite():
    lim = LimitadorDeSolicitudes(por_clave=0, total=0, reloj=Reloj())
    assert all(lim.permitir("1.1.1.1") for _ in range(500))


def test_uso_normal_del_script_de_carga_no_se_bloquea():
    # El script secuencial envía como máximo 1 reclamo cada 2 s: 30 en un minuto repartidos
    reloj = Reloj()
    lim = LimitadorDeSolicitudes(por_clave=20, total=120, reloj=reloj)
    resultados = []
    for i in range(30):
        reloj.t = i * 3.0  # 1 cada 3 s
        resultados.append(lim.permitir("ip-del-equipo"))
    assert all(resultados)


def test_ip_real_desde_x_forwarded_for():
    assert ip_del_cliente("190.43.10.5, 10.0.0.1", "10.0.0.1") == "190.43.10.5"
    assert ip_del_cliente("", "127.0.0.1") == "127.0.0.1"
