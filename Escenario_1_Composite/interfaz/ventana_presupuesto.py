import tkinter as tk
from collections.abc import Callable
from decimal import Decimal, InvalidOperation
from tkinter import messagebox, ttk

from main import construir_presupuesto
from presupuesto import (
    ElementoPresupuestario,
    GrupoPresupuestario,
    PartidaPresupuestaria,
    agregar_grupo_por_codigo,
    buscar_grupo_por_prefijo,
)

Insertar = Callable[[GrupoPresupuestario, ElementoPresupuestario], None]

NotificarError = Callable[[str, str], object]


class VentanaPresupuesto(ttk.Frame):
    """Client gráfico: construye el presupuesto a mano y lo consulta mediante ElementoPresupuestario."""

    def __init__(self, master: tk.Misc, notificar_error: NotificarError = messagebox.showerror) -> None:
        super().__init__(master, padding=12)
        self._notificar_error = notificar_error
        self._presupuesto = self._presupuesto_vacio()
        self._elementos_por_item: dict[str, ElementoPresupuestario] = {}
        self._grupos: list[GrupoPresupuestario] = []
        self.codigo = tk.StringVar()
        self.descripcion = tk.StringVar()
        self.valor = tk.StringVar()
        self._total = tk.StringVar()
        self._destino = tk.StringVar()
        self._construir_formulario()
        self._construir_arbol()
        self._construir_panel_mover()
        self._construir_estructura()
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        self.codigo.trace_add("write", lambda *_: self._actualizar_destino())
        self.refrescar()

    @property
    def presupuesto(self) -> GrupoPresupuestario:
        return self._presupuesto

    @property
    def estructura_mostrada(self) -> str:
        return self._estructura.get("1.0", "end-1c")

    @property
    def total_mostrado(self) -> str:
        return self._total.get()

    @property
    def destino_mostrado(self) -> str:
        return self._destino.get()

    @property
    def grupo_destino_mostrado(self) -> str:
        return self._selector_grupo.get()

    def agregar_partida(self) -> None:
        self._agregar(lambda: PartidaPresupuestaria(self.codigo.get(), self.descripcion.get(), self._leer_valor()))

    def agregar_grupo(self) -> None:
        self._agregar(self._crear_grupo, insertar=lambda padre, grupo: agregar_grupo_por_codigo(self._presupuesto, padre, grupo))

    def eliminar_seleccionado(self) -> None:
        try:
            elemento, grupo = self._elemento_y_grupo_seleccionados()
        except ValueError as error:
            self._notificar_error("No se pudo eliminar", str(error))
            return
        grupo.eliminar(elemento)
        self.refrescar()
        self.seleccionar(grupo)

    def mover_seleccionado(self) -> None:
        try:
            elemento, origen = self._elemento_y_grupo_seleccionados()
            destino = self._grupo_elegido()
            if destino is not origen:
                destino.agregar(elemento)
                origen.eliminar(elemento)
        except ValueError as error:
            self._notificar_error("No se pudo cambiar de grupo", str(error))
            return
        self.refrescar()
        self.seleccionar(elemento)

    def elegir_grupo_destino(self, grupo: GrupoPresupuestario) -> None:
        indice = next(indice for indice, actual in enumerate(self._grupos) if actual is grupo)
        self._selector_grupo.current(indice)

    def cargar_ejemplo(self) -> None:
        self._presupuesto = self._presupuesto_vacio()
        self._presupuesto.agregar(construir_presupuesto())
        self.refrescar()

    def limpiar(self) -> None:
        self._presupuesto = self._presupuesto_vacio()
        self.refrescar()

    def seleccionar(self, elemento: ElementoPresupuestario) -> None:
        item = next(item for item, actual in self._elementos_por_item.items() if actual is elemento)
        self._arbol.selection_set(item)
        self._arbol.focus(item)
        self._al_cambiar_seleccion()

    def quitar_seleccion(self) -> None:
        self._arbol.selection_remove(*self._arbol.selection())
        self._al_cambiar_seleccion()

    def refrescar(self) -> None:
        self._arbol.delete(*self._arbol.get_children())
        self._elementos_por_item.clear()
        self._insertar_en_arbol("", self._presupuesto)
        self._grupos = [elemento for elemento in self._presupuesto.recorrer() if isinstance(elemento, GrupoPresupuestario)]
        self._selector_grupo.configure(values=[self._rotulo(grupo) for grupo in self._grupos])
        self._estructura.configure(state="normal")
        self._estructura.delete("1.0", "end")
        self._estructura.insert("1.0", self._presupuesto.mostrar_estructura())
        self._estructura.configure(state="disabled")
        self._total.set(f"Total: {self._presupuesto.calcular_valor_total():,.2f}")
        self._al_cambiar_seleccion()

    def _crear_grupo(self) -> GrupoPresupuestario:
        if self.valor.get().strip():
            raise ValueError("Un grupo no tiene valor asignado: su total es la suma de sus elementos")
        return GrupoPresupuestario(self.codigo.get(), self.descripcion.get())

    def _al_cambiar_seleccion(self) -> None:
        self._actualizar_destino()
        seleccion = self._arbol.selection()
        item_padre = self._arbol.parent(seleccion[0]) if seleccion else ""
        if item_padre:
            self.elegir_grupo_destino(self._elementos_por_item[item_padre])
        else:
            self._selector_grupo.set("")

    def _actualizar_destino(self) -> None:
        try:
            grupo = self._grupo_para_agregar()
        except ValueError as error:
            self._destino.set(str(error))
            return
        self._destino.set(f"Se agregará en: {self._rotulo(grupo)}")

    def _quitar_seleccion_si_clic_vacio(self, evento: tk.Event) -> None:
        if not self._arbol.identify_row(evento.y):
            self.quitar_seleccion()

    def _agregar(self, crear_elemento: Callable[[], ElementoPresupuestario], insertar: Insertar = GrupoPresupuestario.agregar) -> None:
        try:
            grupo = self._grupo_para_agregar()
            insertar(grupo, crear_elemento())
        except ValueError as error:
            self._notificar_error("No se pudo agregar", str(error))
            return
        for campo in (self.codigo, self.descripcion, self.valor):
            campo.set("")
        self.refrescar()
        self.seleccionar(grupo)

    def _grupo_para_agregar(self) -> GrupoPresupuestario:
        return buscar_grupo_por_prefijo(self._presupuesto, self.codigo.get()) or self._grupo_seleccionado()

    def _grupo_seleccionado(self) -> GrupoPresupuestario:
        seleccion = self._arbol.selection()
        if not seleccion:
            return self._presupuesto
        elemento = self._elementos_por_item[seleccion[0]]
        if not isinstance(elemento, GrupoPresupuestario):
            raise ValueError("Seleccioná un grupo: una partida no puede contener elementos")
        return elemento

    def _elemento_y_grupo_seleccionados(self) -> tuple[ElementoPresupuestario, GrupoPresupuestario]:
        seleccion = self._arbol.selection()
        if not seleccion or self._elementos_por_item[seleccion[0]] is self._presupuesto:
            raise ValueError("Seleccioná un elemento distinto de la raíz")
        return self._elementos_por_item[seleccion[0]], self._elementos_por_item[self._arbol.parent(seleccion[0])]

    def _grupo_elegido(self) -> GrupoPresupuestario:
        indice = self._selector_grupo.current()
        if indice < 0:
            raise ValueError("Elegí el grupo al que querés moverlo")
        return self._grupos[indice]

    def _leer_valor(self) -> Decimal:
        try:
            valor = Decimal(self.valor.get().strip())
        except InvalidOperation:
            raise ValueError("El valor asignado debe ser un número") from None
        if not valor.is_finite():
            raise ValueError("El valor asignado debe ser un número")
        return valor

    def _insertar_en_arbol(self, item_padre: str, elemento: ElementoPresupuestario) -> None:
        es_grupo = isinstance(elemento, GrupoPresupuestario)
        valores = (elemento.descripcion, "Grupo" if es_grupo else "Partida", f"{elemento.calcular_valor_total():,.2f}")
        item = self._arbol.insert(item_padre, "end", text=elemento.codigo, values=valores, open=True)
        self._elementos_por_item[item] = elemento
        for hijo in elemento.elementos if es_grupo else ():
            self._insertar_en_arbol(item, hijo)

    @staticmethod
    def _rotulo(grupo: GrupoPresupuestario) -> str:
        return f"[{grupo.codigo}] {grupo.descripcion}"

    @staticmethod
    def _presupuesto_vacio() -> GrupoPresupuestario:
        return GrupoPresupuestario("PRES", "Presupuesto institucional")

    def _construir_formulario(self) -> None:
        formulario = ttk.LabelFrame(self, text="Nuevo elemento", padding=10)
        formulario.grid(row=0, column=0, rowspan=2, sticky="ns", padx=(0, 12))
        for fila, (etiqueta, variable) in enumerate(
            [("Código", self.codigo), ("Descripción", self.descripcion), ("Valor asignado", self.valor)]
        ):
            ttk.Label(formulario, text=etiqueta).grid(row=fila * 2, column=0, sticky="w")
            ttk.Entry(formulario, textvariable=variable, width=28).grid(row=fila * 2 + 1, column=0, pady=(0, 8))
        ayuda = "El valor solo aplica a partidas.\nSi el prefijo del código existe, va a ese\ngrupo (TI-05 → TI); si no, al seleccionado."
        ttk.Label(formulario, text=ayuda, foreground="gray").grid(row=6, column=0, sticky="w", pady=(0, 4))
        ttk.Label(formulario, textvariable=self._destino, wraplength=220, foreground="#4a90d9").grid(row=7, column=0, sticky="w", pady=(0, 8))
        acciones = [
            ("Agregar partida", self.agregar_partida),
            ("Agregar grupo", self.agregar_grupo),
            ("Quitar selección (Esc)", self.quitar_seleccion),
            ("Eliminar seleccionado", self.eliminar_seleccionado),
            ("Cargar ejemplo", self.cargar_ejemplo),
            ("Limpiar", self.limpiar),
        ]
        for fila, (texto, accion) in enumerate(acciones, start=8):
            ttk.Button(formulario, text=texto, command=accion).grid(row=fila, column=0, sticky="ew", pady=2)

    def _construir_arbol(self) -> None:
        self._arbol = ttk.Treeview(self, columns=("descripcion", "tipo", "total"), selectmode="browse")
        for columna, titulo, ancho in [("#0", "Código", 140), ("descripcion", "Descripción", 240), ("tipo", "Tipo", 80), ("total", "Valor total", 120)]:
            self._arbol.heading(columna, text=titulo)
            self._arbol.column(columna, width=ancho, anchor="e" if columna == "total" else "w")
        self._arbol.grid(row=0, column=1, sticky="nsew")
        self._arbol.bind("<<TreeviewSelect>>", lambda _evento: self._al_cambiar_seleccion())
        self._arbol.bind("<Button-1>", self._quitar_seleccion_si_clic_vacio, add="+")
        self.winfo_toplevel().bind("<Escape>", lambda _evento: self.quitar_seleccion())

    def _construir_panel_mover(self) -> None:
        panel = ttk.LabelFrame(self, text="Cambiar de grupo el elemento seleccionado", padding=8)
        panel.grid(row=1, column=1, sticky="ew", pady=(8, 0))
        self._selector_grupo = ttk.Combobox(panel, state="readonly", width=40)
        self._selector_grupo.pack(side="left", fill="x", expand=True, padx=(0, 8))
        ttk.Button(panel, text="Mover al grupo", command=self.mover_seleccionado).pack(side="left")

    def _construir_estructura(self) -> None:
        resumen = ttk.LabelFrame(self, text="mostrar_estructura()", padding=8)
        resumen.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=(12, 0))
        self._estructura = tk.Text(resumen, height=8, font=("Menlo", 11), state="disabled")
        self._estructura.pack(fill="both", expand=True)
        ttk.Label(resumen, textvariable=self._total, font=("TkDefaultFont", 12, "bold")).pack(anchor="e", pady=(6, 0))
