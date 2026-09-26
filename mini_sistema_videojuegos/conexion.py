# ========================================================================
# IMPORTACION DE LIBRERIAS
# ========================================================================
import pymysql

# ========================================================================
# FUNCION PARA OBTENER LA CONEXION A LA BASE DE DATOS
# ========================================================================
def obtener_conexion():
    # Cada llamada crea una conexión PyMySQL usando la configuración local del proyecto.
    return pymysql.connect(
        host='localhost',
        user='root',
        password='15054505',
        db='juegos'
    )
