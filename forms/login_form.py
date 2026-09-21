"""
Formulario de Autenticación (Login) - Flask-WTF
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """
    Formulario para el inicio de sesión de usuarios autorizados.
    """
    usuario = StringField(
        'Nombre de Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio.'),
            Length(min=3, max=50, message='El usuario debe tener entre 3 y 50 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. admin o anis', 'class': 'form-control', 'autocomplete': 'username'}
    )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.')
        ],
        render_kw={'placeholder': 'Ingrese su contraseña', 'class': 'form-control', 'autocomplete': 'current-password'}
    )
    remember_me = BooleanField(
        'Mantener sesión activa',
        default=False
    )
    submit = SubmitField('Iniciar Sesión')
