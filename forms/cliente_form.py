from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, Length, Regexp


class ClienteForm(FlaskForm):
    provincias = [
        ('', 'Seleccione una provincia'),
        ('Azuay', 'Azuay'),
        ('Bolivar', 'Bolivar'),
        ('Cañar', 'Cañar'),
        ('Carchi', 'Carchi'),
        ('Chimborazo', 'Chimborazo'),
        ('Cotopaxi', 'Cotopaxi'),
        ('El Oro', 'El Oro'),
        ('Esmeraldas', 'Esmeraldas'),
        ('Galapagos', 'Galapagos'),
        ('Guayas', 'Guayas'),
        ('Imbabura', 'Imbabura'),
        ('Loja', 'Loja'),
        ('Los Rios', 'Los Rios'),
        ('Manabi', 'Manabi'),
        ('Morona Santiago', 'Morona Santiago'),
        ('Napo', 'Napo'),
        ('Orellana', 'Orellana'),
        ('Pastaza', 'Pastaza'),
        ('Pichincha', 'Pichincha'),
        ('Santa Elena', 'Santa Elena'),
        ('Santo Domingo de los Tsachilas', 'Santo Domingo de los Tsachilas'),
        ('Sucumbios', 'Sucumbios'),
        ('Tungurahua', 'Tungurahua'),
        ('Zamora Chinchipe', 'Zamora Chinchipe'),
    ]
    nombre = StringField('Nombre del cliente', validators=[DataRequired(), Length(min=3, max=100)])
    negocio = StringField('Tipo de negocio', validators=[DataRequired(), Length(min=3, max=100)])
    celular = StringField('Celular', validators=[
        DataRequired(),
        Regexp(r'^\d{10}$', message='El celular debe tener exactamente 10 dígitos')
    ])
    provincia = SelectField('Provincia', choices=provincias, validators=[DataRequired()])
    canton = StringField('Cantón', validators=[DataRequired(), Length(min=3, max=60)])
    submit = SubmitField('Guardar cliente')