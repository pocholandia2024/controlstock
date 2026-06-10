#!/usr/bin/env python3
"""Punto de entrada para ControlStock."""

import argparse

from controlstock import __version__


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Control de inventario para tienda de tecnología"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Abrir la versión de consola en lugar de la interfaz gráfica",
    )
    parser.add_argument("--version", action="version", version=f"ControlStock {__version__}")
    args = parser.parse_args()

    if args.cli:
        from controlstock.cli import InterfazCLI

        InterfazCLI().ejecutar()
    else:
        from controlstock.gui import main as gui_main

        gui_main()


if __name__ == "__main__":
    main()
