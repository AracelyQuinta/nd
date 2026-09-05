import json, os
from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, request

from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm
from database import (
    initialize_database,
    list_services,
    list_clients,
    create_invoice,
    delete_invoice,
    list_invoices,
    update_invoice,
    create_provider,
    delete_provider,
    get_provider,
    list_providers,
    update_provider,
)
from controllers.clientes import clientes_bp
from controllers.servicios import servicios_bp
from data.seed_data import COTIZACIONES_INICIALES, FACTURAS_INICIALES, PROVEEDORES_INICIALES, SERVICIOS_INICIALES

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get("secret_key", "dev-secret-key-change-me")
app.register_blueprint(servicios_bp)
app.register_blueprint(clientes_bp)

initialize_database(SERVICIOS_INICIALES, FACTURAS_INICIALES, PROVEEDORES_INICIALES)

ESTADOS_FACTURA = [
    ('Pagada', 'Pagada (Totalmente Cancelada)'),
    ('Pendiente', 'Pendiente (Con Saldo por Cobrar)'),
    ('Vencida', 'Vencida / Expirada'),
]
ESTADOS_COTIZACION = [
    ('Aprobada', 'Aprobada por el Cliente (Cotización)'),
    ('En revision', 'En Revisión / Enviada (Cotización)'),
]


def configurar_estados_documento(form, tipo, todos=False):
    form.estado.choices = ESTADOS_FACTURA + ESTADOS_COTIZACION if todos else (
        ESTADOS_COTIZACION if tipo == 'Cotizacion' else ESTADOS_FACTURA
    )


# ---------- RUTAS PRINCIPALES DE VISUALIZACIÓN ----------

@app.route('/')
def inicio():
    mensaje = "Soluciones digitales para hacer crecer tu negocio"
    empresa = {
        "nombre": "Nexo Digital",
        "ubicacion": "Quito / Puyo - Ecuador",
        "modalidad": "Atención 100% en línea"
    }
    return render_template('index.html', mensaje=mensaje, empresa=empresa, servicios=list_services())


@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html', proveedores=list_providers())


@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html', facturas=documentos_facturacion())


def documentos_facturacion():
    return list_invoices() + COTIZACIONES_INICIALES


# ---------- RUTAS CRUD: PROVEEDORES ----------

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        create_provider({
            "nombre": form.nombre.data,
            "servicio": form.servicio.data,
            "sitio": form.sitio.data,
            "estado": form.estado.data
        })
        flash('Proveedor registrado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    return render_template('formulario_proveedor.html', form=form, editando=False)


@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = get_provider(id)
    if proveedor is None:
        flash('El proveedor solicitado no existe.', 'danger')
        return redirect(url_for('proveedores'))

    form = ProveedorForm(data=proveedor) if request.method == 'GET' else ProveedorForm()
    
    if form.validate_on_submit():
        update_provider(id, {
            "nombre": form.nombre.data,
            "servicio": form.servicio.data,
            "sitio": form.sitio.data,
            "estado": form.estado.data
        })
        flash(f'Proveedor "{form.nombre.data}" actualizado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    
    return render_template('formulario_proveedor.html', form=form, editando=True, id=id)


@app.route('/proveedores/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_proveedor(id):
    proveedor = get_provider(id)
    if proveedor is not None:
        nombre = proveedor['nombre']
        delete_provider(id)
        flash(f'Proveedor "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El proveedor solicitado no existe.', 'danger')
    return redirect(url_for('proveedores'))


# ---------- RUTAS CRUD: FACTURACIÓN & COTIZACIONES DINÁMICAS ----------

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    tipo_solicitado = request.form.get('tipo') if request.method == 'POST' else request.args.get(
        'tipo', 'Cotizacion' if request.args.get('servicio_id') is not None else 'Factura'
    )
    form = FacturacionForm()
    configurar_estados_documento(form, tipo_solicitado, todos=request.method == 'GET')
    
    # Sugerir valores por defecto si es GET
    if request.method == 'GET':
        form.tipo.data = tipo_solicitado
        if tipo_solicitado == 'Cotizacion':
            form.numero.data = f"COT-2026-{len(COTIZACIONES_INICIALES) + 1:04d}"
            form.validez.data = "15 días calendario"
            form.estado.data = "En revision"
        else:
            form.numero.data = f"001-001-{len(list_invoices()) + 1:04d}"
            form.validez.data = "30 días"
            form.estado.data = "Pendiente"
        form.fecha.data = str(date.today())
        form.anticipo.data = 0.00
        form.saldo_pendiente.data = 0.00

    if form.validate_on_submit():
        servicios_detalle = []
        if form.servicios_json.data:
            try:
                servicios_detalle = json.loads(form.servicios_json.data)
            except Exception:
                servicios_detalle = []

        subtotal_val = float(form.subtotal.data) if form.subtotal.data is not None else float(form.monto.data)
        iva_val = float(form.iva.data) if form.iva.data is not None else round(subtotal_val * 0.15, 2)
        total_val = float(form.monto.data)
        anticipo_val = float(form.anticipo.data) if form.anticipo.data is not None else 0.00
        saldo_val = float(form.saldo_pendiente.data) if form.saldo_pendiente.data is not None else max(0.0, total_val - anticipo_val)
        
        tipo_doc = form.tipo.data
        estado_final = form.estado.data

        # Si el saldo es 0 y es factura, marcar como pagada
        if tipo_doc == 'Factura' and saldo_val <= 0 and estado_final == 'Pendiente':
            estado_final = 'Pagada'

        documento = {
            "tipo": tipo_doc,
            "numero": form.numero.data,
            "cliente": form.cliente.data,
            "fecha": str(form.fecha.data),
            "validez": form.validez.data or "15 días calendario",
            "servicios_detalle": servicios_detalle,
            "subtotal": subtotal_val,
            "iva": iva_val,
            "monto": total_val,
            "anticipo": anticipo_val,
            "saldo_pendiente": saldo_val,
            "estado": estado_final,
            "notas": form.notas.data or ("Propuesta comercial emitida por NexoDigital." if tipo_doc == 'Cotizacion' else "Comprobante de venta de servicios digitales NexoDigital.")
        }
        if tipo_doc == 'Factura':
            create_invoice(documento)
        else:
            COTIZACIONES_INICIALES.append(documento)
        
        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" guardada exitosamente.', 'success')
        return redirect(url_for('facturacion'))
        
    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=False,
        servicios_catalogo=list_services(),
        clientes_registrados=list_clients(),
        servicio_seleccionado_id=request.args.get('servicio_id', type=int)
    )


@app.route('/facturacion/editar/<int:id>', methods=['GET', 'POST'])
def editar_factura(id):
    documentos = documentos_facturacion()
    if id < 0 or id >= len(documentos):
        flash('El documento solicitado no existe.', 'danger')
        return redirect(url_for('facturacion'))
    
    factura = documentos[id]
    form = FacturacionForm(data=factura) if request.method == 'GET' else FacturacionForm()
    tipo_formulario = request.form.get('tipo', factura.get('tipo', 'Factura'))
    configurar_estados_documento(form, tipo_formulario, todos=request.method == 'GET')

    if request.method == 'GET' and 'servicios_detalle' in factura:
        form.servicios_json.data = json.dumps(factura['servicios_detalle'])

    if form.validate_on_submit():
        servicios_detalle = []
        if form.servicios_json.data:
            try:
                servicios_detalle = json.loads(form.servicios_json.data)
            except Exception:
                servicios_detalle = factura.get('servicios_detalle', [])

        subtotal_val = float(form.subtotal.data) if form.subtotal.data is not None else float(form.monto.data)
        iva_val = float(form.iva.data) if form.iva.data is not None else round(subtotal_val * 0.15, 2)
        total_val = float(form.monto.data)
        anticipo_val = float(form.anticipo.data) if form.anticipo.data is not None else 0.00
        saldo_val = float(form.saldo_pendiente.data) if form.saldo_pendiente.data is not None else max(0.0, total_val - anticipo_val)
        tipo_doc = form.tipo.data

        documento = {
            "tipo": tipo_doc,
            "numero": form.numero.data,
            "cliente": form.cliente.data,
            "fecha": str(form.fecha.data),
            "validez": form.validez.data or "15 días calendario",
            "servicios_detalle": servicios_detalle,
            "subtotal": subtotal_val,
            "iva": iva_val,
            "monto": total_val,
            "anticipo": anticipo_val,
            "saldo_pendiente": saldo_val,
            "estado": form.estado.data,
            "notas": form.notas.data or "Documento generado por NexoDigital."
        }
        if factura.get('_persistida'):
            update_invoice(factura['_db_id'], documento)
        else:
            COTIZACIONES_INICIALES[COTIZACIONES_INICIALES.index(factura)] = documento
        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))
    
    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=True,
        id=id,
        servicios_catalogo=list_services(),
        clientes_registrados=list_clients(),
        detalle_existente=factura.get('servicios_detalle', [])
    )


@app.route('/facturacion/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_factura(id):
    documentos = documentos_facturacion()
    if 0 <= id < len(documentos):
        doc = documentos[id]
        tipo_str = "Cotización" if doc.get('tipo') == 'Cotizacion' else "Factura"
        numero = doc['numero']
        if doc.get('_persistida'):
            delete_invoice(doc['_db_id'])
        else:
            COTIZACIONES_INICIALES.remove(doc)
        flash(f'{tipo_str} "{numero}" eliminada correctamente.', 'success')
    else:
        flash('El documento solicitado no existe.', 'danger')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/comprobante/<int:id>')
def ver_comprobante(id):
    documentos = documentos_facturacion()
    if id < 0 or id >= len(documentos):
        flash('El documento solicitado no existe.', 'danger')
        return redirect(url_for('facturacion'))
    
    factura = documentos[id]
    return render_template('comprobante_factura.html', factura=factura, id=id)


# ---------- PUNTO DE ENTRADA ----------

if __name__ == '__main__':
    app.run(debug=True)