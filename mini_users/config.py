import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "cambia-esta-clave-en-produccion")

    # --- Opcion A (por defecto): SQLite, archivo app.db, cero configuracion ---
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL",
        "sqlite:///" + os.path.join(BASE_DIR, "app.db"),
    )

    # --- Opcion B: MySQL de XAMPP (crea antes la BD "mini_users" en phpMyAdmin) ---
    # SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:@localhost:3306/mini_users"

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
