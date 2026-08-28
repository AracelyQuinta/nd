import json
from datetime import date
from flask import Flask, render_template, redirect, url_for, flash, request

from forms.cliente_form import ClienteForm
from forms.servicio_form import ServicioForm
from forms.proveedor_form import ProveedorForm
from forms.facturacion_form import FacturacionForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'nexodigital_clave_secreta_2026'


# ---------- DATOS DE EJEMPLO REALISTAS (Memoria de Aplicación) ----------

lista_servicios = [
    {
        "nombre": "Diseño y Desarrollo Web Profesional",
        "descripcion": "Sitios web modernos, adaptables a móviles, ultra rápidos y con optimización SEO para posicionamiento en Google.",
        "precio": 250.00,
        "tiempo_estimado": "5 a 7 días laborables",
        "imagen": "https://images.unsplash.com/photo-1547658719-da2b51169166?auto=format&fit=crop&w=800&q=80",
        "disponible": True
    },
    {
        "nombre": "Catálogos Digitales Interactivos",
        "descripcion": "Diseño de catálogos visuales con galerías de productos, filtros por categoría y botón de pedido directo por WhatsApp.",
        "precio": 120.00,
        "tiempo_estimado": "3 a 4 días laborables",
        "imagen": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
        "disponible": True
    },
    {
        "nombre": "Menús Digitales QR para Restaurantes",
        "descripcion": "Menú interactivo accesible por código QR para mesas, con fotos de platos, precios y actualización en tiempo real.",
        "precio": 65.00,
        "tiempo_estimado": "24 a 48 horas",
        "imagen": "https://images.unsplash.com/photo-1595079672139-5470887216e9?auto=format&fit=crop&w=800&q=80",
        "disponible": True
    },
    {
        "nombre": "Formularios Dinámicos y Cotizadores",
        "descripcion": "Formularios avanzados para captura de clientes potenciales, reservas, cotizaciones y pedidos con validaciones en vivo.",
        "precio": 85.00,
        "tiempo_estimado": "2 a 3 días laborables",
        "imagen": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80",
        "disponible": True
    },
    {
        "nombre": "Integración con WhatsApp & Redes",
        "descripcion": "Configuración de canales de atención directa por WhatsApp Business, botones flotantes y enlaces a TikTok, Instagram y Facebook.",
        "precio": 45.00,
        "tiempo_estimado": "24 horas",
        "imagen": "https://images.unsplash.com/photo-1611746872915-64382b5c76da?auto=format&fit=crop&w=800&q=80",
        "disponible": True
    },
    {
        "nombre": "Accesibilidad y Optimización Web",
        "descripcion": "Auditoría técnica y adaptación de sitios web existentes bajo estándares WCAG y buenas prácticas de velocidad.",
        "precio": 110.00,
        "tiempo_estimado": "3 a 5 días laborables",
        "imagen": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
        "disponible": False
    }
]

lista_proveedores = [
    {"nombre": "Hostinger", "servicio": "Hosting Web y Servidores Cloud", "sitio": "hostinger.com", "estado": "Activo"},
    {"nombre": "GoDaddy", "servicio": "Registro de Dominios Internacionales", "sitio": "godaddy.com", "estado": "Activo"},
    {"nombre": "Figma", "servicio": "Software de Prototipado y Diseño UI/UX", "sitio": "figma.com", "estado": "Activo"},
    {"nombre": "Cloudflare", "servicio": "Seguridad Web, SSL y CDN Global", "sitio": "cloudflare.com", "estado": "Pendiente"}
]

lista_clientes = [
    {"nombre": "Panadería El Trigal", "negocio": "Panadería y Pastelería", "servicio": "Diseño Web + Menú QR", "ciudad": "Santo Domingo"},
    {"nombre": "Boutique Bella", "negocio": "Tienda de Ropa y Modas", "servicio": "Catálogo Digital", "ciudad": "Quito"},
    {"nombre": "Taller Mecánico RPM", "negocio": "Servicios Automotrices", "servicio": "Formulario de Citas", "ciudad": "Santo Domingo"},
    {"nombre": "Café Aroma Amazónico", "negocio": "Cafetería y Restaurante", "servicio": "Menú QR + WhatsApp", "ciudad": "Puyo"}
]

lista_facturas = [
    {
        "tipo": "Factura",
        "numero": "001-001-0001",
        "cliente": "Panadería El Trigal",
        "fecha": "2026-01-15",
        "validez": "30 días",
        "servicios_detalle": [
            {"servicio": "Diseño y Desarrollo Web Profesional", "precio": 250.00, "cantidad": 1, "ajuste": 0.00, "total": 250.00},
            {"servicio": "Menús Digitales QR para Restaurantes", "precio": 65.00, "cantidad": 1, "ajuste": 0.00, "total": 65.00}
        ],
        "subtotal": 315.00,
        "iva": 47.25,
        "monto": 362.25,
        "anticipo": 362.25,
        "saldo_pendiente": 0.00,
        "estado": "Pagada",
        "notas": "Factura liquidada al 100%. Proyecto entregado con dominio y hosting activo."
    },
    {
        "tipo": "Cotizacion",
        "numero": "COT-2026-0042",
        "cliente": "Boutique Bella",
        "fecha": "2026-02-18",
        "validez": "15 días calendario",
        "servicios_detalle": [
            {"servicio": "Catálogos Digitales Interactivos", "precio": 120.00, "cantidad": 1, "ajuste": 0.00, "total": 120.00},
            {"servicio": "Integración con WhatsApp & Redes", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00}
        ],
        "subtotal": 165.00,
        "iva": 24.75,
        "monto": 189.75,
        "anticipo": 100.00,
        "saldo_pendiente": 89.75,
        "estado": "Aprobada",
        "notas": "Cotización aprobada. Anticipo de $100 recibido. Saldo restante de $89.75 a cancelar contra entrega del catálogo."
    },
    {
        "tipo": "Cotizacion",
        "numero": "COT-2026-0043",
        "cliente": "Taller Mecánico RPM",
        "fecha": "2026-02-20",
        "validez": "15 días calendario",
        "servicios_detalle": [
            {"servicio": "Formularios Dinámicos y Cotizadores", "precio": 85.00, "cantidad": 1, "ajuste": 15.00, "total": 100.00}
        ],
        "subtotal": 100.00,
        "iva": 15.00,
        "monto": 115.00,
        "anticipo": 0.00,
        "saldo_pendiente": 115.00,
        "estado": "En revision",
        "notas": "Propuesta en revisión por gerencia. Ajuste de $15 por personalización de búsqueda por número de placa."
    },
    {
        "tipo": "Factura",
        "numero": "001-001-0002",
        "cliente": "Café Aroma Amazónico",
        "fecha": "2026-03-10",
        "validez": "15 días",
        "servicios_detalle": [
            {"servicio": "Menús Digitales QR para Restaurantes", "precio": 65.00, "cantidad": 2, "ajuste": 0.00, "total": 130.00},
            {"servicio": "Integración con WhatsApp & Redes", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00}
        ],
        "subtotal": 175.00,
        "iva": 26.25,
        "monto": 201.25,
        "anticipo": 100.00,
        "saldo_pendiente": 101.25,
        "estado": "Pendiente",
        "notas": "Factura emitida con anticipo de $100.00. Diferencia pendiente de $101.25 con plazo de 10 días."
    }
]


# ---------- RUTAS PRINCIPALES DE VISUALIZACIÓN ----------

@app.route('/')
def inicio():
    mensaje = "Soluciones digitales para hacer crecer tu negocio"
    empresa = {
        "nombre": "Nexo Digital",
        "ubicacion": "Quito / Puyo - Ecuador",
        "modalidad": "Atención 100% en línea"
    }
    return render_template('index.html', mensaje=mensaje, empresa=empresa, servicios=lista_servicios)


@app.route('/servicios')
@app.route('/servicio')
def servicios():
    return render_template('servicios.html', servicios=lista_servicios)


@app.route('/proveedores')
def proveedores():
    return render_template('proveedores.html', proveedores=lista_proveedores)


@app.route('/clientes')
def clientes():
    return render_template('clientes.html', clientes=lista_clientes)


@app.route('/facturacion')
def facturacion():
    return render_template('facturacion.html', facturas=lista_facturas)


# ---------- RUTAS CRUD: CLIENTES ----------

@app.route('/clientes/nuevo', methods=['GET', 'POST'])
def nuevo_cliente():
    form = ClienteForm()
    if form.validate_on_submit():
        lista_clientes.append({
            "nombre": form.nombre.data,
            "negocio": form.negocio.data,
            "servicio": form.servicio.data,
            "ciudad": form.ciudad.data
        })
        flash('Cliente registrado correctamente.', 'success')
        return redirect(url_for('clientes'))
    return render_template('formulario_cliente.html', form=form, editando=False)


@app.route('/clientes/editar/<int:id>', methods=['GET', 'POST'])
def editar_cliente(id):
    if id < 0 or id >= len(lista_clientes):
        flash('El cliente solicitado no existe.', 'danger')
        return redirect(url_for('clientes'))
    
    cliente = lista_clientes[id]
    form = ClienteForm(data=cliente) if request.method == 'GET' else ClienteForm()
    
    if form.validate_on_submit():
        lista_clientes[id] = {
            "nombre": form.nombre.data,
            "negocio": form.negocio.data,
            "servicio": form.servicio.data,
            "ciudad": form.ciudad.data
        }
        flash(f'Cliente "{form.nombre.data}" actualizado correctamente.', 'success')
        return redirect(url_for('clientes'))
    
    return render_template('formulario_cliente.html', form=form, editando=True, id=id)


@app.route('/clientes/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_cliente(id):
    if 0 <= id < len(lista_clientes):
        nombre = lista_clientes[id]['nombre']
        lista_clientes.pop(id)
        flash(f'Cliente "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El cliente solicitado no existe.', 'danger')
    return redirect(url_for('clientes'))


# ---------- RUTAS CRUD: SERVICIOS ----------

@app.route('/servicios/nuevo', methods=['GET', 'POST'])
@app.route('/servicio/nuevo', methods=['GET', 'POST'])
def nuevo_servicio():
    form = ServicioForm()
    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80"
        tiempo = form.tiempo_estimado.data.strip() if form.tiempo_estimado.data and form.tiempo_estimado.data.strip() else "2 a 5 días"

        lista_servicios.append({
            "nombre": form.nombre.data,
            "descripcion": form.descripcion.data,
            "precio": float(form.precio.data),
            "tiempo_estimado": tiempo,
            "imagen": imagen_url,
            "disponible": form.disponible.data
        })
        flash('Servicio registrado correctamente.', 'success')
        return redirect(url_for('servicios'))
    return render_template('formulario_servicio.html', form=form, editando=False)


@app.route('/servicios/editar/<int:id>', methods=['GET', 'POST'])
@app.route('/servicio/editar/<int:id>', methods=['GET', 'POST'])
def editar_servicio(id):
    if id < 0 or id >= len(lista_servicios):
        flash('El servicio solicitado no existe.', 'danger')
        return redirect(url_for('servicios'))
    
    servicio = lista_servicios[id]
    form = ServicioForm(data=servicio) if request.method == 'GET' else ServicioForm()
    
    if form.validate_on_submit():
        imagen_url = form.imagen.data.strip() if form.imagen.data and form.imagen.data.strip() else servicio.get("imagen", "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80")
        tiempo = form.tiempo_estimado.data.strip() if form.tiempo_estimado.data and form.tiempo_estimado.data.strip() else "2 a 5 días"

        lista_servicios[id] = {
            "nombre": form.nombre.data,
            "descripcion": form.descripcion.data,
            "precio": float(form.precio.data),
            "tiempo_estimado": tiempo,
            "imagen": imagen_url,
            "disponible": form.disponible.data
        }
        flash(f'Servicio "{form.nombre.data}" actualizado correctamente.', 'success')
        return redirect(url_for('servicios'))
    
    return render_template('formulario_servicio.html', form=form, editando=True, id=id)


@app.route('/servicios/eliminar/<int:id>', methods=['POST', 'GET'])
@app.route('/servicio/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_servicio(id):
    if 0 <= id < len(lista_servicios):
        nombre = lista_servicios[id]['nombre']
        lista_servicios.pop(id)
        flash(f'Servicio "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El servicio solicitado no existe.', 'danger')
    return redirect(url_for('servicios'))


# ---------- RUTAS CRUD: PROVEEDORES ----------

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    form = ProveedorForm()
    if form.validate_on_submit():
        lista_proveedores.append({
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
    if id < 0 or id >= len(lista_proveedores):
        flash('El proveedor solicitado no existe.', 'danger')
        return redirect(url_for('proveedores'))
    
    proveedor = lista_proveedores[id]
    form = ProveedorForm(data=proveedor) if request.method == 'GET' else ProveedorForm()
    
    if form.validate_on_submit():
        lista_proveedores[id] = {
            "nombre": form.nombre.data,
            "servicio": form.servicio.data,
            "sitio": form.sitio.data,
            "estado": form.estado.data
        }
        flash(f'Proveedor "{form.nombre.data}" actualizado correctamente.', 'success')
        return redirect(url_for('proveedores'))
    
    return render_template('formulario_proveedor.html', form=form, editando=True, id=id)


@app.route('/proveedores/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_proveedor(id):
    if 0 <= id < len(lista_proveedores):
        nombre = lista_proveedores[id]['nombre']
        lista_proveedores.pop(id)
        flash(f'Proveedor "{nombre}" eliminado correctamente.', 'success')
    else:
        flash('El proveedor solicitado no existe.', 'danger')
    return redirect(url_for('proveedores'))


# ---------- RUTAS CRUD: FACTURACIÓN & COTIZACIONES DINÁMICAS ----------

@app.route('/facturacion/nueva', methods=['GET', 'POST'])
def nueva_factura():
    form = FacturacionForm()
    tipo_solicitado = request.args.get('tipo', 'Cotizacion' if request.args.get('servicio_id') is not None else 'Factura')
    
    # Sugerir valores por defecto si es GET
    if request.method == 'GET':
        form.tipo.data = tipo_solicitado
        if tipo_solicitado == 'Cotizacion':
            form.numero.data = f"COT-2026-{len(lista_facturas) + 1:04d}"
            form.validez.data = "15 días calendario"
            form.estado.data = "En revision"
        else:
            form.numero.data = f"001-001-{len(lista_facturas) + 1:04d}"
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

        lista_facturas.append({
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
        })
        
        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" guardada exitosamente.', 'success')
        return redirect(url_for('facturacion'))
        
    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=False,
        servicios_catalogo=lista_servicios,
        clientes_registrados=lista_clientes,
        servicio_seleccionado_id=request.args.get('servicio_id', type=int)
    )


@app.route('/facturacion/editar/<int:id>', methods=['GET', 'POST'])
def editar_factura(id):
    if id < 0 or id >= len(lista_facturas):
        flash('El documento solicitado no existe.', 'danger')
        return redirect(url_for('facturacion'))
    
    factura = lista_facturas[id]
    form = FacturacionForm(data=factura) if request.method == 'GET' else FacturacionForm()

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

        lista_facturas[id] = {
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
        nombre_doc = "Cotización" if tipo_doc == 'Cotizacion' else "Factura"
        flash(f'{nombre_doc} "{form.numero.data}" actualizada correctamente.', 'success')
        return redirect(url_for('facturacion'))
    
    return render_template(
        'formulario_facturacion.html',
        form=form,
        editando=True,
        id=id,
        servicios_catalogo=lista_servicios,
        clientes_registrados=lista_clientes,
        detalle_existente=factura.get('servicios_detalle', [])
    )


@app.route('/facturacion/eliminar/<int:id>', methods=['POST', 'GET'])
def eliminar_factura(id):
    if 0 <= id < len(lista_facturas):
        doc = lista_facturas[id]
        tipo_str = "Cotización" if doc.get('tipo') == 'Cotizacion' else "Factura"
        numero = doc['numero']
        lista_facturas.pop(id)
        flash(f'{tipo_str} "{numero}" eliminada correctamente.', 'success')
    else:
        flash('El documento solicitado no existe.', 'danger')
    return redirect(url_for('facturacion'))


@app.route('/facturacion/comprobante/<int:id>')
def ver_comprobante(id):
    if id < 0 or id >= len(lista_facturas):
        flash('El documento solicitado no existe.', 'danger')
        return redirect(url_for('facturacion'))
    
    factura = lista_facturas[id]
    return render_template('comprobante_factura.html', factura=factura, id=id)


# ---------- PUNTO DE ENTRADA ----------

if __name__ == '__main__':
    app.run(debug=True)