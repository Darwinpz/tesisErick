from datetime import datetime
from bson.objectid import ObjectId

class Acta:

    def __init__(self, numero, inventario, entrega, recibe, veedor, estado, session ):
        self.numero = numero
        self.inventario = inventario
        self.entrega = entrega
        self.recibe = recibe
        self.veedor = veedor
        self.estado = estado
        self.resp_id = ObjectId(session["id"])
        self.resp_cedula = session["cedula"]
        self.resp_nombre = session["nombre"]

    def obtener_acta(self):
        return self.__dict__
    
    def crear_acta(self):
        self.fecha_creacion = datetime.now()
    
    def update_acta(self):
        self.fecha_modificacion = datetime.now()