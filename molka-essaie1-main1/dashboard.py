# dashboard.py
import customtkinter as ctk
import tkinter.messagebox as msg

class DashboardWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("🏨 Gestion Hôtel")
        self.root.geometry("1100x650")
        self.root.minsize(900, 500)
        self.build_ui()

    def build_ui(self):
        # ── Sidebar ────────────────────────────
        self.sidebar = ctk.CTkFrame(self.root, width=200, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="🏨 Hôtel",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(pady=30)

        buttons = [
            ("🛏️  Chambres",     self.open_chambres),
            ("👤  Clients",      self.open_clients),
            ("📅  Réservations", self.open_reservations),
            ("🧾  Factures",     self.open_factures),
        ]

        for text, command in buttons:
            ctk.CTkButton(
                self.sidebar,
                text=text,
                height=40,
                command=command
            ).pack(pady=10, padx=20, fill="x")

        ctk.CTkButton(
            self.sidebar,
            text="🚪 Déconnexion",
            height=40,
            fg_color="red",
            hover_color="darkred",
            command=self.deconnexion
        ).pack(pady=10, padx=20, fill="x", side="bottom")

        # ── Zone principale ────────────────────
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(side="right", fill="both", expand=True)

        ctk.CTkLabel(
            self.main_frame,
            text="Bienvenue dans la Gestion Hôtel 🏨",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=50)

        ctk.CTkLabel(
            self.main_frame,
            text="Choisissez une section dans le menu à gauche",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        ).pack()

    def clear_main(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def open_chambres(self):
        self.clear_main()
        from chambres import ChambresWindow
        ChambresWindow(self.main_frame)

    def open_clients(self):
        self.clear_main()
        from clients_frame import ClientsWindow
        ClientsWindow(self.main_frame)

    def open_reservations(self):
        self.clear_main()
        from reservations import ReservationsWindow
        ReservationsWindow(self.main_frame)

    def open_factures(self):
        self.clear_main()
        from factures import FacturesWindow
        FacturesWindow(self.main_frame)

    def deconnexion(self):
        if msg.askyesno("Déconnexion", "Voulez-vous vous déconnecter ?"):
            self.root.destroy()
            import customtkinter as ctk
            from login import LoginWindow
            new_root = ctk.CTk()
            LoginWindow(new_root)
            new_root.mainloop()