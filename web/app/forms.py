# web/app/forms.py
from flask_wtf import FlaskForm
from wtforms import (StringField, TextAreaField, SelectField,
                DateField, PasswordField, BooleanField, SubmitField)
from wtforms.validators import DataRequired, Length, Email, EqualTo, Optional

class ProyectoForm(FlaskForm):
    """Formulario para crear y editar proyectos."""
    titulo = StringField(
        'Título del proyecto',
        validators=[
        DataRequired(message='El título es obligatorio.'),
        Length(min=3, max=100,
        message='El título debe tener entre 3 y 100 caracteres.')
        ]
        )
    descripcion = TextAreaField(
        'Descripción',
        validators=[Optional(), Length(max=500,
        message='La descripción no puede superar los 500 caracteres.')]
        )
    fecha_limite = DateField(
        'Fecha límite',
        validators=[Optional()],
        format='%Y-%m-%d'
        )
    submit = SubmitField('Guardar proyecto')

class TareaForm(FlaskForm):
    """Formulario para crear y editar tareas."""
    titulo = StringField(
        'Título de la tarea',
        validators=[DataRequired(), Length(min=3, max=200)]
        )
    descripcion = TextAreaField(
        'Descripción',
        validators=[Optional()]
        )
    prioridad = SelectField(
        'Prioridad',
        choices=[
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
        ],
        default='media'
        )
    estado = SelectField(
        'Estado',
        choices=[
        ('pendiente', 'Pendiente'),
        ('en_progreso', 'En progreso'),
        ('revision', 'En revisión'),
        ('completada', 'Completada'),
        ],
        default='pendiente'
        )
    fecha_limite = DateField(
        'Fecha límite',
        validators=[Optional()],
        format='%Y-%m-%d'
        )

    submit = SubmitField('Guardar tarea')

class BusquedaForm(FlaskForm):
    """Formulario de búsqueda de proyectos y tareas."""
    q = StringField(
        'Buscar',
        validators=[DataRequired(), Length(min=2,
        message='Escribe al menos 2 caracteres para buscar.')]
        )
    submit = SubmitField('Buscar')
class LoginForm(FlaskForm):
    """Formulario de inicio de sesión (lo usaremos en U05)."""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    recordarme = BooleanField('Recordarme')
    submit = SubmitField('Iniciar sesión')
class RegistroForm(FlaskForm):
    """Formulario de registro de nuevos usuarios (lo usaremos en U05)."""
    nombre = StringField('Nombre', validators=[DataRequired(), Length(2,
            80)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired(),
            Length(min=8, message='La contraseña debe tener al menos 8 caracteres.')])
    confirmar = PasswordField('Confirmar contraseña', validators=[EqualTo('password', 
    message='Las contraseñas no coinciden.')])

    submit = SubmitField('Crear cuenta')
