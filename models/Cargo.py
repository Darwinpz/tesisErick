from datetime import datetime

class Cargo:

    def __init__(self, nombre):
        self.nombre = nombre

    def obtener_cargo(self):
        return self.__dict__
    
    def crear_cargo(self):
        self.fecha_creacion = datetime.now()
    
    def update_cargo(self):
        self.fecha_modificacion = datetime.now()