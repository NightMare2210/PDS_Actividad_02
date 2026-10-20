from collections.abc import Iterator
from decimal import Decimal

from presupuesto.codigo_duplicado_error import CodigoDuplicadoError
from presupuesto.elemento_presupuestario import ElementoPresupuestario


class GrupoPresupuestario(ElementoPresupuestario):
    """Composite: agrupa partidas u otros grupos y delega en ellos sus operaciones."""

    def __init__(self, codigo: str, descripcion: str) -> None:
        super().__init__(codigo, descripcion)
        self._elementos: list[ElementoPresupuestario] = []

    @property
    def elementos(self) -> tuple[ElementoPresupuestario, ...]:
        return tuple(self._elementos)

    def agregar(self, elemento: ElementoPresupuestario) -> None:
        if any(descendiente is self for descendiente in elemento.recorrer()):
            raise ValueError("Un grupo no puede contenerse a sí mismo ni a uno de sus ancestros")
        if any(hijo.coincide_codigo(elemento.codigo) for hijo in self._elementos):
            raise CodigoDuplicadoError(elemento.codigo.strip(), self.codigo, self.descripcion)
        self._elementos.append(elemento)

    def eliminar(self, elemento: ElementoPresupuestario) -> None:
        self._elementos.remove(elemento)

    def calcular_valor_total(self) -> Decimal:
        return sum((elemento.calcular_valor_total() for elemento in self._elementos), Decimal("0"))

    def recorrer(self) -> Iterator[ElementoPresupuestario]:
        yield self
        for elemento in self._elementos:
            yield from elemento.recorrer()

    def mostrar_estructura(self, nivel: int = 0) -> str:
        hijos = (elemento.mostrar_estructura(nivel + 1) for elemento in self._elementos)
        return "\n".join([self._linea("+", nivel), *hijos])
