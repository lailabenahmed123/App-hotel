# views/factures.py
import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as msg
from db import get_connection
import csv

class FacturesWindow:
    def __init__(self, parent):
        self.parent = parent
        self.selected_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        ctk.CTkLabel(
            self.parent,
            text="🧾 Gestion des Factures",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)

        # ── Formulaire ─────────────────────────
        form = ctk.CTkFrame(self.parent)
        form.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form, text="ID Réservation :").grid(row=0, column=0, padx=10, pady=8)
        self.entry_reservation = ctk.CTkEntry(form, width=120)
        self.entry_reservation.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(form, text="Montant :").grid(row=0, column=2, padx=10)
        self.entry_montant = ctk.CTkEntry(form, width=120)
        self.entry_montant.grid(row=0, column=3, padx=10)

        ctk.CTkLabel(form, text="Date (YYYY-MM-DD) :").grid(row=1, column=0, padx=10, pady=8)
        self.entry_date = ctk.CTkEntry(form, width=150)
        self.entry_date.grid(row=1, column=1, padx=10)

        ctk.CTkLabel(form, text="Statut :").grid(row=1, column=2, padx=10)
        self.entry_statut = ctk.CTkEntry(form, width=120)
        self.entry_statut.grid(row=1, column=3, padx=10)
        self.entry_statut.insert(0, "impayée")

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
        ctk.CTkButton(btn_frame, text="📤 Export CSV",
            command=self.export_csv).grid(row=0, column=3, padx=10)

        # ── Tableau ────────────────────────────
        tree_frame = ctk.CTkFrame(self.parent)
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

        self.tree = ttk.Treeview(
            tree_frame,
            columns=("ID", "ID Réservation", "Montant", "Date", "Statut"),
            show="headings"
        )
        for col in ("ID", "ID Réservation", "Montant", "Date", "Statut"):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

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
            cursor.execute("SELECT * FROM factures")
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
            self.entry_reservation.delete(0, "end")
            self.entry_reservation.insert(0, values[1])
            self.entry_montant.delete(0, "end")
            self.entry_montant.insert(0, values[2])
            self.entry_date.delete(0, "end")
            self.entry_date.insert(0, values[3])
            self.entry_statut.delete(0, "end")
            self.entry_statut.insert(0, values[4])

    def ajouter(self):
        reservation = self.entry_reservation.get().strip()
        montant     = self.entry_montant.get().strip()
        date        = self.entry_date.get().strip()
        statut      = self.entry_statut.get().strip()

        if not reservation or not montant or not date:
            msg.showwarning("Attention", "Remplissez tous les champs !")
            return

        try:
            float(montant)
        except ValueError:
            msg.showerror("Erreur", "Le montant doit être un nombre !")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO factures (id_reservation, montant, date_facture, statut) VALUES (%s,%s,%s,%s)",
                (reservation, montant, date, statut)
            )
            conn.commit()
            msg.showinfo("Succès", "Facture ajoutée !")
            self.load_data()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def modifier(self):
        if not self.selected_id:
            msg.showwarning("Attention", "Sélectionnez une facture !")
            return
        reservation = self.entry_reservation.get().strip()
        montant     = self.entry_montant.get().strip()
        date        = self.entry_date.get().strip()
        statut      = self.entry_statut.get().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE factures SET id_reservation=%s, montant=%s, date_facture=%s, statut=%s WHERE id=%s",
                (reservation, montant, date, statut, self.selected_id)
            )
            conn.commit()
            msg.showinfo("Succès", "Facture modifiée !")
            self.load_data()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def supprimer(self):
        if not self.selected_id:
            msg.showwarning("Attention", "Sélectionnez une facture !")
            return
        if msg.askyesno("Confirmation", "Supprimer cette facture ?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM factures WHERE id=%s",
                    (self.selected_id,)
                )
                conn.commit()
                msg.showinfo("Succès", "Facture supprimée !")
                self.load_data()
            except Exception as e:
                msg.showerror("Erreur", str(e))
            finally:
                cursor.close()
                conn.close()

    def export_csv(self):
        with open("factures.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "ID Réservation", "Montant", "Date", "Statut"])
            for row in self.tree.get_children():
                writer.writerow(self.tree.item(row)['values'])
        msg.showinfo("Export", "Export CSV réussi ✅")