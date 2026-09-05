from database import create_client, delete_client, get_client, list_clients, update_client


class Cliente:
    @staticmethod
    def listar():
        return list_clients()

    @staticmethod
    def obtener(cliente_id):
        return get_client(cliente_id)

    @staticmethod
    def crear(datos):
        return create_client(datos)

    @staticmethod
    def actualizar(cliente_id, datos):
        return update_client(cliente_id, datos)

    @staticmethod
    def eliminar(cliente_id):
        return delete_client(cliente_id)
