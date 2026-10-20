from abc import ABC, abstractmethod
from collections.abc import Iterator
from decimal import Decimal


class ElementoPresupuestario(ABC):
    """Component: abstracción común para partidas y grupos presupuestarios."""

    _SANGRIA = "  "

    def __init__(self, codigo: str, descripcion: str) -> None:
        if not codigo.strip():
            raise ValueError("El código es obligatorio")
        self._codigo = codigo
        self._descripcion = descripcion

    @property
    def codigo(self) -> str:
        return self._codigo

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @abstractmethod
    def calcular_valor_total(self) -> Decimal: ...

    @abstractmethod
    def mostrar_estructura(self, nivel: int = 0) -> str: ...

    def recorrer(self) -> Iterator["ElementoPresupuestario"]:
        yield self

    def buscar(self, codigo: str) -> list["ElementoPresupuestario"]:
        return [elemento for elemento in self.recorrer() if elemento.coincide_codigo(codigo)]

    def coincide_codigo(self, codigo: str) -> bool:
        return self._codigo.strip().casefold() == codigo.strip().casefold()

    def _linea(self, simbolo: str, nivel: int) -> str:
        return f"{self._SANGRIA * nivel}{simbolo} [{self._codigo}] {self._descripcion}: {self.calcular_valor_total():,.2f}"
