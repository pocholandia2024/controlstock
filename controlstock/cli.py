from controlstock.inventory import ErrorInventario, Inventario
from controlstock.models import Categoria


def _leer_texto(mensaje: str, obligatorio: bool = True) -> str:
    while True:
        valor = input(mensaje).strip()
        if valor or not obligatorio:
            return valor
        print("  Este campo es obligatorio.")


def _leer_numero(mensaje: str, entero: bool = False, minimo: float | None = None) -> float:
    while True:
        try:
            texto = input(mensaje).strip().replace(",", ".")
            valor = int(texto) if entero else float(texto)
            if minimo is not None and valor < minimo:
                print(f"  El valor debe ser al menos {minimo}.")
                continue
            return valor
        except ValueError:
            print("  Ingresa un número válido.")


def _elegir_categoria() -> Categoria:
    categorias = list(Categoria)
    print("\nCategorías disponibles:")
    for i, cat in enumerate(categorias, start=1):
        print(f"  {i}. {cat.value}")

    while True:
        try:
            opcion = int(input("Elige categoría (número): "))
            if 1 <= opcion <= len(categorias):
                return categorias[opcion - 1]
        except ValueError:
            pass
        print("  Opción no válida.")


def _mostrar_productos(productos) -> None:
    if not productos:
        print("\nNo hay productos para mostrar.")
        return

    print(f"\n{'SKU':<12} {'Nombre':<28} {'Categoría':<14} {'Precio':>10} {'Stock':>6} {'Mín':>5}")
    print("-" * 80)
    for p in productos:
        alerta = " !" if p.stock_bajo() else ""
        print(
            f"{p.sku:<12} {p.nombre[:28]:<28} {p.categoria.value:<14} "
            f"${p.precio:>9.2f} {p.stock:>6}{alerta:>2} {p.stock_minimo:>5}"
        )
    print("\n(!) = stock bajo o en el mínimo")


def _mostrar_movimientos(movimientos, inventario: Inventario) -> None:
    if not movimientos:
        print("\nNo hay movimientos registrados.")
        return

    print(f"\n{'Fecha':<20} {'SKU':<12} {'Tipo':<8} {'Cant':>5} {'Stock':>6}  Motivo")
    print("-" * 80)
    for m in movimientos:
        fecha = m.fecha[:19].replace("T", " ")
        print(
            f"{fecha:<20} {m.sku:<12} {m.tipo.value:<8} {m.cantidad:>5} "
            f"{m.stock_resultante or '-':>6}  {m.motivo}"
        )


class InterfazCLI:
    def __init__(self) -> None:
        self.inventario = Inventario()

    def ejecutar(self) -> None:
        print("=" * 50)
        print("  CONTROLSTOCK — Tienda de Tecnología")
        print("=" * 50)

        acciones = {
            "1": self._menu_resumen,
            "2": self._menu_listar,
            "3": self._menu_buscar,
            "4": self._menu_agregar,
            "5": self._menu_entrada,
            "6": self._menu_salida,
            "7": self._menu_ajustar,
            "8": self._menu_stock_bajo,
            "9": self._menu_historial,
            "10": self._menu_eliminar,
            "0": None,
        }

        while True:
            print("\n--- Menú principal ---")
            print(" 1. Resumen del inventario")
            print(" 2. Listar productos")
            print(" 3. Buscar producto")
            print(" 4. Agregar producto")
            print(" 5. Entrada de stock (compra/reposición)")
            print(" 6. Salida de stock (venta)")
            print(" 7. Ajustar stock")
            print(" 8. Ver productos con stock bajo")
            print(" 9. Historial de movimientos")
            print("10. Eliminar producto")
            print(" 0. Salir")

            opcion = input("\nElige una opción: ").strip()
            accion = acciones.get(opcion)

            if accion is None and opcion == "0":
                print("\n¡Hasta luego!")
                break
            if accion is None:
                print("Opción no válida.")
                continue

            try:
                accion()
            except ErrorInventario as error:
                print(f"\nError: {error}")
            except KeyboardInterrupt:
                print("\n\nOperación cancelada.")

    def _menu_resumen(self) -> None:
        resumen = self.inventario.resumen()
        print("\n--- Resumen ---")
        print(f"  Productos registrados : {resumen['total_productos']}")
        print(f"  Unidades en stock     : {resumen['unidades_en_stock']}")
        print(f"  Valor del inventario  : ${resumen['valor_inventario']:,.2f}")
        print(f"  Productos stock bajo  : {resumen['productos_stock_bajo']}")

    def _menu_listar(self) -> None:
        productos = self.inventario.listar_productos()
        _mostrar_productos(productos)

    def _menu_buscar(self) -> None:
        termino = _leer_texto("\nBuscar (SKU, nombre, marca o categoría): ")
        productos = self.inventario.buscar(termino)
        _mostrar_productos(productos)

    def _menu_agregar(self) -> None:
        print("\n--- Nuevo producto ---")
        sku = _leer_texto("SKU: ").upper()
        nombre = _leer_texto("Nombre: ")
        categoria = _elegir_categoria()
        marca = _leer_texto("Marca (opcional): ", obligatorio=False)
        precio = _leer_numero("Precio de venta: $", minimo=0)
        stock = int(_leer_numero("Stock inicial: ", entero=True, minimo=0))
        stock_minimo = int(_leer_numero("Stock mínimo (alerta): ", entero=True, minimo=0))
        descripcion = _leer_texto("Descripción (opcional): ", obligatorio=False)

        producto = self.inventario.agregar_producto(
            sku=sku,
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            stock=stock,
            stock_minimo=stock_minimo,
            marca=marca,
            descripcion=descripcion,
        )
        print(f"\nProducto '{producto.nombre}' agregado correctamente.")

    def _menu_entrada(self) -> None:
        sku = _leer_texto("\nSKU del producto: ").upper()
        cantidad = int(_leer_numero("Cantidad a ingresar: ", entero=True, minimo=1))
        motivo = _leer_texto("Motivo (ej. compra a proveedor): ", obligatorio=False) or "Reposición"

        producto = self.inventario.entrada_stock(sku, cantidad, motivo)
        print(f"\nEntrada registrada. Stock actual de '{producto.nombre}': {producto.stock}")

    def _menu_salida(self) -> None:
        sku = _leer_texto("\nSKU del producto: ").upper()
        cantidad = int(_leer_numero("Cantidad a vender/salir: ", entero=True, minimo=1))
        motivo = _leer_texto("Motivo (ej. venta mostrador): ", obligatorio=False) or "Venta"

        producto = self.inventario.salida_stock(sku, cantidad, motivo)
        total = producto.precio * cantidad
        print(f"\nSalida registrada. Stock actual de '{producto.nombre}': {producto.stock}")
        print(f"Total de la operación: ${total:,.2f}")

    def _menu_ajustar(self) -> None:
        sku = _leer_texto("\nSKU del producto: ").upper()
        producto = self.inventario.obtener_producto(sku)
        print(f"Stock actual de '{producto.nombre}': {producto.stock}")
        nuevo_stock = int(_leer_numero("Nuevo stock: ", entero=True, minimo=0))
        motivo = _leer_texto("Motivo del ajuste (inventario, merma, etc.): ")

        producto = self.inventario.ajustar_stock(sku, nuevo_stock, motivo)
        print(f"\nStock ajustado. Nuevo stock: {producto.stock}")

    def _menu_stock_bajo(self) -> None:
        productos = self.inventario.listar_productos(solo_stock_bajo=True)
        print("\n--- Productos con stock bajo ---")
        _mostrar_productos(productos)

    def _menu_historial(self) -> None:
        sku = _leer_texto("\nSKU (dejar vacío para ver todos): ", obligatorio=False)
        limite = int(_leer_numero("Cantidad de movimientos a mostrar: ", entero=True, minimo=1))
        movimientos = self.inventario.historial_movimientos(sku or None, limite)
        _mostrar_movimientos(movimientos, self.inventario)

    def _menu_eliminar(self) -> None:
        sku = _leer_texto("\nSKU del producto a eliminar: ").upper()
        producto = self.inventario.obtener_producto(sku)
        confirmar = input(
            f"¿Eliminar '{producto.nombre}' (SKU: {producto.sku})? [s/N]: "
        ).strip().lower()
        if confirmar == "s":
            self.inventario.eliminar_producto(sku)
            print("Producto eliminado.")
        else:
            print("Operación cancelada.")


def main_cli() -> None:
    InterfazCLI().ejecutar()
