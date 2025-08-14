from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Area import Area
from bson.objectid import ObjectId
import json

db = MongoDb().db()

def save_areas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                abreviatura = val.val_vacio(
                    "a_abreviatura", "", request).upper().strip()
                nombre = val.val_vacio("a_nombre", "", request).upper().strip()

                if abreviatura != "" and nombre != "":

                    existe = db.areas.find_one(
                        {"$or": [{'abreviatura': abreviatura}, {'nombre': nombre}]})

                    if existe:
                        return jsonify({"message": "Área Existente"}), 404
                    else:
                        area = Area(abreviatura, nombre)
                        area.crear_area()
                        _id = db.areas.insert_one(
                            area.obtener_area()).inserted_id
                        hist.guardar_historial(
                            "CORRECTO", "CREAR", 'ÁREA "'+abreviatura+'" CON ID "'+str(_id)+'" CREADA CORRECTAMENTE')
                        return jsonify({"message": "Área Creada Correctamente"}), 200
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL ÁREA "'+abreviatura+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear el area"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_areas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                areas = db.areas.find()
                data = {"data": list(areas)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODAS LAS ÁREAS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todas las áreas"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_areas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                abreviatura = val.val_vacio(
                    "a_abreviatura", "", request).upper().strip()
                nombre = val.val_vacio("a_nombre", "", request).upper().strip()
                id = val.val_vacio("a_codigo", "", request).strip()

                existe = db.areas.find_one({"_id": ObjectId(id)})

                if existe:

                    existe_abreviatura = db.areas.find_one(
                        {"abreviatura": abreviatura})

                    if existe_abreviatura:
                        if existe_abreviatura["_id"] != existe["_id"]:
                            return jsonify({"message": "No se puede actualizar, Area Existente"}), 404

                    area = Area(abreviatura, nombre)
                    area.update_area()
                    db.areas.update_one({"_id": ObjectId(id)}, {
                        "$set": area.obtener_area()})
                    hist.guardar_historial(
                        "CORRECTO", "ACTUALIZAR", 'ÁREA "'+abreviatura + '" CON ID "'+str(id)+'" ACTUALIZADA CORRECTAMENTE')
                    return jsonify({"message": "Area Actualizada Correctamente"}), 200
                else:
                    return jsonify({"message": "Area No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR EL ÁREA "'+abreviatura+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar el area"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_areas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id", "", request).strip()
                abreviatura = val.val_vacio(
                    "abreviatura", "", request).upper().strip()
                existe = db.areas.find_one({"_id": ObjectId(id)})

                if existe:

                    dependencia = db.servidores.find_one({"area": ObjectId(id)})

                    if dependencia:
                        return jsonify({"message": "Existen Servidores asociados en el Área a Eliminar"}), 404
                    else:
                        db.areas.delete_one({"_id": ObjectId(id)})
                        hist.guardar_historial(
                            "CORRECTO", "ELIMINAR", 'ÁREA "'+abreviatura+'" CON ID "'+str(id)+'" ELIMINADA CORRECTAMENTE')
                        return jsonify({"message": "Área Eliminada Correctamente"}), 200
                else:
                    return jsonify({"message": "Área NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL ÁREA "'+abreviatura+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el area"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
