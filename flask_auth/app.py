import os
import sys

from flask import Flask, render_template
from sqlalchemy import create_engine, text

from config import DB_NAME, SERVER_URI, Config
from extensions import csrf, db, login_manager


def ensure_database():
    """Crea la base de datos si no existe (el servidor MySQL debe estar encendido)."""
    try:
        engine = create_engine(SERVER_URI)
        with engine.connect() as conn:
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}` CHARACTER SET utf8mb4"))
            conn.commit()
        engine.dispose()
    except Exception as exc:
        sys.exit(f"\nNo pude conectar a MySQL. ¿Está encendido el servidor?\nDetalle: {exc}\n")


def create_app():
    ensure_database()
    app = Flask(__name__)
    app.config.from_object(Config)

    # Configuración pedida en la guía (punto 1.4)
    app.config['SECRET_KEY'] = 'clave_super_secreta'
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['REMEMBER_COOKIE_HTTPONLY'] = True

    # Cookies seguras adicionales
    app.config['SESSION_COOKIE_HTTPONLY'] = True     # JavaScript no puede leer la cookie
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['REMEMBER_COOKIE_SECURE'] = True

    # Solo si el navegador no deja iniciar sesión por HTTP: set COOKIE_SECURE=0
    if os.environ.get("COOKIE_SECURE") == "0":
        app.config['SESSION_COOKIE_SECURE'] = False
        app.config['REMEMBER_COOKIE_SECURE'] = False

    # Extensiones: SQLAlchemy, protección CSRF y Flask-Login
    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "users.login"      # a dónde redirige si no hay sesión
    login_manager.login_message = "Inicia sesión para ver esa página."
    login_manager.login_message_category = "error"

    from models import User

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    from routes import users_bp
    app.register_blueprint(users_bp)

    # Manejo de errores
    @app.errorhandler(401)
    def unauthorized(_e):
        return render_template("error.html", code=401,
                               message="Necesitas iniciar sesión para acceder."), 401

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("error.html", code=403,
                               message="No tienes permiso para acceder a este recurso."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", code=404,
                               message="No encontramos esa página."), 404

    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    # Con SESSION_COOKIE_SECURE=True el navegador acepta la cookie por HTTP
    # solo en "localhost" (no en 127.0.0.1). Por eso se indica esa dirección.
    if os.environ.get("WERKZEUG_RUN_MAIN") != "true":
        proto = "https" if os.environ.get("HTTPS") == "1" else "http"
        print(f"\n>>> Abre {proto}://localhost:5000  (usa 'localhost', no 127.0.0.1)\n")
    if os.environ.get("HTTPS") == "1":
        app.run(debug=True, ssl_context="adhoc")   # certificado temporal
    else:
        app.run(debug=True)
