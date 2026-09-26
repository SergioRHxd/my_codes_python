try:
    import pymysql
except ImportError:
    import mysql.connector as pymysql

import config

#Esta línea permite manejar errores de conexión y operaciones
MySQLError = getattr(pymysql, "MySQLError", getattr(pymysql, "Error", Exception)) 

class ConexionBD:
    """Clase encargada de la conexión con el servidor MySQL."""
    
    def __init__(self):
        self.host = config.DB_HOST
        self.user = config.DB_USER
        self.password = config.DB_PASSWORD
        self.database = config.DB_NAME
        self.conexion = None #esta variable almacenará la conexión a la base de datos

    def conectar(self):
        """Establece la conexión con la base de datos."""
        try:
            print("[SISTEMA] Conectando a la base de datos...")
            #aquí se realiza la conexión a la base de datos utilizando los parámetros de configuración
            self.conexion = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("[SISTEMA] Conexión establecida con éxito.")
            return self.conexion #retorna la conexión para que pueda ser utilizada por otras clases o funciones
        except MySQLError as err:
            print(f"[ERROR CONEXIÓN] {err}")
            return None

    def cerrar(self):
        """Cierra la conexión si está activa."""
        if self.conexion:
            self.conexion.close()
            print("[SISTEMA] Conexión cerrada con éxito.")