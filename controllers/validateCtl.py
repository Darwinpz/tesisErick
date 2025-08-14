import os

class Validaciones:

    def validar_session(session):
        if 'id' in session:
            return True
        
    def validar_admin(session):
        if session["rol"] == "Administrador" or session["rol"] == "Super-Admin":
            return True
        
    def val_vacio(nombre,defecto,request):
        return request.form[nombre] if (nombre in request.form) else defecto
    
    def crear_directorio(path):
        if not os.path.isdir(path):
            os.makedirs(path)

    def validar_cedula_ecuatoriana(cedula):
        # Limpiar la cédula (eliminar caracteres no numéricos)
        cedula_limpia = ''.join(filter(str.isdigit, cedula))
        
        # Verificar longitud (debe tener 10 dígitos)
        if len(cedula_limpia) != 10:
            return False

        # Verificar que todos los caracteres sean dígitos
        if not cedula_limpia.isdigit():
            return False
        
        # Verificar provincia (primeros dos dígitos entre 01 y 24)
        provincia = int(cedula_limpia[:2])
        if provincia < 1 or provincia > 24:
            return False
        
        # Verificar tercer dígito (debe ser menor a 6)
        tercer_digito = int(cedula_limpia[2])
        if tercer_digito > 5:
            return False
        
        # Algoritmo de validación (módulo 10)
        coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2]
        verificador = int(cedula_limpia[9])
        suma = 0
        
        for i in range(9):
            valor = int(cedula_limpia[i]) * coeficientes[i]
            if valor >= 10:
                valor -= 9
            suma += valor
        
        resultado = 0 if suma % 10 == 0 else 10 - (suma % 10)
        
        # El dígito verificador debe coincidir con el resultado
        return resultado == verificador

    def del_archivo(path):
        if os.path.exists(path):
            os.remove(path)