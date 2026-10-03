import os
from urllib.parse import quote_plus

# --- Conexión a MySQL ---
DB_USER = os.environ.get("DB_USER", "root")
DB_PASS = os.environ.get("DB_PASS", "15054505")        # usuario root sin contraseña (ajustar si tu MySQL tiene una)
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_NAME = os.environ.get("DB_NAME", "flask_auth")

SERVER_URI = f"mysql+pymysql://{DB_USER}:{quote_plus(DB_PASS)}@{DB_HOST}:{DB_PORT}"


class Config:
    SQLALCHEMY_DATABASE_URI = f"{SERVER_URI}/{DB_NAME}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True

