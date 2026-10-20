from decimal import Decimal

from presupuesto.elemento_presupuestario import ElementoPresupuestario


class PartidaPresupuestaria(ElementoPresupuestario):
    """Leaf: elemento básico del presupuesto con un valor asignado."""

    def __init__(self, codigo: str, descripcion: str, valor_asignado: Decimal) -> None:
        if valor_asignado < 0:
            raise ValueError("El valor asignado no puede ser negativo")
        super().__init__(codigo, descripcion)
        self._valor_asignado = valor_asignado

    @property
    def valor_asignado(self) -> Decimal:
        return self._valor_asignado

    def calcular_valor_total(self) -> Decimal:
        return self._valor_asignado

    def mostrar_estructura(self, nivel: int = 0) -> str:
        return self._linea("-", nivel)
