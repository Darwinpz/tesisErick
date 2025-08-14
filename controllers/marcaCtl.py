from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Marca import Marca
from bson.objectid import ObjectId
import json

db = MongoDb().db()

def save_marcas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("mar_nombre","",request).upper().strip()

                if nombre != "":

                    dir_mar = "marcas_"+session["tipo"]
                    existe = db[dir_mar].find_one({"nombre": nombre})

                    if existe:
                        return jsonify({"message": "Marca Existente"}), 404
                    else:
                        marca = Marca(nombre)
                        marca.crear_marca()
                        _id = db[dir_mar].insert_one(
                            marca.obtener_marca()).inserted_id
                        hist.guardar_historial(
                            "CORRECTO", "CREAR", 'MARCA "'+nombre+'" CON ID "'+str(_id)+'" CREADA CORRECTAMENTE')
                        return jsonify({"message": "Marca Creada Correctamente"}), 200
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR LA MARCA "'+nombre+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear la marca"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_marcas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                dir_mar = "marcas_"+session["tipo"]
                marcas = db[dir_mar].find()
                data = {"data": list(marcas)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODAS LAS MARCAS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todas las marcas"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_marcas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("mar_nombre","",request).upper().strip()
                id = val.val_vacio("mar_codigo","",request).strip()

                dir_mar = "marcas_"+session["tipo"]
                existe = db[dir_mar].find_one({"_id": ObjectId(id)})

                if existe:

                    existe_nombre = db[dir_mar].find_one({"nombre": nombre})

                    if existe_nombre:
                        if existe_nombre["_id"] != existe["_id"]:
                            return jsonify({"message": "No se puede actualizar, Marca Existente"}), 404

                    marca = Marca(nombre)
                    marca.update_marca()
                    db[dir_mar].update_one({"_id": ObjectId(id)}, {
                        "$set": marca.obtener_marca()})
                    hist.guardar_historial("CORRECTO", "ACTUALIZAR", 'MARCA "' +
                                      nombre+'" CON ID "'+str(id)+'" ACTUALIZADO CORRECTAMENTE')
                    return jsonify({"message": "Marca Actualizada Correctamente"}), 200
                else:
                    return jsonify({"message": "Marca No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR LA MARCA "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar la marca"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_marcas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id","",request).strip()
                nombre = val.val_vacio("nombre","",request).upper().strip()

                dir_mar = "marcas_"+session["tipo"]
                existe = db[dir_mar].find_one({"_id": ObjectId(id)})

                if existe:
                    
                    dir_mod = "modelos_"+session["tipo"]
                    dependencia = db[dir_mod].find_one({"marca": ObjectId(id)})

                    if dependencia:
                        return jsonify({"message": "Existen Modelos asociados a la Marca a Eliminar"}), 404
                    else:
                        db[dir_mar].delete_one({"_id": ObjectId(id)})
                        hist.guardar_historial(
                            "CORRECTO", "ELIMINAR", 'MARCA "'+nombre+'" CON ID "'+str(id)+'" ELIMINADO CORRECTAMENTE')
                        return jsonify({"message": "Marca Eliminada Correctamente"}), 200
                else:
                    return jsonify({"message": "Marca NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR LA MARCA "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar la marca"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500

