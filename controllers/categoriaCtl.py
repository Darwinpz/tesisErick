from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Categoria import Categoria
from bson.objectid import ObjectId
import json

db = MongoDb().db()

def save_categorias(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("cat_nombre","",request).upper().strip()
                codigo = val.val_vacio("cat_cod","off",request).strip()
                serie = val.val_vacio("cat_serie","off",request).strip()
                mod_marc = val.val_vacio("cat_mod_marc","off",request).strip()
                ip_mac = val.val_vacio("cat_ip_mac","off",request).strip()

                if nombre != "":
                
                    dir_cat = "categorias_"+session["tipo"]
                    existe = db[dir_cat].find_one({"nombre": nombre})

                    if existe:
                        return jsonify({"message": "Categoria Existente"}), 404
                    else:

                        items = {"codigo":codigo,"serie": serie,
                                 "mod_marc": mod_marc, "ip_mac": ip_mac}
                        categoria = Categoria(nombre, items)
                        categoria.crear_categoria()
                        _id = db[dir_cat].insert_one(
                            categoria.obtener_categoria()).inserted_id
                        hist.guardar_historial("CORRECTO", "CREAR", 'CATEGORIA "' +
                                          nombre+'" CON ID "'+str(_id)+'" CREADA CORRECTAMENTE')
                        return jsonify({"message": "Categoria Creada Correctamente"}), 200
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR LA CATEGORIA "'+nombre+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear la categoria"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_categorias(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                dir_cat = "categorias_"+session["tipo"]
                categorias = db[dir_cat].find()
                data = {"data": list(categorias)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODAS LAS CATEGORIAS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todas las categorias"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_categorias(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                nombre = val.val_vacio("cat_nombre","",request).upper().strip()
                id = val.val_vacio("cat_codigo","",request).strip()
                codigo = val.val_vacio("cat_cod","off",request).strip()
                serie = val.val_vacio("cat_serie","off",request).strip()
                mod_marc = val.val_vacio("cat_mod_marc","off",request).strip()
                ip_mac = val.val_vacio("cat_ip_mac","off",request).strip()
                
                dir_cat = "categorias_"+session["tipo"]

                existe = db[dir_cat].find_one({"_id": ObjectId(id)})

                if existe:

                    existe_nombre = db[dir_cat].find_one({"nombre": nombre})

                    if existe_nombre:
                        if existe_nombre["_id"] != existe["_id"]:
                            return jsonify({"message": "No se puede actualizar, Categoria Existente"}), 404

                    items = {"codigo":codigo,"serie": serie,
                             "mod_marc": mod_marc, "ip_mac": ip_mac}
                    categoria = Categoria(nombre, items)
                    categoria.update_categoria()
                    db[dir_cat].update_one({"_id": ObjectId(id)}, {
                        "$set": categoria.obtener_categoria()})
                    hist.guardar_historial("CORRECTO", "ACTUALIZAR", 'CATEGORIA "' +
                                      nombre+'" CON ID "'+str(id)+'" ACTUALIZADA CORRECTAMENTE')
                    return jsonify({"message": "Categoria Actualizada Correctamente"}), 200
                else:
                    return jsonify({"message": "Categoria No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial("ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR LA CATEGORIA "' +
                              nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar la Categoria"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_categorias(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                dir_cat = "categorias_"+session["tipo"]
                id = val.val_vacio("id","",request).strip()
                nombre = val.val_vacio("nombre","",request).upper().strip()
                existe = db[dir_cat].find_one({"_id": ObjectId(id)})

                if existe:

                    dir_inv = "inventario_"+session["tipo"]
                    dependencia = db[dir_inv].find_one({"categoria": ObjectId(id)})

                    if dependencia:
                        return jsonify({"message": "Existen Inventarios asociados en la Categoría a Eliminar"}), 404
                    else:
                        db[dir_cat].delete_one({"_id": ObjectId(id)})
                        hist.guardar_historial(
                            "CORRECTO", "ELIMINAR", 'CATEGORIA "'+nombre+'" CON ID "'+str(id)+'" ELIMINADA CORRECTAMENTE')
                        return jsonify({"message": "Categoria Eliminada Correctamente"}), 200
                else:
                    return jsonify({"message": "Categoria NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR LA CATEGORIA "'+nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar la Categoria"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
