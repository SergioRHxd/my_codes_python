# ========================================================================
# IMPORTACION DE CODIGO DE CONEXION
# ========================================================================
from conexion import obtener_conexion

# ========================================================================
# FUNCION PARA INSERTAR UN NUEVO JUEGO EN LA BASE DE DATOS
# ========================================================================
def insertar_juego(nombre, descripcion, precio):
    """ Inserta un nuevo juego en la base de datos. """
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        # Los marcadores %s separan los datos del SQL y evitan concatenar valores en la consulta.
        cursor.execute("INSERT INTO juegos(nombre, descripcion, precio) VALUES (%s, %s, %s)",
                       (nombre, descripcion, precio))
    # Las escrituras requieren confirmación para persistir los cambios.
    conexion.commit()
    conexion.close()

# ========================================================================
# FUNCION PARA OBTENER TODOS LOS JUEGOS DE LA BASE DE DATOS
# ========================================================================
def obtener_juegos():
    """ Obtiene todos los juegos de la base de datos. """
    conexion = obtener_conexion()
    juegos = []
    with conexion.cursor() as cursor:
        # fetchall devuelve todas las filas para mostrarlas en la tabla.
        cursor.execute("SELECT id, nombre, descripcion, precio FROM juegos")
        juegos = cursor.fetchall()
    conexion.close()
    return juegos

# ========================================================================
# FUNCION PARA ELIMINAR UN JUEGO DE LA BASE DE DATOS
# ========================================================================
def eliminar_juego(id):
    """ Elimina un juego de la base de datos por su ID. """
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        # La condición limita el borrado al registro cuyo ID recibió la ruta.
        cursor.execute("DELETE FROM juegos WHERE id = %s", (id,))
    conexion.commit()
    conexion.close()

# ========================================================================
# FUNCION PARA OBTENER UN JUEGO POR SU ID
# ========================================================================
def obtener_juego_por_id(id):
    """ Obtiene un juego de la base de datos por su ID. """
    conexion = obtener_conexion()
    juego = None
    with conexion.cursor() as cursor:
        # fetchone devuelve una sola fila, que se usa para rellenar el formulario de edición.
        cursor.execute(
            "SELECT id, nombre, descripcion, precio FROM juegos WHERE id = %s", (id,))
        juego = cursor.fetchone()
    conexion.close()
    return juego

# ========================================================================
# FUNCION PARA ACTUALIZAR UN JUEGO EN LA BASE DE DATOS
# ========================================================================
def actualizar_juego(nombre, descripcion, precio, id):
    """ Actualiza un juego en la base de datos por su ID. """
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        # Actualiza los campos editables únicamente para el juego indicado por su ID.
        cursor.execute("UPDATE juegos SET nombre = %s, descripcion = %s, precio = %s WHERE id = %s",
                       (nombre, descripcion, precio, id))
    conexion.commit()
    conexion.close()
