from functools import wraps

from flask import (Blueprint, abort, flash, redirect, render_template,
                   request, session, url_for)

from extensions import db
from forms import EditProfileForm, LoginForm, RegisterForm
from models import User

users_bp = Blueprint("users", __name__)


# ---------- Autenticación básica----------
def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "user_id" not in session:
            flash("Debes iniciar sesión para ver esa página.", "error")
            return redirect(url_for("users.login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


def current_user():
    uid = session.get("user_id")
    return db.session.get(User, uid) if uid else None


@users_bp.app_context_processor
def inject_current_user():
    """Deja `current_user` disponible en todas las plantillas."""
    return {"current_user": current_user()}


# ---------- Rutas ----------
@users_bp.route("/")
def index():
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template("user_list.html", users=users)


@users_bp.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data.strip(),
                    email=form.email.data.strip().lower())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("¡Registro exitoso! Ya puedes iniciar sesión.", "success")
        return redirect(url_for("users.login"))
    if request.method == "POST":
        flash("Revisa los errores del formulario.", "error")
    return render_template("register.html", form=form)


@users_bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data.strip()).first()
        if user and user.check_password(form.password.data):
            session.clear()
            session["user_id"] = user.id
            flash(f"Bienvenido, {user.username}.", "success")
            nxt = request.args.get("next")
            if nxt and nxt.startswith("/") and not nxt.startswith("//"):
                return redirect(nxt)
            return redirect(url_for("users.profile", id=user.id))
        flash("Usuario o contraseña incorrectos.", "error")
    return render_template("login.html", form=form)


@users_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada.", "success")
    return redirect(url_for("users.index"))


@users_bp.route("/profile/<int:id>")
@login_required
def profile(id):
    user = db.get_or_404(User, id)
    return render_template("profile.html", user=user)


@users_bp.route("/profile/<int:id>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(id):
    user = db.get_or_404(User, id)
    if user.id != session["user_id"]:
        abort(403)

    form = EditProfileForm(user, obj=user if request.method == "GET" else None)
    if form.validate_on_submit():
        user.username = form.username.data.strip()
        user.email = form.email.data.strip().lower()
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash("Perfil actualizado correctamente.", "success")
        return redirect(url_for("users.profile", id=user.id))
    if request.method == "POST":
        flash("No se pudo guardar: revisa los errores.", "error")
    return render_template("edit_profile.html", form=form, user=user)


@users_bp.route("/profile/<int:id>/delete", methods=["POST"])
@login_required
def delete_profile(id):
    user = db.get_or_404(User, id)
    if user.id != session["user_id"]:
        abort(403)
    db.session.delete(user)
    db.session.commit()
    session.clear()
    flash("Tu cuenta fue eliminada.", "success")
    return redirect(url_for("users.index"))
