import os
from producto import Producto

class Inventario:
    def __init__(self, archivo="inventario.txt"):
        self.archivo = archivo
        self.productos = []
        self.cargar_desde_archivo()

    def guardar_en_archivo(self):
        """Guarda los productos en el archivo."""
        try:
            with open(self.archivo, "w", encoding="utf-8") as f:
                for p in self.productos:
                    f.write(f"{p.get_id()},{p.get_nombre()},{p.get_cantidad()},{p.get_precio()}\n")
            print(" Inventario guardado en archivo.")
        except PermissionError:
            print(" Error: No tienes permisos para escribir en el archivo.")
        except Exception as e:
            print(f" Error al guardar inventario: {e}")

    def cargar_desde_archivo(self):
        """Carga productos desde el archivo si existe."""
        if not os.path.exists(self.archivo):
            print("No existe inventario.txt, se creará cuando guardes productos.")
            return

        try:
            with open(self.archivo, "r", encoding="utf-8") as f:
                for linea in f:
                    try:
                        id_producto, nombre, cantidad, precio = linea.strip().split(",")
                        self.productos.append(Producto(int(id_producto), nombre, int(cantidad), float(precio)))
                    except ValueError:
                        print(f" Línea corrupta ignorada: {linea.strip()}")
            print(" Inventario cargado desde archivo.")
        except PermissionError:
            print(" Error: No tienes permisos para leer el archivo.")
        except Exception as e:
            print(f" Error al cargar inventario: {e}")

    def añadir_producto(self, producto: Producto):
        for p in self.productos:
            if p.get_id() == producto.get_id():
                print(" Error: Ya existe un producto con ese ID.")
                return
        self.productos.append(producto)
        print(f" Producto '{producto.get_nombre()}' añadido.")
        self.guardar_en_archivo()

    def eliminar_producto(self, id_producto: int):
        for p in self.productos:
            if p.get_id() == id_producto:
                self.productos.remove(p)
                print(f" Producto '{p.get_nombre()}' eliminado.")
                self.guardar_en_archivo()
                return
        print(" No se encontró un producto con ese ID.")

    def actualizar_producto(self, id_producto: int, cantidad: int = None, precio: float = None):
        for p in self.productos:
            if p.get_id() == id_producto:
                if cantidad is not None:
                    p.set_cantidad(cantidad)
                if precio is not None:
                    p.set_precio(precio)
                print(f" Producto '{p.get_nombre()}' actualizado.")
                self.guardar_en_archivo()
                return
        print(" No se encontró un producto con ese ID.")

    def buscar_producto(self, nombre: str):
        encontrados = [p for p in self.productos if nombre.lower() in p.get_nombre().lower()]
        if encontrados:
            print( "Resultados de búsqueda:")
            for p in encontrados:
                print(p)
        else:
            print(" No se encontraron productos con ese nombre.")

    def mostrar_productos(self):
        if not self.productos:
            print(" Inventario vacío.")
        else:
            print("\n=== Inventario actual ===")
            for p in self.productos:
                print(p)

