from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Modalidad import Modalidad
from bson.objectid import ObjectId
import json

db = MongoDb().db()

def save_modalidades(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre =  val.val_vacio("m_nombre","",request).upper().strip()

                if nombre != "":

                    existe = db.modalidades.find_one({"nombre": nombre})

                    if existe:
                        return jsonify({"message": "Modalidad Existente"}), 404
                    else:
                        modalidad = Modalidad(nombre)
                        modalidad.crear_modalidad()
                        _id = db.modalidades.insert_one(
                            modalidad.obtener_modalidad()).inserted_id
                        hist.guardar_historial(
                            "CORRECTO", "CREAR", 'MODALIDAD "'+nombre+'" CON ID "'+str(_id)+'" CREADA CORRECTAMENTE')
                        return jsonify({"message": "Modalidad Creada Correctamente"}), 200
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR LA MODALIDAD "'+nombre+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear la modalidad"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_modalidades(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                modalidades = db.modalidades.find()
                data = {"data": list(modalidades)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODAS LAS MODALIDADES - "'+str(e)+'"')
            return jsonify({"message": "Error al visualizar todas las modalidades"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_modalidades(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre =  val.val_vacio("m_nombre","",request).upper().strip()
                id =  val.val_vacio("m_codigo","",request).strip()

                existe = db.modalidades.find_one({"_id": ObjectId(id)})

                if existe:

                    existe_nombre = db.modalidades.find_one({"nombre": nombre})

                    if existe_nombre:
                        if existe_nombre["_id"] != existe["_id"]:
                            return jsonify({"message": "No se puede actualizar, Modalidad Existente"}), 404

                    modalidad = Modalidad(nombre)
                    modalidad.update_modalidad()
                    db.modalidades.update_one({"_id": ObjectId(id)}, {
                        "$set": modalidad.obtener_modalidad()})
                    hist.guardar_historial(
                        "CORRECTO", "ACTUALIZAR", 'MODALIDAD "' + nombre+'" CON ID "'+str(id)+'" ACTUALIZADA CORRECTAMENTE')
                    return jsonify({"message": "Modalidad Actualizada Correctamente"}), 200
                else:
                    return jsonify({"message": "Modalidad No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR LA MODALIDAD "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar la modalidad"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_modalidades(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id","",request).strip()
                nombre = val.val_vacio("nombre","",request).upper().strip()
                existe = db.modalidades.find_one({"_id": ObjectId(id)})

                if existe:

                    dependencia = db.servidores.find_one({"modalidad": ObjectId(id)})

                    if dependencia:
                        return jsonify({"message": "Existen Servidores asociados a la Modalidad a Eliminar"}), 404
                    else:
                        db.modalidades.delete_one({"_id": ObjectId(id)})
                        hist.guardar_historial(
                            "CORRECTO", "ELIMINAR", 'MODALIDAD "'+nombre+'" CON ID "'+str(id)+'" ELIMINADA CORRECTAMENTE')
                        return jsonify({"message": "Modalidad Eliminada Correctamente"}), 200
                else:
                    return jsonify({"message": "Modalidad NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR LA MODALIDAD "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar la modalidad"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500

