import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "nexodigital.db"


def get_connection():
    DATA_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def _table_columns(connection, table_name):
    return {row[1] for row in connection.execute(f"PRAGMA table_info({table_name})")}


def _state_id(connection, entity, name):
    row = connection.execute(
        "SELECT id FROM estados WHERE entidad = ? AND nombre = ?",
        (entity, name),
    ).fetchone()
    return row[0]


def initialize_database(seed_services=None, seed_invoices=None, seed_providers=None):
    connection = get_connection()
    try:
        legacy_clients = False
        legacy_locations = False
        connection.execute("DROP TABLE IF EXISTS facturas_legacy")
        connection.execute("DROP TABLE IF EXISTS factura_detalle_legacy")
        connection.execute("DROP TABLE IF EXISTS proveedores_legacy")
        client_columns = _table_columns(connection, "clientes")
        if "servicio_contratado_id" in client_columns:
            if _table_columns(connection, "facturas"):
                connection.execute("ALTER TABLE facturas RENAME TO facturas_clients_legacy")
            if _table_columns(connection, "factura_detalle"):
                connection.execute("ALTER TABLE factura_detalle RENAME TO factura_detalle_clients_legacy")
            connection.execute("ALTER TABLE clientes RENAME TO clientes_legacy")
            legacy_clients = True
        if "barrio" in _table_columns(connection, "ubicaciones"):
            if _table_columns(connection, "facturas"):
                connection.execute("ALTER TABLE facturas RENAME TO facturas_locations_legacy")
            if _table_columns(connection, "factura_detalle"):
                connection.execute("ALTER TABLE factura_detalle RENAME TO factura_detalle_locations_legacy")
            if _table_columns(connection, "clientes"):
                connection.execute("ALTER TABLE clientes RENAME TO clientes_locations_legacy")
            connection.execute("ALTER TABLE ubicaciones RENAME TO ubicaciones_legacy")
            legacy_locations = True
        legacy_products = None
        legacy_providers = None
        if _table_columns(connection, "productos") and "tiempo_estimado" in _table_columns(connection, "productos"):
            connection.execute("ALTER TABLE productos RENAME TO productos_legacy")
            legacy_products = "productos_legacy"

        invoice_columns = _table_columns(connection, "facturas")
        if invoice_columns and ({"cliente", "subtotal", "iva", "monto", "anticipo", "saldo_pendiente"} & invoice_columns):
            connection.execute("ALTER TABLE facturas RENAME TO facturas_legacy")

        if _table_columns(connection, "proveedores") and "estado" in _table_columns(connection, "proveedores"):
            connection.execute("ALTER TABLE proveedores RENAME TO proveedores_legacy")

        if _table_columns(connection, "clientes") and "negocio" in _table_columns(connection, "clientes"):
            connection.execute("DROP TABLE IF EXISTS clientes_legacy")
            connection.execute("ALTER TABLE clientes RENAME TO clientes_legacy")

        detail_columns = _table_columns(connection, "factura_detalle")
        if detail_columns and ({"producto_id", "total"} & detail_columns):
            connection.execute("ALTER TABLE factura_detalle RENAME TO factura_detalle_legacy")

        connection.execute("DROP TABLE IF EXISTS producto_proveedor")

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS estados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entidad TEXT NOT NULL,
                nombre TEXT NOT NULL,
                UNIQUE (entidad, nombre)
            )
            """
        )
        connection.executemany(
            "INSERT OR IGNORE INTO estados (entidad, nombre) VALUES (?, ?)",
            [
                ("servicio", "Activo"),
                ("servicio", "Inactivo"),
                ("proveedor", "Activo"),
                ("proveedor", "Pendiente"),
                ("proveedor", "Inactivo"),
                ("factura", "Pagada"),
                ("factura", "Pendiente"),
                ("factura", "Aprobada"),
                ("factura", "En revision"),
                ("factura", "Vencida"),
                ("pago", "Registrado"),
                ("pago", "Anulado"),
            ],
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS servicios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                precio REAL NOT NULL,
                imagen TEXT NOT NULL,
                estado_id INTEGER NOT NULL,
                FOREIGN KEY (estado_id) REFERENCES estados(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tipos_negocio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS ubicaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provincia TEXT NOT NULL,
                canton TEXT NOT NULL,
                UNIQUE (provincia, canton)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                celular TEXT NOT NULL CHECK (length(celular) = 10 AND celular NOT GLOB '*[^0-9]*'),
                tipo_negocio_id INTEGER NOT NULL,
                ubicacion_id INTEGER NOT NULL,
                FOREIGN KEY (tipo_negocio_id) REFERENCES tipos_negocio(id),
                FOREIGN KEY (ubicacion_id) REFERENCES ubicaciones(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS proveedores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                servicio TEXT NOT NULL,
                sitio TEXT NOT NULL,
                estado_id INTEGER NOT NULL,
                FOREIGN KEY (estado_id) REFERENCES estados(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS facturas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tipo TEXT NOT NULL CHECK (tipo IN ('Factura', 'Cotizacion')),
                numero TEXT NOT NULL UNIQUE,
                cliente_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                validez TEXT,
                estado_id INTEGER NOT NULL,
                notas TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (estado_id) REFERENCES estados(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS factura_detalle (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER NOT NULL,
                servicio_id INTEGER NOT NULL,
                descripcion TEXT NOT NULL,
                precio_unitario REAL NOT NULL,
                cantidad INTEGER NOT NULL DEFAULT 1 CHECK (cantidad > 0),
                ajuste REAL NOT NULL DEFAULT 0,
                FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
                FOREIGN KEY (servicio_id) REFERENCES servicios(id)
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                factura_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                monto REAL NOT NULL CHECK (monto > 0),
                metodo_pago TEXT NOT NULL,
                estado_id INTEGER NOT NULL,
                referencia TEXT,
                notas TEXT,
                FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
                FOREIGN KEY (estado_id) REFERENCES estados(id)
            )
            """
        )
        if any(row[2] == "facturas_legacy" for row in connection.execute("PRAGMA foreign_key_list(pagos)").fetchall()):
            connection.execute("ALTER TABLE pagos RENAME TO pagos_legacy")
            connection.execute(
                """
                CREATE TABLE pagos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    factura_id INTEGER NOT NULL,
                    fecha TEXT NOT NULL,
                    monto REAL NOT NULL CHECK (monto > 0),
                    metodo_pago TEXT NOT NULL,
                    estado_id INTEGER NOT NULL,
                    referencia TEXT,
                    notas TEXT,
                    FOREIGN KEY (factura_id) REFERENCES facturas(id) ON DELETE CASCADE,
                    FOREIGN KEY (estado_id) REFERENCES estados(id)
                )
                """
            )
            connection.execute(
                """
                INSERT INTO pagos
                    (id, factura_id, fecha, monto, metodo_pago, estado_id, referencia, notas)
                SELECT id, factura_id, fecha, monto, metodo_pago, estado_id, referencia, notas
                FROM pagos_legacy
                """
            )
            connection.execute("DROP TABLE pagos_legacy")
        connection.execute("DROP VIEW IF EXISTS resumen_facturas")
        connection.execute(
            """
            CREATE VIEW resumen_facturas AS
            SELECT
                f.id,
                f.numero,
                f.tipo,
                f.cliente_id,
                f.fecha,
                (
                    SELECT COALESCE(SUM((d.precio_unitario * d.cantidad) + d.ajuste), 0)
                    FROM factura_detalle AS d
                    WHERE d.factura_id = f.id
                ) AS subtotal,
                (
                    SELECT COALESCE(SUM((d.precio_unitario * d.cantidad) + d.ajuste), 0) * 0.15
                    FROM factura_detalle AS d
                    WHERE d.factura_id = f.id
                ) AS iva,
                (
                    SELECT COALESCE(SUM((d.precio_unitario * d.cantidad) + d.ajuste), 0) * 1.15
                    FROM factura_detalle AS d
                    WHERE d.factura_id = f.id
                ) AS monto,
                (SELECT COALESCE(SUM(p.monto), 0) FROM pagos AS p WHERE p.factura_id = f.id) AS anticipo,
                MAX(
                    (
                        SELECT COALESCE(SUM((d.precio_unitario * d.cantidad) + d.ajuste), 0) * 1.15
                        FROM factura_detalle AS d
                        WHERE d.factura_id = f.id
                    ) - (SELECT COALESCE(SUM(p.monto), 0) FROM pagos AS p WHERE p.factura_id = f.id),
                    0
                ) AS saldo_pendiente
            FROM facturas AS f
            """
        )

        activo = _state_id(connection, "servicio", "Activo")
        inactivo = _state_id(connection, "servicio", "Inactivo")
        proveedor_activo = _state_id(connection, "proveedor", "Activo")
        if legacy_providers:
            connection.execute(
                """
                INSERT INTO proveedores (nombre, servicio, sitio, estado_id)
                SELECT nombre, servicio, sitio, ? FROM proveedores_legacy
                """,
                (proveedor_activo,),
            )
            connection.execute("DROP TABLE proveedores_legacy")
        if legacy_products:
            connection.execute(
                """
                INSERT INTO servicios (nombre, descripcion, precio, imagen, estado_id)
                SELECT nombre, descripcion, precio, imagen,
                       CASE WHEN disponible = 1 THEN ? ELSE ? END
                FROM productos_legacy
                """,
                (activo, inactivo),
            )
            connection.execute("DROP TABLE productos_legacy")
        elif seed_services and connection.execute("SELECT COUNT(*) FROM servicios").fetchone()[0] == 0:
            connection.executemany(
                """
                INSERT INTO servicios (nombre, descripcion, precio, imagen, estado_id)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        service["nombre"],
                        service["descripcion"],
                        service["precio"],
                        service["imagen"],
                        activo if service.get("disponible", True) else inactivo,
                    )
                    for service in seed_services
                ],
            )
        if seed_invoices and connection.execute("SELECT COUNT(*) FROM facturas").fetchone()[0] == 0:
            for invoice in seed_invoices:
                if invoice.get("tipo") != "Factura":
                    continue
                _insert_invoice(connection, invoice)
        if seed_providers and connection.execute("SELECT COUNT(*) FROM proveedores").fetchone()[0] == 0:
            connection.executemany(
                "INSERT INTO proveedores (nombre, servicio, sitio, estado_id) VALUES (?, ?, ?, ?)",
                [
                    (
                        provider["nombre"],
                        provider["servicio"],
                        provider["sitio"],
                        _state_id(connection, "proveedor", provider["estado"]),
                    )
                    for provider in seed_providers
                ],
            )
        if legacy_clients:
            connection.execute(
                """
                INSERT INTO clientes (id, nombre, celular, tipo_negocio_id, ubicacion_id)
                SELECT id, nombre, celular, tipo_negocio_id, ubicacion_id
                FROM clientes_legacy
                """
            )
            if _table_columns(connection, "facturas_clients_legacy"):
                connection.execute(
                    """
                    INSERT INTO facturas
                        (id, tipo, numero, cliente_id, fecha, validez, estado_id, notas)
                    SELECT id, tipo, numero, cliente_id, fecha, validez, estado_id, notas
                    FROM facturas_clients_legacy
                    """
                )
            if _table_columns(connection, "factura_detalle_clients_legacy"):
                connection.execute(
                    """
                    INSERT INTO factura_detalle
                        (id, factura_id, servicio_id, descripcion, precio_unitario, cantidad, ajuste)
                    SELECT id, factura_id, servicio_id, descripcion, precio_unitario, cantidad, ajuste
                    FROM factura_detalle_clients_legacy
                    """
                )
        if legacy_locations:
            connection.execute(
                """
                INSERT OR IGNORE INTO ubicaciones (id, provincia, canton)
                SELECT MIN(id), provincia, canton
                FROM ubicaciones_legacy
                GROUP BY provincia, canton
                """
            )
            connection.execute(
                """
                INSERT INTO clientes (id, nombre, celular, tipo_negocio_id, ubicacion_id)
                SELECT c.id, c.nombre, c.celular, c.tipo_negocio_id, u.id
                FROM clientes_locations_legacy AS c
                JOIN ubicaciones_legacy AS old_u ON old_u.id = c.ubicacion_id
                JOIN ubicaciones AS u
                  ON u.provincia = old_u.provincia AND u.canton = old_u.canton
                """
            )
            if _table_columns(connection, "facturas_locations_legacy"):
                connection.execute(
                    """
                    INSERT INTO facturas
                        (id, tipo, numero, cliente_id, fecha, validez, estado_id, notas)
                    SELECT id, tipo, numero, cliente_id, fecha, validez, estado_id, notas
                    FROM facturas_locations_legacy
                    """
                )
            if _table_columns(connection, "factura_detalle_locations_legacy"):
                connection.execute(
                    """
                    INSERT INTO factura_detalle
                        (id, factura_id, servicio_id, descripcion, precio_unitario, cantidad, ajuste)
                    SELECT id, factura_id, servicio_id, descripcion, precio_unitario, cantidad, ajuste
                    FROM factura_detalle_locations_legacy
                    """
                )
        connection.execute("DROP TABLE IF EXISTS facturas_legacy")
        connection.execute("DROP TABLE IF EXISTS factura_detalle_legacy")
        connection.execute("DROP TABLE IF EXISTS proveedores_legacy")
        connection.execute("DROP TABLE IF EXISTS clientes_legacy")
        connection.execute("DROP TABLE IF EXISTS facturas_clients_legacy")
        connection.execute("DROP TABLE IF EXISTS factura_detalle_clients_legacy")
        connection.execute("DROP TABLE IF EXISTS clientes_locations_legacy")
        connection.execute("DROP TABLE IF EXISTS ubicaciones_legacy")
        connection.execute("DROP TABLE IF EXISTS facturas_locations_legacy")
        connection.execute("DROP TABLE IF EXISTS factura_detalle_locations_legacy")
        connection.execute("DROP TABLE IF EXISTS servicios_contratados")
        connection.commit()
    finally:
        connection.close()


def list_services():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT s.id, s.nombre, s.descripcion, s.precio, s.imagen, e.nombre AS estado
            FROM servicios AS s
            JOIN estados AS e ON e.id = s.estado_id
            ORDER BY s.id
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_service(service_id):
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT s.id, s.nombre, s.descripcion, s.precio, s.imagen, e.nombre AS estado
            FROM servicios AS s
            JOIN estados AS e ON e.id = s.estado_id
            WHERE s.id = ?
            """,
            (service_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def create_service(service):
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO servicios (nombre, descripcion, precio, imagen, estado_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                service["nombre"],
                service["descripcion"],
                service["precio"],
                service["imagen"],
                _state_id(connection, "servicio", service["estado"]),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update_service(service_id, service):
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE servicios
            SET nombre = ?, descripcion = ?, precio = ?, imagen = ?, estado_id = ?
            WHERE id = ?
            """,
            (
                service["nombre"],
                service["descripcion"],
                service["precio"],
                service["imagen"],
                _state_id(connection, "servicio", service["estado"]),
                service_id,
            ),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def delete_service(service_id):
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM servicios WHERE id = ?", (service_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def _catalog_id(connection, table, name):
    row = connection.execute(f"SELECT id FROM {table} WHERE nombre = ?", (name,)).fetchone()
    if row:
        return row[0]
    cursor = connection.execute(f"INSERT INTO {table} (nombre) VALUES (?)", (name,))
    return cursor.lastrowid


def _location_id(connection, client):
    row = connection.execute(
        "SELECT id FROM ubicaciones WHERE provincia = ? AND canton = ?",
        (client["provincia"], client["canton"]),
    ).fetchone()
    if row:
        return row[0]
    cursor = connection.execute(
        "INSERT INTO ubicaciones (provincia, canton) VALUES (?, ?)",
        (client["provincia"], client["canton"]),
    )
    return cursor.lastrowid


def list_clients():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
                     SELECT c.id, c.nombre, c.celular, tn.nombre AS negocio,
                         u.provincia, u.canton,
                         u.provincia || ', ' || u.canton AS ciudad
            FROM clientes AS c
            JOIN tipos_negocio AS tn ON tn.id = c.tipo_negocio_id
            JOIN ubicaciones AS u ON u.id = c.ubicacion_id
            ORDER BY c.id
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_client(client_id):
    clients = list_clients()
    return next((client for client in clients if client["id"] == client_id), None)


def create_client(client):
    connection = get_connection()
    try:
        negocio_id = _catalog_id(connection, "tipos_negocio", client["negocio"])
        ubicacion_id = _location_id(connection, client)
        cursor = connection.execute(
            """
            INSERT INTO clientes (nombre, celular, tipo_negocio_id, ubicacion_id)
            VALUES (?, ?, ?, ?)
            """,
            (client["nombre"], client["celular"], negocio_id, ubicacion_id),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update_client(client_id, client):
    connection = get_connection()
    try:
        negocio_id = _catalog_id(connection, "tipos_negocio", client["negocio"])
        ubicacion_id = _location_id(connection, client)
        cursor = connection.execute(
            """
            UPDATE clientes
            SET nombre = ?, celular = ?, tipo_negocio_id = ?, ubicacion_id = ?
            WHERE id = ?
            """,
            (client["nombre"], client["celular"], negocio_id, ubicacion_id, client_id),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def delete_client(client_id):
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM clientes WHERE id = ?", (client_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def list_providers():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT p.id, p.nombre, p.servicio, p.sitio, e.nombre AS estado
            FROM proveedores AS p
            JOIN estados AS e ON e.id = p.estado_id
            ORDER BY p.id
            """
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        connection.close()


def get_provider(provider_id):
    connection = get_connection()
    try:
        row = connection.execute(
            """
            SELECT p.id, p.nombre, p.servicio, p.sitio, e.nombre AS estado
            FROM proveedores AS p
            JOIN estados AS e ON e.id = p.estado_id
            WHERE p.id = ?
            """,
            (provider_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        connection.close()


def create_provider(provider):
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            INSERT INTO proveedores (nombre, servicio, sitio, estado_id)
            VALUES (?, ?, ?, ?)
            """,
            (
                provider["nombre"],
                provider["servicio"],
                provider["sitio"],
                _state_id(connection, "proveedor", provider["estado"]),
            ),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update_provider(provider_id, provider):
    connection = get_connection()
    try:
        cursor = connection.execute(
            """
            UPDATE proveedores
            SET nombre = ?, servicio = ?, sitio = ?, estado_id = ?
            WHERE id = ?
            """,
            (
                provider["nombre"],
                provider["servicio"],
                provider["sitio"],
                _state_id(connection, "proveedor", provider["estado"]),
                provider_id,
            ),
        )
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def delete_provider(provider_id):
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM proveedores WHERE id = ?", (provider_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()


def _invoice_client_id(connection, name):
    row = connection.execute("SELECT id FROM clientes WHERE nombre = ?", (name,)).fetchone()
    if row:
        return row[0]
    business_id = _catalog_id(connection, "tipos_negocio", "Cliente de factura")
    location_id = _location_id(connection, {"provincia": "Pichincha", "canton": "Quito"})
    cursor = connection.execute(
        """
        INSERT INTO clientes (nombre, celular, tipo_negocio_id, ubicacion_id)
        VALUES (?, ?, ?, ?)
        """,
        (name, "0999999999", business_id, location_id),
    )
    return cursor.lastrowid


def _invoice_service_id(connection, detail):
    name = detail.get("servicio") or detail.get("descripcion") or "Servicio personalizado"
    row = connection.execute("SELECT id FROM servicios WHERE nombre = ?", (name,)).fetchone()
    if row:
        return row[0], name
    active_id = _state_id(connection, "servicio", "Activo")
    cursor = connection.execute(
        """
        INSERT INTO servicios (nombre, descripcion, precio, imagen, estado_id)
        VALUES (?, ?, ?, ?, ?)
        """,
        (name, name, float(detail.get("precio", 0)), "", active_id),
    )
    return cursor.lastrowid, name


def _insert_invoice(connection, invoice):
    client_id = _invoice_client_id(connection, invoice["cliente"])
    state_id = _state_id(connection, "factura", invoice["estado"])
    cursor = connection.execute(
        """
        INSERT INTO facturas (tipo, numero, cliente_id, fecha, validez, estado_id, notas)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            "Factura",
            invoice["numero"],
            client_id,
            invoice["fecha"],
            invoice.get("validez"),
            state_id,
            invoice.get("notas"),
        ),
    )
    invoice_id = cursor.lastrowid
    for detail in invoice.get("servicios_detalle", []):
        service_id, description = _invoice_service_id(connection, detail)
        connection.execute(
            """
            INSERT INTO factura_detalle
                (factura_id, servicio_id, descripcion, precio_unitario, cantidad, ajuste)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                invoice_id,
                service_id,
                description,
                float(detail.get("precio", 0)),
                int(detail.get("cantidad", 1)),
                float(detail.get("ajuste", 0)),
            ),
        )
    anticipo = float(invoice.get("anticipo", 0) or 0)
    if anticipo > 0:
        connection.execute(
            """
            INSERT INTO pagos (factura_id, fecha, monto, metodo_pago, estado_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (invoice_id, invoice["fecha"], anticipo, "Abono", _state_id(connection, "pago", "Registrado")),
        )
    return invoice_id


def create_invoice(invoice):
    connection = get_connection()
    try:
        invoice_id = _insert_invoice(connection, invoice)
        connection.commit()
        return invoice_id
    finally:
        connection.close()


def _invoice_details(connection, invoice_id):
    rows = connection.execute(
        """
        SELECT descripcion AS servicio, precio_unitario AS precio, cantidad, ajuste,
               (precio_unitario + ajuste) * cantidad AS total
        FROM factura_detalle
        WHERE factura_id = ?
        ORDER BY id
        """,
        (invoice_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def list_invoices():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT f.id AS _db_id, f.tipo, f.numero, c.nombre AS cliente, f.fecha,
                   f.validez, f.notas, e.nombre AS estado,
                   r.subtotal, r.iva, r.monto, r.anticipo, r.saldo_pendiente
            FROM facturas AS f
            JOIN clientes AS c ON c.id = f.cliente_id
            JOIN estados AS e ON e.id = f.estado_id
            JOIN resumen_facturas AS r ON r.id = f.id
            ORDER BY f.id
            """
        ).fetchall()
        invoices = []
        for row in rows:
            invoice = dict(row)
            invoice["servicios_detalle"] = _invoice_details(connection, row["_db_id"])
            invoice["_persistida"] = True
            invoices.append(invoice)
        return invoices
    finally:
        connection.close()


def update_invoice(invoice_id, invoice):
    connection = get_connection()
    try:
        connection.execute("DELETE FROM factura_detalle WHERE factura_id = ?", (invoice_id,))
        connection.execute("DELETE FROM pagos WHERE factura_id = ?", (invoice_id,))
        connection.execute("DELETE FROM facturas WHERE id = ?", (invoice_id,))
        _insert_invoice(connection, invoice)
        connection.commit()
    finally:
        connection.close()


def delete_invoice(invoice_id):
    connection = get_connection()
    try:
        cursor = connection.execute("DELETE FROM facturas WHERE id = ?", (invoice_id,))
        connection.commit()
        return cursor.rowcount > 0
    finally:
        connection.close()
