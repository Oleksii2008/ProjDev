"""
Auteur : Oleksii Kamarali
Version : 2.0
Module : ProjDev
Date de rendu du Sprint 1 : 09.11.2026
"""
import tkinter as tk # Interface graphique
from tkinter import ttk,filedialog,simpledialog,messagebox # Éléments de l'interface graphique
from pathlib import Path # Gestion des chemins
from datetime import datetime # Gestion des dates
import shutil # Gestion des fichiers et dossiers
import os # Gestion du système
import sys # Détection du système d'exploitation
import subprocess # Exécution de commandes externes

# Association entre les éléments de l'arbre et leurs chemins
node_paths = {}
root_folder = None
clipboard_path = None
clipboard_action = None

# Efface les informations affichées
def clear_info():
    for entry in info_entries:
        entry.delete(0,tk.END)

# Retourne le chemin de l'élément sélectionné
def get_selected_path():
    selected_nodes = tree.selection() # Récupère les éléments sélectionnés dans l'arbre
    if not selected_nodes: # Vérifie si aucun élément n'est sélectionné
        status_bar.config(text="Sélectionnez un fichier ou un dossier.") # Affiche un message
        return None
    path = node_paths.get(selected_nodes[0]) # Récupère le chemin correspondant à l'élément sélectionné
    if path is None or not path.exists(): # Vérifie si le chemin n'existe pas ou si le fichier a été supprimé
        status_bar.config(text="Cet élément n'existe plus. Rechargez le répertoire.") # Affiche un message
        return None
    return path

# Affiche les informations du fichier sélectionné
def display_file_info(event=None):
    clear_info()
    selected_nodes = tree.selection() # Récupère l'élément sélectionné dans l'arbre
    if not selected_nodes:
        return
    file_path = node_paths.get(selected_nodes[0]) # Récupère le chemin de l'élément sélectionné
    if file_path is None or not file_path.is_file():
        return
    try:
        file_info = file_path.stat()
        permissions = "".join([ # Vérifie les permissions de lecture, écriture et exécution
            "R" if os.access(file_path, os.R_OK) else "", # Ajoute R si le fichier est lisible
            "W" if os.access(file_path, os.W_OK) else "", # Ajoute W si le fichier est modifiable
            "X" if os.access(file_path, os.X_OK) else ""  # Ajoute X si le fichier est exécutable
        ])
        values = [file_path.name, # Nom du fichier
                  str(file_path), # Chemin complet du fichier
                  file_path.suffix or "sans extension", # Extension du fichier ou message si aucune extension
                  str(file_info.st_size)+" octets", # Taille du fichier en octets
                  str(datetime.fromtimestamp(file_info.st_mtime).replace(microsecond=0)), # Date et heure de la dernière modification
                  permissions or "Aucun accès"] # Permissions du fichier ou message si aucun accès
        for entry,value in zip(info_entries,values):
            entry.insert(0,value)
    except OSError as error:
        status_bar.config(text=str(error)) # Affiche le message d'erreur

# Ajoute les fichiers et dossiers dans l'arbre
def populate_tree(tree,parent,folder):
    try:
        for item in folder.iterdir():
            icon = "📁" if item.is_dir() else "🗎" # Choisit une icône selon le type d'élément
            node = tree.insert(parent,"end",text=f"{icon} {item.name}") # Ajoute l'élément dans l'arbre
            node_paths[node] = item
            if item.is_dir() and not item.is_symlink(): # Vérifie si l'élément est un dossier et n'est pas un lien symbolique
                populate_tree(tree,node,item)
    except OSError as error:
        print("Impossible de lire :",folder,error) # Affiche un message si le répertoire ne peut pas être lu

# Recharge l'arbre après une modification
def refresh_tree(selected_path=None):
    children = tree.get_children()
    if children:
        tree.delete(*children)
    node_paths.clear()
    clear_info()
    if root_folder is None or not root_folder.is_dir():
        return
    root_node = tree.insert("","end",text=f"📁 {root_folder}",open=True) # Ajoute le répertoire racine dans l'arbre
    node_paths[root_node] = root_folder
    populate_tree(tree,root_node,root_folder)
    for node,path in node_paths.items():
        if path == selected_path: # Vérifie si le chemin correspond à l'élément précédemment sélectionné
            tree.selection_set(node) # Sélectionne à nouveau l'élément
            tree.focus(node) # Place le curseur sur l'élément
            tree.see(node) # Fait défiler l'arbre jusqu'à l'élément
            break

# Affiche le contenu d'un répertoire sélectionné
def display_directory():
    global root_folder
    selected_folder = filedialog.askdirectory(parent=window)
    if not selected_folder:
        return
    root_folder = Path(selected_folder).resolve()
    refresh_tree()
    status_bar.config(text=f"Répertoire affiché : {root_folder}")

# Ouvre un fichier ou un dossier avec l'application par défaut
def open_file():
    file_path = get_selected_path() # Récupère le chemin de l'élément sélectionné
    if file_path is None:
        return
    try:
        if sys.platform == "win32": # Vérifie si le système utilisé est Windows
            os.startfile(str(file_path))
        elif sys.platform == "darwin": # Vérifie si le système utilisé est macOS
            subprocess.Popen(["open",str(file_path)])
        else:
            subprocess.Popen(["xdg-open",str(file_path)]) # Vérifie si le système utilisé est Linux
        status_bar.config(text=f"Ouverture demandée : {file_path.name}")
    except OSError as error:
        messagebox.showerror("Open",str(error),parent=window) # Affiche un message d'erreur


# Supprime le fichier ou dossier sélectionné
def delete_file():
    global clipboard_path,clipboard_action
    file_path = get_selected_path()
    if file_path is None:
        return
    # Demande confirmation avant la suppression définitive
    if not messagebox.askyesno("Delete",f"Supprimer définitivement {file_path.name} ?",parent=window):
        return
    try:
        # Supprime un fichier ou un lien symbolique
        if file_path.is_symlink() or file_path.is_file():
            file_path.unlink()
        else:
            # Supprime le dossier et tout son contenu
            shutil.rmtree(file_path)
        # Efface le chemin mémorisé s'il correspond à l'élément supprimé
        if clipboard_path is not None and (clipboard_path == file_path or file_path in clipboard_path.parents):
            clipboard_path = None
            clipboard_action = None
        # Actualise l'arbre après la suppression
        refresh_tree()
        status_bar.config(text=f"Supprimé : {file_path.name}")
    except OSError as error:
        messagebox.showerror("Delete",str(error),parent=window)

# Vérifie que le nom ne contient pas de chemin
def valid_name(name):
    if name in (".","..") or any(char in name for char in '<>:"/\\|?*') or name.endswith((" ",".")):
        raise ValueError("Nom invalide. Entrez uniquement un nom de fichier ou de dossier.")

# Renomme l'élément et actualise les chemins
# Fonction (rename_file) réalisée avec l'aide de l'intelligence artificielle (IA). 
def rename_file():
    global root_folder,clipboard_path
    file_path = get_selected_path()
    if file_path is None:
        return
    # Demande le nouveau nom à l'utilisateur
    new_name = simpledialog.askstring("Rename","Nouveau nom :",initialvalue=file_path.name,parent=window)
    if not new_name or new_name == file_path.name:
        return
    try:
        valid_name(new_name) # Vérifie que le nouveau nom est valide
        new_path = file_path.parent/new_name # Construit le nouveau chemin
        # Vérifie que le nouveau nom n'existe pas déjà
        if new_path.exists() or new_path.is_symlink():
            raise ValueError("Un élément porte déjà ce nom.")
        file_path.rename(new_path)# Renomme le fichier ou le dossier
        # Met à jour le dossier racine si nécessaire
        if root_folder == file_path or file_path in root_folder.parents:
            root_folder = new_path/root_folder.relative_to(file_path)
        # Met à jour le chemin mémorisé si nécessaire
        if clipboard_path is not None and (clipboard_path == file_path or file_path in clipboard_path.parents):
            clipboard_path = new_path/clipboard_path.relative_to(file_path)
        # Actualise l'arbre et sélectionne l'élément renommé
        refresh_tree(new_path)
        status_bar.config(text=f"Renommé : {new_name}")
    except (OSError,ValueError) as error:
        messagebox.showerror("Rename",str(error),parent=window)

# Ajoute un nouveau fichier vide dans le dossier sélectionné
def add_file():
    selected_path = get_selected_path()
    if selected_path is None:
        return
    # Si un fichier est sélectionné, utilise son dossier parent
    # Sinon, utilise directement le dossier sélectionné
    folder_path = selected_path.parent if selected_path.is_file() else selected_path
    # Crée une fenêtre secondaire
    add_window = tk.Toplevel(window)
    add_window.title("Add File")
    add_window.geometry("500x160")
    add_window.resizable(False,False)
    add_window.transient(window)
    # Centre la fenêtre secondaire par rapport à la fenêtre principale

    add_window.update_idletasks() # Code réalisé avec l'aide de l'intelligence artificielle (IA).
    x = window.winfo_x()+(window.winfo_width()-add_window.winfo_width())//2 # Code réalisé avec l'aide de l'intelligence artificielle (IA).
    y = window.winfo_y()+(window.winfo_height()-add_window.winfo_height())//2 # Code réalisé avec l'aide de l'intelligence artificielle (IA).
    add_window.geometry(f"+{x}+{y}") # Code réalisé avec l'aide de l'intelligence artificielle (IA).

    # Empêche d'utiliser la fenêtre principale avant de fermer celle-ci
    add_window.grab_set()
    # Ajoute les libellés des champs
    ttk.Label(add_window,text="Nom du fichier :").grid(row=0,column=0,padx=10,pady=(15,5),sticky="w")
    ttk.Label(add_window,text="Type :").grid(row=0,column=1,padx=10,pady=(15,5),sticky="w")
    # Champ dans lequel l'utilisateur saisit le nom du fichier
    name_entry = ttk.Entry(add_window,width=35)
    name_entry.grid(row=1,column=0,padx=10,pady=5)
    # Extensions disponibles pour le nouveau fichier
    file_types = [".txt", ".py", ".bmp", ".docx", ".pptx", ".xlsx", ".zip"]
    # Liste déroulante pour choisir l'extension
    type_box = ttk.Combobox(add_window,values=file_types,state="readonly",width=15)
    type_box.grid(row=1,column=1,padx=10,pady=5)
    type_box.set(".txt")

    # Crée le fichier vide
    def create_file():
        file_name = name_entry.get().strip() # Récupère le nom saisi et retire les espaces superflus
        extension = type_box.get() # Récupère l'extension sélectionnée
        if not file_name:
            status_bar.config(text="Entrez un nom de fichier.")
            return
        try:
            valid_name(file_name) # Vérifie que le nom est valide
            if not file_name.lower().endswith(extension.lower()): # Ajoute l'extension si elle n'est pas déjà présente
                file_name += extension
            new_file = folder_path/file_name # Construit le chemin complet du nouveau fichier
            with new_file.open("xb"): # Crée un fichier vide sans écraser un fichier existant
                pass
            refresh_tree(new_file) # Actualise l'arbre et sélectionne le nouveau fichier
            status_bar.config(text=f"Fichier vide créé : {file_name}")
            add_window.destroy()
        except (OSError,ValueError) as error:
            messagebox.showerror("Add File",str(error),parent=add_window) # Affiche l'erreur si la création échoue

    ttk.Button(add_window,text="Créer",command=create_file).grid(row=2,column=0,padx=10,pady=15,sticky="e")
    ttk.Button(add_window,text="Annuler",command=add_window.destroy).grid(row=2,column=1,padx=10,pady=15,sticky="w")
    name_entry.focus()

# Fenêtre principale
window = tk.Tk()
window.title("Student Project Manager")
window.geometry("1200x700")
window.configure(bg="black")

# Configure les trois colonnes
window.columnconfigure(0,weight=1,uniform="colonnes")
window.columnconfigure(1,weight=1,uniform="colonnes")
window.columnconfigure(2,weight=1,uniform="colonnes")
window.rowconfigure(0,weight=1)

# Menu
menu_bar = tk.Menu(window)
file_menu = tk.Menu(menu_bar,tearoff=False)
file_menu.add_command(label="Display Directory",command=display_directory)
file_menu.add_separator()
file_menu.add_command(label="Quit",command=window.destroy)
menu_bar.add_cascade(label="File",menu=file_menu)
tools_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Tools",menu=tools_menu)
help_menu = tk.Menu(menu_bar,tearoff=False)
menu_bar.add_cascade(label="Help",menu=help_menu)
window.config(menu=menu_bar)

# Arbre des fichiers
tree_frame = ttk.LabelFrame(window,text="Directory Tree",padding=10)
tree_frame.grid(row=0,column=0,sticky="nsew",padx=10,pady=10)
tree_frame.rowconfigure(0,weight=1)
tree_frame.columnconfigure(0,weight=1)
tree = ttk.Treeview(tree_frame,selectmode="browse")
tree.heading("#0",text="Directory")
tree.grid(row=0,column=0,sticky="nsew")
tree.bind("<<TreeviewSelect>>",display_file_info)

# Informations du fichier
info_frame = ttk.LabelFrame(window,text="File Information",padding=10)
info_frame.grid(row=0,column=1,sticky="nsew",padx=10,pady=10)
info_frame.columnconfigure(0,weight=1)
info_entries = []
# Liste qui contient les champs d'informations
labels = ["Name:","Path:","Type:","Size:","Modified:","Permissions:"]
for i,texte in enumerate(labels):
    ttk.Label(info_frame,text=texte).grid(row=i*2,column=0,sticky="w",pady=(5,2))
    entry = ttk.Entry(info_frame)
    entry.grid(row=i*2+1,column=0,sticky="ew",pady=(0,10))
    info_entries.append(entry)

# Zone des actions
project_frame = ttk.LabelFrame(window,text="Student Project Area",padding=10)
project_frame.grid(row=0,column=2,sticky="nsew",padx=10,pady=10)
project_frame.columnconfigure(0,weight=1)
project_frame.columnconfigure(1,weight=1)
ttk.Button(project_frame,text="Open",command=open_file).grid(row=0,column=0,sticky="ew",padx=5,pady=5)
ttk.Button(project_frame,text="Rename",command=rename_file).grid(row=0,column=1,sticky="ew",padx=5,pady=5)
ttk.Button(project_frame,text="Delete",command=delete_file).grid(row=3,column=0,sticky="ew",padx=5,pady=5)
ttk.Button(project_frame,text="Add File",command=add_file).grid(row=3,column=1,sticky="ew",padx=5,pady=5)
status_bar = ttk.Label(window,text="...",relief="sunken",anchor="w")
status_bar.grid(row=1,column=0,columnspan=3,sticky="ew",padx=10,pady=(0,10))
window.mainloop()
