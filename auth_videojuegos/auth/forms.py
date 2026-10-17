from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError

from models import User


class LoginForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Ingresar')


class RegistrationForm(FlaskForm):
    username = StringField(
        'Usuario',
        validators=[DataRequired(), Length(min=3, max=64)],
    )
    password = PasswordField(
        'Contraseña',
        validators=[DataRequired(), Length(min=6, message='Mínimo 6 caracteres.')],
    )
    password2 = PasswordField(
        'Confirmar contraseña',
        validators=[DataRequired(), EqualTo('password', message='Las contraseñas no coinciden.')],
    )
    submit = SubmitField('Registrarme')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.strip()).first():
            raise ValidationError('Ese nombre de usuario ya está en uso.')
