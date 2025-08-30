"""
Sistema avanzado de gestión de inventarios (POO + Colecciones + Archivos)
-----------------------------------------------------------------------
Características principales:
- POO: Clases Producto e Inventario con validaciones y encapsulamiento.
- Colecciones:
    * dict: almacenamiento principal de productos por ID (búsqueda O(1)).
    * set: índice auxiliar por nombre normalizado para búsquedas exactas rápidas.
    * list: resultados de consultas / listado ordenado para impresión.
    * tuple: resumen del inventario (total ítems, valor total, productos únicos).
- Archivos: persistencia en JSON (serialización/deserialización) y exportación a CSV.
- Interfaz de consola: menú interactivo para gestionar el inventario.

Cómo ejecutar en PyCharm o terminal:
1) Guarda este archivo como `inventario_poo_archivos.py`.
2) (Opcional) Crea un entorno virtual e instala dependencias (no se requiere ninguna extra).
3) Ejecuta: `python inventario_poo_archivos.py`.
4) El sistema carga automáticamente `inventario.json` si existe y guarda los cambios en el mismo archivo.

Estructura de archivos generados:
- inventario.json : almacena el inventario completo en formato JSON.
- inventario_export.csv : exportación a CSV bajo demanda.
"""
from __future__ import annotations

import json
import csv
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Set, List, Tuple, Optional


INVENTARIO_JSON = Path("inventario.json")
EXPORT_CSV = Path("inventario_export.csv")


def _norm_nombre(nombre: str) -> str:
    """Normaliza un nombre para búsquedas (minúsculas, sin espacios extremos)."""
    return nombre.strip().casefold()


@dataclass
class Producto:
    """Representa un producto con validaciones básicas.

    Aunque @dataclass genera __init__, definimos propiedades para validar al modificar.
    """
    id: int
    nombre: str
    cantidad: int
    precio: float

    # --- Propiedades con validación ---
    @property
    def precio(self) -> float:  # type: ignore[override]
        return self._precio

    @precio.setter
    def precio(self, value: float) -> None:  # type: ignore[override]
        if value < 0:
            raise ValueError("El precio no puede ser negativo")
        self._precio = float(value)

    @property
    def cantidad(self) -> int:  # type: ignore[override]
        return self._cantidad

    @cantidad.setter
    def cantidad(self, value: int) -> None:  # type: ignore[override]
        if value < 0:
            raise ValueError("La cantidad no puede ser negativa")
        self._cantidad = int(value)

    @property
    def nombre(self) -> str:  # type: ignore[override]
        return self._nombre

    @nombre.setter
    def nombre(self, value: str) -> None:  # type: ignore[override]
        if not value or not value.strip():
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = value.strip()

    # dataclass asigna directamente atributos, por lo que debemos
    # reubicar los valores en las propiedades para forzar validaciones.
    def __post_init__(self) -> None:
        # Asignaciones pasan por los setters para validar
        self.nombre = self.nombre
        self.cantidad = self.cantidad
        self.precio = self.precio

    # --- Serialización ---
    def to_dict(self) -> Dict:
        d = asdict(self)
        # asdict incluye los campos del dataclass originales; sin _privados
        return d

    @staticmethod
    def from_dict(data: Dict) -> "Producto":
        return Producto(
            id=int(data["id"]),
            nombre=str(data["nombre"]),
            cantidad=int(data["cantidad"]),
            precio=float(data["precio"]),
        )

    # --- Utilidad ---
    def valor_total(self) -> float:
        return self.cantidad * self.precio


class Inventario:
    """Gestiona productos usando colecciones para operaciones eficientes."""

    def __init__(self) -> None:
        # Almacenamiento principal: dict[ID, Producto]
        self._productos: Dict[int, Producto] = {}
        # Índice por nombre normalizado: dict[nombre_norm, set[ID]]
        self._idx_nombre: Dict[str, Set[int]] = {}

    # --- Métodos internos de índice ---
    def _indexar(self, p: Producto) -> None:
        key = _norm_nombre(p.nombre)
        self._idx_nombre.setdefault(key, set()).add(p.id)

    def _desindexar(self, p: Producto) -> None:
        key = _norm_nombre(p.nombre)
        ids = self._idx_nombre.get(key)
        if ids:
            ids.discard(p.id)
            if not ids:
                self._idx_nombre.pop(key, None)

    # --- API pública ---
    def agregar(self, p: Producto) -> None:
        if p.id in self._productos:
            raise KeyError(f"Ya existe un producto con ID {p.id}")
        self._productos[p.id] = p
        self._indexar(p)

    def eliminar(self, id_: int) -> Producto:
        if id_ not in self._productos:
            raise KeyError(f"No existe producto con ID {id_}")
        p = self._productos.pop(id_)
        self._desindexar(p)
        return p

    def actualizar_cantidad(self, id_: int, nueva_cantidad: int) -> None:
        if id_ not in self._productos:
            raise KeyError(f"No existe producto con ID {id_}")
        self._productos[id_].cantidad = nueva_cantidad

    def ajustar_cantidad(self, id_: int, delta: int) -> None:
        """Ajusta cantidad sumando delta (puede ser negativo)."""
        if id_ not in self._productos:
            raise KeyError(f"No existe producto con ID {id_}")
        nueva = self._productos[id_].cantidad + int(delta)
        if nueva < 0:
            raise ValueError("El ajuste dejaría cantidad negativa")
        self._productos[id_].cantidad = nueva

    def actualizar_precio(self, id_: int, nuevo_precio: float) -> None:
        if id_ not in self._productos:
            raise KeyError(f"No existe producto con ID {id_}")
        self._productos[id_].precio = nuevo_precio

    def actualizar_nombre(self, id_: int, nuevo_nombre: str) -> None:
        if id_ not in self._productos:
            raise KeyError(f"No existe producto con ID {id_}")
        p = self._productos[id_]
        self._desindexar(p)
        p.nombre = nuevo_nombre
        self._indexar(p)

    def buscar_por_nombre(self, texto: str, exacto: bool = False) -> List[Producto]:
        """Busca por nombre. Si exacto=True usa índice O(k), si no, busca por substring O(n)."""
        if exacto:
            ids = self._idx_nombre.get(_norm_nombre(texto), set())
            return [self._productos[i] for i in ids]
        # Búsqueda por substring (case-insensitive)
        nt = _norm_nombre(texto)
        return [p for p in self._productos.values() if nt in _norm_nombre(p.nombre)]

    def obtener(self, id_: int) -> Optional[Producto]:
        return self._productos.get(id_)

    def listar(self, orden: str = "id") -> List[Producto]:
        """Devuelve lista de productos ordenados por 'id' | 'nombre' | 'precio' | 'cantidad'."""
        key_map = {
            "id": lambda p: p.id,
            "nombre": lambda p: _norm_nombre(p.nombre),
            "precio": lambda p: p.precio,
            "cantidad": lambda p: p.cantidad,
        }
        k = key_map.get(orden, key_map["id"])  # default por id
        return sorted(self._productos.values(), key=k)

    # --- Persistencia ---
    def guardar_json(self, ruta: Path = INVENTARIO_JSON) -> None:
        data = [p.to_dict() for p in self._productos.values()]
        ruta.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    def cargar_json(self, ruta: Path = INVENTARIO_JSON) -> int:
        if not ruta.exists():
            return 0
        data = json.loads(ruta.read_text(encoding="utf-8"))
        self._productos.clear()
        self._idx_nombre.clear()
        for item in data:
            p = Producto.from_dict(item)
            self._productos[p.id] = p
            self._indexar(p)
        return len(self._productos)

    def exportar_csv(self, ruta: Path = EXPORT_CSV) -> None:
        with ruta.open("w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Nombre", "Cantidad", "Precio", "Valor total"])
            for p in self.listar():
                writer.writerow([p.id, p.nombre, p.cantidad, f"{p.precio:.2f}", f"{p.valor_total():.2f}"])

    # --- Métricas / tuple demonstration ---
    def resumen(self) -> Tuple[int, int, float]:
        """Devuelve (items_distintos, unidades_totales, valor_total)."""
        items = len(self._productos)
        unidades = sum(p.cantidad for p in self._productos.values())
        valor = sum(p.valor_total() for p in self._productos.values())
        return (items, unidades, valor)


# ---------------- Interfaz de Usuario (CLI) ----------------

def _input_int(msg: str) -> int:
    while True:
        try:
            return int(input(msg).strip())
        except ValueError:
            print("Debe ingresar un número entero.")


def _input_float(msg: str) -> float:
    while True:
        try:
            return float(input(msg).strip().replace(",", "."))
        except ValueError:
            print("Debe ingresar un número (use punto o coma para decimales).")


def _pausa() -> None:
    input("\nPresione ENTER para continuar...")


def menu() -> None:
    inv = Inventario()
    cargados = inv.cargar_json(INVENTARIO_JSON)
    if cargados:
        print(f"Inventario cargado: {cargados} productos desde '{INVENTARIO_JSON}'.")
    else:
        print("No se encontró inventario previo. Se creará uno nuevo.")

    opciones = {
        "1": "Añadir producto",
        "2": "Eliminar producto",
        "3": "Actualizar cantidad",
        "4": "Actualizar precio",
        "5": "Buscar por nombre",
        "6": "Mostrar todos",
        "7": "Exportar a CSV",
        "8": "Resumen del inventario",
        "9": "Guardar y salir",
    }

    while True:
        print("\n=== MENÚ DE INVENTARIO ===")
        for k in sorted(opciones):
            print(f"{k}. {opciones[k]}")
        op = input("Seleccione una opción: ").strip()

        try:
            if op == "1":
                print("\n-- Añadir producto --")
                id_ = _input_int("ID (entero, único): ")
                nombre = input("Nombre: ").strip()
                cantidad = _input_int("Cantidad: ")
                precio = _input_float("Precio: ")
                inv.agregar(Producto(id_, nombre, cantidad, precio))
                inv.guardar_json(INVENTARIO_JSON)
                print("Producto añadido y guardado.")

            elif op == "2":
                print("\n-- Eliminar producto --")
                id_ = _input_int("ID a eliminar: ")
                p = inv.eliminar(id_)
                inv.guardar_json(INVENTARIO_JSON)
                print(f"Eliminado: {p.id} - {p.nombre}")

            elif op == "3":
                print("\n-- Actualizar cantidad --")
                id_ = _input_int("ID del producto: ")
                modo = input("¿(A)juste +/- o (S)etear cantidad exacta? [A/S]: ").strip().upper()
                if modo == "A":
                    delta = _input_int("Delta (puede ser negativo): ")
                    inv.ajustar_cantidad(id_, delta)
                else:
                    nueva = _input_int("Nueva cantidad: ")
                    inv.actualizar_cantidad(id_, nueva)
                inv.guardar_json(INVENTARIO_JSON)
                print("Cantidad actualizada y guardada.")

            elif op == "4":
                print("\n-- Actualizar precio --")
                id_ = _input_int("ID del producto: ")
                nuevo = _input_float("Nuevo precio: ")
                inv.actualizar_precio(id_, nuevo)
                inv.guardar_json(INVENTARIO_JSON)
                print("Precio actualizado y guardado.")

            elif op == "5":
                print("\n-- Búsqueda por nombre --")
                texto = input("Texto a buscar: ").strip()
                exacto = input("¿Búsqueda exacta? [s/N]: ").strip().lower() == "s"
                resultados = inv.buscar_por_nombre(texto, exacto=exacto)
                if not resultados:
                    print("Sin coincidencias.")
                else:
                    print(f"{len(resultados)} coincidencia(s):")
                    for p in sorted(resultados, key=lambda x: x.id):
                        print(f"  ID:{p.id:<4} | {p.nombre:<20} | Cant:{p.cantidad:<5} | $ {p.precio:>8.2f} | $Tot {p.valor_total():>8.2f}")

            elif op == "6":
                print("\n-- Listado de productos --")
                criterio = input("Orden por [id/nombre/precio/cantidad] (enter=id): ").strip() or "id"
                for p in inv.listar(criterio):
                    print(f"  ID:{p.id:<4} | {p.nombre:<20} | Cant:{p.cantidad:<5} | $ {p.precio:>8.2f} | $Tot {p.valor_total():>8.2f}")

            elif op == "7":
                inv.exportar_csv(EXPORT_CSV)
                print(f"Exportado a '{EXPORT_CSV}'.")

            elif op == "8":
                items, unidades, valor = inv.resumen()
                print("\n-- Resumen --")
                print(f"Productos distintos: {items}")
                print(f"Unidades totales : {unidades}")
                print(f"Valor total      : $ {valor:.2f}")

            elif op == "9":
                inv.guardar_json(INVENTARIO_JSON)
                print(f"Inventario guardado en '{INVENTARIO_JSON}'. ¡Hasta luego!")
                break

            else:
                print("Opción no válida.")
        except (ValueError, KeyError) as e:
            print(f"Error: {e}")
        finally:
            _pausa()


if __name__ == "__main__":
    menu()
