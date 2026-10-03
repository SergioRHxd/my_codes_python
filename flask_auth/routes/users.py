from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, url_for)
from flask_login import (current_user, login_required, login_user,
                         logout_user)
from werkzeug.security import check_password_hash, generate_password_hash

from extensions import db
from forms import EditProfileForm, LoginForm, RegistrationForm
from models import User

users_bp = Blueprint("users", __name__)


@users_bp.route("/")
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("user_list.html", users=users)


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("users.profile"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip(),
                    password_hash=generate_password_hash(form.password.data))
        db.session.add(user)
        db.session.commit()
        flash("Registro exitoso. Ya puedes iniciar sesión.", "success")
        return redirect(url_for("users.login"))
    if request.method == "POST":
        flash("Revisa los errores del formulario.", "error")
    return render_template("register.html", form=form)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("users.profile"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and check_password_hash(user.password_hash, form.password.data):
            login_user(user)
            flash(f"Bienvenido, {user.username}.", "success")
            nxt = request.args.get("next")
            if nxt and nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("users.profile"))
        flash("Credenciales inválidas.", "error")
    return render_template("login.html", form=form)


@users_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("users.index"))


@users_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")


@users_bp.route("/profile/edit", methods=["GET", "POST"])
@login_required
def edit_profile():
    user = current_user._get_current_object()
    form = EditProfileForm(user, obj=user if request.method == "GET" else None)
    if form.validate_on_submit():
        user.username = form.username.data.strip()
        if form.password.data:
            user.password_hash = generate_password_hash(form.password.data)
        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("users.profile"))
    if request.method == "POST":
        flash("No se pudo guardar: revisa los errores.", "error")
    return render_template("edit_profile.html", form=form)


@users_bp.route("/profile/delete", methods=["POST"])
@login_required
def delete_profile():
    user = current_user._get_current_object()
    logout_user()
    db.session.delete(user)
    db.session.commit()
    flash("Tu cuenta fue eliminada.", "success")
    return redirect(url_for("users.index"))


@users_bp.route("/admin")
@login_required
def admin():
    """Ruta de prueba para provocar un 403 (captura del manejador de errores)."""
    abort(403)
