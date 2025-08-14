from datetime import datetime

class Servidor:
    
    def __init__(self, cedula, nombres, correo, area, jefe, modalidad, estado, cargo, url_foto):
        self.cedula = cedula
        self.nombres = nombres
        self.correo = correo
        self.area = area
        self.jefe = jefe
        self.modalidad = modalidad
        self.estado = estado
        self.cargo = cargo
        self.url_foto = url_foto

    def obtener_servidor(self):
        return self.__dict__
    
    def crear_servidor(self):
        self.fecha_creacion = datetime.now()
    
    def update_servidor(self):
        self.fecha_modificacion = datetime.now()
    