from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Cargo import Cargo
from bson.objectid import ObjectId
import json

db = MongoDb().db()

def save_cargos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("c_nombre","",request).upper().strip()

                if nombre != "":

                    existe = db.cargos.find_one({"nombre": nombre})

                    if existe:
                        return jsonify({"message": "Cargo Existente"}), 404
                    else:
                        cargo = Cargo(nombre)
                        cargo.crear_cargo()
                        _id = db.cargos.insert_one(
                            cargo.obtener_cargo()).inserted_id
                        hist.guardar_historial(
                            "CORRECTO", "CREAR", 'CARGO "'+nombre+'" CON ID "'+str(_id)+'" CREADO CORRECTAMENTE')
                        return jsonify({"message": "Cargo Creado Correctamente"}), 200
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL CARGO "'+nombre+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear el cargo"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_cargos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                cargos = db.cargos.find()
                data = {"data": list(cargos)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODOS LOS CARGOS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todos los cargos"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_cargos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("c_nombre","",request).upper().strip()
                id = val.val_vacio("c_codigo","",request).strip()

                existe = db.cargos.find_one({"_id": ObjectId(id)})

                if existe:

                    existe_nombre = db.cargos.find_one({"nombre": nombre})

                    if existe_nombre:
                        if existe_nombre["_id"] != existe["_id"]:
                            return jsonify({"message": "No se puede actualizar, Cargo Existente"}), 404

                    cargo = Cargo(nombre)
                    cargo.update_cargo()
                    db.cargos.update_one({"_id": ObjectId(id)}, {
                        "$set": cargo.obtener_cargo()})
                    hist.guardar_historial("CORRECTO", "ACTUALIZAR", 'CARGO "' +
                                      nombre+'" CON ID "'+str(id)+'" ACTUALIZADO CORRECTAMENTE')
                    return jsonify({"message": "Cargo Actualizado Correctamente"}), 200
                else:
                    return jsonify({"message": "Cargo No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR EL CARGO "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar el cargo"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_cargos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id","",request).strip()
                nombre = val.val_vacio("nombre","",request).upper().strip()
                existe = db.cargos.find_one({"_id": ObjectId(id)})

                if existe:

                    dependencia = db.servidores.find_one({"cargo": ObjectId(id)})

                    if dependencia:
                        return jsonify({"message": "Existen Servidores asociados al Cargo a Eliminar"}), 404
                    else:
                        db.cargos.delete_one({"_id": ObjectId(id)})
                        hist.guardar_historial(
                            "CORRECTO", "ELIMINAR", 'CARGO "'+nombre+'" CON ID "'+str(id)+'" ELIMINADO CORRECTAMENTE')
                        return jsonify({"message": "Cargo Eliminado Correctamente"}), 200
                else:
                    return jsonify({"message": "Cargo NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL CARGO "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el cargo"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500

