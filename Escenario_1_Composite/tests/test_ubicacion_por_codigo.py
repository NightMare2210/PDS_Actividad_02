import unittest
from decimal import Decimal

from main import construir_presupuesto
from presupuesto import (
    CodigoDuplicadoError,
    GrupoPresupuestario,
    PartidaPresupuestaria,
    agregar_grupo_por_codigo,
    buscar_grupo_por_prefijo,
    siguiente_codigo,
)


def presupuesto_institucional() -> GrupoPresupuestario:
    raiz = GrupoPresupuestario("PRES", "Presupuesto institucional")
    raiz.agregar(construir_presupuesto())
    return raiz


class TestBuscarGrupoPorPrefijo(unittest.TestCase):
    def setUp(self):
        self.raiz = presupuesto_institucional()

    def test_usa_el_prefijo_antes_del_ultimo_guion(self):
        casos = {"TI-05": "TI", "TI-02-04": "TI-02", "ti-02-04": "TI-02"}
        for codigo, esperado in casos.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(buscar_grupo_por_prefijo(self.raiz, codigo).codigo, esperado)

    def test_sin_guion_no_encuentra_grupo(self):
        self.assertIsNone(buscar_grupo_por_prefijo(self.raiz, "TH"))

    def test_prefijo_inexistente_no_encuentra_grupo(self):
        self.assertIsNone(buscar_grupo_por_prefijo(self.raiz, "XX-01"))

    def test_rechaza_un_prefijo_que_es_una_partida(self):
        with self.assertRaises(ValueError) as contexto:
            buscar_grupo_por_prefijo(self.raiz, "TI-01-01")

        self.assertEqual(str(contexto.exception), "TI-01 es una partida: no puede contener elementos")

    def test_rechaza_un_prefijo_ambiguo(self):
        ti = self.raiz.elementos[0]
        ti.agregar(GrupoPresupuestario("TI-04", "Seguridad"))
        ti.elementos[1].agregar(GrupoPresupuestario("TI-04", "Seguridad física"))

        with self.assertRaises(ValueError):
            buscar_grupo_por_prefijo(self.raiz, "TI-04-01")

    def test_un_prefijo_que_coincide_con_partida_y_grupo_usa_el_grupo(self):
        ti = self.raiz.elementos[0]
        ti.elementos[1].agregar(PartidaPresupuestaria("TI-04", "Seguridad física", Decimal("1")))
        ti.agregar(GrupoPresupuestario("TI-04", "Seguridad"))

        self.assertEqual(buscar_grupo_por_prefijo(self.raiz, "TI-04-01").descripcion, "Seguridad")


class TestSiguienteCodigo(unittest.TestCase):
    def test_grupo_vacio_empieza_en_01(self):
        self.assertEqual(siguiente_codigo(GrupoPresupuestario("PR", "Proyectos")), "PR-01")

    def test_continua_despues_del_mayor_numero(self):
        grupo = GrupoPresupuestario("PR", "Proyectos")
        grupo.agregar(PartidaPresupuestaria("PR-01", "Obra", Decimal("1")))
        grupo.agregar(PartidaPresupuestaria("PR-03", "Diseño", Decimal("1")))
        grupo.agregar(PartidaPresupuestaria("OTRO", "Sin numeración", Decimal("1")))

        self.assertEqual(siguiente_codigo(grupo), "PR-04")


class TestAgregarGrupoPorCodigo(unittest.TestCase):
    def setUp(self):
        self.raiz = GrupoPresupuestario("PRES", "Presupuesto institucional")

    def test_absorbe_la_partida_con_el_mismo_codigo_y_la_numera(self):
        self.raiz.agregar(PartidaPresupuestaria("PR", "Proyecto piloto", Decimal("500")))
        proyectos = GrupoPresupuestario("PR", "Proyectos")

        agregar_grupo_por_codigo(self.raiz, self.raiz, proyectos)

        self.assertEqual(self.raiz.elementos, (proyectos,))
        absorbida = proyectos.elementos[0]
        self.assertIsInstance(absorbida, PartidaPresupuestaria)
        self.assertEqual((absorbida.codigo, absorbida.descripcion, absorbida.valor_asignado), ("PR-01", "Proyecto piloto", Decimal("500")))
        self.assertEqual(self.raiz.calcular_valor_total(), Decimal("500"))

    def test_sin_partida_homonima_solo_agrega_el_grupo(self):
        proyectos = GrupoPresupuestario("PR", "Proyectos")

        agregar_grupo_por_codigo(self.raiz, self.raiz, proyectos)

        self.assertEqual(self.raiz.elementos, (proyectos,))
        self.assertEqual(proyectos.elementos, ())

    def test_un_grupo_homonimo_sigue_siendo_codigo_duplicado(self):
        self.raiz.agregar(GrupoPresupuestario("PR", "Proyectos"))

        with self.assertRaises(CodigoDuplicadoError):
            agregar_grupo_por_codigo(self.raiz, self.raiz, GrupoPresupuestario("PR", "Otros proyectos"))


class TestReubicarHuerfanos(unittest.TestCase):
    def setUp(self):
        self.raiz = presupuesto_institucional()
        self.ti = self.raiz.elementos[0]

    def codigos(self, grupo: GrupoPresupuestario) -> list[str]:
        return [elemento.codigo for elemento in grupo.elementos]

    def test_mueve_las_partidas_existentes_con_su_prefijo(self):
        self.raiz.agregar(PartidaPresupuestaria("PR-01", "Obra", Decimal("100")))
        self.raiz.agregar(PartidaPresupuestaria("PR-02", "Diseño", Decimal("50")))
        proyectos = GrupoPresupuestario("PR", "Proyectos")

        agregar_grupo_por_codigo(self.raiz, self.raiz, proyectos)

        self.assertEqual(self.codigos(proyectos), ["PR-01", "PR-02"])
        self.assertEqual(self.codigos(self.raiz), ["TI", "PR"])
        self.assertEqual(self.raiz.calcular_valor_total(), Decimal("90150"))

    def test_funciona_con_cualquier_codigo_y_en_cualquier_nivel(self):
        self.raiz.agregar(PartidaPresupuestaria("TI-02-04", "Respaldo", Decimal("5")))
        self.ti.agregar(PartidaPresupuestaria("TH-01", "Capacitación", Decimal("8000")))
        talento_humano = GrupoPresupuestario("TH", "Talento Humano")

        agregar_grupo_por_codigo(self.raiz, self.raiz, talento_humano)

        self.assertEqual(self.codigos(talento_humano), ["TH-01"])
        self.assertNotIn("TH-01", self.codigos(self.ti))
        self.assertIn("TI-02-04", self.codigos(self.raiz))

    def test_mueve_un_grupo_huerfano_con_todos_sus_hijos(self):
        obras = GrupoPresupuestario("PR-01", "Obras")
        obras.agregar(PartidaPresupuestaria("PR-01-01", "Cimientos", Decimal("700")))
        self.raiz.agregar(obras)
        proyectos = GrupoPresupuestario("PR", "Proyectos")

        agregar_grupo_por_codigo(self.raiz, self.raiz, proyectos)

        self.assertEqual(proyectos.elementos, (obras,))
        self.assertEqual(proyectos.calcular_valor_total(), Decimal("700"))

    def test_no_le_quita_elementos_a_otro_grupo_con_el_mismo_codigo(self):
        seguridad = GrupoPresupuestario("TI-04", "Seguridad")
        seguridad.agregar(PartidaPresupuestaria("TI-04-01", "Antivirus", Decimal("300")))
        self.ti.agregar(seguridad)
        otra_seguridad = GrupoPresupuestario("TI-04", "Seguridad física")

        agregar_grupo_por_codigo(self.raiz, self.ti.elementos[1], otra_seguridad)

        self.assertEqual(self.codigos(seguridad), ["TI-04-01"])
        self.assertEqual(otra_seguridad.elementos, ())

    def test_numera_la_partida_absorbida_despues_de_los_huerfanos(self):
        self.raiz.agregar(PartidaPresupuestaria("PR", "Proyecto piloto", Decimal("500")))
        self.raiz.agregar(PartidaPresupuestaria("PR-01", "Obra", Decimal("100")))
        proyectos = GrupoPresupuestario("PR", "Proyectos")

        agregar_grupo_por_codigo(self.raiz, self.raiz, proyectos)

        self.assertEqual(self.codigos(proyectos), ["PR-01", "PR-02"])
        self.assertEqual(proyectos.elementos[1].descripcion, "Proyecto piloto")

    def test_un_huerfano_con_codigo_repetido_se_queda_donde_esta(self):
        self.raiz.agregar(PartidaPresupuestaria("PR-01", "Obra", Decimal("100")))
        self.ti.agregar(PartidaPresupuestaria("PR-01", "Obra TI", Decimal("40")))
        proyectos = GrupoPresupuestario("PR", "Proyectos")

        agregar_grupo_por_codigo(self.raiz, self.raiz, proyectos)

        self.assertEqual(self.codigos(proyectos), ["PR-01"])
        self.assertIn("PR-01", self.codigos(self.ti))
        self.assertEqual(self.raiz.calcular_valor_total(), Decimal("90140"))


if __name__ == "__main__":
    unittest.main()
