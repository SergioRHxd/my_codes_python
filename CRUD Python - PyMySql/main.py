from database import ConexionBD
from modelos import Usuario
from dao import UsuarioDAO

def menu():
    print("\n" + "="*30)
    print("   MENÚ CRUD USUARIOS")
    print("="*30)
    print("1. Crear Tabla")
    print("2. Insertar Usuario")
    print("3. Actualizar Usuario")
    print("4. Eliminar Usuario")
    print("5. Consultar Usuario por ID")
    print("6. Salir")
    return input("Selecciona una opción (1-6): ")

def pedir_datos_usuario(pedir_id=True):
    idusuario = int(input("Dame id del usuario: ")) if pedir_id else None
    nombres = input("Dame los nombres del usuario: ")
    ap = input("Dame el apellido paterno: ")
    am = input("Dame el apellido materno: ")
    user = input("Dame el usuario: ")
    pwd = input("Dame la contraseña: ")
    return Usuario(idusuario, nombres, ap, am, user, pwd)

def main():
    db = ConexionBD()
    conexion = db.conectar()

    if not conexion:
        print("No se pudo iniciar el sistema sin conexión a la BD.")
        return

    dao = UsuarioDAO(conexion)

    while True:
        opcion = menu()

        if opcion == "1":
            dao.crear_tabla()
        elif opcion == "2":
            u = pedir_datos_usuario(pedir_id=True)
            dao.insertar(u)
        elif opcion == "3":
            u = pedir_datos_usuario(pedir_id=True)
            dao.actualizar(u)
        elif opcion == "4":
            id_eliminar = int(input("Dame id del usuario a eliminar: "))
            dao.eliminar(id_eliminar)
        elif opcion == "5":
            id_buscar = int(input("Dame id del usuario a consultar: "))
            resultados = dao.listar_por_id(id_buscar)
            for r in resultados:
                print("   -> Registros:", r)
        elif opcion == "6":
            db.cerrar()
            print("¡Hasta luego!")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

if __name__ == "__main__":
    main()