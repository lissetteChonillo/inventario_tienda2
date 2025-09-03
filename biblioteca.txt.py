class Libro:
    def __init__(self, titulo, autor, categoria, isbn):
        self.titulo_autor = (titulo, autor)  # Tupla inmutable
        self.categoria = categoria
        self.isbn = isbn

    @property
    def titulo(self): return self.titulo_autor[0]
    @property
    def autor(self): return self.titulo_autor[1]

    def __str__(self):
        return f"{self.titulo} - {self.autor} (ISBN: {self.isbn}, Cat.: {self.categoria})"


class Usuario:
    def __init__(self, nombre, id_usuario):
        self.nombre = nombre
        self.id_usuario = id_usuario
        self.libros_prestados = []

    def tomar_prestado(self, isbn):
        if isbn not in self.libros_prestados:
            self.libros_prestados.append(isbn)

    def devolver(self, isbn):
        if isbn in self.libros_prestados:
            self.libros_prestados.remove(isbn)


class Biblioteca:
    def __init__(self):
        self.catalogo = {}              # ISBN -> Libro
        self.libros_disponibles = {}    # ISBN -> Libro
        self.usuarios = {}              # id_usuario -> Usuario
        self.ids_usuarios = set()       # IDs únicos
        self.prestamos = {}             # ISBN -> id_usuario

    def añadir_libro(self, libro):
        if libro.isbn not in self.catalogo:
            self.catalogo[libro.isbn] = libro
            self.libros_disponibles[libro.isbn] = libro

    def quitar_libro(self, isbn):
        if isbn in self.prestamos:
            raise ValueError("Libro prestado, no se puede quitar.")
        self.catalogo.pop(isbn, None)
        self.libros_disponibles.pop(isbn, None)

    def registrar_usuario(self, nombre, id_usuario):
        if id_usuario in self.ids_usuarios:
            raise ValueError("ID ya registrado.")
        usuario = Usuario(nombre, id_usuario)
        self.usuarios[id_usuario] = usuario
        self.ids_usuarios.add(id_usuario)

    def dar_baja_usuario(self, id_usuario):
        usuario = self.usuarios[id_usuario]
        if usuario.libros_prestados:
            raise ValueError("Usuario tiene libros pendientes.")
        self.usuarios.pop(id_usuario)
        self.ids_usuarios.remove(id_usuario)

    def prestar_libro(self, isbn, id_usuario):
        if isbn not in self.libros_disponibles:
            raise ValueError("No disponible.")
        self.prestamos[isbn] = id_usuario
        self.usuarios[id_usuario].tomar_prestado(isbn)
        self.libros_disponibles.pop(isbn)

    def devolver_libro(self, isbn, id_usuario):
        if self.prestamos.get(isbn) != id_usuario:
            raise ValueError("Libro no está prestado a este usuario.")
        self.usuarios[id_usuario].devolver(isbn)
        self.libros_disponibles[isbn] = self.catalogo[isbn]
        self.prestamos.pop(isbn)

    def buscar_por_titulo(self, titulo):
        return [l for l in self.catalogo.values() if titulo.lower() in l.titulo.lower()]

    def buscar_por_autor(self, autor):
        return [l for l in self.catalogo.values() if autor.lower() in l.autor.lower()]

    def buscar_por_categoria(self, categoria):
        return [l for l in self.catalogo.values() if categoria.lower() in l.categoria.lower()]

    def listar_libros_prestados(self, id_usuario):
        return [self.catalogo[isbn] for isbn in self.usuarios[id_usuario].libros_prestados]


# --- DEMO ---
if __name__ == "__main__":
    b = Biblioteca()
    l1 = Libro("Cien años de soledad", "García Márquez", "Novela", "111")
    l2 = Libro("El nombre del viento", "Patrick Rothfuss", "Fantasía", "222")
    b.añadir_libro(l1)
    b.añadir_libro(l2)

    b.registrar_usuario("Paola", "U1")
    b.prestar_libro("111", "U1")

    print("Libros prestados a U1:", b.listar_libros_prestados("U1"))
    b.devolver_libro("111", "U1")
    print("Libros disponibles:", list(b.libros_disponibles.values()))
