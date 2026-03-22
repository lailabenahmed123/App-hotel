
import customtkinter as ctk
from tkinter import messagebox
from db import get_connection

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🏨 Gestion Hôtel")
        self.root.geometry("450x550")
        self.root.minsize(450, 550)
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(
            self.root,
            text="🏨",
            font=ctk.CTkFont(size=50)
        ).pack(pady=(40, 5))

        ctk.CTkLabel(
            self.root,
            text="Gestion Hôtel",
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            self.root,
            text="Connectez-vous pour continuer",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        ).pack(pady=(0, 30))

        frame = ctk.CTkFrame(self.root, corner_radius=15)
        frame.pack(padx=40, fill="x")

        ctk.CTkLabel(
            frame,
            text="Nom d'utilisateur",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=20, pady=(20, 5))

        self.entry_username = ctk.CTkEntry(
            frame,
            placeholder_text="Entrez votre nom d'utilisateur",
            width=300,
            height=40,
            corner_radius=8
        )
        self.entry_username.pack(padx=20, pady=(0, 15))

        ctk.CTkLabel(
            frame,
            text="Mot de passe",
            font=ctk.CTkFont(size=13)
        ).pack(anchor="w", padx=20)

        self.entry_password = ctk.CTkEntry(
            frame,
            placeholder_text="Entrez votre mot de passe",
            show="*",
            width=300,
            height=40,
            corner_radius=8
        )
        self.entry_password.pack(padx=20, pady=(5, 20))

        self.label_error = ctk.CTkLabel(
            self.root,
            text="",
            text_color="red",
            font=ctk.CTkFont(size=12)
        )
        self.label_error.pack(pady=(10, 0))

        ctk.CTkButton(
            self.root,
            text="Se connecter",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=45,
            corner_radius=10,
            command=self.login
        ).pack(padx=40, pady=15, fill="x")

        self.root.bind("<Return>", lambda e: self.login())

    def login(self):
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            self.label_error.configure(
                text="⚠️ Veuillez remplir tous les champs."
            )
            return

        conn = get_connection()
        if conn is None:
            messagebox.showerror("Erreur", "Connexion BDD impossible.")
            return

        try:
            cursor = conn.cursor()
            query = "SELECT * FROM utilisateurs WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()

            if result:
                self.open_dashboard()
            else:
                self.label_error.configure(
                    text="❌ Identifiants incorrects."
                )
        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            cursor.close()
            conn.close()

    def open_dashboard(self):
        self.root.destroy()
        from dashboard import DashboardWindow
        new_root = ctk.CTk()
        DashboardWindow(new_root)
        new_root.mainloop()