import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
import os
import shutil
import subprocess
from datetime import datetime

# ===== STYLE =====
bg = "#0a0a0a"
fg = "#00ffcc"
btn_bg = "#1a1a1a"
btn_fg = "#00ffcc"
btn_danger = "#cc3333"

FONT = ("Segoe UI", 10)
FONT_BOLD = ("Segoe UI", 10, "bold")
FONT_TITLE = ("Segoe UI", 16, "bold")

# ===== DOSSIERS SYSTÈME INTERDITS =====
DOSSIERS_INTERDITS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
    os.path.expanduser("~\\AppData"),
]

def est_interdit(chemin):
    chemin = os.path.abspath(chemin)
    for interdit in DOSSIERS_INTERDITS:
        if chemin.lower().startswith(os.path.abspath(interdit).lower()):
            return True
    return False

# ===== JOURNAL DES ACTIONS =====
def journaliser(action, details):
    try:
        with open("laurent_manager_log.txt", "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action} : {details}\n")
    except:
        pass

# ===== FENÊTRE PRINCIPALE =====
root = tk.Tk()
root.title("Laurent Manager")
root.geometry("1050x750")
root.configure(bg=bg)

presse_papier = []
action_presse = ""

# ===== TITRE =====
tk.Label(root, text="📁 LAURENT MANAGER", font=FONT_TITLE, fg=fg, bg=bg).pack(pady=(10, 0))
tk.Label(root, text="Créé par Laurent Bajika", font=FONT, fg="#aaaaaa", bg=bg).pack(pady=(0, 10))

# ===== BARRE DE CHEMIN =====
frame_path = tk.Frame(root, bg=bg)
frame_path.pack(fill=tk.X, padx=10, pady=5)

tk.Label(frame_path, text="📂 Dossier :", font=FONT_BOLD, fg=fg, bg=bg).pack(side=tk.LEFT)

chemin_var = tk.StringVar(value=os.path.expanduser("~"))
entry_path = tk.Entry(frame_path, textvariable=chemin_var, font=FONT, bg="#1a1a1a", fg="white", insertbackground="white", relief="flat")
entry_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

def parcourir():
    dossier = filedialog.askdirectory()
    if dossier:
        if est_interdit(dossier):
            messagebox.showerror("Accès refusé", "⛔ Ce dossier est protégé par Laurent Manager.")
            return
        chemin_var.set(dossier)
        lister_fichiers()

btn_parcourir = tk.Button(frame_path, text="Parcourir", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=parcourir)
btn_parcourir.pack(side=tk.LEFT, padx=5)

# ===== BARRE DE RECHERCHE =====
frame_search = tk.Frame(root, bg=bg)
frame_search.pack(fill=tk.X, padx=10, pady=5)

tk.Label(frame_search, text="🔍 Rechercher :", font=FONT_BOLD, fg=fg, bg=bg).pack(side=tk.LEFT)

recherche_var = tk.StringVar()
entry_search = tk.Entry(frame_search, textvariable=recherche_var, font=FONT, bg="#1a1a1a", fg="white", insertbackground="white", relief="flat")
entry_search.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

def rechercher(event=None):
    tree.delete(*tree.get_children())
    dossier = chemin_var.get()
    filtre = recherche_var.get().lower()
    try:
        for item in os.listdir(dossier):
            if filtre in item.lower():
                chemin = os.path.join(dossier, item)
                if os.path.isdir(chemin):
                    type_item = "📁 Dossier"
                    taille = "-"
                else:
                    type_item = "📄 Fichier"
                    taille = f"{os.path.getsize(chemin) / 1024:.1f} Ko"
                tree.insert("", tk.END, values=(item, type_item, taille))
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

entry_search.bind("<KeyRelease>", rechercher)

# ===== BARRE D'OUTILS =====
frame_tools = tk.Frame(root, bg=bg)
frame_tools.pack(fill=tk.X, padx=10, pady=5)

def retour():
    parent = os.path.dirname(chemin_var.get())
    if parent and not est_interdit(parent):
        chemin_var.set(parent)
        recherche_var.set("")
        lister_fichiers()

def nouveau_dossier():
    nom = simpledialog.askstring("Nouveau dossier", "Nom du dossier :")
    if nom:
        try:
            os.makedirs(os.path.join(chemin_var.get(), nom))
            lister_fichiers()
            journaliser("NOUVEAU DOSSIER", nom)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

def nouveau_fichier():
    nom = simpledialog.askstring("Nouveau fichier", "Nom du fichier (avec extension) :")
    if nom:
        try:
            open(os.path.join(chemin_var.get(), nom), "w").close()
            lister_fichiers()
            journaliser("NOUVEAU FICHIER", nom)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

def copier_chemin():
    item = tree.selection()
    if item:
        chemin_complet = os.path.join(chemin_var.get(), tree.item(item[0], "values")[0])
        root.clipboard_clear()
        root.clipboard_append(chemin_complet)
        status.config(text=f"📋 Chemin copié : {chemin_complet}")

def tout_selectionner():
    for item in tree.get_children():
        tree.selection_add(item)

def tout_deselectionner():
    tree.selection_remove(*tree.selection())

btn_retour = tk.Button(frame_tools, text="⬅️ Retour", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=retour)
btn_retour.pack(side=tk.LEFT, padx=5)

btn_new_dossier = tk.Button(frame_tools, text="📁 Nouveau dossier", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=nouveau_dossier)
btn_new_dossier.pack(side=tk.LEFT, padx=5)

btn_new_fichier = tk.Button(frame_tools, text="📄 Nouveau fichier", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=nouveau_fichier)
btn_new_fichier.pack(side=tk.LEFT, padx=5)

btn_copy_path = tk.Button(frame_tools, text="🔗 Copier le chemin", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=copier_chemin)
btn_copy_path.pack(side=tk.LEFT, padx=5)

btn_tout_sel = tk.Button(frame_tools, text="✅ Tout sélectionner", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=tout_selectionner)
btn_tout_sel.pack(side=tk.LEFT, padx=5)

btn_tout_desel = tk.Button(frame_tools, text="❌ Désélectionner", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=tout_deselectionner)
btn_tout_desel.pack(side=tk.LEFT, padx=5)

# ===== LISTE DES FICHIERS =====
frame_liste = tk.Frame(root, bg=bg)
frame_liste.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

colonnes = ("Nom", "Type", "Taille")
tree = ttk.Treeview(frame_liste, columns=colonnes, show="headings", selectmode="extended")
tree.heading("Nom", text="Nom", command=lambda: trier("Nom"))
tree.heading("Type", text="Type", command=lambda: trier("Type"))
tree.heading("Taille", text="Taille", command=lambda: trier("Taille"))
tree.column("Nom", width=450)
tree.column("Type", width=150)
tree.column("Taille", width=150)

scrollbar = ttk.Scrollbar(frame_liste, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)
tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# ===== TRIER =====
ordre_tri = {"colonne": "Nom", "croissant": True}

def trier(colonne):
    ordre_tri["croissant"] = not ordre_tri["croissant"] if ordre_tri["colonne"] == colonne else True
    ordre_tri["colonne"] = colonne
    items = [(tree.item(i, "values"), i) for i in tree.get_children()]
    items.sort(key=lambda x: x[0][colonnes.index(colonne)], reverse=not ordre_tri["croissant"])
    for index, (_, i) in enumerate(items):
        tree.move(i, "", index)

# ===== LISTER LES FICHIERS =====
def lister_fichiers():
    tree.delete(*tree.get_children())
    dossier = chemin_var.get()
    try:
        fichiers = os.listdir(dossier)
        for item in fichiers:
            chemin = os.path.join(dossier, item)
            if os.path.isdir(chemin):
                type_item = "📁 Dossier"
                taille = "-"
            else:
                type_item = "📄 Fichier"
                taille = f"{os.path.getsize(chemin) / 1024:.1f} Ko"
            tree.insert("", tk.END, values=(item, type_item, taille))
        # Mise à jour du nombre d'éléments
        nb_elements.config(text=f"📊 {len(fichiers)} élément(s)")
    except Exception as e:
        messagebox.showerror("Erreur", str(e))

# ===== DOUBLE-CLIC =====
def double_clic(event):
    item = tree.selection()
    if item:
        nom = tree.item(item[0], "values")[0]
        chemin = os.path.join(chemin_var.get(), nom)
        if os.path.isdir(chemin):
            if est_interdit(chemin):
                messagebox.showerror("Accès refusé", "⛔ Ce dossier est protégé.")
                return
            chemin_var.set(chemin)
            recherche_var.set("")
            lister_fichiers()
        else:
            try:
                os.startfile(chemin)
                journaliser("OUVRIR", chemin)
            except Exception as e:
                messagebox.showerror("Erreur", str(e))

tree.bind("<Double-1>", double_clic)

# ===== COPIER / COUPER / COLLER =====
def copier():
    global presse_papier, action_presse
    presse_papier = [os.path.join(chemin_var.get(), tree.item(i, "values")[0]) for i in tree.selection()]
    action_presse = "copier"
    status.config(text=f"✅ Copié : {len(presse_papier)} élément(s)")
    journaliser("COPIER", f"{len(presse_papier)} élément(s)")

def couper():
    global presse_papier, action_presse
    if not messagebox.askyesno("Confirmation", "Couper les fichiers sélectionnés ?"):
        return
    presse_papier = [os.path.join(chemin_var.get(), tree.item(i, "values")[0]) for i in tree.selection()]
    action_presse = "couper"
    status.config(text=f"✂️ Coupé : {len(presse_papier)} élément(s)")
    journaliser("COUPER", f"{len(presse_papier)} élément(s)")

def coller():
    global presse_papier, action_presse
    if not presse_papier:
        messagebox.showinfo("Info", "Rien à coller.")
        return
    if est_interdit(chemin_var.get()):
        messagebox.showerror("Accès refusé", "⛔ Coller ici est interdit.")
        return
    dossier_dest = chemin_var.get()
    for chemin in presse_papier:
        nom = os.path.basename(chemin)
        destination = os.path.join(dossier_dest, nom)
        try:
            if action_presse == "copier":
                if os.path.isdir(chemin):
                    shutil.copytree(chemin, destination)
                else:
                    shutil.copy2(chemin, destination)
            elif action_presse == "couper":
                shutil.move(chemin, destination)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    lister_fichiers()
    status.config(text=f"📋 Collé dans : {dossier_dest}")
    journaliser("COLLER", f"vers {dossier_dest}")
    presse_papier = []
    action_presse = ""

# ===== SUPPRIMER =====
def supprimer():
    items = tree.selection()
    if not items:
        return
    if est_interdit(chemin_var.get()):
        messagebox.showerror("Accès refusé", "⛔ Suppression interdite dans ce dossier.")
        return
    if not messagebox.askyesno("⚠️ Confirmation", f"⚠️ Supprimer DÉFINITIVEMENT {len(items)} élément(s) ?\n\nCette action est irréversible."):
        return
    for i in items:
        chemin = os.path.join(chemin_var.get(), tree.item(i, "values")[0])
        try:
            if os.path.isdir(chemin):
                shutil.rmtree(chemin)
            else:
                os.remove(chemin)
            journaliser("SUPPRIMER", chemin)
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
    lister_fichiers()
    status.config(text="🗑️ Supprimé")

# ===== RENOMMER =====
def renommer():
    items = tree.selection()
    if len(items) != 1:
        messagebox.showinfo("Info", "Sélectionne UN seul fichier.")
        return
    if est_interdit(chemin_var.get()):
        messagebox.showerror("Accès refusé", "⛔ Renommage interdit dans ce dossier.")
        return
    ancien_nom = tree.item(items[0], "values")[0]
    nouveau_nom = simpledialog.askstring("Renommer", "Nouveau nom :", initialvalue=ancien_nom)
    if nouveau_nom:
        try:
            os.rename(os.path.join(chemin_var.get(), ancien_nom), os.path.join(chemin_var.get(), nouveau_nom))
            lister_fichiers()
            status.config(text=f"✏️ Renommé en : {nouveau_nom}")
            journaliser("RENOMMER", f"{ancien_nom} → {nouveau_nom}")
        except Exception as e:
            messagebox.showerror("Erreur", str(e))

# ===== BARRE DE BOUTONS =====
frame_actions = tk.Frame(root, bg=bg)
frame_actions.pack(pady=10)

btn_copier = tk.Button(frame_actions, text="📋 Copier", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=copier)
btn_copier.pack(side=tk.LEFT, padx=5)

btn_couper = tk.Button(frame_actions, text="✂️ Couper", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=couper)
btn_couper.pack(side=tk.LEFT, padx=5)

btn_coller = tk.Button(frame_actions, text="📥 Coller", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=coller)
btn_coller.pack(side=tk.LEFT, padx=5)

btn_renommer = tk.Button(frame_actions, text="✏️ Renommer", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=renommer)
btn_renommer.pack(side=tk.LEFT, padx=5)

btn_supprimer = tk.Button(frame_actions, text="🗑️ Supprimer", font=FONT_BOLD, bg=btn_danger, fg="white", relief="flat", command=supprimer)
btn_supprimer.pack(side=tk.LEFT, padx=5)

btn_refresh = tk.Button(frame_actions, text="🔄 Actualiser", font=FONT_BOLD, bg=btn_bg, fg=btn_fg, relief="flat", command=lister_fichiers)
btn_refresh.pack(side=tk.LEFT, padx=5)

# ===== BARRE DE STATUT =====
frame_status = tk.Frame(root, bg=bg)
frame_status.pack(fill=tk.X, padx=10, pady=(0, 10))

status = tk.Label(frame_status, text="💡 Prêt", font=FONT, fg="#888888", bg=bg, anchor="w")
status.pack(side=tk.LEFT)

nb_elements = tk.Label(frame_status, text="📊 0 élément(s)", font=FONT_BOLD, fg=fg, bg=bg)
nb_elements.pack(side=tk.RIGHT)

# ===== LANCEMENT =====
lister_fichiers()
root.mainloop()