from decimal import Decimal

from presupuesto import ElementoPresupuestario, GrupoPresupuestario, PartidaPresupuestaria


def construir_presupuesto() -> GrupoPresupuestario:
    servidores = PartidaPresupuestaria("TI-02-01", "Servidores", Decimal("30000"))
    almacenamiento = PartidaPresupuestaria("TI-02-02", "Almacenamiento", Decimal("15000"))
    comunicaciones = PartidaPresupuestaria("TI-02-03", "Comunicaciones", Decimal("10000"))
    infraestructura = GrupoPresupuestario("TI-02", "Infraestructura")
    for partida in (servidores, almacenamiento, comunicaciones):
        infraestructura.agregar(partida)

    licenciamiento = PartidaPresupuestaria("TI-01", "Licenciamiento", Decimal("20000"))
    servicios = PartidaPresupuestaria("TI-03", "Servicios", Decimal("15000"))
    ti = GrupoPresupuestario("TI", "Tecnologías de la Información")
    for elemento in (licenciamiento, infraestructura, servicios):
        ti.agregar(elemento)
    return ti


def resumir(elemento: ElementoPresupuestario) -> str:
    return f"{elemento.codigo} | {elemento.descripcion} | total: {elemento.calcular_valor_total():,.2f}"


def main() -> None:
    ti = construir_presupuesto()
    print("=== Estructura del presupuesto ===")
    print(ti.mostrar_estructura())
    print("\n=== Consulta uniforme ===")
    for elemento in (ti, *ti.elementos):
        print(resumir(elemento))


if __name__ == "__main__":
    main()
