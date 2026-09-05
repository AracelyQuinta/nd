from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, SelectField, TextAreaField, HiddenField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, Optional


class FacturacionForm(FlaskForm):
    tipo = SelectField('Tipo de Documento', choices=[
        ('Factura', 'Factura de Venta (Comprobante Fiscal)'),
        ('Cotizacion', 'Cotización / Proforma Comercial')
    ], validators=[DataRequired()])

    numero = StringField('N° Documento / Código', validators=[
        DataRequired(message='El número de documento es obligatorio'),
        Length(min=3, max=40)
    ])
    cliente = StringField('Cliente / Razón Social', validators=[
        DataRequired(message='El nombre del cliente es obligatorio'),
        Length(min=3, max=100)
    ])
    fecha = StringField('Fecha de emisión', validators=[
        DataRequired(message='La fecha es obligatoria'),
        Length(min=8, max=10)
    ])
    validez = StringField('Vigencia / Plazo de la oferta', validators=[
        Optional(),
        Length(max=50)
    ])
    
    # Campo oculto para guardar la lista de ítems en formato JSON
    servicios_json = HiddenField('Detalle de Servicios')
    
    subtotal = FloatField('Subtotal ($)', validators=[
        Optional(),
        NumberRange(min=0, message='El subtotal no puede ser negativo')
    ])
    iva = FloatField('IVA 15% ($)', validators=[
        Optional(),
        NumberRange(min=0, message='El IVA no puede ser negativo')
    ])
    monto = FloatField('Total General ($)', validators=[
        DataRequired(message='El total es obligatorio'),
        NumberRange(min=0.01, message='El total debe ser mayor a 0')
    ])
    anticipo = FloatField('Abono recibido ($)', validators=[
        Optional(),
        NumberRange(min=0, message='El anticipo no puede ser negativo')
    ], default=0.00)
    saldo_pendiente = FloatField('Saldo Pendiente / Diferencia ($)', validators=[
        Optional(),
        NumberRange(min=0, message='El saldo no puede ser negativo')
    ], default=0.00)
    
    estado = SelectField('Estado del Documento', choices=[
        ('Pagada', 'Pagada (Totalmente Cancelada)'),
        ('Pendiente', 'Pendiente (Con Saldo por Cobrar)'),
        ('Aprobada', 'Aprobada por el Cliente (Cotización)'),
        ('En revision', 'En Revisión / Enviada (Cotización)'),
        ('Vencida', 'Vencida / Expirada')
    ], validators=[DataRequired()])

    notas = TextAreaField('Notas, Términos y Condiciones de Pago', validators=[
        Optional(),
        Length(max=400)
    ])
    submit = SubmitField('Guardar y Emitir Documento')