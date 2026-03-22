import customtkinter as ctk      # importer CustomTkinter
from login import LoginWindow  # importer la classe Login

if __name__ == "__main__":       # point de départ du programme
    root = ctk.CTk()             # créer la fenêtre principale
    app = LoginWindow(root)      # lancer l'interface login
    root.mainloop()              # garder la fenêtre ouverte