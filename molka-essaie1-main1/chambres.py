# views/chambres.py
import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as msg
from db import get_connection
import csv

class ChambresWindow:
    def __init__(self, parent):
        self.parent = parent
        self.selected_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        ctk.CTkLabel(
            self.parent,
            text="🛏️ Gestion des Chambres",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)

        # ── Recherche ──────────────────────────
        search_frame = ctk.CTkFrame(self.parent)
        search_frame.pack(pady=5, padx=10, fill="x")

        ctk.CTkLabel(search_frame, text="🔍 Recherche :").pack(side="left", padx=5)
        self.entry_search = ctk.CTkEntry(search_frame, width=250,
            placeholder_text="Numéro ou type...")
        self.entry_search.pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="Rechercher", width=110,
            command=self.search).pack(side="left", padx=5)
        ctk.CTkButton(search_frame, text="✖ Effacer", width=90,
            command=lambda: [self.entry_search.delete(0,"end"), self.load_data()]
        ).pack(side="left", padx=5)

        # ── Formulaire ─────────────────────────
        form = ctk.CTkFrame(self.parent)
        form.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form, text="Numéro :").grid(row=0, column=0, padx=10, pady=8)
        self.entry_numero = ctk.CTkEntry(form, width=120)
        self.entry_numero.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(form, text="Type :").grid(row=0, column=2, padx=10)
        self.entry_type = ctk.CTkEntry(form, width=120)
        self.entry_type.grid(row=0, column=3, padx=10)

        ctk.CTkLabel(form, text="Prix :").grid(row=0, column=4, padx=10)
        self.entry_prix = ctk.CTkEntry(form, width=100)
        self.entry_prix.grid(row=0, column=5, padx=10)

        # ── Boutons ────────────────────────────
        btn_frame = ctk.CTkFrame(self.parent)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="➕ Ajouter",
            command=self.ajouter).grid(row=0, column=0, padx=10)
        ctk.CTkButton(btn_frame, text="✏️ Modifier",
            command=self.modifier).grid(row=0, column=1, padx=10)
        ctk.CTkButton(btn_frame, text="🗑️ Supprimer",
            fg_color="red", hover_color="darkred",
            command=self.supprimer).grid(row=0, column=2, padx=10)
        ctk.CTkButton(btn_frame, text="🔄 Actualiser",
            command=self.load_data).grid(row=0, column=3, padx=10)
        ctk.CTkButton(btn_frame, text="📤 Export CSV",
            command=self.export_csv).grid(row=0, column=4, padx=10)

        # ── Tableau ────────────────────────────
        tree_frame = ctk.CTkFrame(self.parent)
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "Numéro", "Type", "Prix", "Disponible"),
            show="headings"
        )
        for col in ("ID", "Numéro", "Type", "Prix", "Disponible"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        sy = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        sx = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=sy.set, xscrollcommand=sx.set)
        sy.pack(side="right", fill="y")
        sx.pack(side="bottom", fill="x")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM chambres")
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def search(self):
        keyword = self.entry_search.get().strip()
        if not keyword:
            self.load_data()
            return
        for row in self.tree.get_children():
            self.tree.delete(row)
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM chambres WHERE numero LIKE %s OR type LIKE %s",
                (f"%{keyword}%", f"%{keyword}%")
            )
            for row in cursor.fetchall():
                self.tree.insert("", "end", values=row)
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def on_select(self, event):
        selected = self.tree.focus()
        if selected:
            values = self.tree.item(selected, "values")
            self.selected_id = values[0]
            self.entry_numero.delete(0, "end")
            self.entry_numero.insert(0, values[1])
            self.entry_type.delete(0, "end")
            self.entry_type.insert(0, values[2])
            self.entry_prix.delete(0, "end")
            self.entry_prix.insert(0, values[3])

    def ajouter(self):
        numero = self.entry_numero.get().strip()
        type_  = self.entry_type.get().strip()
        prix   = self.entry_prix.get().strip()

        if not numero or not type_ or not prix:
            msg.showwarning("Attention", "Remplissez tous les champs !")
            return

        try:
            prix_float = float(prix)
        except ValueError:
            msg.showerror("Erreur", "Le prix doit être un nombre !")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO chambres (numero, type, prix) VALUES (%s, %s, %s)",
                (numero, type_, prix_float)
            )
            conn.commit()
            msg.showinfo("Succès", "Chambre ajoutée !")
            self.load_data()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def modifier(self):
        if not self.selected_id:
            msg.showwarning("Attention", "Sélectionnez une chambre !")
            return
        numero = self.entry_numero.get().strip()
        type_  = self.entry_type.get().strip()
        prix   = self.entry_prix.get().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE chambres SET numero=%s, type=%s, prix=%s WHERE id=%s",
                (numero, type_, prix, self.selected_id)
            )
            conn.commit()
            msg.showinfo("Succès", "Chambre modifiée !")
            self.load_data()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def supprimer(self):
        if not self.selected_id:
            msg.showwarning("Attention", "Sélectionnez une chambre !")
            return
        if msg.askyesno("Confirmation", "Supprimer cette chambre ?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM chambres WHERE id=%s",
                    (self.selected_id,)
                )
                conn.commit()
                msg.showinfo("Succès", "Chambre supprimée !")
                self.load_data()
            except Exception as e:
                msg.showerror("Erreur", str(e))
            finally:
                cursor.close()
                conn.close()

    def export_csv(self):
        with open("chambres.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "Numéro", "Type", "Prix", "Disponible"])
            for row in self.tree.get_children():
                writer.writerow(self.tree.item(row)['values'])
        msg.showinfo("Export", "Export CSV réussi ✅")