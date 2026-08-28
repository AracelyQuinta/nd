from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Length

class ProveedorForm(FlaskForm):
    nombre = StringField('Nombre del proveedor', validators=[DataRequired(), Length(min=3, max=100)])
    servicio = StringField('Servicio que ofrece', validators=[DataRequired(), Length(min=3, max=100)])
    sitio = StringField('Sitio web', validators=[DataRequired(), Length(min=3, max=100)])
    estado = SelectField('Estado', choices=[('Activo', 'Activo'), ('Pendiente', 'Pendiente'), ('Inactivo', 'Inactivo')], validators=[DataRequired()])
    submit = SubmitField('Guardar proveedor')
