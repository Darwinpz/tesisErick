from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Servidor import Servidor
from bson.objectid import ObjectId
import uuid
import json
import os

db = MongoDb().db()

def save_servidores(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                foto = request.files['s_foto']
                cedula = val.val_vacio("s_cedula", "", request).upper().strip()
                ciudadano = val.val_vacio(
                    "s_ciudadano", "", request).upper().strip()
                correo = val.val_vacio("s_correo", "", request).lower().strip()
                area = val.val_vacio("s_area", "", request).strip()
                jefe = val.val_vacio("s_jefe", "", request).strip()
                cargo = val.val_vacio("s_cargo", "", request).strip()
                modalidad = val.val_vacio("s_modalidad", "", request).strip()
                estado = val.val_vacio("s_estado", "", request).upper().strip()

                path = ("public/servidores")

                val.crear_directorio(path)

                url_foto = ""

                if cedula != "" and ciudadano != "" and correo != "" and area != "" and jefe != "" and cargo != "" and modalidad != "" and estado != "":

                    if val.validar_cedula_ecuatoriana(cedula):

                        existe = db.servidores.find_one(
                            {"$or": [{'cedula': cedula}, {'correo': correo}]})

                        if existe:
                            return jsonify({"message": "Cedula y/o Correo de Servidor Existente"}), 404
                        else:

                            existeJefe = db.servidores.find_one({"$and": [{'area': ObjectId(area)}, {'jefe': 'SI'}]})

                            if existeJefe and jefe == "SI":
                                return jsonify({"message": "El área ya tiene un Jefe asignado"}), 404 

                            if foto.filename != '':
                                id = str(uuid.uuid1())
                                file_ext = os.path.splitext(foto.filename)[1]
                                url_foto = id+file_ext
                                foto.save(os.path.join(path, url_foto))

                            servidor = Servidor(cedula, ciudadano, correo, ObjectId(area), jefe, ObjectId(
                                modalidad), estado, ObjectId(cargo), url_foto)
                            servidor.crear_servidor()
                            _id = db.servidores.insert_one(
                                servidor.obtener_servidor()).inserted_id
                            hist.guardar_historial(
                                "CORRECTO", "CREAR", 'SERVIDOR "'+cedula+'" CON ID "'+str(_id)+'" CREADO CORRECTAMENTE')
                            return jsonify({"message": "Servidor Creado Correctamente"}), 200
                    else:
                        return jsonify({"message": "Cedula no válida"}), 404
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL SERVIDOR "'+cedula+'" - "'+str(e)+'"')
            val.del_archivo(os.path.join(path, url_foto))
            return jsonify({"message": "Error al Crear el servidor"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_servidores(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                validar = val.val_vacio("s_validar", "", request).strip()

                servidores = []

                if validar == "":

                    servidores = db.servidores.aggregate([

                        {"$match": {'cedula': {
                            "$nin":  [session["cedula"]]}}},
                        {"$lookup": {"from": "cargos", "localField": "cargo",
                                     "foreignField": "_id", "as": "cargo"}},
                        {"$unwind": "$cargo"},
                        {"$lookup": {"from": "areas", "localField": "area",
                                     "foreignField": "_id", "as": "area"}},
                        {"$unwind": "$area"},
                        {"$lookup": {"from": "modalidades", "localField": "modalidad",
                                     "foreignField": "_id", "as": "modalidad"}},
                        {"$unwind": "$modalidad"},
                        # {"$project": {"area._id": 0, "cargo._id": 0, "modalidad._id": 0}}
                    ])
                elif validar == "true":

                    datos = list(db.servidores.find(
                        {}, {"_id": 1, "cedula": 1, "nombres": 1}))

                    for s in datos:
                        if db.usuarios.find_one({"cedula": s["cedula"]}) == None:
                            servidores.append(s)
                elif validar == "false":
                    servidores = db.servidores.find()
                else:
                    servidores = db.servidores.aggregate([
                        {"$lookup": {"from": "areas", "localField": "area",
                                     "foreignField": "_id", "as": "area"}},
                        {"$unwind": "$area"},
                        {"$match": {'area.abreviatura': validar}},
                    ])

                data = {"data": list(servidores)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODOS LOS SERVIDORES - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todos los servidores"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_servidores(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                foto = request.files['s_foto']
                cedula = val.val_vacio("s_cedula", "", request).upper().strip()
                ciudadano = val.val_vacio(
                    "s_ciudadano", "", request).upper().strip()
                correo = val.val_vacio("s_correo", "", request).lower().strip()
                area = val.val_vacio("s_area", "", request).strip()
                jefe = val.val_vacio("s_jefe", "", request).strip()
                cargo = val.val_vacio("s_cargo", "", request).strip()
                modalidad = val.val_vacio("s_modalidad", "", request).strip()
                estado = val.val_vacio("s_estado", "", request).upper().strip()

                if cedula != "" and ciudadano != "" and correo != "" and area != "" and jefe != "" and cargo != "" and modalidad != "" and estado != "":

                    existe = db.servidores.find_one(
                        {"$or": [{'cedula': cedula}, {'correo': correo}]})

                    if existe:

                        existeJefe = db.servidores.find_one({"$and": [{'area': ObjectId(area)}, {'jefe': 'SI'}]})

                        if existeJefe and jefe == "SI" and existeJefe["cedula"] != cedula:
                            return jsonify({"message": "El área ya tiene un Jefe asignado"}), 404

                        path = ("public/servidores")

                        val.crear_directorio(path)

                        url_foto = existe["url_foto"]

                        if foto.filename != '':

                            if existe["url_foto"] != "":
                                path_temp = (
                                    "public/servidores/"+existe["url_foto"])
                                val.del_archivo(path_temp)

                            id = str(uuid.uuid1())
                            file_ext = os.path.splitext(foto.filename)[1]
                            url_foto = id+file_ext
                            foto.save(os.path.join(path, url_foto))

                        servidor = Servidor(cedula, ciudadano, correo, ObjectId(
                            area), jefe, ObjectId(modalidad), estado, ObjectId(cargo), url_foto)
                        servidor.update_servidor()
                        db.servidores.update_one({"_id": ObjectId(existe["_id"])}, {
                            "$set": servidor.obtener_servidor()})
                        hist.guardar_historial(
                            "CORRECTO", "ACTUALIZAR", 'SERVIDOR "'+cedula+'" CON ID "'+str(existe["_id"])+'" ACTUALIZADO CORRECTAMENTE')
                        return jsonify({"message": "Servidor Actualizado Correctamente"}), 200
                    else:
                        return jsonify({"message": "Servidor No Existente"}), 404
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR EL SERVIDOR "'+cedula+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar el servidor"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_servidores(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                cedula = val.val_vacio("cedula", "", request).upper().strip()
                existe = db.servidores.find_one({"cedula": cedula})

                if existe:

                    ver_usuario = db.usuarios.find_one({"cedula": cedula})
                    dir_inv = "inventario_"+session["tipo"]
                            
                    if ver_usuario:
                        return jsonify({"message": "Debes eliminar el USUARIO asignado"}), 404

                    inventario = db[dir_inv].find_one({"custodio":cedula})

                    if inventario:
                        return jsonify({"message": "Existe Inventario asociado al Servidor a Eliminar"}), 404
                        
                    certificado = db.certificados.find_one({"secretario":cedula})

                    if certificado:
                        return jsonify({"message": "Existen Certificados asociado al Servidor a Eliminar"}), 404
                            
                    if existe["url_foto"] != "":
                        path = ("public/servidores/"+existe["url_foto"])
                        val.del_archivo(path)

                    db.servidores.delete_one({"cedula": cedula})
                    hist.guardar_historial("CORRECTO", "ELIMINAR", 'SERVIDOR "'+cedula+'" ELIMINADO CORRECTAMENTE')
                    return jsonify({"message": "Servidor Eliminado Correctamente"}), 200 
                            
                else:
                    return jsonify({"message": "Servidor NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL SERVIDOR "'+cedula+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el servidor"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
