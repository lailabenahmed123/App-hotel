from db import get_connection

conn = get_connection()
print("Connexion réussie")
conn.close()