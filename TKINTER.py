import tkinter as tk
from tkinter import messagebox

def add_task(event=None):
    task = entry.get().strip()
    if task:
        listbox.insert(tk.END, task)
        entry.delete(0, tk.END)
    else:
        messagebox.showwarning("Advertencia", "No puedes añadir una tarea vacía.")

def complete_task(event=None):
    selected = listbox.curselection()
    if selected:
        index = selected[0]
        text = listbox.get(index)
        if text.endswith("✔"):
            text = text.replace(" ✔", "")
        else:
            text += " ✔"
        listbox.delete(index)
        listbox.insert(index, text)
    else:
        messagebox.showwarning("Advertencia", "Selecciona una tarea para completar.")

def delete_task(event=None):
    selected = listbox.curselection()
    if selected:
        listbox.delete(selected[0])
    else:
        messagebox.showwarning("Advertencia", "Selecciona una tarea para eliminar.")

# Ventana principal
root = tk.Tk()
root.title("Lista de Tareas")
root.geometry("400x400")

# Entrada
entry = tk.Entry(root, width=30, font=("Arial", 12))
entry.pack(pady=10)
entry.focus()

# Botones
frame = tk.Frame(root)
frame.pack()

tk.Button(frame, text="Añadir", command=add_task).grid(row=0, column=0, padx=5)
tk.Button(frame, text="Completar", command=complete_task).grid(row=0, column=1, padx=5)
tk.Button(frame, text="Eliminar", command=delete_task).grid(row=0, column=2, padx=5)

# Lista
listbox = tk.Listbox(root, width=50, height=15, font=("Arial", 11))
listbox.pack(pady=10)

# Atajos de teclado
root.bind("<Return>", add_task)      # Enter = añadir
root.bind("c", complete_task)        # C = completar
root.bind("d", delete_task)          # D = eliminar
root.bind("<Delete>", delete_task)   # Tecla Supr = eliminar
root.bind("<Escape>", lambda e: root.quit())  # Escape = salir

root.mainloop()
