from datetime import datetime

class Inventario:

    def __init__(self, nombre, estado, descripcion, precio, categoria,cta_contable, codigo, serie, marca, modelo, ip, mac, adquisicion, custodio, url_foto, items):
        self.nombre = nombre
        self.estado = estado
        self.descripcion = descripcion
        self.precio = precio
        self.categoria = categoria
        self.cta_contable = cta_contable
        self.codigo = codigo
        self.serie = serie
        self.marca = marca
        self.modelo = modelo
        self.ip = ip
        self.mac = mac
        self.adquisicion = adquisicion
        self.custodio = custodio
        self.url_foto = url_foto
        self.items = items

    def obtener_inventario(self):
        return self.__dict__

    def crear_inventario(self):
        self.fecha_creacion = datetime.now()
    
    def update_inventario(self):
        self.fecha_modificacion = datetime.now()