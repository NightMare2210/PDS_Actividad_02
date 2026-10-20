class CodigoDuplicadoError(ValueError):
    """Se lanza al agregar a un grupo un elemento cuyo código ya existe en ese mismo grupo."""

    def __init__(self, codigo: str, codigo_grupo: str, descripcion_grupo: str) -> None:
        super().__init__(f"Ya existe un elemento con el código {codigo} en el grupo [{codigo_grupo}] {descripcion_grupo}")
