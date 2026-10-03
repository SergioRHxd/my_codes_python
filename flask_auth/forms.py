from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import (DataRequired, EqualTo, Length, Optional,
                                ValidationError)

from models import User


class RegistrationForm(FlaskForm):
    username = StringField(
        "Usuario",
        validators=[DataRequired(message="El usuario es obligatorio."),
                    Length(min=3, max=30, message="Debe tener entre 3 y 30 caracteres.")],
    )
    password = PasswordField(
        "Contraseña",
        validators=[DataRequired(message="La contraseña es obligatoria."),
                    Length(min=6, message="Mínimo 6 caracteres.")],
    )
    confirm_password = PasswordField(
        "Confirmar contraseña",
        validators=[DataRequired(message="Confirma tu contraseña."),
                    EqualTo("password", message="Las contraseñas no coinciden.")],
    )
    submit = SubmitField("Registrarme")

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError("Ese usuario ya existe.")


class LoginForm(FlaskForm):
    username = StringField("Usuario", validators=[DataRequired(message="Campo obligatorio.")])
    password = PasswordField("Contraseña", validators=[DataRequired(message="Campo obligatorio.")])
    submit = SubmitField("Iniciar sesión")


class EditProfileForm(FlaskForm):
    username = StringField(
        "Usuario",
        validators=[DataRequired(message="El usuario es obligatorio."),
                    Length(min=3, max=30, message="Debe tener entre 3 y 30 caracteres.")],
    )
    # Opcionales: si se dejan vacías, la contraseña no cambia.
    password = PasswordField(
        "Nueva contraseña (opcional)",
        validators=[Optional(), Length(min=6, message="Mínimo 6 caracteres.")],
    )
    confirm_password = PasswordField(
        "Confirmar nueva contraseña",
        validators=[EqualTo("password", message="Las contraseñas no coinciden.")],
    )
    submit = SubmitField("Guardar cambios")

    def __init__(self, original_user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_user = original_user

    def validate_username(self, field):
        other = User.query.filter_by(username=field.data.strip()).first()
        if other and other.id != self.original_user.id:
            raise ValidationError("Ese usuario ya existe.")
