import unittest
from decimal import Decimal

from presupuesto import (
    CodigoDuplicadoError,
    ElementoPresupuestario,
    GrupoPresupuestario,
    PartidaPresupuestaria,
)
from main import construir_presupuesto


class TestPartidaPresupuestaria(unittest.TestCase):
    def test_expone_codigo_y_descripcion(self):
        partida = PartidaPresupuestaria("TI-01", "Licenciamiento", Decimal("20000"))

        self.assertEqual(partida.codigo, "TI-01")
        self.assertEqual(partida.descripcion, "Licenciamiento")

    def test_valor_total_es_el_valor_asignado(self):
        partida = PartidaPresupuestaria("TI-01", "Licenciamiento", Decimal("20000"))

        self.assertEqual(partida.calcular_valor_total(), Decimal("20000"))

    def test_rechaza_codigo_vacio(self):
        with self.assertRaises(ValueError):
            PartidaPresupuestaria("  ", "Licenciamiento", Decimal("20000"))

    def test_rechaza_valor_negativo(self):
        with self.assertRaises(ValueError):
            PartidaPresupuestaria("TI-01", "Licenciamiento", Decimal("-1"))

    def test_muestra_su_estructura_con_sangria_por_nivel(self):
        partida = PartidaPresupuestaria("TI-01", "Licenciamiento", Decimal("20000"))

        self.assertEqual(partida.mostrar_estructura(), "- [TI-01] Licenciamiento: 20,000.00")
        self.assertEqual(partida.mostrar_estructura(2), "    - [TI-01] Licenciamiento: 20,000.00")


class TestGrupoPresupuestario(unittest.TestCase):
    def test_grupo_vacio_vale_cero(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")

        self.assertEqual(grupo.calcular_valor_total(), Decimal("0"))

    def test_suma_las_partidas_que_contiene(self):
        grupo = GrupoPresupuestario("TI-02", "Infraestructura")
        grupo.agregar(PartidaPresupuestaria("TI-02-01", "Servidores", Decimal("30000")))
        grupo.agregar(PartidaPresupuestaria("TI-02-02", "Almacenamiento", Decimal("15000")))

        self.assertEqual(grupo.calcular_valor_total(), Decimal("45000"))

    def test_suma_recursivamente_los_grupos_internos(self):
        ti = construir_presupuesto()

        self.assertEqual(ti.calcular_valor_total(), Decimal("90000"))

    def test_eliminar_actualiza_el_total(self):
        grupo = GrupoPresupuestario("TI-02", "Infraestructura")
        servidores = PartidaPresupuestaria("TI-02-01", "Servidores", Decimal("30000"))
        grupo.agregar(servidores)
        grupo.agregar(PartidaPresupuestaria("TI-02-02", "Almacenamiento", Decimal("15000")))

        grupo.eliminar(servidores)

        self.assertEqual(grupo.calcular_valor_total(), Decimal("15000"))
        self.assertEqual(len(grupo.elementos), 1)

    def test_rechaza_una_partida_con_codigo_repetido_en_el_mismo_grupo(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")
        grupo.agregar(PartidaPresupuestaria("TI-04", "Seguridad", Decimal("5000")))

        with self.assertRaises(CodigoDuplicadoError):
            grupo.agregar(PartidaPresupuestaria("TI-04", "Antivirus", Decimal("1000")))

        self.assertEqual(len(grupo.elementos), 1)
        self.assertEqual(grupo.calcular_valor_total(), Decimal("5000"))

    def test_rechaza_un_grupo_con_codigo_repetido_en_el_mismo_grupo(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")
        grupo.agregar(PartidaPresupuestaria("TI-04", "Seguridad", Decimal("5000")))

        with self.assertRaises(CodigoDuplicadoError):
            grupo.agregar(GrupoPresupuestario("TI-04", "Seguridad informática"))

    def test_compara_codigos_sin_distinguir_mayusculas_ni_espacios(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")
        grupo.agregar(PartidaPresupuestaria("TI-04", "Seguridad", Decimal("5000")))

        for codigo in ("ti-04", " TI-04 "):
            with self.subTest(codigo=codigo), self.assertRaises(CodigoDuplicadoError):
                grupo.agregar(PartidaPresupuestaria(codigo, "Seguridad", Decimal("1")))

    def test_el_error_indica_el_codigo_y_el_grupo(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")
        grupo.agregar(PartidaPresupuestaria("TI-04", "Seguridad", Decimal("5000")))

        with self.assertRaises(CodigoDuplicadoError) as contexto:
            grupo.agregar(PartidaPresupuestaria("TI-04", "Antivirus", Decimal("1000")))

        self.assertEqual(str(contexto.exception), "Ya existe un elemento con el código TI-04 en el grupo [TI] Tecnologías de la Información")

    def test_el_mismo_codigo_se_permite_en_grupos_distintos(self):
        ti = construir_presupuesto()
        infraestructura = ti.elementos[1]

        ti.agregar(PartidaPresupuestaria("TI-04", "Seguridad", Decimal("5000")))
        infraestructura.agregar(PartidaPresupuestaria("TI-04", "Seguridad física", Decimal("2000")))

        self.assertEqual(ti.calcular_valor_total(), Decimal("97000"))

    def test_el_error_de_codigo_duplicado_es_un_value_error(self):
        self.assertTrue(issubclass(CodigoDuplicadoError, ValueError))

    def test_no_puede_contener_a_uno_de_sus_ancestros(self):
        ti = construir_presupuesto()
        infraestructura = ti.elementos[1]

        with self.assertRaises(ValueError):
            infraestructura.agregar(ti)

        self.assertEqual(len(infraestructura.elementos), 3)

    def test_no_puede_contenerse_a_si_mismo(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")

        with self.assertRaises(ValueError):
            grupo.agregar(grupo)

    def test_elementos_no_permite_modificar_la_coleccion_interna(self):
        grupo = GrupoPresupuestario("TI", "Tecnologías de la Información")

        self.assertIsInstance(grupo.elementos, tuple)

    def test_muestra_la_estructura_jerarquica(self):
        ti = construir_presupuesto()

        esperado = "\n".join([
            "+ [TI] Tecnologías de la Información: 90,000.00",
            "  - [TI-01] Licenciamiento: 20,000.00",
            "  + [TI-02] Infraestructura: 55,000.00",
            "    - [TI-02-01] Servidores: 30,000.00",
            "    - [TI-02-02] Almacenamiento: 15,000.00",
            "    - [TI-02-03] Comunicaciones: 10,000.00",
            "  - [TI-03] Servicios: 15,000.00",
        ])
        self.assertEqual(ti.mostrar_estructura(), esperado)


class TestRecorridoYBusqueda(unittest.TestCase):
    def test_recorrer_devuelve_el_elemento_y_sus_descendientes_en_preorden(self):
        ti = construir_presupuesto()

        codigos = [elemento.codigo for elemento in ti.recorrer()]

        self.assertEqual(codigos, ["TI", "TI-01", "TI-02", "TI-02-01", "TI-02-02", "TI-02-03", "TI-03"])

    def test_una_partida_se_recorre_a_si_misma(self):
        partida = PartidaPresupuestaria("TI-01", "Licenciamiento", Decimal("20000"))

        self.assertEqual(list(partida.recorrer()), [partida])

    def test_buscar_encuentra_elementos_anidados_sin_distinguir_mayusculas(self):
        ti = construir_presupuesto()

        encontrados = ti.buscar(" ti-02-01 ")

        self.assertEqual([elemento.descripcion for elemento in encontrados], ["Servidores"])

    def test_buscar_devuelve_lista_vacia_si_no_existe(self):
        self.assertEqual(construir_presupuesto().buscar("XX-99"), [])


class TestTratamientoUniforme(unittest.TestCase):
    def test_partidas_y_grupos_se_usan_con_la_misma_abstraccion(self):
        ti = construir_presupuesto()
        infraestructura = ti.elementos[1]
        licenciamiento = ti.elementos[0]

        totales = {}
        for elemento in (ti, infraestructura, licenciamiento):
            self.assertIsInstance(elemento, ElementoPresupuestario)
            totales[elemento.codigo] = elemento.calcular_valor_total()

        self.assertEqual(totales, {
            "TI": Decimal("90000"),
            "TI-02": Decimal("55000"),
            "TI-01": Decimal("20000"),
        })

    def test_no_se_puede_instanciar_la_abstraccion(self):
        with self.assertRaises(TypeError):
            ElementoPresupuestario()


if __name__ == "__main__":
    unittest.main()
