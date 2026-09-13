from flask import Flask, render_template, redirect, session, url_for, flash
from forms import RegistroForm 

app = Flask(__name__)
app.config['SECRET_KEY'] = '19734628'

@app.route('/', methods=['GET', 'POST'])
def index():
    form = RegistroForm()

    if form.validate_on_submit():
        session['nombre'] = form.name.data
        flash('Registro realizado correctamente.')
        return redirect(url_for('index'))

    return render_template(
        'index.html',
        form=form,
        nombre=session.get('nombre')
    )
    
@app.errorhandler(404)
def pagina_no_encontrada(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)
    
    
    