from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class ClienteForm(FlaskForm):
    nombre = StringField('Nombre del cliente', validators=[DataRequired(), Length(min=3, max=100)])
    negocio = StringField('Tipo de negocio', validators=[DataRequired(), Length(min=3, max=100)])
    servicio = StringField('Servicio contratado', validators=[DataRequired(), Length(min=3, max=100)])
    celular = StringField('Celular', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='El celular debe tener exactamente 10 dígitos')
    ])
    provincia = StringField('Provincia', validators=[DataRequired(), Length(min=3, max=60)])
    canton = StringField('Cantón', validators=[DataRequired(), Length(min=3, max=60)])
    barrio = StringField('Barrio', validators=[DataRequired(), Length(min=3, max=100)])
    submit = SubmitField('Guardar cliente')