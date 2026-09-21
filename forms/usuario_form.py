"""
Formulario de Registro de Usuario - Flask-WTF
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from models import Usuario


class RegistroUsuarioForm(FlaskForm):
    """
    Formulario para dar de alta nuevos usuarios en el sistema.
    Valida la unicidad del nombre de usuario y la coincidencia de contraseñas.
    """
    usuario = StringField(
        'Nombre de Usuario',
        validators=[
            DataRequired(message='El nombre de usuario es obligatorio.'),
            Length(min=3, max=50, message='El usuario debe contener entre 3 y 50 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. claudia_admin', 'class': 'form-control', 'autocomplete': 'username'}
    )
    nombre = StringField(
        'Nombre Completo',
        validators=[
            DataRequired(message='El nombre completo es obligatorio.'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres.')
        ],
        render_kw={'placeholder': 'Ej. Claudia Patricia Morales', 'class': 'form-control'}
    )
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es obligatoria.'),
            Length(min=6, message='La contraseña debe contener al menos 6 caracteres.')
        ],
        render_kw={'placeholder': 'Mínimo 6 caracteres', 'class': 'form-control', 'autocomplete': 'new-password'}
    )
    confirm_password = PasswordField(
        'Confirmar Contraseña',
        validators=[
            DataRequired(message='Confirme la contraseña.'),
            EqualTo('password', message='Las contraseñas no coinciden.')
        ],
        render_kw={'placeholder': 'Repita la contraseña anterior', 'class': 'form-control', 'autocomplete': 'new-password'}
    )
    rol = SelectField(
        'Rol de Acceso',
        choices=[
            ('admin', 'Administrador del Sistema'),
            ('operador', 'Operador de Inventario y Ventas')
        ],
        default='admin',
        render_kw={'class': 'form-select'}
    )
    submit = SubmitField('Crear Cuenta de Usuario')

    def validate_usuario(self, field):
        """
        Comprueba que no exista otro usuario registrado con el mismo nombre.
        """
        existente = Usuario.obtener_por_usuario(field.data.strip())
        if existente:
            raise ValidationError('Este nombre de usuario ya se encuentra registrado. Elija otro diferente.')
