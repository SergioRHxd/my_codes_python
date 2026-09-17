#DAO (Data Access Object) para la tabla 'usuario1' en la base de datos.
try:
    import pymysql
except ImportError:
    import mysql.connector as pymysql

#Esta linea permite manejar errores de conexión y operaciones 
MySQLError = getattr(pymysql, "MySQLError", getattr(pymysql, "Error", Exception))

# Clase DAO para la entidad Usuario
class UsuarioDAO:
    """Clase DAO encargada del CRUD en la base de datos."""
    #El constructor recibe la conexión a la base de datos y la almacena para su uso en los métodos CRUD.
    def __init__(self, conexion):
        self.conexion = conexion
        
    #definir los métodos CRUD: crear_tabla, insertar, actualizar, eliminar y listar_por_id. 
    def crear_tabla(self):
        print("\n--> [INICIO] Creando tabla 'usuario1'...")
        try:
            cursor = self.conexion.cursor()
            cursor.execute("DROP TABLE IF EXISTS usuario1")
            cursor.execute(
                """CREATE TABLE usuario1 (
                    Idusuario INT PRIMARY KEY AUTO_INCREMENT,
                    nombres VARCHAR(25),
                    apellidoPaterno VARCHAR(25),
                    apellidoMaterno VARCHAR(25),
                    user VARCHAR(10),
                    pwd VARCHAR(10)
                )"""
            )
            self.conexion.commit()
            cursor.close()
            print("<-- [ÉXITO] Tabla 'usuario1' creada correctamente.")
        except MySQLError as err:
            print(f"<-- [ERROR] No se pudo crear la tabla: {err}")

    def pedir_datos_usuario(pedir_id=True):
        idusuario = int(input("Dame id del usuario: ")) if pedir_id else None
        nombres = input("Dame los nombres del usuario: ")
        ap = input("Dame el apellido paterno: ")
        am = input("Dame el apellido materno: ")
        user = input("Dame el usuario: ")
        pwd = input("Dame la contraseña: ")
        return Usuario(idusuario, nombres, ap, am, user, pwd)

    def insertar(self, usuario):
        print(f"\n--> [INICIO] Insertando usuario ID: {usuario.idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = "INSERT INTO usuario1 VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql, (
                usuario.idusuario,
                usuario.nombres,
                usuario.apellido_paterno,
                usuario.apellido_materno,
                usuario.user,
                usuario.pwd
            ))
            self.conexion.commit()
            cursor.close()
            print(f"<-- [ÉXITO] Usuario '{usuario.nombres}' insertado correctamente.")
        except MySQLError as err:
            print(f"<-- [ERROR] No se pudo insertar el usuario: {err}")

    def actualizar(self, usuario):
        print(f"\n--> [INICIO] Actualizando usuario ID: {usuario.idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = """UPDATE usuario1 
                     SET nombres=%s, apellidoPaterno=%s, apellidoMaterno=%s, user=%s, pwd=%s 
                     WHERE Idusuario=%s"""
            cursor.execute(sql, (
                usuario.nombres,
                usuario.apellido_paterno,
                usuario.apellido_materno,
                usuario.user,
                usuario.pwd,
                usuario.idusuario
            ))
            self.conexion.commit()
            cursor.close()
            print(f"<-- [ÉXITO] Usuario ID {usuario.idusuario} actualizado correctamente.")
        except MySQLError as err:
            print(f"<-- [ERROR] No se pudo actualizar el usuario: {err}")

    def eliminar(self, idusuario):
        print(f"\n--> [INICIO] Eliminando usuario ID: {idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = "DELETE FROM usuario1 WHERE Idusuario = %s"
            cursor.execute(sql, (idusuario,))
            self.conexion.commit()
            cursor.close()
            print(f"<-- [ÉXITO] Usuario ID {idusuario} eliminado correctamente.")
        except MySQLError as err:
            print(f"<-- [ERROR] No se pudo eliminar el usuario: {err}")

    def listar_por_id(self, idusuario):
        print(f"\n--> [INICIO] Consultando usuario ID: {idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = "SELECT * FROM usuario1 WHERE Idusuario = %s"
            cursor.execute(sql, (idusuario,))
            filas = cursor.fetchall()
            cursor.close()
            print("<-- [ÉXITO] Consulta realizada.")
            return filas
        except MySQLError as err:
            print(f"<-- [ERROR] No se pudo consultar: {err}")
            return []