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


def initialize_database(seed_services=None):
    connection = get_connection()
    try:
        connection.execute("DROP TABLE IF EXISTS facturas_legacy")
        connection.execute("DROP TABLE IF EXISTS factura_detalle_legacy")
        connection.execute("DROP TABLE IF EXISTS proveedores_legacy")
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
            CREATE TABLE IF NOT EXISTS servicios_contratados (
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
                barrio TEXT NOT NULL,
                UNIQUE (provincia, canton, barrio)
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
                servicio_contratado_id INTEGER NOT NULL,
                ubicacion_id INTEGER NOT NULL,
                FOREIGN KEY (tipo_negocio_id) REFERENCES tipos_negocio(id),
                FOREIGN KEY (servicio_contratado_id) REFERENCES servicios_contratados(id),
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
        connection.execute("DROP TABLE IF EXISTS facturas_legacy")
        connection.execute("DROP TABLE IF EXISTS factura_detalle_legacy")
        connection.execute("DROP TABLE IF EXISTS proveedores_legacy")
        connection.execute("DROP TABLE IF EXISTS clientes_legacy")
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
        "SELECT id FROM ubicaciones WHERE provincia = ? AND canton = ? AND barrio = ?",
        (client["provincia"], client["canton"], client["barrio"]),
    ).fetchone()
    if row:
        return row[0]
    cursor = connection.execute(
        "INSERT INTO ubicaciones (provincia, canton, barrio) VALUES (?, ?, ?)",
        (client["provincia"], client["canton"], client["barrio"]),
    )
    return cursor.lastrowid


def list_clients():
    connection = get_connection()
    try:
        rows = connection.execute(
            """
            SELECT c.id, c.nombre, c.celular, tn.nombre AS negocio,
                   sc.nombre AS servicio, u.provincia, u.canton, u.barrio,
                   u.provincia || ', ' || u.canton || ', ' || u.barrio AS ciudad
            FROM clientes AS c
            JOIN tipos_negocio AS tn ON tn.id = c.tipo_negocio_id
            JOIN servicios_contratados AS sc ON sc.id = c.servicio_contratado_id
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
        servicio_id = _catalog_id(connection, "servicios_contratados", client["servicio"])
        ubicacion_id = _location_id(connection, client)
        cursor = connection.execute(
            """
            INSERT INTO clientes (nombre, celular, tipo_negocio_id, servicio_contratado_id, ubicacion_id)
            VALUES (?, ?, ?, ?, ?)
            """,
            (client["nombre"], client["celular"], negocio_id, servicio_id, ubicacion_id),
        )
        connection.commit()
        return cursor.lastrowid
    finally:
        connection.close()


def update_client(client_id, client):
    connection = get_connection()
    try:
        negocio_id = _catalog_id(connection, "tipos_negocio", client["negocio"])
        servicio_id = _catalog_id(connection, "servicios_contratados", client["servicio"])
        ubicacion_id = _location_id(connection, client)
        cursor = connection.execute(
            """
            UPDATE clientes
            SET nombre = ?, celular = ?, tipo_negocio_id = ?,
                servicio_contratado_id = ?, ubicacion_id = ?
            WHERE id = ?
            """,
            (client["nombre"], client["celular"], negocio_id, servicio_id, ubicacion_id, client_id),
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
