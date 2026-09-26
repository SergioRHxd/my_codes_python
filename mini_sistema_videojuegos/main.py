from flask import Flask, render_template, request, redirect, url_for
import controlador_juegos

app = Flask(__name__)

# La ruta inicial envía al usuario al listado, que es la vista principal del CRUD.
@app.route("/")
def inicio():
    return redirect(url_for("juegos"))

# Consulta los registros mediante el controlador y los entrega a la plantilla.
@app.route("/juegos")
def juegos():
    lista_juegos = controlador_juegos.obtener_juegos()
    return render_template("juegos.html", juegos=lista_juegos)

# Muestra el formulario vacío; el guardado se procesa en una ruta POST aparte.
@app.route("/agregar_juego")
def formulario_agregar_juego():
    return render_template("agregar_juego.html")

@app.route("/guardar_juego", methods=["POST"])
def guardar_juego():
    # Flask obtiene estos valores de los campos enviados por el formulario.
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controlador_juegos.insertar_juego(nombre, descripcion, precio)
    # El patrón POST/redirect/GET evita repetir el envío al recargar la página.
    return redirect(url_for("juegos"))

@app.route("/eliminar_juego", methods=["POST"])
def eliminar_juego():
    controlador_juegos.eliminar_juego(request.form["id"])
    return redirect(url_for("juegos"))

@app.route("/formulario_editar_juego/<int:id>")
def editar_juego(id):
    # Se carga el registro seleccionado para precargar sus datos en el formulario.
    juego = controlador_juegos.obtener_juego_por_id(id)
    return render_template("editar_juego.html", juego=juego)

@app.route("/actualizar_juego", methods=["POST"])
def actualizar_juego():
    # El ID identifica qué registro actualizar; los demás campos contienen sus nuevos valores.
    id = request.form["id"]
    nombre = request.form["nombre"]
    descripcion = request.form["descripcion"]
    precio = request.form["precio"]
    controlador_juegos.actualizar_juego(nombre, descripcion, precio, id)
    return redirect(url_for("juegos"))

if __name__ == "__main__":
    app.run(debug=True)
