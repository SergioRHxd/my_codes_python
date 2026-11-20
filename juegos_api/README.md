# juegos_api – Mini‑Proyecto Flask

[![CI](https://github.com/SergioRHxd/my_codes_python/actions/workflows/ci.yml/badge.svg)](https://github.com/SergioRHxd/my_codes_python/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/SergioRHxd/my_codes_python/branch/main/graph/badge.svg)](https://codecov.io/gh/SergioRHxd/my_codes_python)

## Integración continua (GitHub Actions)

El workflow `.github/workflows/ci.yml` (en la raíz del repo) se ejecuta en cada `push` y `pull_request` a `main`/`master`:

1. Descarga el código (`actions/checkout`).
2. Instala Python 3.12 y las dependencias (`requirements.txt`, `pytest`, `pytest-cov`).
3. Corre `pytest --cov=. --cov-report=xml` (61 pruebas, cobertura ≈ 99 %).
4. Sube `coverage.xml` a Codecov.

Para activarlo: sube el repo a GitHub, agrégalo en codecov.io y guarda el token como secreto `CODECOV_TOKEN` (Settings → Secrets and variables → Actions).

Ejecución local: `pip install pytest pytest-cov && pytest --cov=.`

---

# Pruebas unitarias

## Cómo ejecutar

```bash
pip install -r requirements.txt
python -m unittest discover -v
```

La salida completa de la última ejecución está en `results.txt` (61 pruebas, todas OK).

## Estructura

| Archivo | Qué prueba |
|---|---|
| `__init__.py` | Configuración común: BD en memoria, `TESTING`, CSRF desactivado y la clase `BaseTestCase` con `setUp`/`tearDown`. |
| `test_models.py` | Modelos `User` y `Juego` + funciones de `controlador_juegos.py`. |
| `test_routes.py` | Rutas HTML: protección con login, registro/login/logout y CRUD de juegos. |
| `test_api.py` | API REST `/api/juegos` (GET, POST, PUT, DELETE). |

## setUp / tearDown

Antes de cada prueba se abre un `app_context` y se ejecuta `db.create_all()`; al terminar se hace `db.session.remove()`, `db.drop_all()` y se cierra el contexto. Cada prueba parte de una BD vacía y son independientes entre sí. En `test_routes.py` además se crea un cliente nuevo (`app.test_client()`) por prueba para no compartir sesión.

## Cobertura

- **Modelos (`test_models.py`, 17 pruebas):** `password` es solo escritura, el hash nunca guarda texto plano, `verify_password` correcto/incorrecto, hashes distintos para la misma contraseña, `username` único y obligatorio, `user_loader`, `__repr__`; CRUD del controlador (insertar, listar, obtener por id, actualizar, eliminar, ids inexistentes) y restricción de campos obligatorios en `Juego`.
- **Rutas (`test_routes.py`, 27 pruebas):** todas las rutas protegidas redirigen a `/auth/login` sin sesión; registro (éxito, contraseña corta, contraseñas distintas, usuario duplicado); login (correcto, contraseña errónea, usuario inexistente, `next` interno y bloqueo de open redirect); logout; CRUD de juegos con datos válidos e inválidos (400), ids inexistentes (404) y `eliminar` solo por POST (405).
- **API (`test_api.py`, 17 pruebas):** códigos 200/201/204/400/404/405, formato JSON de la respuesta, validación por campo (vacíos, precio negativo, mayor al máximo, booleano, nulo, texto demasiado largo), cuerpo que no es JSON, id no entero y flujo CRUD completo.

## Retos y soluciones

1. **MySQL en memoria no existe.** MySQL no soporta BD en memoria, así que las pruebas usan SQLite en memoria (`sqlite:///:memory:`) mediante la variable de entorno `DATABASE_URL`, que `app.py` ya leía. La BD real `juegos` nunca se toca.
2. **La app no usa application factory.** `app.py` lee la configuración al importarse, por lo que `DATABASE_URL` se define en `tests/__init__.py` *antes* de `from app import app`.
3. **CSRF en formularios (Flask‑WTF).** Se desactiva con `WTF_CSRF_ENABLED = False` solo en pruebas; si no, login y registro siempre fallan la validación.
4. **Rutas protegidas.** Se prueba con el cliente sin sesión (302 a login) y se inicia sesión con un POST real a `/auth/login`, de modo que la cookie de sesión queda en el cliente.
5. **Datos obsoletos entre sesión de prueba y petición.** Tras modificar vía el cliente se usa `db.session.expire_all()` antes de verificar en la BD.
6. **Imports.** Se ejecuta desde la raíz del proyecto (`python -m unittest discover`) y `tests/__init__.py` añade la raíz a `sys.path`.
