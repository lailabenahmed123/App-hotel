# ================= IMPORTS =================
import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as msg
from db import get_connection
import re
import csv

# ================= CONFIG THEME =================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# ================= FENETRE =================
root = ctk.CTk()
root.title("Gestion Clients")
root.geometry("1100x650")
root.minsize(900, 500)

# ================= SWITCH THEME =================
def apply_scrollbar_style():
    style = ttk.Style()
    mode = ctk.get_appearance_mode()
    if mode == "Dark":
        style.configure("Vertical.TScrollbar",
            background="#2b2b2b", troughcolor="#1a1a1a",
            arrowcolor="white", bordercolor="#2b2b2b")
        style.configure("Horizontal.TScrollbar",
            background="#2b2b2b", troughcolor="#1a1a1a",
            arrowcolor="white", bordercolor="#2b2b2b")
    else:
        style.configure("Vertical.TScrollbar",
            background="#d0d0d0", troughcolor="#f0f0f0",
            arrowcolor="black", bordercolor="#d0d0d0")
        style.configure("Horizontal.TScrollbar",
            background="#d0d0d0", troughcolor="#f0f0f0",
            arrowcolor="black", bordercolor="#d0d0d0")

def toggle_theme():
    current = ctk.get_appearance_mode()
    if current == "Light":
        ctk.set_appearance_mode("dark")
    else:
        ctk.set_appearance_mode("light")
    apply_scrollbar_style()

theme_btn = ctk.CTkButton(root, text="🌙 / ☀️", width=50, command=toggle_theme)
theme_btn.pack(anchor="ne", padx=10, pady=10)

# ================= FRAME PRINCIPAL =================
main_frame = ctk.CTkFrame(root)
main_frame.pack(fill="both", expand=True, padx=10, pady=10)

# ================= TREEVIEW + SCROLLBARS =================
tree_frame = ctk.CTkFrame(main_frame)
tree_frame.pack(fill="both", expand=True, pady=10)

tree = ttk.Treeview(tree_frame, columns=("id","nom","prenom","email"), show="headings")

tree.heading("id", text="ID")
tree.heading("nom", text="Nom")
tree.heading("prenom", text="Prénom")
tree.heading("email", text="Email")

tree.column("id", width=50, anchor="center")
tree.column("nom", width=150)
tree.column("prenom", width=150)
tree.column("email", width=200)

scrollbar_y = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
scrollbar_x = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

scrollbar_y.pack(side="right", fill="y")
scrollbar_x.pack(side="bottom", fill="x")
tree.pack(fill="both", expand=True)

# ================= FORMULAIRE =================
form_frame = ctk.CTkFrame(main_frame)
form_frame.pack(pady=10)

def set_placeholder(entry, text):
    entry.insert(0, text)
    entry.configure(text_color=("black", "white"))

    def on_focus_in(event):
        if entry.get() == text:
            entry.delete(0, "end")
            entry.configure(text_color=("black", "white"))

    def on_focus_out(event):
        if entry.get() == "":
            entry.insert(0, text)
            entry.configure(text_color=("black", "white"))

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)

def create_input(parent, icon, placeholder, row):
    frame = ctk.CTkFrame(parent)
    frame.grid(row=row, column=0, pady=8, padx=10)

    ctk.CTkLabel(frame, text=icon, width=30).pack(side="left", padx=5)

    entry = ctk.CTkEntry(frame, width=250)
    entry.pack(side="left", padx=5)

    set_placeholder(entry, placeholder)

    return entry

entry_nom = create_input(form_frame, "👤", "Nom", 0)
entry_prenom = create_input(form_frame, "👤", "Prénom", 1)
entry_email = create_input(form_frame, "📧", "Email", 2)

# ================= BARRE DE RECHERCHE =================
def search_clients(event=None):
    keyword = entry_search.get().strip()
    if not keyword:
        load_clients()
        return
    tree.delete(*tree.get_children())
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, nom, prenom, email 
               FROM Clients 
               WHERE nom LIKE %s 
               OR prenom LIKE %s 
               OR email LIKE %s""",
            (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
        )
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    except Exception as e:
        msg.showerror("Erreur", str(e))
    finally:
        cursor.close()
        conn.close()

search_frame = ctk.CTkFrame(main_frame)
search_frame.pack(pady=5, padx=10, fill="x")

ctk.CTkLabel(search_frame, text="🔍 Recherche :").pack(side="left", padx=(10, 5))

entry_search = ctk.CTkEntry(search_frame, width=300, placeholder_text="Nom, prénom ou email...")
entry_search.pack(side="left", padx=5)

ctk.CTkButton(search_frame, text="Rechercher", width=110, command=search_clients).pack(side="left", padx=5)
ctk.CTkButton(search_frame, text="✖ Effacer", width=90, command=lambda: [entry_search.delete(0, "end"), load_clients()]).pack(side="left", padx=5)

entry_search.bind("<Return>", search_clients)

# ================= BOUTONS =================
btn_frame = ctk.CTkFrame(main_frame)
btn_frame.pack(pady=10)

ctk.CTkButton(btn_frame, text="Nouveau", command=lambda: clear_fields()).grid(row=0, column=0, padx=10)
ctk.CTkButton(btn_frame, text="Ajouter", command=lambda: add_client()).grid(row=0, column=1, padx=10)
ctk.CTkButton(btn_frame, text="Modifier", command=lambda: edit_client()).grid(row=0, column=2, padx=10)
ctk.CTkButton(btn_frame, text="Supprimer", command=lambda: delete_client()).grid(row=0, column=3, padx=10)

# ================= EXPORT CSV =================
def export_csv():
    with open("clients.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["ID","Nom","Prenom","Email"])
        for row in tree.get_children():
            writer.writerow(tree.item(row)['values'])
    msg.showinfo("Export", "Export réussi")

ctk.CTkButton(root, text="Exporter CSV", command=export_csv).pack(pady=5)

# ================= REMPLISSAGE FORMULAIRE =================
def fill_form(event=None):
    selected = tree.focus()
    if selected:
        values = tree.item(selected)['values']
        entry_nom.delete(0, "end")
        entry_prenom.delete(0, "end")
        entry_email.delete(0, "end")
        entry_nom.insert(0, values[1])
        entry_prenom.insert(0, values[2])
        entry_email.insert(0, values[3])
        entry_nom.configure(text_color=("black", "white"))
        entry_prenom.configure(text_color=("black", "white"))
        entry_email.configure(text_color=("black", "white"))

tree.bind("<<TreeviewSelect>>", fill_form)

# ================= VALIDATION EMAIL =================
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

# ================= LOAD =================
def load_clients():
    tree.delete(*tree.get_children())
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nom, prenom, email FROM Clients")
        for row in cursor.fetchall():
            tree.insert("", "end", values=row)
    except Exception as e:
        msg.showerror("Erreur", str(e))
    finally:
        cursor.close()
        conn.close()

# ================= CLEAR =================
def clear_fields():
    tree.selection_remove(tree.selection())
    tree.focus("")
    for entry, text in [
        (entry_nom, "Nom"),
        (entry_prenom, "Prénom"),
        (entry_email, "Email")
    ]:
        entry.delete(0, "end")
        entry.insert(0, text)
        entry.configure(text_color=("black", "white"))

# ================= ADD =================
def add_client():
    nom = entry_nom.get()
    prenom = entry_prenom.get()
    email = entry_email.get()

    if nom in ["", "Nom"] or prenom in ["", "Prénom"] or email in ["", "Email"]:
        msg.showerror("Erreur", "Remplir tous les champs")
        return

    if not is_valid_email(email):
        msg.showerror("Erreur", "Email invalide")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Clients WHERE email=%s", (email,))
        if cursor.fetchone():
            msg.showerror("Erreur", "Email existe déjà")
            return
        cursor.execute(
            "INSERT INTO Clients (nom, prenom, email) VALUES (%s,%s,%s)",
            (nom, prenom, email)
        )
        conn.commit()
        load_clients()
        clear_fields()
    except Exception as e:
        msg.showerror("Erreur", str(e))
    finally:
        cursor.close()
        conn.close()

# ================= EDIT =================
def edit_client():
    selected = tree.focus()
    if not selected:
        msg.showerror("Erreur", "Sélectionnez un client")
        return

    values = tree.item(selected)['values']
    client_id = values[0]

    nom = entry_nom.get().strip()
    prenom = entry_prenom.get().strip()
    email = entry_email.get().strip()

    if nom == "Nom": nom = values[1]
    if prenom == "Prénom": prenom = values[2]
    if email == "Email": email = values[3]

    if not is_valid_email(email):
        msg.showerror("Erreur", "Email invalide")
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM Clients WHERE email=%s AND id!=%s",
            (email, client_id)
        )
        if cursor.fetchone():
            msg.showerror("Erreur", "Email déjà utilisé")
            return
        cursor.execute(
            "UPDATE Clients SET nom=%s, prenom=%s, email=%s WHERE id=%s",
            (nom, prenom, email, client_id)
        )
        conn.commit()
        load_clients()
        clear_fields()
        msg.showinfo("Succès", "Client modifié avec succès")
    except Exception as e:
        msg.showerror("Erreur", str(e))
    finally:
        cursor.close()
        conn.close()

# ================= DELETE =================
def delete_client():
    selected = tree.focus()
    if not selected:
        msg.showerror("Erreur", "Sélectionner un client")
        return

    if not msg.askyesno("Confirmation", "Supprimer ?"):
        return

    try:
        conn = get_connection()
        cursor = conn.cursor()
        client_id = tree.item(selected)['values'][0]
        cursor.execute("DELETE FROM Clients WHERE id=%s", (client_id,))
        conn.commit()
        load_clients()
    except Exception as e:
        msg.showerror("Erreur", str(e))
    finally:
        cursor.close()
        conn.close()

# ================= INIT =================
apply_scrollbar_style()
load_clients()
root.mainloop()