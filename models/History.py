from datetime import datetime
from bson.objectid import ObjectId

class History:

    def __init__(self, tipo,accion,mensaje, session):
        self.tipo  = tipo
        self.accion = accion
        self.mensaje = mensaje
        self.id_user = ObjectId(session["id"])
        self.ip = session["ip"]
        self.cedula = session["cedula"]
        self.nombre = session["nombre"]
        self.tipo_user = session["tipo"]
        self.rol = session["rol"]
        self.fecha_accion = datetime.now()
    
    def obtener_history(self):
        return self.__dict__
    