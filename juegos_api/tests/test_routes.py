import unittest
from decimal import Decimal

import controlador_juegos
from auth.views import destino_seguro
from extensions import db
from models import Juego, User
from tests import BaseTestCase

VALIDO = {'nombre': 'Zelda', 'descripcion': 'Aventura', 'precio': '999.99'}


class RoutesBase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.client = self.app.test_client()

    def crear_usuario(self, username='ana', password='secreto'):
        u = User(username=username)
        u.password = password
        db.session.add(u)
        db.session.commit()
        return u

    def login(self, username='ana', password='secreto'):
        return self.client.post(
            '/auth/login',
            data={'username': username, 'password': password},
            follow_redirects=False,
        )

    def autenticar(self):
        self.crear_usuario()
        self.login()


class RutasProtegidasTest(RoutesBase, unittest.TestCase):

    def test_rutas_redirigen_a_login_sin_sesion(self):
        for metodo, url in [
            ('get', '/'), ('get', '/juegos'), ('get', '/agregar_juego'),
            ('post', '/agregar_juego'), ('get', '/editar_juego/1'),
            ('post', '/eliminar_juego/1'), ('get', '/auth/logout'),
        ]:
            with self.subTest(metodo=metodo, url=url):
                r = getattr(self.client, metodo)(url)
                self.assertEqual(r.status_code, 302)
                self.assertIn('/auth/login', r.headers['Location'])

    def test_login_conserva_next(self):
        r = self.client.get('/agregar_juego')
        self.assertIn('next=', r.headers['Location'])

    def test_no_crea_juego_sin_sesion(self):
        self.client.post('/agregar_juego', data=VALIDO)
        self.assertEqual(Juego.query.count(), 0)


class AuthTest(RoutesBase, unittest.TestCase):

    def test_pagina_login_y_registro(self):
        self.assertEqual(self.client.get('/auth/login').status_code, 200)
        self.assertEqual(self.client.get('/auth/register').status_code, 200)

    def test_registro_exitoso(self):
        r = self.client.post('/auth/register', data={
            'username': 'luis', 'password': 'abcdef', 'password2': 'abcdef'})
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers['Location'].endswith('/auth/login'))
        u = User.query.filter_by(username='luis').first()
        self.assertIsNotNone(u)
        self.assertTrue(u.verify_password('abcdef'))

    def test_registro_password_corto(self):
        r = self.client.post('/auth/register', data={
            'username': 'luis', 'password': '123', 'password2': '123'})
        self.assertEqual(r.status_code, 200)
        self.assertIn('Mínimo 6 caracteres', r.get_data(as_text=True))
        self.assertEqual(User.query.count(), 0)

    def test_registro_passwords_distintos(self):
        r = self.client.post('/auth/register', data={
            'username': 'luis', 'password': 'abcdef', 'password2': 'abcxyz'})
        self.assertIn('no coinciden', r.get_data(as_text=True))
        self.assertEqual(User.query.count(), 0)

    def test_registro_usuario_duplicado(self):
        self.crear_usuario('ana')
        r = self.client.post('/auth/register', data={
            'username': 'ana', 'password': 'abcdef', 'password2': 'abcdef'})
        self.assertIn('ya está en uso', r.get_data(as_text=True))
        self.assertEqual(User.query.count(), 1)

    def test_login_correcto(self):
        self.crear_usuario()
        r = self.login()
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers['Location'].endswith('/juegos'))
        self.assertEqual(self.client.get('/juegos').status_code, 200)

    def test_login_password_incorrecto(self):
        self.crear_usuario()
        r = self.login(password='mal')
        self.assertEqual(r.status_code, 200)
        self.assertIn('inválidos', r.get_data(as_text=True))
        self.assertEqual(self.client.get('/juegos').status_code, 302)

    def test_login_usuario_inexistente(self):
        r = self.login('nadie', 'x')
        self.assertEqual(r.status_code, 200)
        self.assertIn('inválidos', r.get_data(as_text=True))

    def test_login_respeta_next_interno(self):
        self.crear_usuario()
        r = self.client.post('/auth/login?next=/agregar_juego',
                             data={'username': 'ana', 'password': 'secreto'})
        self.assertTrue(r.headers['Location'].endswith('/agregar_juego'))

    def test_login_bloquea_open_redirect(self):
        self.crear_usuario()
        r = self.client.post('/auth/login?next=https://evil.com',
                             data={'username': 'ana', 'password': 'secreto'})
        self.assertTrue(r.headers['Location'].endswith('/juegos'))
        self.assertNotIn('evil.com', r.headers['Location'])

    def test_destino_seguro(self):
        self.assertTrue(destino_seguro('/juegos'))
        for malo in (None, '', 'https://evil.com', '//evil.com', 'juegos', '/\\evil.com'):
            with self.subTest(destino=malo):
                self.assertFalse(destino_seguro(malo))

    def test_logout(self):
        self.autenticar()
        r = self.client.get('/auth/logout')
        self.assertEqual(r.status_code, 302)
        self.assertEqual(self.client.get('/juegos').status_code, 302)

    def test_autenticado_redirige_desde_login_y_registro(self):
        self.autenticar()
        for url in ('/auth/login', '/auth/register'):
            with self.subTest(url=url):
                r = self.client.get(url)
                self.assertEqual(r.status_code, 302)
                self.assertTrue(r.headers['Location'].endswith('/juegos'))


class CrudJuegosTest(RoutesBase, unittest.TestCase):

    def setUp(self):
        super().setUp()
        self.autenticar()

    def test_listado_vacio_y_con_datos(self):
        self.assertEqual(self.client.get('/').status_code, 200)
        controlador_juegos.insertar_juego('Mario Kart', 'Carreras', Decimal('800'))
        html = self.client.get('/juegos').get_data(as_text=True)
        self.assertIn('Mario Kart', html)

    def test_form_agregar(self):
        self.assertEqual(self.client.get('/agregar_juego').status_code, 200)

    def test_agregar_juego(self):
        r = self.client.post('/agregar_juego', data=VALIDO)
        self.assertEqual(r.status_code, 302)
        self.assertTrue(r.headers['Location'].endswith('/juegos'))
        j = Juego.query.one()
        self.assertEqual((j.nombre, j.precio), ('Zelda', Decimal('999.99')))

    def test_agregar_datos_invalidos(self):
        casos = [
            {**VALIDO, 'nombre': ''},
            {**VALIDO, 'descripcion': '   '},
            {**VALIDO, 'precio': 'abc'},
            {**VALIDO, 'precio': ''},
            {**VALIDO, 'precio': 'NaN'},
            {'nombre': 'x', 'descripcion': 'y'},
        ]
        for datos in casos:
            with self.subTest(datos=datos):
                r = self.client.post('/agregar_juego', data=datos)
                self.assertEqual(r.status_code, 400)
        self.assertEqual(Juego.query.count(), 0)

    def test_editar_form(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        r = self.client.get(f'/editar_juego/{j.id}')
        self.assertEqual(r.status_code, 200)

    def test_editar_juego(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        r = self.client.post(f'/editar_juego/{j.id}', data=VALIDO)
        self.assertEqual(r.status_code, 302)
        db.session.expire_all()
        self.assertEqual(db.session.get(Juego, j.id).nombre, 'Zelda')

    def test_editar_datos_invalidos(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        r = self.client.post(f'/editar_juego/{j.id}', data={**VALIDO, 'precio': 'x'})
        self.assertEqual(r.status_code, 400)
        db.session.expire_all()
        self.assertEqual(db.session.get(Juego, j.id).nombre, 'A')

    def test_editar_inexistente_404(self):
        self.assertEqual(self.client.get('/editar_juego/999').status_code, 404)
        self.assertEqual(self.client.post('/editar_juego/999', data=VALIDO).status_code, 404)

    def test_eliminar_juego(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        r = self.client.post(f'/eliminar_juego/{j.id}')
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Juego.query.count(), 0)

    def test_eliminar_inexistente_404(self):
        self.assertEqual(self.client.post('/eliminar_juego/999').status_code, 404)

    def test_eliminar_solo_post(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        self.assertEqual(self.client.get(f'/eliminar_juego/{j.id}').status_code, 405)
        self.assertEqual(Juego.query.count(), 1)


if __name__ == '__main__':
    unittest.main()
