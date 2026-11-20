"""A5 - Manejo de errores y seguridad básica en Flask (microaplicación de videojuegos)."""
import logging
import os

import sentry_sdk
from flask import Flask, abort, jsonify, render_template, request
from sentry_sdk.integrations.flask import FlaskIntegration
from werkzeug.exceptions import BadRequest, HTTPException, MethodNotAllowed

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Sentry (opcional): define la variable de entorno SENTRY_DSN con tu DSN real.
#   Windows (PowerShell):  $env:SENTRY_DSN="https://xxx@oXXX.ingest.sentry.io/XXX"
#   Linux/Mac:             export SENTRY_DSN="https://xxx@oXXX.ingest.sentry.io/XXX"
# ---------------------------------------------------------------------------
SENTRY_DSN = os.getenv("SENTRY_DSN")
if SENTRY_DSN:
    sentry_sdk.init(dsn=SENTRY_DSN, integrations=[FlaskIntegration()])

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Registro de errores en errors.log
# ---------------------------------------------------------------------------
file_handler = logging.FileHandler(os.path.join(BASE_DIR, "errors.log"), encoding="utf-8")
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
app.logger.addHandler(file_handler)

# ---------------------------------------------------------------------------
# Datos de ejemplo
# ---------------------------------------------------------------------------
VIDEOGAMES = {
    1: {"id": 1, "title": "The Legend of Zelda: Breath of the Wild", "genre": "Aventura", "year": 2017},
    2: {"id": 2, "title": "Hades", "genre": "Roguelike", "year": 2020},
    3: {"id": 3, "title": "Celeste", "genre": "Plataformas", "year": 2018},
    4: {"id": 4, "title": "Stardew Valley", "genre": "Simulación", "year": 2016},
}


def is_api_request():
    return request.path.startswith("/api/")


def json_error(e):
    """Respuesta JSON uniforme para errores en rutas /api/*."""
    response = e.get_response()
    response.data = jsonify(code=e.code, name=e.name, description=e.description).data
    response.content_type = "application/json"
    return response


# ---------------------------------------------------------------------------
# Rutas
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html", games=VIDEOGAMES.values())


@app.route("/videogame/<int:id>")
def videogame(id):
    # Parámetro obligatorio: si falta, 400 Bad Request.
    plataforma = request.args.get("plataforma")
    if not plataforma:
        abort(400, description="Falta el parámetro obligatorio 'plataforma'.")
    game = VIDEOGAMES.get(id)
    if game is None:
        abort(404, description="El videojuego solicitado no existe.")
    return render_template("videogame.html", game=game, plataforma=plataforma)


@app.route("/pruebas")
def pruebas():
    return render_template("pruebas.html")


@app.route("/error-500")
def error_500():
    # Error NO HTTP forzado: ZeroDivisionError -> 500 + registro en errors.log
    return str(1 / 0)


@app.route("/api/videogames")
def api_videogames():
    return jsonify(list(VIDEOGAMES.values()))


@app.route("/api/videogame/<int:id>")
def api_videogame(id):
    plataforma = request.args.get("plataforma")
    if not plataforma:
        abort(400, description="Falta el parámetro obligatorio 'plataforma'.")
    game = VIDEOGAMES.get(id)
    if game is None:
        abort(404, description="El videojuego solicitado no existe.")
    return jsonify(game)


@app.route("/api/error")
def api_error():
    return jsonify(result=1 / 0)  # 500 en formato JSON


# ---------------------------------------------------------------------------
# Manejadores de error específicos (HTML, o JSON si la ruta es /api/*)
# ---------------------------------------------------------------------------
@app.errorhandler(BadRequest)
def handle_400(e):
    if is_api_request():
        return json_error(e)
    return render_template("400.html", error=e), 400


@app.errorhandler(404)
def handle_404(e):
    if is_api_request():
        return json_error(e)
    return render_template("404.html", error=e), 404


@app.errorhandler(MethodNotAllowed)
def handle_405(e):
    if is_api_request():
        return json_error(e)
    return render_template("405.html", error=e), 405


@app.errorhandler(500)
def handle_500(e):
    # Flask ya registra el traceback en app.logger (-> errors.log y Sentry).
    if is_api_request():
        return json_error(e)
    return render_template("500.html", error=e), 500


# ---------------------------------------------------------------------------
# Manejador genérico: cualquier otra HTTPException (403, 415, 429, ...)
# ---------------------------------------------------------------------------
@app.errorhandler(HTTPException)
def handle_api_error(e):
    if is_api_request():
        return json_error(e)
    return e


if __name__ == "__main__":
    # debug=False es necesario para ver la página 500 personalizada
    # (con debug=True Flask muestra el depurador en lugar de 500.html).
    app.run(debug=False)
