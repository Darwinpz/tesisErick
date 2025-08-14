from datetime import datetime

class Categoria:

    def __init__(self, nombre,items):
        self.nombre = nombre
        self.items = items

    def obtener_categoria(self):
        return self.__dict__
    
    def crear_categoria(self):
        self.fecha_creacion = datetime.now()
    
    def update_categoria(self):
        self.fecha_modificacion = datetime.now()