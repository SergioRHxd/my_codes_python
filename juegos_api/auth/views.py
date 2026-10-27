from urllib.parse import urlparse

from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from extensions import db
from models import User
from . import auth
from .forms import LoginForm, RegistrationForm


def destino_seguro(destino):
    """Acepta solo rutas internas ("/algo") para evitar open redirect."""
    if not destino:
        return False
    partes = urlparse(destino)
    return not partes.netloc and not partes.scheme and destino.startswith('/') \
        and not destino.startswith('//') and '\\' not in destino


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('juegos'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            flash(f'Bienvenido, {user.username}.', 'success')
            siguiente = request.args.get('next')
            if not destino_seguro(siguiente):
                siguiente = url_for('juegos')
            return redirect(siguiente)
        flash('Usuario o contraseña inválidos.', 'danger')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión.', 'info')
    return redirect(url_for('auth.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('juegos'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip())
        user.password = form.password.data  # el setter genera el hash
        db.session.add(user)
        db.session.commit()
        flash('Cuenta creada. Ya puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
