from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()

# Se crea aquí (sin app) para evitar imports circulares entre app.py y models.py.
# La configuración (login_view, session_protection) se aplica en app.py.
login_manager = LoginManager()
