from flask import jsonify, session
import controllers.historyCtl as hist
from database.mongoDb import MongoDb
from models.Inventario import Inventario
from bson.objectid import ObjectId
from controllers.validateCtl import Validaciones as val
import json
import os
import uuid

db = MongoDb().db()

def save_inventario(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                foto = request.files['i_foto']
                nombre =  val.val_vacio("i_nombre","",request).upper().strip()
                estado =  val.val_vacio("i_estado","",request).upper().strip()
                descripcion = val.val_vacio("i_descripcion","",request).upper().strip()
                precio = val.val_vacio("i_precio","0",request).upper().strip()
                categoria = val.val_vacio("i_categoria","",request).strip()
                cta_contable = val.val_vacio("i_cta_contable","",request).upper().strip()
                codigo = val.val_vacio("i_codigo","",request).upper().strip()
                serie = val.val_vacio("i_serie","",request).upper().strip()
                marca = val.val_vacio("i_marca","",request).strip()
                modelo = val.val_vacio("i_modelo","",request).strip()
                ip = val.val_vacio("i_ip","",request).upper().strip()
                mac = val.val_vacio("i_mac","",request).upper().strip()
                adquisicion = val.val_vacio("i_adquisicion","",request).upper().strip()
                
                item_pieza = request.form.getlist("pieza[]")
                item_serie = request.form.getlist("serie[]")
                item_modelo = request.form.getlist("modelo[]")
                item_detalle = request.form.getlist("detalle[]")

                path = ("public/inventarios")

                val.crear_directorio(path)

                url_foto = ""
                items = []
                dir_inv = "inventario_"+session["tipo"]

                if nombre != "" and estado != "" and categoria != "" and adquisicion != "":

                    jefeArea = db.servidores.aggregate([
                        {"$lookup": {"from": "areas", "localField": "area",
                                     "foreignField": "_id", "as": "area"}},
                        {"$unwind": "$area"},
                        {"$match": {"$and": [{'area.abreviatura': session["tipo"]}, {'jefe': 'SI'}]}},
                        {"$project": { "cedula": 1, "_id": 0 }},
                        {"$limit": 1}
                    ])

                    jefeArea = next(jefeArea, None)

                    if jefeArea:
                            
                        custodio = val.val_vacio("i_custodio",str(jefeArea["cedula"]),request).upper().strip() # CEDULA DEL JEFE ÁREA

                        if len(descripcion) > 56:
                            return jsonify({"message": "Descripción muy larga"}), 404

                        if not precio.isdigit():
                            return jsonify({"message": "No puedes colocar precios negativos"}), 404

                        if cta_contable != "":
                            existe = db[dir_inv].find_one({'cta_contable': cta_contable})
                            if existe:
                                return jsonify({"message": "Cuenta Contable de Inventario existente"}), 404

                        if codigo != "":
                            existe = db[dir_inv].find_one({'codigo': codigo})
                            if existe:
                                return jsonify({"message": "Código de Inventario existente"}), 404

                        if ip != "":
                            existe = db[dir_inv].find_one({'ip': ip})
                            if existe:
                                return jsonify({"message": "Dirección IP existente"}), 404

                        if mac != "":
                            existe = db[dir_inv].find_one({'mac': mac})
                            if existe:
                                return jsonify({"message": "Dirección MAC existente"}), 404

                        if marca != "":
                            marca = ObjectId(marca)
                            if modelo != "":
                                modelo = ObjectId(modelo)
                            else:
                                return jsonify({"message": "Debes Seleccionar el Modelo"}), 404

                        if foto.filename != '':
                            id = str(uuid.uuid1())
                            file_ext = os.path.splitext(foto.filename)[1]
                            url_foto = id+file_ext
                            foto.save(os.path.join(path, url_foto))

                        if len(item_pieza) == len(item_serie) == len(item_modelo) == len(item_detalle):
                            for i in range(len(item_pieza)):
                                items.append(
                                    {"pieza": item_pieza[i], "serie": item_serie[i], "modelo": item_modelo[i], "detalle": item_detalle[i]})

                        inventario = Inventario(nombre, estado, descripcion, precio, ObjectId(categoria), cta_contable,
                                                codigo, serie, marca, modelo, ip, mac, adquisicion, custodio, url_foto, items)
                        inventario.crear_inventario()
                        _id = db[dir_inv].insert_one(
                            inventario.obtener_inventario()).inserted_id
                        hist.guardar_historial("CORRECTO", "CREAR", 'INVENTARIO "' +
                                        nombre+'" CON ID "'+str(_id)+'" CREADO CORRECTAMENTE')
                        return jsonify({"message": "Inventario Creado Correctamente"}), 200
                    else:
                        return jsonify({"message": "No existe un jefe de Área a asignar el inventario por defecto"}), 404
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL INVENTARIO "'+nombre+'" - "'+str(e)+'"')
            val.del_archivo(path.join(path, url_foto))
            return jsonify({"message": "Error al Crear el inventario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def buscar_inventarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                custodio = val.val_vacio("custodio","",request).strip()

                dir_inv = "inventario_"+session["tipo"]
                dir_cat = "categorias_"+session["tipo"]
                dir_mar = "marcas_"+session["tipo"]
                dir_mod = "modelos_"+session["tipo"]

                if custodio == "":
                    return json.dumps({"data":list([])}, default=str), 200
                
                consulta = [

                    {"$lookup": {"from": "servidores", "localField": "custodio",
                                 "foreignField": "cedula", "as": "servidor"}},
                    {"$unwind": "$servidor"},
                    {"$lookup": {"from": dir_cat, "localField": "categoria",
                                 "foreignField": "_id", "as": "categoria"}},
                    {"$unwind": "$categoria"},
                    {"$lookup": {"from": dir_mar, "localField": "marca",
                                 "foreignField": "_id", "as": "marca"}},
                    {"$unwind": {"path": "$marca", "preserveNullAndEmptyArrays": True}},
                    {"$lookup": {"from": dir_mod, "localField": "modelo",
                                 "foreignField": "_id", "as": "modelo"}},
                    {"$unwind": {"path": "$modelo", "preserveNullAndEmptyArrays": True}},
                    {
                        "$addFields": {
                            "marca.nombre": {"$ifNull": ["$marca.nombre", "N/A"]},
                            "modelo.nombre": {"$ifNull": ["$modelo.nombre", "N/A"]}
                        }
                    },
                    {"$project": 
                        {
                            "codigo": 1,
                            "serie": 1,
                            "categoria.nombre": 1,
                            "nombre":1,
                            "marca.nombre":1,
                            "modelo.nombre":1,
                            "estado":1,
                        }
                    }
                ]

                if custodio != "" and custodio != "-":
                    consulta.insert(2,{"$match": {'custodio': custodio}})

                inventarios = db[dir_inv].aggregate(consulta)

                data = {"data": list(inventarios)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            print(e)
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODO EL INVENTARIO - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todo el Inventario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def ver_inventarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                dir_inv = "inventario_"+session["tipo"]
                dir_cat = "categorias_"+session["tipo"]
                dir_mar = "marcas_"+session["tipo"]
                dir_mod = "modelos_"+session["tipo"]

                consulta = [

                    {"$lookup": {"from": "servidores", "localField": "custodio",
                                 "foreignField": "cedula", "as": "servidor"}},
                    {"$unwind": "$servidor"},
                    {"$lookup": {"from": dir_cat, "localField": "categoria",
                                 "foreignField": "_id", "as": "categoria"}},
                    {"$unwind": "$categoria"},
                    {"$lookup": {"from": dir_mar, "localField": "marca",
                                 "foreignField": "_id", "as": "marca"}},
                    {"$unwind": {"path": "$marca", "preserveNullAndEmptyArrays": True}},
                    {"$lookup": {"from": dir_mod, "localField": "modelo",
                                 "foreignField": "_id", "as": "modelo"}},
                    {"$unwind": {"path": "$modelo", "preserveNullAndEmptyArrays": True}},
                    {
                        "$addFields": {
                            "marca.nombre": {"$ifNull": ["$marca.nombre", "N/A"]},
                            "modelo.nombre": {"$ifNull": ["$modelo.nombre", "N/A"]}
                        }
                    }
                ]

                inventarios = db[dir_inv].aggregate(consulta)

                data = {"data": list(inventarios)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            print(e)
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODO EL INVENTARIO - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todo el Inventario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def edit_inventarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("i_id","",request).strip()            
                foto = request.files['i_foto']
                nombre =  val.val_vacio("i_nombre","",request).upper().strip()
                estado =  val.val_vacio("i_estado","",request).upper().strip()
                descripcion = val.val_vacio("i_descripcion","",request).upper().strip()
                precio = val.val_vacio("i_precio","0",request).upper().strip()
                categoria = val.val_vacio("i_categoria","",request).strip()
                cta_contable = val.val_vacio("i_cta_contable","",request).upper().strip()
                codigo = val.val_vacio("i_codigo","",request).upper().strip()
                serie = val.val_vacio("i_serie","",request).upper().strip()
                marca = val.val_vacio("i_marca","",request).strip()
                modelo = val.val_vacio("i_modelo","",request).strip()
                ip = val.val_vacio("i_ip","",request).upper().strip()
                mac = val.val_vacio("i_mac","",request).upper().strip()
                adquisicion = val.val_vacio("i_adquisicion","",request).upper().strip()
                
                item_pieza = request.form.getlist("pieza[]")
                item_serie = request.form.getlist("serie[]")
                item_modelo = request.form.getlist("modelo[]")
                item_detalle = request.form.getlist("detalle[]")

                path = ("public/inventarios")

                val.crear_directorio(path)

                url_foto = ""
                items = []
                dir_inv = "inventario_"+session["tipo"]

                if nombre != "" and estado != "" and categoria != "" and adquisicion != "":

                    existe = db[dir_inv].find_one({"_id": ObjectId(id)})

                    if existe:

                        jefeArea = db.servidores.aggregate([
                        {"$lookup": {"from": "areas", "localField": "area",
                                     "foreignField": "_id", "as": "area"}},
                        {"$unwind": "$area"},
                        {"$match": {"$and": [{'area.abreviatura': session["tipo"]}, {'jefe': 'SI'}]}},
                        {"$project": { "cedula": 1, "_id": 0 }},
                        {"$limit": 1}
                        ])

                        jefeArea = next(jefeArea, None)

                        if jefeArea:

                            custodio = val.val_vacio("i_custodio",str(jefeArea["cedula"]),request).upper().strip() # CEDULA DEL JEFE ÁREA

                            if len(descripcion) > 56:
                                return jsonify({"message": "Descripción muy larga"}), 404

                            if cta_contable != "" and cta_contable != existe["cta_contable"]:
                                existe_cta_contable = db[dir_inv].find_one({'cta_contable': cta_contable})
                                if existe_cta_contable:
                                    return jsonify({"message": "Cuenta Contable de Inventario existente"}), 404

                            if codigo != "" and codigo != existe["codigo"]:
                                existe_cod = db[dir_inv].find_one({'codigo': codigo})
                                if existe_cod:
                                    return jsonify({"message": "Código de Inventario existente"}), 404

                            if ip != "" and ip != existe["ip"]:
                                existe_ip = db[dir_inv].find_one({'ip': ip})
                                if existe_ip:
                                    return jsonify({"message": "Dirección IP existente"}), 404

                            if mac != "" and mac != existe["mac"]:
                                existe_mac = db[dir_inv].find_one({'mac': mac})
                                if existe_mac:
                                    return jsonify({"message": "Dirección MAC existente"}), 404
                                
                            if marca != "":
                                marca = ObjectId(marca)
                                if modelo != "":
                                    modelo = ObjectId(modelo)
                                else:
                                    return jsonify({"message": "Debes Seleccionar el Modelo"}), 404

                            if foto.filename != '':

                                if existe["url_foto"] != "":
                                    path_temp = ("public/inventarios/" +
                                                existe["url_foto"])
                                    val.del_archivo(path_temp)

                                id = str(uuid.uuid1())
                                file_ext = os.path.splitext(foto.filename)[1]
                                url_foto = id+file_ext
                                foto.save(os.path.join(path, url_foto))

                            if len(item_pieza) == len(item_serie) == len(item_modelo) == len(item_detalle):
                                for i in range(len(item_pieza)):
                                    items.append(
                                        {"pieza": item_pieza[i], "serie": item_serie[i], "modelo": item_modelo[i], "detalle": item_detalle[i]})
                            else:
                                return jsonify({"message": "Completa los Componentes Adicionales"}), 404
                            inventario = Inventario(nombre, estado, descripcion, precio, ObjectId(categoria), cta_contable,
                                                    codigo, serie, marca, modelo, ip, mac, adquisicion, custodio, url_foto, items)
                            inventario.update_inventario()
                            db[dir_inv].update_one({"_id": ObjectId(existe["_id"])}, {
                                "$set": inventario.obtener_inventario()})
                            hist.guardar_historial("CORRECTO", "ACTUALIZAR", 'INVENTARIO "' +
                                            nombre+'" CON ID "'+str(id)+'" ACTUALIZADO CORRECTAMENTE')
                            return jsonify({"message": "Inventario Actualizado Correctamente"}), 200   
                        else:
                            return jsonify({"message": "No existe un jefe de Área a asignar el inventario por defecto"}), 404 
                    else:
                        return jsonify({"message": "Inventario NO Existente"}), 404
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial("ERROR", "ACTUALIZAR", 'ERROR AL ACTUALIZAR EL INVENTARIO "' +
                              nombre+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Actualizar el inventario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_inventarios(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):
                
                dir_inv = "inventario_"+session["tipo"]
                id =  val.val_vacio("id","",request).strip()
                existe = db[dir_inv].find_one({"_id": ObjectId(id)})

                if existe:

                    if existe["url_foto"] != "":
                        path = ("public/inventarios/"+existe["url_foto"])
                        val.del_archivo(path)

                    db[dir_inv].delete_one({"_id": ObjectId(id)})
                    hist.guardar_historial(
                        "CORRECTO", "ELIMINAR", 'INVENTARIO "'+existe["nombre"]+'" CON ID "'+str(id)+'" ELIMINADO CORRECTAMENTE')
                    return jsonify({"message": "Inventario Eliminado Correctamente"}), 200
                else:
                    return jsonify({"message": "Inventario NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL INVENTARIO "'+existe["nombre"]+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el Inventario"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
