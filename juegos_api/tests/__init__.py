"""Configuración común de las pruebas.

Se ejecuta antes que cualquier test: apunta la app a SQLite en memoria
(evita tocar la base MySQL real) y agrega la raíz del proyecto al path.
"""
import os
import sys

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ.setdefault('SECRET_KEY', 'clave-de-pruebas')
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app  # noqa: E402
from extensions import db  # noqa: E402

app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)


class BaseTestCase:
    """Mixin: crea las tablas antes de cada prueba y las borra después."""

    def setUp(self):
        self.app = app
        self.ctx = app.app_context()
        self.ctx.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.ctx.pop()
