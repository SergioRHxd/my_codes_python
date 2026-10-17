from flask import Flask, render_template, request, redirect, url_for
from flask import abort
from flask_login import login_required
from decimal import Decimal, InvalidOperation
import os
from extensions import db, login_manager

app = Flask(__name__)

# Clave para firmar la sesión y los tokens CSRF. En producción define la
# variable de entorno SECRET_KEY; el valor por defecto es solo para desarrollo.
app.config['SECRET_KEY'] = os.environ.get(
    'SECRET_KEY',
    '5f2b8e1c9d4a47b0a3e6c7d81f09b2a4e5c6d7f8091a2b3c4d5e6f708192a3b4',
)

# Configuración de conexión a MySQL usando PyMySQL como driver
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'mysql+pymysql://root:@localhost/juegos'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Configuración de Flask-Login
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'warning'
login_manager.session_protection = 'strong'

import controlador_juegos
import models  # registra User y Juego (y el user_loader) antes de create_all()

# Blueprint de autenticación con prefijo /auth
from auth import auth as auth_blueprint
app.register_blueprint(auth_blueprint, url_prefix='/auth')


def obtener_datos_juego():
    nombre = request.form.get('nombre', '').strip()
    descripcion = request.form.get('descripcion', '').strip()

    try:
        precio = Decimal(request.form.get('precio', '').strip())
    except InvalidOperation:
        return None

    if not nombre or not descripcion or not precio.is_finite():
        return None

    return nombre, descripcion, precio


@app.route('/')
@app.route('/juegos')
@login_required
def juegos():
    lista_juegos = controlador_juegos.obtener_juegos()
    return render_template('juegos.html', juegos=lista_juegos)

@app.route('/agregar_juego', methods=['GET', 'POST'])
@login_required
def agregar_juego():
    if request.method == 'POST':
        datos = obtener_datos_juego()
        if datos is None:
            return render_template(
                'agregar_juego.html',
                error='Ingresa un nombre, una descripción y un precio válido.',
            ), 400

        nombre, descripcion, precio = datos
        controlador_juegos.insertar_juego(nombre, descripcion, precio)
        return redirect(url_for('juegos'))
    return render_template('agregar_juego.html')

@app.route('/editar_juego/<int:id>', methods=['GET', 'POST'])
@login_required
def editar_juego(id):
    juego = controlador_juegos.obtener_juego_por_id(id)
    if juego is None:
        abort(404)

    if request.method == 'POST':
        datos = obtener_datos_juego()
        if datos is None:
            return render_template(
                'editar_juego.html',
                juego=juego,
                error='Ingresa un nombre, una descripción y un precio válido.',
            ), 400

        nombre, descripcion, precio = datos
        controlador_juegos.actualizar_juego(id, nombre, descripcion, precio)
        return redirect(url_for('juegos'))
    
    return render_template('editar_juego.html', juego=juego)

@app.route('/eliminar_juego/<int:id>', methods=['POST'])
@login_required
def eliminar_juego(id):
    if controlador_juegos.obtener_juego_por_id(id) is None:
        abort(404)

    controlador_juegos.eliminar_juego(id)
    return redirect(url_for('juegos'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas automáticamente si no existen
    app.run(debug=True)