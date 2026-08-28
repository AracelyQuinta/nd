import sys
import json
sys.path.insert(0, r'c:\Users\quiar\Documents\GitHub\NEXODIGITAL')

from app import app, lista_servicios, lista_clientes, lista_proveedores, lista_facturas

app.config['WTF_CSRF_ENABLED'] = False
client = app.test_client()

print("=== 1. VERIFICAR TODAS LAS RUTAS GET ===")
routes = [
    '/',
    '/servicios',
    '/proveedores',
    '/clientes',
    '/facturacion',
    '/servicios/nuevo',
    '/clientes/nuevo',
    '/proveedores/nuevo',
    '/facturacion/nueva',
    '/facturacion/nueva?tipo=Cotizacion',
    '/facturacion/nueva?tipo=Factura&servicio_id=0',
    '/servicios/editar/0',
    '/clientes/editar/0',
    '/proveedores/editar/0',
    '/facturacion/editar/0',
    '/facturacion/comprobante/0',
    '/facturacion/comprobante/1'
]

for r in routes:
    res = client.get(r)
    print(f"GET {r:45} -> {res.status_code}")
    assert res.status_code == 200, f"Error en ruta {r}"

print("\n=== 2. CREAR SERVICIO CON PRECIO E IMAGEN ===")
serv_count = len(lista_servicios)
res_new_serv = client.post('/servicios/nuevo', data={
    'nombre': 'App Móvil PWA para Clientes',
    'descripcion': 'Aplicación web progresiva instalable en Android e iOS sin pasar por tiendas.',
    'precio': '320.00',
    'tiempo_estimado': '7 a 10 días',
    'imagen': 'https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c',
    'disponible': 'y'
}, follow_redirects=True)
assert res_new_serv.status_code == 200
assert len(lista_servicios) == serv_count + 1
print("Servicio creado exitosamente!")

print("\n=== 3. CREAR COTIZACIÓN CON ANTICIPO Y SALDO PENDIENTE (DIFERENCIA) ===")
cant_inicial = len(lista_facturas)
items_cotizacion = [
    {"servicio": "Diseño y Desarrollo Web Profesional", "precio": 250.00, "cantidad": 1, "ajuste": 50.00, "total": 300.00},
    {"servicio": "Integración con WhatsApp & Redes", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00}
]

res_cot = client.post('/facturacion/nueva', data={
    'tipo': 'Cotizacion',
    'numero': 'COT-2026-0099',
    'cliente': 'Hotel & Spa Selva Verde',
    'fecha': '2026-08-28',
    'validez': '15 días calendario',
    'servicios_json': json.dumps(items_cotizacion),
    'subtotal': '345.00',
    'iva': '51.75',
    'monto': '396.75',
    'anticipo': '150.00',
    'saldo_pendiente': '246.75',
    'estado': 'En revision',
    'notas': 'Cotización con entrega en 5 días. Anticipo de $150 para kickoff y saldo contra entrega.'
}, follow_redirects=True)

assert res_cot.status_code == 200
assert len(lista_facturas) == cant_inicial + 1
nueva_cot = lista_facturas[-1]
assert nueva_cot['tipo'] == 'Cotizacion'
assert nueva_cot['anticipo'] == 150.00
assert nueva_cot['saldo_pendiente'] == 246.75
print(f"Cotización Creada: {nueva_cot['numero']} | Total: ${nueva_cot['monto']} | Anticipo: ${nueva_cot['anticipo']} | Saldo Pendiente: ${nueva_cot['saldo_pendiente']}")

print("\n=== 4. CREAR FACTURA CON SALDO LIQUIDADO ===")
res_fac = client.post('/facturacion/nueva', data={
    'tipo': 'Factura',
    'numero': '001-001-0088',
    'cliente': 'Comercializadora El Oriente',
    'fecha': '2026-08-28',
    'validez': '30 días',
    'servicios_json': json.dumps([{"servicio": "Menús Digitales QR", "precio": 65.00, "cantidad": 1, "ajuste": 0.00, "total": 65.00}]),
    'subtotal': '65.00',
    'iva': '9.75',
    'monto': '74.75',
    'anticipo': '74.75',
    'saldo_pendiente': '0.00',
    'estado': 'Pagada',
    'notas': 'Cancelado en su totalidad.'
}, follow_redirects=True)

assert res_fac.status_code == 200
assert len(lista_facturas) == cant_inicial + 2
print("Factura creada exitosamente!")

print("\n=== 5. COMPROBAR RENDERIZADO DEL COMPROBANTE/COTIZACIÓN ===")
res_view = client.get(f'/facturacion/comprobante/{len(lista_facturas)-2}')
assert res_view.status_code == 200
assert b'COTIZACI' in res_view.data
assert b'246.75' in res_view.data
assert b'150.00' in res_view.data
print("El comprobante renderizó correctamente el documento como COTIZACIÓN con el desglose de anticipo y saldo!")

print("\n>>> ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE (100%)! <<<")
