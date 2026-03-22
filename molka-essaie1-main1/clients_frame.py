# clients_frame.py
import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as msg
from db import get_connection
import re
import csv

class ClientsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.build_ui()
        self.load_clients()

    def build_ui(self):
        ctk.CTkLabel(
            self.parent,
            text="👤 Gestion des Clients",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)

        # ── Recherche ──────────────────────────
        search_frame = ctk.CTkFrame(self.parent)
        search_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(search_frame, text="🔍 Recherche :").pack(side="left", padx=5)
        self.entry_search = ctk.CTkEntry(
            search_frame, width=300,
            placeholder_text="Nom, prénom ou email..."
        )
        self.entry_search.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Rechercher",
            width=110, command=self.search_clients).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="✖ Effacer", width=90,
            command=lambda: [self.entry_search.delete(0,"end"), self.load_clients()]
        ).pack(side="left", padx=5)
        self.entry_search.bind("<Return>", self.search_clients)

        # ── Formulaire ─────────────────────────
        form_frame = ctk.CTkFrame(self.parent)
        form_frame.pack(pady=10)

        self.entry_nom    = self._create_input(form_frame, "👤", "Nom", 0)
        self.entry_prenom = self._create_input(form_frame, "👤", "Prénom", 1)
        self.entry_email  = self._create_input(form_frame, "📧", "Email", 2)

        # ── Boutons ────────────────────────────
        btn_frame = ctk.CTkFrame(self.parent)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="➕ Ajouter",
            command=self.add_client).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="✏️ Modifier",
            command=self.edit_client).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_frame, text="🗑️ Supprimer",
            fg_color="red", hover_color="darkred",
            command=self.delete_client).grid(row=0, column=2, padx=10)
        ctk.CTkButton(btn_frame, text="📤 Export CSV",
            command=self.export_csv).grid(row=0, column=3, padx=10)
        ctk.CTkButton(btn_frame, text="🔄 Nouveau",
            command=self.clear_fields).grid(row=0, column=4, padx=10)

        # ── Tableau ────────────────────────────
        tree_frame = ctk.CTkFrame(self.parent)
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("id", "nom", "prenom", "email"),
            show="headings"
        )
        self.tree.heading("id",     text="ID")
        self.tree.heading("nom",    text="Nom")
        self.tree.heading("prenom", text="Prénom")
        self.tree.heading("email",  text="Email")

        self.tree.column("id",     width=50,  anchor="center")
        self.tree.column("nom",    width=150)
        self.tree.column("prenom", width=150)
        self.tree.column("email",  width=200)

        sy = ttk.Scrollbar(tree_frame, orient="vertical",   command=self.tree.yview)
        sx = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right",  fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.fill_form)

    def _create_input(self, parent, icon, placeholder, row):
        frame = ctk.CTkFrame(parent)
        frame.grid(row=row, column=0, pady=8, padx=10)
        ctk.CTkLabel(frame, text=icon, width=30).pack(side="left", padx=5)
        entry = ctk.CTkEntry(frame, width=250, placeholder_text=placeholder)
        entry.pack(side="left", padx=5)
        return entry

    def is_valid_email(self, email):
        return re.match(r"^[\w\.-]+@[\w\.-]+\.\w+$", email)

    def load_clients(self):
        self.tree.delete(*self.tree.get_children())
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nom, prenom, email FROM Clients")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def search_clients(self, event=None):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_clients()
            return
        self.tree.delete(*self.tree.get_children())
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                """SELECT id, nom, prenom, email FROM Clients
                   WHERE nom LIKE %s OR prenom LIKE %s OR email LIKE %s""",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%")
            )
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def fill_form(self, event=None):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected)['values']
            self.entry_nom.delete(0, "end")
            self.entry_nom.insert(0, values[1])
            self.entry_prenom.delete(0, "end")
            self.entry_prenom.insert(0, values[2])
            self.entry_email.delete(0, "end")
            self.entry_email.insert(0, values[3])

    def clear_fields(self):
        self.tree.selection_remove(self.tree.selection())
        self.entry_nom.delete(0, "end")
        self.entry_prenom.delete(0, "end")
        self.entry_email.delete(0, "end")

    def add_client(self):
        nom    = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        email  = self.entry_email.get().strip()

        if not nom or not prenom or not email:
            msg.showerror("Erreur", "Remplir tous les champs")
            return
        if not self.is_valid_email(email):
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
            self.load_clients()
            self.clear_fields()
            msg.showinfo("Succès", "Client ajouté !")
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def edit_client(self):
        selected = self.tree.focus()
        if not selected:
            msg.showerror("Erreur", "Sélectionnez un client")
            return
        values    = self.tree.item(selected)['values']
        client_id = values[0]
        nom    = self.entry_nom.get().strip()
        prenom = self.entry_prenom.get().strip()
        email  = self.entry_email.get().strip()

        if not self.is_valid_email(email):
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
            self.load_clients()
            self.clear_fields()
            msg.showinfo("Succès", "Client modifié !")
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def delete_client(self):
        selected = self.tree.focus()
        if not selected:
            msg.showerror("Erreur", "Sélectionner un client")
            return
        if not msg.askyesno("Confirmation", "Supprimer ?"):
            return
        try:
            conn = get_connection()
            cursor = conn.cursor()
            client_id = self.tree.item(selected)['values'][0]
            cursor.execute("DELETE FROM Clients WHERE id=%s", (client_id,))
            conn.commit()
            self.load_clients()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def export_csv(self):
        with open("clients.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Nom", "Prénom", "Email"])
            for row in self.tree.get_children():
                writer.writerow(self.tree.item(row)['values'])
        msg.showinfo("Export", "Export CSV réussi ✅")

