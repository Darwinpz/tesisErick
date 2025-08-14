from datetime import datetime

class Usuario:

    def __init__(self, cedula, usuario, clave, estado, rol):
        self.cedula = cedula
        self.usuario = usuario
        self.clave = clave
        self.estado = estado
        self.rol = rol
    
    def obtener_usuario(self):
        return self.__dict__
    
    def crear_usuario(self):
        self.fecha_creacion = datetime.now()
    
    def update_usuario(self):
        self.fecha_modificacion = datetime.now()
    