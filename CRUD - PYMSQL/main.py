import pymysql

# ==============================================================================
# 1. CONFIGURACIÓN DE CREDENCIALES
# ==============================================================================
# Defino las variables globales para conectarme a MySQL en XAMPP
DB_HOST = 'localhost'
DB_USER = 'root'
DB_PASSWORD = '15054505'
DB_NAME = 'dbPython'  # <-- Nombre explícito de mi base de datos


# ==============================================================================
# 2. CLASE DE CONEXIÓN Y ADMINISTRACIÓN DE BD
# ==============================================================================
class ConexionBD:
    """Administro la creación de la BD 'dbPython', apertura y cierre de conexión."""

    def __init__(self):
        # Guardo los atributos de conexión en mi instancia mediante 'self'
        self.host = DB_HOST
        self.user = DB_USER
        self.password = DB_PASSWORD
        self.database = DB_NAME  # Asigno la constante 'dbPython'
        self.conexion = None

    def crear_base_datos(self):
        """Elimino la base de datos 'dbPython' si existe y la creo de nuevo."""
        print(f"\n--> [INICIO] Creando base de datos '{self.database}'...")
        try:
            # Me conecto al servidor sin especificar base de datos para poder crearla desde cero
            temp_conn = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = temp_conn.cursor()
            # Elimino y creo la base de datos 'dbPython' sin que marque error si ya existía
            cursor.execute(f"DROP DATABASE IF EXISTS {self.database}")
            cursor.execute(f"CREATE DATABASE {self.database}")
            temp_conn.commit() #Este commit asegura que los cambios se guarden en el servidor MySQL.
            cursor.close()
            temp_conn.close()
            print(f"<-- [ÉXITO] Base de datos '{self.database}' creada correctamente.")
        except pymysql.MySQLError as err:
            print(f"<-- [ERROR] No pude crear la base de datos: {err}")

    def conectar(self):
        """Abro la conexión con MySQL seleccionando mi base de datos 'dbPython'."""
        try:
            print(f"\n[SISTEMA] Intentando conectar a la base de datos '{self.database}'...")
            self.conexion = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            print("[SISTEMA] Conexión establecida con éxito.")
            return self.conexion
        except pymysql.MySQLError as err:
            print(f"[ERROR CONEXIÓN] {err}")
            return None

    def cerrar(self):
        """Cierro la conexión activa para liberar recursos en el servidor."""
        if self.conexion:
            self.conexion.close()
            print("[SISTEMA] Conexión cerrada correctamente.")


# ==============================================================================
# 3. CLASE MODELO (ENTIDAD DE DATOS)
# ==============================================================================
class Usuario:
    """Represento al usuario como un objeto en mi código Python."""

    def __init__(self, idusuario=None, nombres="", apellido_paterno="", apellido_materno="", user="", pwd=""):
        self.idusuario = idusuario
        self.nombres = nombres
        self.apellido_paterno = apellido_paterno
        self.apellido_materno = apellido_materno
        self.user = user
        self.pwd = pwd


# ==============================================================================
# 4. CLASE DAO (DATA ACCESS OBJECT - OPERACIONES SQL)
# ==============================================================================
class UsuarioDAO:
    """Encapsulo todas mis sentencias SQL para manipular la tabla 'usuario1'."""

    def __init__(self, conexion):
        self.conexion = conexion

    def crear_tabla(self):
        """Elimino la tabla previa si existe y la vuelvo a crear."""
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
        except pymysql.MySQLError as err:
            print(f"<-- [ERROR] No pude crear la tabla: {err}")

    def insertar(self, usuario):
        """Recibo un objeto Usuario e inserto sus datos en la base de datos."""
        print(f"\n--> [INICIO] Insertando usuario ID: {usuario.idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = "INSERT INTO usuario1 VALUES (%s, %s, %s, %s, %s, %s)"
            cursor.execute(sql,(
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
        except pymysql.MySQLError as err:
            print(f"<-- [ERROR] No pude insertar el usuario: {err}")

    def actualizar(self, usuario):
        """Actualizo los datos de un usuario usando el ID de mi objeto Usuario."""
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
        except pymysql.MySQLError as err:
            print(f"<-- [ERROR] No pude actualizar el usuario: {err}")

    def eliminar(self, idusuario):
        """Elimino un usuario especificando su ID como argumento."""
        print(f"\n--> [INICIO] Eliminando usuario ID: {idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = "DELETE FROM usuario1 WHERE Idusuario = %s"
            cursor.execute(sql, (idusuario,))
            self.conexion.commit()
            cursor.close()
            print(f"<-- [ÉXITO] Usuario ID {idusuario} eliminado correctamente.")
        except pymysql.MySQLError as err:
            print(f"<-- [ERROR] No pude eliminar el usuario: {err}")

    def listar_por_id(self, idusuario):
        """Busco y retorno los registros que coinciden con el ID ingresado."""
        print(f"\n--> [INICIO] Consultando usuario ID: {idusuario}...")
        try:
            cursor = self.conexion.cursor()
            sql = "SELECT * FROM usuario1 WHERE Idusuario = %s"
            cursor.execute(sql, (idusuario,))
            filas = cursor.fetchall()
            cursor.close()
            print("<-- [ÉXITO] Consulta realizada.")
            return filas
        except pymysql.MySQLError as err:
            print(f"<-- [ERROR] No pude consultar los datos: {err}")
            return []


# ==============================================================================
# 5. FUNCIONES DE INTERFAZ DE USUARIO (CONSOLA)
# ==============================================================================
def pedir_datos_usuario(pedir_id=True):
    """Pido los datos por teclado (input) y construyo mi objeto Usuario."""
    idusuario = int(input("Dame id del usuario: ")) if pedir_id else None
    nombres = input("Dame los nombres del usuario: ")
    ap = input("Dame el apellido paterno: ")
    am = input("Dame el apellido materno: ")
    user = input("Dame el usuario: ")
    pwd = input("Dame la contraseña: ")
    return Usuario(idusuario, nombres, ap, am, user, pwd)

def menu():
    """Muestro las opciones del sistema en la terminal."""
    print("\n" + "="*35)
    print("   MENÚ CRUD USUARIOS (POO)")
    print("="*35)
    print("1. Crear Base de Datos 'dbPython'")
    print("2. Crear Tabla 'usuario1'")
    print("3. Insertar Usuario")
    print("4. Actualizar Usuario")
    print("5. Eliminar Usuario")
    print("6. Consultar Usuario por ID")
    print("7. Salir")
    return input("Selecciona una opción (1-7): ")


# ==============================================================================
# 6. BLOQUE DE EJECUCIÓN PRINCIPAL
# ==============================================================================
if __name__ == "__main__":
    db = ConexionBD()
    conexion = None
    dao = None

    while True:
        opcion = menu()

        if opcion == "1":
            # Creo la base de datos dbPython e inicio la conexión activa
            db.crear_base_datos()
            conexion = db.conectar()
            if conexion:
                dao = UsuarioDAO(conexion)
        elif opcion in ["2", "3", "4", "5", "6"]:
            # Verifico que tenga una conexión activa antes de ejecutar mi CRUD
            if not conexion:
                conexion = db.conectar()
                if conexion:
                    dao = UsuarioDAO(conexion)

            if not conexion:
                print("[ERROR] No puedo continuar sin conexión a la base de datos.")
                continue

            if opcion == "2":
                dao.crear_tabla()
            elif opcion == "3":
                nuevo_usuario = pedir_datos_usuario(pedir_id=True)
                dao.insertar(nuevo_usuario)
            elif opcion == "4":
                usuario_actualizado = pedir_datos_usuario(pedir_id=True)
                dao.actualizar(usuario_actualizado)
            elif opcion == "5":
                id_eliminar = int(input("Dame id del usuario a eliminar: "))
                dao.eliminar(id_eliminar)
            elif opcion == "6":
                id_buscar = int(input("Dame id del usuario a consultar: "))
                resultados = dao.listar_por_id(id_buscar)
                for registro in resultados:
                    print("   -> Registro encontrado:", registro)
        elif opcion == "7":
            db.cerrar()
            print("¡Sistema finalizado con éxito!")
            break
        else:
            print("Opción no válida. Por favor, intenta de nuevo.")