from flask import Blueprint

auth = Blueprint('auth', __name__, template_folder='templates')

# Se importa al final para que views.py pueda usar el blueprint ya creado.
from . import views  # noqa: E402,F401
