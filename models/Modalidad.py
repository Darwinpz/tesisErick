from datetime import datetime

class Modalidad:

    def __init__(self, nombre):
        self.nombre = nombre

    def obtener_modalidad(self):
        return self.__dict__
    
    def crear_modalidad(self):
        self.fecha_creacion = datetime.now()
    
    def update_modalidad(self):
        self.fecha_modificacion = datetime.now()