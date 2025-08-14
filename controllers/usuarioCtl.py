from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.User import Usuario
from bson.objectid import ObjectId
import controllers.encryptCtl as ctl_encrypt
import json

db = MongoDb().db()

def save_usuarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                if val.validar_admin(session):

                    cedula = val.val_vacio("u_servidor","",request).upper().strip()
                    nom_user = val.val_vacio("u_nombre","",request).lower().strip()
                    estado = val.val_vacio("u_estado","",request).upper().strip()
                    rol = val.val_vacio("u_rol","",request).strip()
                    clave = val.val_vacio("u_clave","",request)
                    rep_clave = val.val_vacio("u_rep_clave","",request)

                    if cedula != "" and nom_user != "" and estado != "" and rol != "" and clave != "" and rep_clave != "":

                        if clave == rep_clave:

                            existe = db.usuarios.find_one(
                                {"$or": [{'cedula': cedula}, {'usuario': nom_user}]})

                            if existe:
                                return jsonify({"message": "Usuario Existente"}), 404
                            else:
                                clave = ctl_encrypt.encrypt(clave)
                                usuario = Usuario(cedula, nom_user,
                                                  clave, estado, rol)
                                usuario.crear_usuario()
                                _id = db.usuarios.insert_one(
                                    usuario.obtener_usuario()).inserted_id
                                hist.guardar_historial(
                                    "CORRECTO", "CREAR", 'USUARIO "'+nom_user+'" CON ID "'+str(_id)+'" CREADO CORRECTAMENTE')
                                return jsonify({"message": "Usuario Creado Correctamente"}), 200
                        else:
                            return jsonify({"message": "Las Claves no Coinciden"}), 404
                    else:
                        return jsonify({"message": "Información Incompleta"}), 404
                else:
                    return jsonify({"message": "Debes ser Administrador"}), 401
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL USUARIO "'+nom_user+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear el Usuario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_usuarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):
                
                if val.validar_admin(session):

                    usuarios = db.usuarios.aggregate([
                        {"$match": {'cedula': {
                            "$nin":  [session["cedula"]]}}},
                        {"$lookup": {"from": "servidores", "localField": "cedula",
                                     "foreignField": "cedula", "as": "servidor"}},
                        {"$unwind": "$servidor"},
                        {"$project": {"servidor._id": 0}},
                        {"$lookup": {"from": "areas", "localField": "servidor.area",
                             "foreignField": "_id", "as": "area"}},
                        {"$unwind": "$area"},
                    ])

                    datos = list(usuarios)

                    for us in datos:
                        us["clave"] = ctl_encrypt.decrypt(us["clave"])

                    data = {"data": datos}

                    return json.dumps(data, default=str), 200
                else:
                    return jsonify({"message": "Debes ser Administrador"}), 401
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODOS LOS USUARIOS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todos los usuarios"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_usuarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                if val.validar_admin(session):

                    cedula = val.val_vacio("u_cedula","",request).upper().strip()
                    nom_user = val.val_vacio("u_nombre","",request).lower().strip()
                    estado = val.val_vacio("u_estado","",request).upper().strip()
                    rol = val.val_vacio("u_rol","",request).strip()
                    clave = val.val_vacio("u_clave","",request)
                    rep_clave = val.val_vacio("u_rep_clave","",request)

                    if cedula != "" and nom_user != "" and estado != "" and rol != "" and clave != "" and rep_clave != "":

                        if clave == rep_clave:

                            existe = db.usuarios.find_one({'cedula': cedula})

                            if existe:

                                existe_usuario = db.usuarios.find_one(
                                    {'usuario': nom_user})

                                if existe_usuario:
                                    if existe_usuario["_id"] != existe["_id"]:
                                        return jsonify({"message": "Nombre de Usuario en Uso"}), 404

                                clave = ctl_encrypt.encrypt(clave)
                                usuario = Usuario(
                                    cedula, nom_user, clave, estado, rol)
                                usuario.update_usuario()
                                db.usuarios.update_one({"_id": ObjectId(existe["_id"])}, {
                                    "$set": usuario.obtener_usuario()})
                                hist.guardar_historial(
                                    "CORRECTO", "ACTUALIZAR", 'USUARIO "'+nom_user+'" ACTUALIZADO CORRECTAMENTE')
                                return jsonify({"message": "Usuario Actualizado Correctamente"}), 200

                            else:
                                return jsonify({"message": "Usuario No Existente"}), 404
                        else:
                            return jsonify({"message": "Las Claves no Coinciden"}), 404
                    else:
                        return jsonify({"message": "Información Incompleta"}), 404
                else:
                    return jsonify({"message": "Debes ser Administrador"}), 401
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR EL USUARIO "'+cedula+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar el Usuario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_usuarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                if val.validar_admin(session):

                    cedula = val.val_vacio("cedula","",request).upper().strip()
                    existe = db.usuarios.find_one({"cedula": cedula})

                    if existe:

                        dir_inv = "inventario_"+session["tipo"]
                        dependencia = db[dir_inv].find_one({"custodio": cedula})

                        if dependencia:
                            return jsonify({"message": "Existe Inventario asociado en el Usuario a Eliminar"}), 404
                        else:
                            db.usuarios.delete_one({"cedula": cedula})
                            hist.guardar_historial(
                                "CORRECTO", "ELIMINAR", 'USUARIO "'+cedula+'" ELIMINADO CORRECTAMENTE')
                            return jsonify({"message": "Usuario Eliminado Correctamente"}), 200
                    else:
                        return jsonify({"message": "Usuario NO Existente"}), 404
                else:
                    return jsonify({"message": "Debes ser Administrador"}), 401
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL USUARIO "'+cedula+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el Usuario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
