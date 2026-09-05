SERVICIOS_INICIALES = [
    {
        "nombre": "Diseño y Desarrollo Web Profesional",
        "descripcion": "Sitios web modernos, adaptables a móviles, ultra rápidos y con optimización SEO para posicionamiento en Google.",
        "precio": 250.00,
        "imagen": "https://images.unsplash.com/photo-1547658719-da2b51169166?auto=format&fit=crop&w=800&q=80",
        "estado": "Activo",
        "disponible": True,
    },
    {
        "nombre": "Catálogos Digitales Interactivos",
        "descripcion": "Diseño de catálogos visuales con galerías de productos, filtros por categoría y botón de pedido directo por WhatsApp.",
        "precio": 120.00,
        "imagen": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=800&q=80",
        "estado": "Activo",
        "disponible": True,
    },
    {
        "nombre": "Menús Digitales QR para Restaurantes",
        "descripcion": "Menú interactivo accesible por código QR para mesas, con fotos de platos, precios y actualización en tiempo real.",
        "precio": 65.00,
        "imagen": "https://images.unsplash.com/photo-1595079672139-5470887216e9?auto=format&fit=crop&w=800&q=80",
        "estado": "Activo",
        "disponible": True,
    },
    {
        "nombre": "Formularios Dinámicos y Cotizadores",
        "descripcion": "Formularios avanzados para captura de clientes potenciales, reservas, cotizaciones y pedidos con validaciones en vivo.",
        "precio": 85.00,
        "imagen": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=800&q=80",
        "estado": "Activo",
        "disponible": True,
    },
    {
        "nombre": "Integración con WhatsApp & Redes",
        "descripcion": "Configuración de canales de atención directa por WhatsApp Business, botones flotantes y enlaces a TikTok, Instagram y Facebook.",
        "precio": 45.00,
        "imagen": "https://images.unsplash.com/photo-1611746872915-64382b5c76da?auto=format&fit=crop&w=800&q=80",
        "estado": "Activo",
        "disponible": True,
    },
    {
        "nombre": "Accesibilidad y Optimización Web",
        "descripcion": "Auditoría técnica y adaptación de sitios web existentes bajo estándares WCAG y buenas prácticas de velocidad.",
        "precio": 110.00,
        "imagen": "https://images.unsplash.com/photo-1507238691740-187a5b1d37b8?auto=format&fit=crop&w=800&q=80",
        "estado": "Inactivo",
        "disponible": False,
    },
]

PROVEEDORES_INICIALES = [
    {"nombre": "Hostinger", "servicio": "Hosting Web y Servidores Cloud", "sitio": "hostinger.com", "estado": "Activo"},
    {"nombre": "GoDaddy", "servicio": "Registro de Dominios Internacionales", "sitio": "godaddy.com", "estado": "Activo"},
    {"nombre": "Figma", "servicio": "Software de Prototipado y Diseño UI/UX", "sitio": "figma.com", "estado": "Activo"},
    {"nombre": "Cloudflare", "servicio": "Seguridad Web, SSL y CDN Global", "sitio": "cloudflare.com", "estado": "Pendiente"},
]

FACTURAS_INICIALES = [
    {
        "tipo": "Factura",
        "numero": "001-001-0001",
        "cliente": "Panadería El Trigal",
        "fecha": "2026-01-15",
        "validez": "30 días",
        "servicios_detalle": [
            {"servicio": "Diseño y Desarrollo Web Profesional", "precio": 250.00, "cantidad": 1, "ajuste": 0.00, "total": 250.00},
            {"servicio": "Menús Digitales QR para Restaurantes", "precio": 65.00, "cantidad": 1, "ajuste": 0.00, "total": 65.00},
        ],
        "anticipo": 362.25,
        "estado": "Pagada",
        "notas": "Factura liquidada al 100%. Proyecto entregado con dominio y hosting activo.",
    },
    {
        "tipo": "Cotizacion",
        "numero": "COT-2026-0042",
        "cliente": "Boutique Bella",
        "fecha": "2026-02-18",
        "validez": "15 días calendario",
        "servicios_detalle": [
            {"servicio": "Catálogos Digitales Interactivos", "precio": 120.00, "cantidad": 1, "ajuste": 0.00, "total": 120.00},
            {"servicio": "Integración con WhatsApp & Redes", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00},
        ],
        "subtotal": 165.00,
        "iva": 24.75,
        "monto": 189.75,
        "anticipo": 100.00,
        "saldo_pendiente": 89.75,
        "estado": "Aprobada",
        "notas": "Cotización aprobada. Anticipo de $100 recibido.",
    },
    {
        "tipo": "Cotizacion",
        "numero": "COT-2026-0043",
        "cliente": "Taller Mecánico RPM",
        "fecha": "2026-02-20",
        "validez": "15 días calendario",
        "servicios_detalle": [
            {"servicio": "Formularios Dinámicos y Cotizadores", "precio": 85.00, "cantidad": 1, "ajuste": 15.00, "total": 100.00},
        ],
        "subtotal": 100.00,
        "iva": 15.00,
        "monto": 115.00,
        "anticipo": 0.00,
        "saldo_pendiente": 115.00,
        "estado": "En revision",
        "notas": "Propuesta en revisión por gerencia.",
    },
    {
        "tipo": "Factura",
        "numero": "001-001-0002",
        "cliente": "Café Aroma Amazónico",
        "fecha": "2026-03-10",
        "validez": "15 días",
        "servicios_detalle": [
            {"servicio": "Menús Digitales QR para Restaurantes", "precio": 65.00, "cantidad": 2, "ajuste": 0.00, "total": 130.00},
            {"servicio": "Integración con WhatsApp & Redes", "precio": 45.00, "cantidad": 1, "ajuste": 0.00, "total": 45.00},
        ],
        "anticipo": 100.00,
        "estado": "Pendiente",
        "notas": "Factura emitida con anticipo de $100.00.",
    },
]

COTIZACIONES_INICIALES = [
    invoice for invoice in FACTURAS_INICIALES if invoice["tipo"] == "Cotizacion"
]
