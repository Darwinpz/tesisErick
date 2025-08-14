from datetime import datetime

class Marca:

    def __init__(self, nombre):
        self.nombre = nombre

    def obtener_marca(self):
        return self.__dict__
    
    def crear_marca(self):
        self.fecha_creacion = datetime.now()
    
    def update_marca(self):
        self.fecha_modificacion = datetime.now()