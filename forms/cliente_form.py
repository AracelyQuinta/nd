from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre del cliente', validators=[DataRequired(), Length(min=3, max=100)])
    negocio = StringField('Tipo de negocio', validators=[DataRequired(), Length(min=3, max=100)])
    servicio = StringField('Servicio contratado', validators=[DataRequired(), Length(min=3, max=100)])
    ciudad = StringField('Ciudad', validators=[DataRequired(), Length(min=3, max=50)])
    submit = SubmitField('Guardar cliente')