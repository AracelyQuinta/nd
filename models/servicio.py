from database import create_service, delete_service, get_service, list_services, update_service


class Servicio:
    @staticmethod
    def listar():
        return list_services()

    @staticmethod
    def obtener(servicio_id):
        return get_service(servicio_id)

    @staticmethod
    def crear(datos):
        return create_service(datos)

    @staticmethod
    def actualizar(servicio_id, datos):
        return update_service(servicio_id, datos)

    @staticmethod
    def eliminar(servicio_id):
        return delete_service(servicio_id)
