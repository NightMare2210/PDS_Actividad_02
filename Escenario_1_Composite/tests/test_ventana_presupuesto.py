import tkinter as tk
import unittest
from decimal import Decimal

from interfaz import VentanaPresupuesto
from presupuesto import GrupoPresupuestario, PartidaPresupuestaria


class TestVentanaPresupuesto(unittest.TestCase):
    def setUp(self):
        try:
            self.raiz = tk.Tk()
        except tk.TclError:
            self.skipTest("No hay entorno gráfico disponible")
        self.raiz.withdraw()
        self.errores: list[str] = []
        self.ventana = VentanaPresupuesto(self.raiz, notificar_error=lambda _titulo, mensaje: self.errores.append(mensaje))

    def tearDown(self):
        self.raiz.destroy()

    def completar(self, codigo: str, descripcion: str, valor: str = "") -> None:
        self.ventana.codigo.set(codigo)
        self.ventana.descripcion.set(descripcion)
        self.ventana.valor.set(valor)

    def ti(self) -> GrupoPresupuestario:
        return self.ventana.presupuesto.elementos[0]

    def test_inicia_con_un_presupuesto_vacio(self):
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("0"))

    def test_sin_seleccion_agrega_la_partida_a_la_raiz(self):
        self.completar("TI-01", "Licenciamiento", "20000")

        self.ventana.agregar_partida()

        self.assertEqual(self.errores, [])
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("20000"))

    def test_agrega_elementos_dentro_del_grupo_seleccionado(self):
        self.completar("TI-02", "Infraestructura")
        self.ventana.agregar_grupo()
        infraestructura = self.ventana.presupuesto.elementos[0]

        self.ventana.seleccionar(infraestructura)
        self.completar("TI-02-01", "Servidores", "30000")
        self.ventana.agregar_partida()

        self.assertEqual(infraestructura.calcular_valor_total(), Decimal("30000"))
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("30000"))

    def test_limpia_los_campos_despues_de_agregar(self):
        self.completar("TI-01", "Licenciamiento", "20000")

        self.ventana.agregar_partida()

        self.assertEqual((self.ventana.codigo.get(), self.ventana.descripcion.get(), self.ventana.valor.get()), ("", "", ""))

    def test_no_permite_agregar_dentro_de_una_partida(self):
        self.completar("TI-01", "Licenciamiento", "20000")
        self.ventana.agregar_partida()
        self.ventana.seleccionar(self.ventana.presupuesto.elementos[0])

        self.completar("TI-01-01", "Office", "500")
        self.ventana.agregar_partida()

        self.assertEqual(len(self.errores), 1)
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("20000"))

    def test_rechaza_un_valor_que_no_es_numero(self):
        for valor in ("abc", "", "NaN"):
            with self.subTest(valor=valor):
                self.completar("TI-01", "Licenciamiento", valor)
                self.ventana.agregar_partida()

        self.assertEqual(len(self.errores), 3)
        self.assertEqual(self.ventana.presupuesto.elementos, ())

    def test_informa_los_errores_del_dominio(self):
        self.completar("  ", "Sin código", "100")

        self.ventana.agregar_partida()

        self.assertEqual(self.errores, ["El código es obligatorio"])

    def test_no_permite_asignar_valor_a_un_grupo(self):
        self.completar("TI-04", "Seguridad", "5000")

        self.ventana.agregar_grupo()

        self.assertEqual(len(self.errores), 1)
        self.assertEqual(self.ventana.presupuesto.elementos, ())

    def test_muestra_donde_se_agregara_el_elemento(self):
        self.ventana.cargar_ejemplo()
        self.assertEqual(self.ventana.destino_mostrado, "Se agregará en: [PRES] Presupuesto institucional")

        self.ventana.seleccionar(self.ti().elementos[1])

        self.assertEqual(self.ventana.destino_mostrado, "Se agregará en: [TI-02] Infraestructura")

    def test_avisa_cuando_la_seleccion_es_una_partida(self):
        self.ventana.cargar_ejemplo()

        self.ventana.seleccionar(self.ti().elementos[0])

        self.assertEqual(self.ventana.destino_mostrado, "Seleccioná un grupo: una partida no puede contener elementos")

    def test_quitar_seleccion_vuelve_a_agregar_en_la_raiz(self):
        self.ventana.cargar_ejemplo()
        self.ventana.seleccionar(self.ti().elementos[1])

        self.ventana.quitar_seleccion()
        self.completar("TH", "Talento Humano")
        self.ventana.agregar_grupo()

        self.assertEqual(self.ventana.presupuesto.elementos[-1].codigo, "TH")

    def test_permite_agregar_grupos_al_mismo_nivel_que_ti(self):
        self.ventana.cargar_ejemplo()
        self.completar("TH", "Talento Humano")
        self.ventana.agregar_grupo()
        talento_humano = self.ventana.presupuesto.elementos[1]

        self.ventana.seleccionar(talento_humano)
        self.completar("TH-01", "Capacitación", "8000")
        self.ventana.agregar_partida()

        self.assertEqual([elemento.codigo for elemento in self.ventana.presupuesto.elementos], ["TI", "TH"])
        self.assertEqual(self.ti().calcular_valor_total(), Decimal("90000"))
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("98000"))

    def test_informa_un_codigo_repetido_en_el_mismo_grupo(self):
        self.ventana.cargar_ejemplo()
        self.ventana.seleccionar(self.ti())

        self.completar("TI-01", "Licenciamiento duplicado", "100")
        self.ventana.agregar_partida()

        self.assertEqual(self.errores, ["Ya existe un elemento con el código TI-01 en el grupo [TI] Tecnologías de la Información"])
        self.assertEqual(self.ti().calcular_valor_total(), Decimal("90000"))

    def test_sin_seleccion_ubica_el_elemento_segun_el_prefijo_del_codigo(self):
        self.ventana.cargar_ejemplo()
        self.ventana.quitar_seleccion()

        self.completar("TI-05", "Soporte", "4000")
        self.ventana.agregar_partida()

        self.assertEqual(self.ti().elementos[-1].codigo, "TI-05")
        self.assertEqual(self.ti().calcular_valor_total(), Decimal("94000"))

    def test_el_destino_se_actualiza_mientras_se_escribe_el_codigo(self):
        self.ventana.cargar_ejemplo()
        self.ventana.quitar_seleccion()

        self.ventana.codigo.set("TI-02-09")

        self.assertEqual(self.ventana.destino_mostrado, "Se agregará en: [TI-02] Infraestructura")

    def test_el_prefijo_existente_tiene_prioridad_sobre_la_seleccion(self):
        self.ventana.cargar_ejemplo()
        self.ventana.seleccionar(self.ti().elementos[1])

        self.completar("TI-05", "Soporte", "4000")
        self.ventana.agregar_partida()

        self.assertEqual(self.ti().elementos[-1].codigo, "TI-05")

    def test_sin_prefijo_existente_usa_el_grupo_seleccionado(self):
        self.ventana.cargar_ejemplo()
        infraestructura = self.ti().elementos[1]
        self.ventana.seleccionar(infraestructura)

        self.completar("RED", "Cableado", "700")
        self.ventana.agregar_partida()

        self.assertEqual(infraestructura.elementos[-1].codigo, "RED")

    def test_con_una_partida_seleccionada_igual_ubica_por_prefijo(self):
        self.ventana.cargar_ejemplo()
        self.ventana.seleccionar(self.ti().elementos[0])

        self.completar("TI-05", "Soporte", "4000")
        self.ventana.agregar_partida()

        self.assertEqual(self.errores, [])
        self.assertEqual(self.ti().elementos[-1].codigo, "TI-05")

    def test_despues_de_crear_un_grupo_sus_partidas_van_dentro_por_prefijo(self):
        self.completar("PR", "Proyectos")
        self.ventana.agregar_grupo()

        self.completar("PR-01", "Obra", "100")
        self.ventana.agregar_partida()

        proyectos = self.ventana.presupuesto.elementos[0]
        self.assertEqual([elemento.codigo for elemento in proyectos.elementos], ["PR-01"])

    def test_crear_un_grupo_reubica_las_partidas_existentes_con_su_prefijo(self):
        self.completar("PR-01", "Obra", "100")
        self.ventana.agregar_partida()
        self.completar("PR-02", "Diseño", "50")
        self.ventana.agregar_partida()

        self.completar("PR", "Proyectos")
        self.ventana.agregar_grupo()

        proyectos = self.ventana.presupuesto.elementos[0]
        self.assertEqual([elemento.codigo for elemento in proyectos.elementos], ["PR-01", "PR-02"])
        self.assertEqual(len(self.ventana.presupuesto.elementos), 1)

    def test_crear_un_grupo_absorbe_la_partida_con_su_mismo_codigo(self):
        self.completar("PR", "Proyecto piloto", "500")
        self.ventana.agregar_partida()
        self.ventana.quitar_seleccion()

        self.completar("PR", "Proyectos")
        self.ventana.agregar_grupo()

        self.assertEqual(self.errores, [])
        proyectos = self.ventana.presupuesto.elementos[0]
        self.assertIsInstance(proyectos, GrupoPresupuestario)
        self.assertEqual([elemento.codigo for elemento in proyectos.elementos], ["PR-01"])
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("500"))

    def test_mueve_una_partida_a_otro_grupo(self):
        self.ventana.cargar_ejemplo()
        servicios = self.ti().elementos[2]
        infraestructura = self.ti().elementos[1]

        self.ventana.seleccionar(servicios)
        self.ventana.elegir_grupo_destino(infraestructura)
        self.ventana.mover_seleccionado()

        self.assertEqual(self.errores, [])
        self.assertIn(servicios, infraestructura.elementos)
        self.assertNotIn(servicios, self.ti().elementos)
        self.assertEqual(infraestructura.calcular_valor_total(), Decimal("70000"))
        self.assertEqual(self.ti().calcular_valor_total(), Decimal("90000"))

    def test_al_seleccionar_propone_el_grupo_actual(self):
        self.ventana.cargar_ejemplo()

        self.ventana.seleccionar(self.ti().elementos[1].elementos[0])

        self.assertEqual(self.ventana.grupo_destino_mostrado, "[TI-02] Infraestructura")

    def test_no_permite_mover_un_grupo_dentro_de_su_descendiente(self):
        self.ventana.cargar_ejemplo()
        infraestructura = self.ti().elementos[1]

        self.ventana.seleccionar(self.ti())
        self.ventana.elegir_grupo_destino(infraestructura)
        self.ventana.mover_seleccionado()

        self.assertEqual(len(self.errores), 1)
        self.assertIn(self.ti(), self.ventana.presupuesto.elementos)

    def test_no_mueve_si_el_destino_tiene_el_mismo_codigo(self):
        self.ventana.cargar_ejemplo()
        infraestructura = self.ti().elementos[1]
        infraestructura.agregar(PartidaPresupuestaria("TI-03", "Servicios de red", Decimal("1")))
        servicios = self.ti().elementos[2]

        self.ventana.seleccionar(servicios)
        self.ventana.elegir_grupo_destino(infraestructura)
        self.ventana.mover_seleccionado()

        self.assertEqual(len(self.errores), 1)
        self.assertIn(servicios, self.ti().elementos)

    def test_no_permite_mover_la_raiz(self):
        self.ventana.cargar_ejemplo()
        self.ventana.seleccionar(self.ventana.presupuesto)
        self.ventana.elegir_grupo_destino(self.ti())

        self.ventana.mover_seleccionado()

        self.assertEqual(len(self.errores), 1)

    def test_elimina_el_elemento_seleccionado(self):
        self.completar("TI-01", "Licenciamiento", "20000")
        self.ventana.agregar_partida()
        self.completar("TI-03", "Servicios", "15000")
        self.ventana.agregar_partida()

        self.ventana.seleccionar(self.ventana.presupuesto.elementos[0])
        self.ventana.eliminar_seleccionado()

        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("15000"))

    def test_no_permite_eliminar_la_raiz(self):
        self.ventana.seleccionar(self.ventana.presupuesto)

        self.ventana.eliminar_seleccionado()

        self.assertEqual(len(self.errores), 1)

    def test_cargar_ejemplo_pone_ti_dentro_del_presupuesto_institucional(self):
        self.ventana.cargar_ejemplo()

        self.assertEqual(self.ventana.presupuesto.codigo, "PRES")
        self.assertEqual(self.ti().codigo, "TI")
        self.assertEqual(self.ventana.presupuesto.calcular_valor_total(), Decimal("90000"))

    def test_limpiar_reinicia_el_presupuesto(self):
        self.ventana.cargar_ejemplo()

        self.ventana.limpiar()

        self.assertIsInstance(self.ventana.presupuesto, GrupoPresupuestario)
        self.assertEqual(self.ventana.presupuesto.elementos, ())

    def test_muestra_la_estructura_del_presupuesto(self):
        self.ventana.cargar_ejemplo()

        self.assertEqual(self.ventana.estructura_mostrada, self.ventana.presupuesto.mostrar_estructura())
        self.assertEqual(self.ventana.total_mostrado, "Total: 90,000.00")


if __name__ == "__main__":
    unittest.main()
