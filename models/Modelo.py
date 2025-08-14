from datetime import datetime

class Modelo:

    def __init__(self, nombre, marca):
        self.nombre = nombre
        self.marca = marca

    def obtener_modelo(self):
        return self.__dict__
    
    def crear_modelo(self):
        self.fecha_creacion = datetime.now()
    
    def update_modelo(self):
        self.fecha_modificacion = datetime.now()