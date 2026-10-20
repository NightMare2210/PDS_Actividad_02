import tkinter as tk

from interfaz import VentanaPresupuesto


def main() -> None:
    raiz = tk.Tk()
    raiz.title("Presupuesto institucional — Composite")
    raiz.minsize(960, 760)
    ventana = VentanaPresupuesto(raiz)
    ventana.cargar_ejemplo()
    ventana.pack(fill="both", expand=True)
    raiz.mainloop()


if __name__ == "__main__":
    main()
