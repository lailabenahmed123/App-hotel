# views/reservations.py
import customtkinter as ctk
from tkinter import ttk
import tkinter.messagebox as msg
from db import get_connection
import csv

class ReservationsWindow:
    def __init__(self, parent):
        self.parent = parent
        self.selected_id = None
        self.build_ui()
        self.load_data()

    def build_ui(self):
        ctk.CTkLabel(
            self.parent,
            text="📅 Gestion des Réservations",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=15)

        # ── Formulaire ─────────────────────────
        form = ctk.CTkFrame(self.parent)
        form.pack(padx=20, pady=5, fill="x")

        ctk.CTkLabel(form, text="ID Client :").grid(row=0, column=0, padx=10, pady=8)
        self.entry_client = ctk.CTkEntry(form, width=100)
        self.entry_client.grid(row=0, column=1, padx=10)

        ctk.CTkLabel(form, text="ID Chambre :").grid(row=0, column=2, padx=10)
        self.entry_chambre = ctk.CTkEntry(form, width=100)
        self.entry_chambre.grid(row=0, column=3, padx=10)

        ctk.CTkLabel(form, text="Arrivée (YYYY-MM-DD) :").grid(row=1, column=0, padx=10, pady=8)
        self.entry_arrivee = ctk.CTkEntry(form, width=150)
        self.entry_arrivee.grid(row=1, column=1, padx=10)

        ctk.CTkLabel(form, text="Départ (YYYY-MM-DD) :").grid(row=1, column=2, padx=10)
        self.entry_depart = ctk.CTkEntry(form, width=150)
        self.entry_depart.grid(row=1, column=3, padx=10)

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
            columns=("ID", "ID Client", "ID Chambre", "Arrivée", "Départ"),
            show="headings"
        )
        for col in ("ID", "ID Client", "ID Chambre", "Arrivée", "Départ"):
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
            cursor.execute("SELECT * FROM reservations")
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
            self.entry_client.delete(0, "end")
            self.entry_client.insert(0, values[1])
            self.entry_chambre.delete(0, "end")
            self.entry_chambre.insert(0, values[2])
            self.entry_arrivee.delete(0, "end")
            self.entry_arrivee.insert(0, values[3])
            self.entry_depart.delete(0, "end")
            self.entry_depart.insert(0, values[4])

    def ajouter(self):
        client  = self.entry_client.get().strip()
        chambre = self.entry_chambre.get().strip()
        arrivee = self.entry_arrivee.get().strip()
        depart  = self.entry_depart.get().strip()

        if not client or not chambre or not arrivee or not depart:
            msg.showwarning("Attention", "Remplissez tous les champs !")
            return

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO reservations (id_client, id_chambre, date_arrivee, date_depart) VALUES (%s,%s,%s,%s)",
                (client, chambre, arrivee, depart)
            )
            conn.commit()
            msg.showinfo("Succès", "Réservation ajoutée !")
            self.load_data()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def modifier(self):
        if not self.selected_id:
            msg.showwarning("Attention", "Sélectionnez une réservation !")
            return
        client  = self.entry_client.get().strip()
        chambre = self.entry_chambre.get().strip()
        arrivee = self.entry_arrivee.get().strip()
        depart  = self.entry_depart.get().strip()

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE reservations SET id_client=%s, id_chambre=%s, date_arrivee=%s, date_depart=%s WHERE id=%s",
                (client, chambre, arrivee, depart, self.selected_id)
            )
            conn.commit()
            msg.showinfo("Succès", "Réservation modifiée !")
            self.load_data()
        except Exception as e:
            msg.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def supprimer(self):
        if not self.selected_id:
            msg.showwarning("Attention", "Sélectionnez une réservation !")
            return
        if msg.askyesno("Confirmation", "Supprimer cette réservation ?"):
            try:
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(
                    "DELETE FROM reservations WHERE id=%s",
                    (self.selected_id,)
                )
                conn.commit()
                msg.showinfo("Succès", "Réservation supprimée !")
                self.load_data()
            except Exception as e:
                msg.showerror("Erreur", str(e))
            finally:
                cursor.close()
                conn.close()

    def export_csv(self):
        with open("reservations.csv", "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["ID", "ID Client", "ID Chambre", "Arrivée", "Départ"])
            for row in self.tree.get_children():
                writer.writerow(self.tree.item(row)['values'])
        msg.showinfo("Export", "Export CSV réussi ✅")