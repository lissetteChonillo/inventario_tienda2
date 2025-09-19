import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry  # Necesita: pip install tkcalendar
import datetime

class AgendaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Agenda Personal")

        # ===== Frame superior: Treeview =====
        frame_view = ttk.Frame(root, padding=10)
        frame_view.pack(fill="both", expand=True)

        self.tree = ttk.Treeview(frame_view, columns=("fecha", "hora", "desc"), show="headings", height=10)
        self.tree.heading("fecha", text="Fecha")
        self.tree.heading("hora", text="Hora")
        self.tree.heading("desc", text="Descripción")
        self.tree.column("fecha", width=100, anchor="center")
        self.tree.column("hora", width=80, anchor="center")
        self.tree.column("desc", width=300, anchor="w")
        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(frame_view, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        # ===== Frame medio: Entradas =====
        frame_input = ttk.Frame(root, padding=10)
        frame_input.pack(fill="x")

        ttk.Label(frame_input, text="Fecha:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_fecha = DateEntry(frame_input, date_pattern="yyyy-MM-dd", width=12)
        self.entry_fecha.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame_input, text="Hora (HH:MM):").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.entry_hora = ttk.Entry(frame_input, width=10)
        self.entry_hora.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(frame_input, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_desc = ttk.Entry(frame_input, width=40)
        self.entry_desc.grid(row=1, column=1, columnspan=3, padx=5, pady=5, sticky="w")

        # ===== Frame inferior: Botones =====
        frame_buttons = ttk.Frame(root, padding=10)
        frame_buttons.pack(fill="x")

        ttk.Button(frame_buttons, text="Agregar Evento", command=self.add_event).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Eliminar Seleccionado", command=self.delete_event).pack(side="left", padx=5)
        ttk.Button(frame_buttons, text="Salir", command=root.quit).pack(side="right", padx=5)

    def add_event(self):
        fecha = self.entry_fecha.get()
        hora = self.entry_hora.get().strip()
        desc = self.entry_desc.get().strip()

        # Validaciones
        if not hora or not desc:
            messagebox.showwarning("Campos incompletos", "Por favor completa hora y descripción.")
            return
        try:
            datetime.datetime.strptime(hora, "%H:%M")
        except ValueError:
            messagebox.showerror("Hora inválida", "Formato correcto: HH:MM")
            return

        # Insertar en Treeview
        self.tree.insert("", "end", values=(fecha, hora, desc))

        # Limpiar entradas
        self.entry_hora.delete(0, tk.END)
        self.entry_desc.delete(0, tk.END)

    def delete_event(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Eliminar", "Selecciona un evento primero.")
            return
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar el evento seleccionado?"):
            for item in selected:
                self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = AgendaApp(root)
    root.mainloop()
