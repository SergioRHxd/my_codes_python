from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Email

class RegistroForm(FlaskForm):
    name = StringField('Nombre', validators=[DataRequired(), Length(min=3, max=50)])
    email = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    submit = SubmitField('Registrarse')
    