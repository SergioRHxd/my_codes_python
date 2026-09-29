from flask import Flask, render_template

from config import Config
from extensions import csrf, db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    csrf.init_app(app)

    from routes import users_bp
    app.register_blueprint(users_bp)

    @app.errorhandler(403)
    def forbidden(_e):
        return render_template("error.html", code=403,
                               message="No tienes permiso para hacer eso."), 403

    @app.errorhandler(404)
    def not_found(_e):
        return render_template("error.html", code=404,
                               message="No encontramos esa página."), 404

    with app.app_context():
        import models  # noqa: F401  (registra las tablas)
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
