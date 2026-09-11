"""
Auteur : Oleksii Kamarali
Version : 1.0
Module : ProjDev
Date de rendu du Sprint 1 : 11.09.2026
"""

import tkinter as tk # Interface graphique
from tkinter import ttk # Widgets Tkinter
from tkinter import filedialog # Sélection de fichiers et dossiers
from tkinter import simpledialog # Fenêtres de saisie
from pathlib import Path # Gestion des chemins
from datetime import datetime # Gestion des dates
import shutil # Gestion des fichiers et dossiers

# Association entre les éléments de l'arbre et leurs chemins
node_paths = {}

# Affiche les informations du fichier sélectionné.
def display_file_info(event):
    selected_nodes = tree.selection()
    if not selected_nodes:
        return
    file_path = node_paths[selected_nodes[0]]
    if not file_path.is_file():
        return
    file_info = file_path.stat()
    name = file_path.name
    path = str(file_path)
    file_type = file_path.suffix or "sans extension"
    size = str(file_info.st_size) + "octets"
    modified = str(datetime.fromtimestamp(file_info.st_mtime))
    permissions = oct(file_info.st_mode)[-3:]

# Efface les anciennes informations et affiche les nouvelles informations du fichier
    for entry in info_entries:
        entry.delete(0, tk.END)
    info_entries[0].insert(0, name)
    info_entries[1].insert(0, path)
    info_entries[2].insert(0, file_type)
    info_entries[3].insert(0, size)
    info_entries[4].insert(0, modified)
    info_entries[5].insert(0, permissions)

# Affiche le contenu d'un répertoire sélectionné.
def display_directory():
    tree.delete(*tree.get_children())
    node_paths.clear()
    selected_folder = filedialog.askdirectory()
    if not selected_folder:
        return
    root_folder = Path(selected_folder)
    root_node = tree.insert("","end",text=f"📁 {root_folder.resolve()}",open=True) # Ajouter le dossier principal
    node_paths[root_node] = root_folder
    populate_tree(tree, root_node, root_folder)

    for node, path in node_paths.items():
        print(node, ":", path)

    status_bar.config(text=f"Répertoire affiché : {root_folder}")

# Ajoute les fichiers et dossiers dans l'arbre.
def populate_tree(tree, parent, folder):
    try:
        for item in folder.iterdir():
            if item.is_dir():
                item_name = f"📁 {item.name}"
            else:
                item_name = f"🗎 {item.name}"
            node = tree.insert(parent,"end",text=item_name)
            node_paths[node] = item
            if item.is_dir(): # Parcourir les sous-dossiers
                populate_tree(tree, node, item)
    except PermissionError:
        print("Accès refusé :", folder)

# Supprime le fichier ou dossier sélectionné.
def delete_file():
    selected_nodes = tree.selection()
    if not selected_nodes:
        return
    file_path = node_paths[selected_nodes[0]]
    if file_path.is_file():
        file_path.unlink()
    elif file_path.is_dir():
        shutil.rmtree(file_path)
    tree.delete(selected_nodes[0])
    status_bar.config(text=f"Supprimé : {file_path.name}")

# Renomme le fichier ou dossier sélectionné.
def rename_file():
    selected_nodes = tree.selection()
    if not selected_nodes:
        return
    file_path = node_paths[selected_nodes[0]]
    new_name = simpledialog.askstring("Rename","Nouveau nom :",initialvalue=file_path.name)
    if not new_name:
        return
    new_path = file_path.parent / new_name
    file_path.rename(new_path)
    node_paths[selected_nodes[0]] = new_path
    if new_path.is_dir():
        tree.item(selected_nodes[0],text=f"📁 {new_name}")
    else:
        tree.item(selected_nodes[0],text=f"🗎 {new_name}")
    status_bar.config(text=f"Renommé : {new_name}")

# Fenêtre principale
window = tk.Tk()
window.title("Student Project Manager")
window.geometry("1200x700")
window.configure(bg="black")
window.columnconfigure(0, weight=1, uniform="colonnes")
window.columnconfigure(1, weight=1, uniform="colonnes")
window.columnconfigure(2, weight=1, uniform="colonnes")
window.rowconfigure(0, weight=1)

# Menu
menu_bar = tk.Menu(window)

file_menu = tk.Menu(menu_bar, tearoff=False)
file_menu.add_command(label="display directory",command=display_directory)
file_menu.add_separator()
file_menu.add_command(label="Quit",command=window.destroy)

menu_bar.add_cascade(label="File",menu=file_menu)
tools_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Tools",menu=tools_menu)
help_menu = tk.Menu(menu_bar, tearoff=False)
menu_bar.add_cascade(label="Help",menu=help_menu)
window.config(menu=menu_bar)

# Arbre des fichiers
tree_frame = ttk.LabelFrame(window,text="Directory Tree",padding=10)
tree_frame.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
tree_frame.rowconfigure(0, weight=1)
tree_frame.columnconfigure(0, weight=1)

tree = ttk.Treeview(tree_frame)
tree.heading("#0",text="Directory")
tree.grid(row=0,column=0,sticky="nsew")
tree.bind("<<TreeviewSelect>>",display_file_info)

# Informations du fichier
info_frame = ttk.LabelFrame(window,text="File Information",padding=10)
info_frame.grid(row=0,column=1,sticky="nsew",padx=10,pady=10)
info_frame.columnconfigure(0, weight=1)
info_entries = []

# Noms des informations affichées dans la zone "File Information"
labels = [
    "Name:",
    "Path:",
    "Type:",
    "Size:",
    "Modified:",
    "Permissions:"
]

for i, texte in enumerate(labels):
    ttk.Label(info_frame,text=texte
    ).grid(row=i * 2,column=0,sticky="w",pady=(5, 2))
    entry = ttk.Entry(info_frame)
    entry.grid(row=i * 2 + 1,column=0,sticky="ew",pady=(0, 10))
    info_entries.append(entry)

# Zone des actions
project_frame = ttk.LabelFrame(window,text="Student Project Area",padding=10)
project_frame.grid(row=0,column=2,sticky="nsew",padx=10,pady=10)
project_frame.columnconfigure(0,weight=1)
project_frame.columnconfigure(1,weight=1)

# Création des boutons pour les différentes actions
ttk.Button(project_frame,text="Open").grid(row=0,column=0,sticky="ew",padx=5,pady=5)
ttk.Button(project_frame,text="Copy").grid(row=0,column=1,sticky="ew",padx=5,pady=5)

ttk.Button(project_frame,text="Move").grid(row=1,column=0,sticky="ew",padx=5,pady=5)
ttk.Button(project_frame,text="Rename",command=rename_file).grid(row=1,column=1,sticky="ew",padx=5,pady=5)

ttk.Button(project_frame,text="Delete",command=delete_file).grid(row=2,column=0,sticky="ew",padx=5,pady=5)
ttk.Button(project_frame,text="Add File").grid(row=2,column=1,sticky="ew",padx=5,pady=5)

status_bar = ttk.Label(window,text="...",relief="sunken",anchor="w")
status_bar.grid(row=1,column=0,columnspan=3,sticky="ew",padx=10,pady=(0, 10))

window.mainloop()