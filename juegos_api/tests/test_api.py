import unittest
from decimal import Decimal

import controlador_juegos
from extensions import db
from models import Juego
from tests import BaseTestCase

ZELDA = {'nombre': 'Zelda', 'descripcion': 'Aventura', 'precio': 999.99}


class ApiJuegosTest(BaseTestCase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()

    def crear(self, nombre='A', precio='1'):
        return controlador_juegos.insertar_juego(nombre, 'desc', Decimal(precio))

    # --- GET /api/juegos ---
    def test_listar_vacio(self):
        r = self.client.get('/api/juegos')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), [])

    def test_listar_con_datos(self):
        self.crear('A')
        self.crear('B')
        r = self.client.get('/api/juegos')
        self.assertEqual(r.status_code, 200)
        self.assertEqual([j['nombre'] for j in r.get_json()], ['A', 'B'])
        self.assertEqual(set(r.get_json()[0]), {'id', 'nombre', 'descripcion', 'precio'})

    # --- POST /api/juegos ---
    def test_crear(self):
        r = self.client.post('/api/juegos', json=ZELDA)
        self.assertEqual(r.status_code, 201)
        data = r.get_json()
        self.assertEqual(data['nombre'], 'Zelda')
        self.assertEqual(data['precio'], 999.99)
        self.assertEqual(Juego.query.count(), 1)

    def test_crear_recorta_espacios_y_acepta_precio_texto(self):
        r = self.client.post('/api/juegos', json={
            'nombre': '  Zelda ', 'descripcion': ' x ', 'precio': '10.5'})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.get_json()['nombre'], 'Zelda')
        self.assertEqual(r.get_json()['precio'], 10.5)

    def test_crear_campos_invalidos(self):
        casos = {
            'vacíos': {'nombre': '', 'precio': 'abc'},
            'sin descripcion': {'nombre': 'x', 'precio': 1},
            'precio negativo': {**ZELDA, 'precio': -5},
            'precio excede máximo': {**ZELDA, 'precio': 10000},
            'precio booleano': {**ZELDA, 'precio': True},
            'precio nulo': {**ZELDA, 'precio': None},
            'nombre muy largo': {**ZELDA, 'nombre': 'x' * 256},
            'nombre no texto': {**ZELDA, 'nombre': 123},
        }
        for nombre, body in casos.items():
            with self.subTest(caso=nombre):
                r = self.client.post('/api/juegos', json=body)
                self.assertEqual(r.status_code, 400)
                self.assertIn('message', r.get_json())
        self.assertEqual(Juego.query.count(), 0)

    def test_crear_errores_por_campo(self):
        r = self.client.post('/api/juegos', json={'nombre': '', 'precio': 'abc'})
        self.assertEqual(set(r.get_json()['message']),
                         {'nombre', 'descripcion', 'precio'})

    def test_crear_cuerpo_no_json(self):
        r = self.client.post('/api/juegos', data='esto no es json',
                             content_type='application/json')
        self.assertEqual(r.status_code, 400)
        r = self.client.post('/api/juegos', json=[1, 2])
        self.assertEqual(r.status_code, 400)

    # --- GET /api/juegos/<id> ---
    def test_obtener(self):
        j = self.crear('A', '5')
        r = self.client.get(f'/api/juegos/{j.id}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json(), {
            'id': j.id, 'nombre': 'A', 'descripcion': 'desc', 'precio': 5.0})

    def test_obtener_inexistente(self):
        r = self.client.get('/api/juegos/999')
        self.assertEqual(r.status_code, 404)
        self.assertIn('999', r.get_json()['message'])

    def test_id_no_entero_404(self):
        self.assertEqual(self.client.get('/api/juegos/abc').status_code, 404)

    # --- PUT /api/juegos/<id> ---
    def test_actualizar(self):
        j = self.crear()
        r = self.client.put(f'/api/juegos/{j.id}', json={
            'nombre': 'Zelda TotK', 'descripcion': 'Aventura', 'precio': 1299.5})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.get_json()['nombre'], 'Zelda TotK')
        self.assertEqual(r.get_json()['precio'], 1299.5)
        db.session.expire_all()
        self.assertEqual(db.session.get(Juego, j.id).nombre, 'Zelda TotK')

    def test_actualizar_invalido(self):
        j = self.crear('Original')
        r = self.client.put(f'/api/juegos/{j.id}', json={
            'nombre': 'X', 'descripcion': 'Y', 'precio': -5})
        self.assertEqual(r.status_code, 400)
        db.session.expire_all()
        self.assertEqual(db.session.get(Juego, j.id).nombre, 'Original')

    def test_actualizar_inexistente(self):
        r = self.client.put('/api/juegos/999', json=ZELDA)
        self.assertEqual(r.status_code, 404)

    # --- DELETE /api/juegos/<id> ---
    def test_eliminar(self):
        j = self.crear()
        r = self.client.delete(f'/api/juegos/{j.id}')
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.get_data(), b'')
        self.assertEqual(self.client.get(f'/api/juegos/{j.id}').status_code, 404)

    def test_eliminar_inexistente(self):
        self.assertEqual(self.client.delete('/api/juegos/999').status_code, 404)

    # --- Métodos no permitidos ---
    def test_metodo_no_permitido(self):
        self.assertEqual(self.client.delete('/api/juegos').status_code, 405)
        self.assertEqual(self.client.post('/api/juegos/1', json=ZELDA).status_code, 405)

    # --- Flujo completo ---
    def test_flujo_crud_completo(self):
        r = self.client.post('/api/juegos', json=ZELDA)
        id_ = r.get_json()['id']
        self.assertEqual(self.client.get(f'/api/juegos/{id_}').status_code, 200)
        self.assertEqual(self.client.put(f'/api/juegos/{id_}', json={**ZELDA, 'nombre': 'Z2'}).status_code, 200)
        self.assertEqual(self.client.delete(f'/api/juegos/{id_}').status_code, 204)
        self.assertEqual(self.client.get('/api/juegos').get_json(), [])


if __name__ == '__main__':
    unittest.main()
