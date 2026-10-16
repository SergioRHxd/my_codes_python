from flask import Flask, render_template, request, redirect, url_for
from flask import abort
from decimal import Decimal, InvalidOperation
from extensions import db

app = Flask(__name__)

# Configuración de conexión a MySQL usando PyMySQL como driver
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/juegos'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

import controlador_juegos


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
def juegos():
    lista_juegos = controlador_juegos.obtener_juegos()
    return render_template('juegos.html', juegos=lista_juegos)

@app.route('/agregar_juego', methods=['GET', 'POST'])
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
def eliminar_juego(id):
    if controlador_juegos.obtener_juego_por_id(id) is None:
        abort(404)

    controlador_juegos.eliminar_juego(id)
    return redirect(url_for('juegos'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Crea las tablas automáticamente si no existen
    app.run(debug=True)