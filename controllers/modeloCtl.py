from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Modelo import Modelo
from bson.objectid import ObjectId
import json

db = MongoDb().db()

def save_modelos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("mod_nombre","",request).upper().strip()
                marca = val.val_vacio("mod_marca","",request).upper().strip()

                if nombre != "" and marca != "":

                    dir_mod = "modelos_"+session["tipo"]
                    existe = db[dir_mod].find_one({"$and": [{'nombre': nombre}, {'marca': ObjectId(marca)}]})

                    if existe:
                        return jsonify({"message": "Modelo Existente"}), 404
                    else:
                        modelo = Modelo(nombre,ObjectId(marca))
                        modelo.crear_modelo()
                        _id = db[dir_mod].insert_one(
                            modelo.obtener_modelo()).inserted_id
                        hist.guardar_historial(
                            "CORRECTO", "CREAR", 'MODELO "'+nombre+'" CON ID "'+str(_id)+'" CREADO CORRECTAMENTE')
                        return jsonify({"message": "Modelo Creado Correctamente"}), 200
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL MODELO "'+nombre+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear el modelo"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_modelos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                marca = val.val_vacio("marca","",request).strip()

                dir_mod = "modelos_"+session["tipo"]
                dir_marc = "marcas_"+session["tipo"]

                consulta = [{"$lookup": {"from": dir_marc, "localField": "marca",
                                         "foreignField": "_id", "as": "marca"}},
                                         {"$unwind": "$marca"}]
                
                if marca != "":
                    consulta.insert(2,{"$match": {'marca._id': ObjectId(marca)}})

                modelos = db[dir_mod].aggregate(consulta)
                data = {"data": list(modelos)}
                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODOS LOS MODELOS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todos los modelos"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_modelos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("mod_nombre","",request).upper().strip()
                marca = val.val_vacio("mod_marca","",request).upper().strip()
                id = val.val_vacio("mod_codigo","",request).strip()

                dir_mod = "modelos_"+session["tipo"]
                existe = db[dir_mod].find_one({"_id": ObjectId(id)})

                if existe:

                    existe_nombre = db[dir_mod].find_one({"$and": [{'nombre': nombre}, {'marca': ObjectId(marca)}]})

                    if existe_nombre:
                        if existe_nombre["_id"] != existe["_id"]:
                            return jsonify({"message": "No se puede actualizar, Modelo Existente"}), 404

                    modelo = Modelo(nombre, ObjectId(marca))
                    modelo.update_modelo()
                    db[dir_mod].update_one({"_id": ObjectId(id)}, {
                        "$set": modelo.obtener_modelo()})
                    hist.guardar_historial("CORRECTO", "ACTUALIZAR", 'MODELO "' +
                                      nombre+'" CON ID "'+str(id)+'" ACTUALIZADO CORRECTAMENTE')
                    return jsonify({"message": "Modelo Actualizado Correctamente"}), 200
                else:
                    return jsonify({"message": "Modelo No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR EL MODELO "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar el modelo"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_modelos(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id","",request).strip()
                nombre = val.val_vacio("nombre","",request).upper().strip()

                dir_mod = "modelos_"+session["tipo"]
                existe = db[dir_mod].find_one({"_id": ObjectId(id)})

                if existe:
                    
                    dir_inv = "inventario_"+session["tipo"]
                    dependencia = db[dir_inv].find_one({"modelo": ObjectId(id)})

                    if dependencia:
                        return jsonify({"message": "Existen Modelos asociados al Inventario a Eliminar"}), 404
                    else:
                        db[dir_mod].delete_one({"_id": ObjectId(id)})
                        hist.guardar_historial(
                            "CORRECTO", "ELIMINAR", 'MODELO "'+nombre+'" CON ID "'+str(id)+'" ELIMINADO CORRECTAMENTE')
                        return jsonify({"message": "Modelo Eliminado Correctamente"}), 200
                else:
                    return jsonify({"message": "Modelo NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL MODELO "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el modelo"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500

