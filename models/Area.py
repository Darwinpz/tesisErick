from datetime import datetime

class Area:

    def __init__(self, abreviatura,nombre):
        self.abreviatura = abreviatura
        self.nombre = nombre

    def obtener_area(self):
        return self.__dict__
    
    def crear_area(self):
        self.fecha_creacion = datetime.now()
    
    def update_area(self):
        self.fecha_modificacion = datetime.now()