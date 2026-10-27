"""API REST de juegos con Flask-RESTful.

Base: /api

    GET    /api/juegos        -> 200  lista de juegos
    POST   /api/juegos        -> 201  crea un juego (JSON)
    GET    /api/juegos/<id>   -> 200  un juego | 404
    PUT    /api/juegos/<id>   -> 200  reemplaza un juego (JSON) | 400 | 404
    DELETE /api/juegos/<id>   -> 204  elimina un juego | 404

Cuerpo JSON de POST/PUT (los tres campos son obligatorios):

    {"nombre": "Zelda", "descripcion": "Aventura", "precio": 999.99}

Errores: siempre JSON con la forma {"message": "..."}.
"""
from decimal import Decimal, InvalidOperation

from flask import Blueprint, request
from flask_restful import Api, Resource, abort, fields, marshal_with

import controlador_juegos

api_bp = Blueprint('api', __name__, url_prefix='/api')
api = Api(api_bp)

# Cómo se serializa un objeto Juego a JSON (usado por marshal_with).
juego_fields = {
    'id': fields.Integer,
    'nombre': fields.String,
    'descripcion': fields.String,
    'precio': fields.Float,
}

PRECIO_MAX = Decimal('9999999.99')  # límite de Numeric(9, 2)


def leer_datos_juego():
    """Valida el JSON del request y devuelve (nombre, descripcion, precio).

    Aborta con 400 si el cuerpo no es JSON, falta un campo o un valor es inválido.
    """
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        abort(400, message='El cuerpo debe ser un objeto JSON (Content-Type: application/json).')

    errores = {}

    textos = {}
    for campo in ('nombre', 'descripcion'):
        valor = datos.get(campo)
        if not isinstance(valor, str) or not valor.strip():
            errores[campo] = 'Obligatorio, texto no vacío.'
        elif len(valor.strip()) > 255:
            errores[campo] = 'Máximo 255 caracteres.'
        else:
            textos[campo] = valor.strip()

    precio = datos.get('precio')
    if isinstance(precio, bool) or not isinstance(precio, (int, float, str)):
        errores['precio'] = 'Obligatorio, número.'
    else:
        try:
            precio = Decimal(str(precio).strip())
            if not precio.is_finite() or precio < 0 or precio > PRECIO_MAX:
                raise InvalidOperation
            precio = precio.quantize(Decimal('0.01'))
        except InvalidOperation:
            errores['precio'] = f'Debe ser un número entre 0 y {PRECIO_MAX}.'

    if errores:
        abort(400, message=errores)

    return textos['nombre'], textos['descripcion'], precio


def obtener_o_404(id):
    juego = controlador_juegos.obtener_juego_por_id(id)
    if juego is None:
        abort(404, message=f'No existe el juego con id {id}.')
    return juego


class JuegoList(Resource):
    """Colección de juegos: /api/juegos"""

    @marshal_with(juego_fields)
    def get(self):
        """Lista todos los juegos. Responde 200 con un arreglo JSON."""
        return controlador_juegos.obtener_juegos(), 200

    @marshal_with(juego_fields)
    def post(self):
        """Crea un juego. Responde 201 con el juego creado.

        Body JSON: nombre, descripcion, precio. 400 si algún dato es inválido.
        """
        nombre, descripcion, precio = leer_datos_juego()
        return controlador_juegos.insertar_juego(nombre, descripcion, precio), 201


class JuegoResource(Resource):
    """Un juego: /api/juegos/<id>"""

    @marshal_with(juego_fields)
    def get(self, id):
        """Devuelve un juego. 200, o 404 si el id no existe."""
        return obtener_o_404(id), 200

    @marshal_with(juego_fields)
    def put(self, id):
        """Reemplaza nombre, descripcion y precio. 200 con el juego
        actualizado; 400 si los datos son inválidos; 404 si el id no existe."""
        obtener_o_404(id)
        nombre, descripcion, precio = leer_datos_juego()
        return controlador_juegos.actualizar_juego(id, nombre, descripcion, precio), 200

    def delete(self, id):
        """Elimina un juego. 204 sin cuerpo, o 404 si el id no existe."""
        obtener_o_404(id)
        controlador_juegos.eliminar_juego(id)
        return '', 204


api.add_resource(JuegoList, '/juegos')
api.add_resource(JuegoResource, '/juegos/<int:id>')
