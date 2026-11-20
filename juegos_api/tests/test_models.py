import unittest
from decimal import Decimal

from sqlalchemy.exc import IntegrityError

import controlador_juegos
from extensions import db
from models import Juego, User
from tests import BaseTestCase


class UserModelTest(BaseTestCase, unittest.TestCase):

    def test_password_es_solo_escritura(self):
        u = User(username='ana')
        u.password = 'secreto'
        with self.assertRaises(AttributeError):
            _ = u.password

    def test_hash_no_guarda_texto_plano(self):
        u = User(username='ana')
        u.password = 'secreto'
        self.assertNotEqual(u.password_hash, 'secreto')
        self.assertNotIn('secreto', u.password_hash)

    def test_verify_password(self):
        u = User(username='ana')
        u.password = 'secreto'
        self.assertTrue(u.verify_password('secreto'))
        self.assertFalse(u.verify_password('otra'))

    def test_mismo_password_distinto_hash(self):
        a, b = User(username='a'), User(username='b')
        a.password = b.password = 'igual123'
        self.assertNotEqual(a.password_hash, b.password_hash)

    def test_username_unico(self):
        for _ in range(2):
            u = User(username='ana')
            u.password = 'secreto'
            db.session.add(u)
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_username_obligatorio(self):
        db.session.add(User(password_hash='x'))
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_repr(self):
        self.assertEqual(repr(User(username='ana')), '<User ana>')

    def test_user_loader(self):
        from models import load_user
        u = User(username='ana')
        u.password = 'secreto'
        db.session.add(u)
        db.session.commit()
        self.assertEqual(load_user(str(u.id)).username, 'ana')
        self.assertIsNone(load_user('999'))


class JuegoModelTest(BaseTestCase, unittest.TestCase):

    def test_crear_juego(self):
        j = controlador_juegos.insertar_juego('Zelda', 'Aventura', Decimal('999.99'))
        self.assertIsNotNone(j.id)
        self.assertEqual(Juego.query.count(), 1)
        self.assertEqual(j.precio, Decimal('999.99'))

    def test_repr(self):
        self.assertEqual(repr(Juego(nombre='Zelda')), '<Juego Zelda>')

    def test_campos_obligatorios(self):
        db.session.add(Juego(nombre='Sin precio', descripcion='x'))
        with self.assertRaises(IntegrityError):
            db.session.commit()
        db.session.rollback()

    def test_obtener_juegos(self):
        self.assertEqual(controlador_juegos.obtener_juegos(), [])
        controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        controlador_juegos.insertar_juego('B', 'b', Decimal('2'))
        self.assertEqual(len(controlador_juegos.obtener_juegos()), 2)

    def test_obtener_por_id(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        self.assertEqual(controlador_juegos.obtener_juego_por_id(j.id).nombre, 'A')
        self.assertIsNone(controlador_juegos.obtener_juego_por_id(999))

    def test_actualizar_juego(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        controlador_juegos.actualizar_juego(j.id, 'B', 'b', Decimal('5.50'))
        actualizado = controlador_juegos.obtener_juego_por_id(j.id)
        self.assertEqual(
            (actualizado.nombre, actualizado.descripcion, actualizado.precio),
            ('B', 'b', Decimal('5.50')),
        )

    def test_actualizar_inexistente(self):
        self.assertIsNone(controlador_juegos.actualizar_juego(999, 'x', 'x', Decimal('1')))

    def test_eliminar_juego(self):
        j = controlador_juegos.insertar_juego('A', 'a', Decimal('1'))
        controlador_juegos.eliminar_juego(j.id)
        self.assertIsNone(controlador_juegos.obtener_juego_por_id(j.id))

    def test_eliminar_inexistente_no_falla(self):
        controlador_juegos.eliminar_juego(999)
        self.assertEqual(Juego.query.count(), 0)


if __name__ == '__main__':
    unittest.main()
