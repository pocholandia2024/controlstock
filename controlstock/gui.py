"""Interfaz gráfica de ControlStock para macOS."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from controlstock.inventory import ErrorInventario, Inventario
from controlstock.models import Categoria


class AplicacionGUI:
    def __init__(self) -> None:
        self.inventario = Inventario()
        self.ventana = tk.Tk()
        self.ventana.title("ControlStock")
        self.ventana.geometry("980x620")
        self.ventana.minsize(860, 520)

        self._configurar_estilos()
        self._crear_interfaz()
        self.actualizar_vistas()

    def _configurar_estilos(self) -> None:
        estilo = ttk.Style()
        if "aqua" in estilo.theme_names():
            estilo.theme_use("aqua")
        elif "clam" in estilo.theme_names():
            estilo.theme_use("clam")

    def _crear_interfaz(self) -> None:
        encabezado = ttk.Frame(self.ventana, padding=12)
        encabezado.pack(fill="x")
        ttk.Label(
            encabezado,
            text="ControlStock",
            font=("", 18, "bold"),
        ).pack(side="left")
        self.lbl_db = ttk.Label(encabezado, foreground="gray")
        self.lbl_db.pack(side="right")
        self.lbl_db.config(text=f"Base de datos: {self.inventario.ruta_base_de_datos}")

        notebook = ttk.Notebook(self.ventana)
        notebook.pack(fill="both", expand=True, padx=12, pady=(0, 12))

        self.tab_resumen = ttk.Frame(notebook, padding=12)
        self.tab_productos = ttk.Frame(notebook, padding=12)
        self.tab_movimientos = ttk.Frame(notebook, padding=12)

        notebook.add(self.tab_resumen, text="Resumen")
        notebook.add(self.tab_productos, text="Productos")
        notebook.add(self.tab_movimientos, text="Movimientos")

        self._crear_tab_resumen()
        self._crear_tab_productos()
        self._crear_tab_movimientos()

    def _crear_tab_resumen(self) -> None:
        marco = ttk.LabelFrame(self.tab_resumen, text="Estado del inventario", padding=16)
        marco.pack(fill="x")

        self.lbl_total_productos = ttk.Label(marco, text="Productos registrados: —")
        self.lbl_unidades = ttk.Label(marco, text="Unidades en stock: —")
        self.lbl_valor = ttk.Label(marco, text="Valor del inventario: —")
        self.lbl_stock_bajo = ttk.Label(marco, text="Productos con stock bajo: —")

        for etiqueta in (
            self.lbl_total_productos,
            self.lbl_unidades,
            self.lbl_valor,
            self.lbl_stock_bajo,
        ):
            etiqueta.pack(anchor="w", pady=4)

        ttk.Button(
            self.tab_resumen,
            text="Actualizar resumen",
            command=self.actualizar_vistas,
        ).pack(anchor="w", pady=(12, 0))

        marco_alertas = ttk.LabelFrame(self.tab_resumen, text="Alertas de stock bajo", padding=8)
        marco_alertas.pack(fill="both", expand=True, pady=(16, 0))

        columnas = ("sku", "nombre", "stock", "minimo")
        self.tree_alertas = ttk.Treeview(
            marco_alertas, columns=columnas, show="headings", height=8
        )
        for col, titulo, ancho in (
            ("sku", "SKU", 120),
            ("nombre", "Nombre", 280),
            ("stock", "Stock", 80),
            ("minimo", "Mínimo", 80),
        ):
            self.tree_alertas.heading(col, text=titulo)
            self.tree_alertas.column(col, width=ancho, anchor="w")
        self.tree_alertas.pack(fill="both", expand=True)

    def _crear_tab_productos(self) -> None:
        barra = ttk.Frame(self.tab_productos)
        barra.pack(fill="x", pady=(0, 8))

        ttk.Label(barra, text="Buscar:").pack(side="left")
        self.var_busqueda = tk.StringVar()
        self.var_busqueda.trace_add("write", lambda *_: self.actualizar_productos())
        ttk.Entry(barra, textvariable=self.var_busqueda, width=30).pack(
            side="left", padx=(6, 12)
        )

        ttk.Button(barra, text="Agregar producto", command=self._dialogo_agregar).pack(
            side="left", padx=4
        )
        ttk.Button(barra, text="Eliminar seleccionado", command=self._eliminar_producto).pack(
            side="left", padx=4
        )
        ttk.Button(barra, text="Actualizar", command=self.actualizar_productos).pack(
            side="left", padx=4
        )

        columnas = ("sku", "nombre", "categoria", "marca", "precio", "stock", "minimo")
        self.tree_productos = ttk.Treeview(
            self.tab_productos, columns=columnas, show="headings"
        )
        for col, titulo, ancho in (
            ("sku", "SKU", 110),
            ("nombre", "Nombre", 220),
            ("categoria", "Categoría", 110),
            ("marca", "Marca", 100),
            ("precio", "Precio", 90),
            ("stock", "Stock", 70),
            ("minimo", "Mín.", 60),
        ):
            self.tree_productos.heading(col, text=titulo)
            self.tree_productos.column(col, width=ancho, anchor="w")

        scroll = ttk.Scrollbar(
            self.tab_productos, orient="vertical", command=self.tree_productos.yview
        )
        self.tree_productos.configure(yscrollcommand=scroll.set)
        self.tree_productos.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        self.tree_productos.tag_configure("bajo", foreground="#c0392b")

    def _crear_tab_movimientos(self) -> None:
        marco_form = ttk.LabelFrame(self.tab_movimientos, text="Registrar movimiento", padding=12)
        marco_form.pack(fill="x")

        ttk.Label(marco_form, text="SKU").grid(row=0, column=0, sticky="w", padx=4, pady=4)
        self.var_sku_mov = tk.StringVar()
        ttk.Entry(marco_form, textvariable=self.var_sku_mov, width=18).grid(
            row=0, column=1, sticky="w", padx=4, pady=4
        )

        ttk.Label(marco_form, text="Cantidad").grid(row=0, column=2, sticky="w", padx=4, pady=4)
        self.var_cantidad_mov = tk.StringVar(value="1")
        ttk.Entry(marco_form, textvariable=self.var_cantidad_mov, width=10).grid(
            row=0, column=3, sticky="w", padx=4, pady=4
        )

        ttk.Label(marco_form, text="Motivo").grid(row=1, column=0, sticky="w", padx=4, pady=4)
        self.var_motivo_mov = tk.StringVar()
        ttk.Entry(marco_form, textvariable=self.var_motivo_mov, width=50).grid(
            row=1, column=1, columnspan=3, sticky="we", padx=4, pady=4
        )

        botones = ttk.Frame(marco_form)
        botones.grid(row=2, column=0, columnspan=4, sticky="w", pady=(8, 0))
        ttk.Button(botones, text="Entrada (+)", command=self._entrada_stock).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(botones, text="Salida (−)", command=self._salida_stock).pack(
            side="left", padx=(0, 6)
        )
        ttk.Button(botones, text="Ajustar stock", command=self._ajustar_stock).pack(side="left")

        marco_hist = ttk.LabelFrame(self.tab_movimientos, text="Historial reciente", padding=8)
        marco_hist.pack(fill="both", expand=True, pady=(12, 0))

        columnas = ("fecha", "sku", "tipo", "cantidad", "stock", "motivo")
        self.tree_movimientos = ttk.Treeview(
            marco_hist, columns=columnas, show="headings", height=12
        )
        for col, titulo, ancho in (
            ("fecha", "Fecha", 150),
            ("sku", "SKU", 100),
            ("tipo", "Tipo", 80),
            ("cantidad", "Cant.", 60),
            ("stock", "Stock", 60),
            ("motivo", "Motivo", 320),
        ):
            self.tree_movimientos.heading(col, text=titulo)
            self.tree_movimientos.column(col, width=ancho, anchor="w")
        self.tree_movimientos.pack(fill="both", expand=True)

    def actualizar_vistas(self) -> None:
        self.actualizar_resumen()
        self.actualizar_productos()
        self.actualizar_movimientos()

    def actualizar_resumen(self) -> None:
        resumen = self.inventario.resumen()
        self.lbl_total_productos.config(
            text=f"Productos registrados: {resumen['total_productos']}"
        )
        self.lbl_unidades.config(text=f"Unidades en stock: {resumen['unidades_en_stock']}")
        self.lbl_valor.config(
            text=f"Valor del inventario: ${resumen['valor_inventario']:,.2f}"
        )
        self.lbl_stock_bajo.config(
            text=f"Productos con stock bajo: {resumen['productos_stock_bajo']}"
        )

        for item in self.tree_alertas.get_children():
            self.tree_alertas.delete(item)
        for producto in self.inventario.listar_productos(solo_stock_bajo=True):
            self.tree_alertas.insert(
                "",
                "end",
                values=(producto.sku, producto.nombre, producto.stock, producto.stock_minimo),
            )

    def actualizar_productos(self) -> None:
        termino = self.var_busqueda.get().strip()
        productos = (
            self.inventario.buscar(termino)
            if termino
            else self.inventario.listar_productos()
        )

        for item in self.tree_productos.get_children():
            self.tree_productos.delete(item)

        for producto in productos:
            tags = ("bajo",) if producto.stock_bajo() else ()
            self.tree_productos.insert(
                "",
                "end",
                tags=tags,
                values=(
                    producto.sku,
                    producto.nombre,
                    producto.categoria.value,
                    producto.marca,
                    f"${producto.precio:,.2f}",
                    producto.stock,
                    producto.stock_minimo,
                ),
            )

    def actualizar_movimientos(self) -> None:
        for item in self.tree_movimientos.get_children():
            self.tree_movimientos.delete(item)

        for movimiento in self.inventario.historial_movimientos(limite=50):
            fecha = movimiento.fecha[:19].replace("T", " ")
            self.tree_movimientos.insert(
                "",
                "end",
                values=(
                    fecha,
                    movimiento.sku,
                    movimiento.tipo.value,
                    movimiento.cantidad,
                    movimiento.stock_resultante if movimiento.stock_resultante is not None else "—",
                    movimiento.motivo,
                ),
            )

    def _dialogo_agregar(self) -> None:
        dialogo = tk.Toplevel(self.ventana)
        dialogo.title("Agregar producto")
        dialogo.transient(self.ventana)
        dialogo.grab_set()
        dialogo.resizable(False, False)

        campos: dict[str, tk.Variable] = {
            "sku": tk.StringVar(),
            "nombre": tk.StringVar(),
            "marca": tk.StringVar(),
            "precio": tk.StringVar(value="0"),
            "stock": tk.StringVar(value="0"),
            "stock_minimo": tk.StringVar(value="5"),
            "descripcion": tk.StringVar(),
        }
        categoria = tk.StringVar(value=Categoria.LAPTOP.value)

        filas = [
            ("SKU", "sku"),
            ("Nombre", "nombre"),
            ("Marca", "marca"),
            ("Precio", "precio"),
            ("Stock inicial", "stock"),
            ("Stock mínimo", "stock_minimo"),
            ("Descripción", "descripcion"),
        ]

        marco = ttk.Frame(dialogo, padding=16)
        marco.pack(fill="both", expand=True)

        for i, (etiqueta, clave) in enumerate(filas):
            ttk.Label(marco, text=etiqueta).grid(row=i, column=0, sticky="w", pady=4, padx=4)
            ttk.Entry(marco, textvariable=campos[clave], width=36).grid(
                row=i, column=1, sticky="we", pady=4, padx=4
            )

        ttk.Label(marco, text="Categoría").grid(
            row=len(filas), column=0, sticky="w", pady=4, padx=4
        )
        ttk.Combobox(
            marco,
            textvariable=categoria,
            values=[c.value for c in Categoria],
            state="readonly",
            width=33,
        ).grid(row=len(filas), column=1, sticky="we", pady=4, padx=4)

        def guardar() -> None:
            try:
                producto = self.inventario.agregar_producto(
                    sku=campos["sku"].get(),
                    nombre=campos["nombre"].get(),
                    categoria=Categoria(categoria.get()),
                    precio=float(campos["precio"].get().replace(",", ".")),
                    stock=int(campos["stock"].get()),
                    stock_minimo=int(campos["stock_minimo"].get()),
                    marca=campos["marca"].get(),
                    descripcion=campos["descripcion"].get(),
                )
            except (ValueError, ErrorInventario) as error:
                messagebox.showerror("Error", str(error), parent=dialogo)
                return

            messagebox.showinfo(
                "Producto agregado",
                f"Se registró '{producto.nombre}' correctamente.",
                parent=dialogo,
            )
            dialogo.destroy()
            self.actualizar_vistas()

        botones = ttk.Frame(marco)
        botones.grid(row=len(filas) + 1, column=0, columnspan=2, sticky="e", pady=(12, 0))
        ttk.Button(botones, text="Cancelar", command=dialogo.destroy).pack(side="right", padx=4)
        ttk.Button(botones, text="Guardar", command=guardar).pack(side="right")

    def _sku_seleccionado(self) -> str | None:
        seleccion = self.tree_productos.selection()
        if seleccion:
            return str(self.tree_productos.item(seleccion[0], "values")[0])
        return self.var_sku_mov.get().strip().upper() or None

    def _leer_cantidad(self) -> int:
        return int(self.var_cantidad_mov.get().strip())

    def _entrada_stock(self) -> None:
        sku = self._sku_seleccionado()
        if not sku:
            messagebox.showwarning("Falta SKU", "Indica un SKU o selecciona un producto.")
            return
        try:
            cantidad = self._leer_cantidad()
            motivo = self.var_motivo_mov.get().strip() or "Reposición"
            producto = self.inventario.entrada_stock(sku, cantidad, motivo)
        except (ValueError, ErrorInventario) as error:
            messagebox.showerror("Error", str(error))
            return

        messagebox.showinfo("Entrada registrada", f"Stock actual: {producto.stock}")
        self.actualizar_vistas()

    def _salida_stock(self) -> None:
        sku = self._sku_seleccionado()
        if not sku:
            messagebox.showwarning("Falta SKU", "Indica un SKU o selecciona un producto.")
            return
        try:
            cantidad = self._leer_cantidad()
            motivo = self.var_motivo_mov.get().strip() or "Venta"
            producto = self.inventario.salida_stock(sku, cantidad, motivo)
        except (ValueError, ErrorInventario) as error:
            messagebox.showerror("Error", str(error))
            return

        total = producto.precio * cantidad
        messagebox.showinfo(
            "Salida registrada",
            f"Stock actual: {producto.stock}\nTotal: ${total:,.2f}",
        )
        self.actualizar_vistas()

    def _ajustar_stock(self) -> None:
        sku = self._sku_seleccionado()
        if not sku:
            messagebox.showwarning("Falta SKU", "Indica un SKU o selecciona un producto.")
            return
        try:
            producto = self.inventario.obtener_producto(sku)
            nuevo_stock = self._leer_cantidad()
            motivo = self.var_motivo_mov.get().strip()
            if not motivo:
                raise ErrorInventario("Indica un motivo para el ajuste.")
            producto = self.inventario.ajustar_stock(sku, nuevo_stock, motivo)
        except (ValueError, ErrorInventario) as error:
            messagebox.showerror("Error", str(error))
            return

        messagebox.showinfo("Stock ajustado", f"Nuevo stock: {producto.stock}")
        self.actualizar_vistas()

    def _eliminar_producto(self) -> None:
        sku = self._sku_seleccionado()
        if not sku:
            messagebox.showwarning("Sin selección", "Selecciona un producto de la lista.")
            return

        producto = self.inventario.obtener_producto(sku)
        if not messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar '{producto.nombre}' (SKU: {producto.sku})?",
        ):
            return

        try:
            self.inventario.eliminar_producto(sku)
        except ErrorInventario as error:
            messagebox.showerror("Error", str(error))
            return

        self.actualizar_vistas()

    def ejecutar(self) -> None:
        self.ventana.mainloop()


def main() -> None:
    AplicacionGUI().ejecutar()
