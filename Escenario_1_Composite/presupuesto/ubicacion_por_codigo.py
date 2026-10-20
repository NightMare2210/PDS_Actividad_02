import re
from collections import deque
from collections.abc import Iterator

from presupuesto.elemento_presupuestario import ElementoPresupuestario
from presupuesto.grupo_presupuestario import GrupoPresupuestario
from presupuesto.partida_presupuestaria import PartidaPresupuestaria


def buscar_grupo_por_prefijo(raiz: GrupoPresupuestario, codigo: str) -> GrupoPresupuestario | None:
    """Busca el grupo cuyo código es el prefijo antes del último guion: 'TI-02-04' pertenece a 'TI-02'."""
    prefijo = _prefijo(codigo)
    if not prefijo:
        return None
    encontrados = raiz.buscar(prefijo)
    grupos = [elemento for elemento in encontrados if isinstance(elemento, GrupoPresupuestario)]
    if encontrados and not grupos:
        raise ValueError(f"{prefijo} es una partida: no puede contener elementos")
    if len(grupos) > 1:
        raise ValueError(f"Hay varios grupos con el código {prefijo}: seleccioná el grupo en el árbol")
    return grupos[0] if grupos else None


def siguiente_codigo(grupo: GrupoPresupuestario) -> str:
    """Devuelve el próximo código numerado libre del grupo: 'PR-01', 'PR-02', ..."""
    patron = re.compile(rf"{re.escape(grupo.codigo.strip())}-(\d+)", re.IGNORECASE)
    numeros = [int(coincidencia[1]) for elemento in grupo.elementos if (coincidencia := patron.fullmatch(elemento.codigo.strip()))]
    return f"{grupo.codigo.strip()}-{max(numeros, default=0) + 1:02d}"


def agregar_grupo_por_codigo(raiz: GrupoPresupuestario, padre: GrupoPresupuestario, grupo: GrupoPresupuestario) -> None:
    """Agrega el grupo, le mueve los elementos huérfanos de su prefijo y absorbe la partida homónima del padre."""
    homonima = next((elemento for elemento in padre.elementos if elemento.coincide_codigo(grupo.codigo)), None)
    if isinstance(homonima, PartidaPresupuestaria):
        padre.eliminar(homonima)
    padre.agregar(grupo)
    _reubicar_huerfanos(raiz, grupo)
    if isinstance(homonima, PartidaPresupuestaria):
        grupo.agregar(PartidaPresupuestaria(siguiente_codigo(grupo), homonima.descripcion, homonima.valor_asignado))


def _reubicar_huerfanos(raiz: GrupoPresupuestario, grupo: GrupoPresupuestario) -> None:
    for elemento, origen in list(_elementos_con_padre(raiz)):
        es_huerfano = grupo.coincide_codigo(_prefijo(elemento.codigo)) and not origen.coincide_codigo(grupo.codigo)
        if not es_huerfano:
            continue
        try:
            grupo.agregar(elemento)
        except ValueError:
            continue
        origen.eliminar(elemento)


def _elementos_con_padre(raiz: GrupoPresupuestario) -> Iterator[tuple[ElementoPresupuestario, GrupoPresupuestario]]:
    """Recorre por niveles (en anchura) para que, ante códigos repetidos, gane el huérfano más cercano a la raíz."""
    pendientes = deque([raiz])
    while pendientes:
        grupo = pendientes.popleft()
        for elemento in grupo.elementos:
            yield elemento, grupo
            if isinstance(elemento, GrupoPresupuestario):
                pendientes.append(elemento)


def _prefijo(codigo: str) -> str:
    return codigo.strip().rpartition("-")[0]
