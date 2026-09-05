from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class ServicioForm(FlaskForm):
    nombre = StringField('Nombre del servicio', validators=[
        DataRequired(message='El nombre del servicio es obligatorio'),
        Length(min=3, max=100, message='Debe tener entre 3 y 100 caracteres')
    ])
    precio = FloatField('Precio base ($ USD)', validators=[
        DataRequired(message='Ingresa un precio válido'),
        NumberRange(min=0.01, message='El precio debe ser mayor a 0')
    ])
    imagen = StringField('URL de imagen del servicio (Opcional)', validators=[
        Optional(),
        Length(max=500, message='La URL es demasiado larga')
    ])
    descripcion = TextAreaField('Descripción detallada', validators=[
        DataRequired(message='La descripción es obligatoria'),
        Length(min=10, max=500, message='Debe tener entre 10 y 500 caracteres')
    ])
    estado = SelectField('Estado del servicio', choices=[
        ('Activo', 'Activo'),
        ('Inactivo', 'Inactivo')
    ], validators=[DataRequired()])
    submit = SubmitField('Guardar servicio')