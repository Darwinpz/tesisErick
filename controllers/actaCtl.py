from flask import jsonify, session
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from controllers.validateCtl import Validaciones as val
from models.Acta import Acta
from bson.objectid import ObjectId
import json
from datetime import datetime

db = MongoDb().db()

fecha = datetime.now()
sys_anio = fecha.year

def obtener_servidores(cedulas):
    consulta = [
        {"$match": {'cedula': {"$in": [str(cedula) for cedula in cedulas]}}},
        {"$lookup": {"from": "cargos", "localField": "cargo", "foreignField": "_id", "as": "cargo"}},
        {"$unwind": "$cargo"},
        {"$lookup": {"from": "areas", "localField": "area", "foreignField": "_id", "as": "area"}},
        {"$unwind": "$area"},
    ]
    return list(db.servidores.aggregate(consulta))

def save_actas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                entrega = val.val_vacio("act_entrega", "", request).strip()
                recibe = val.val_vacio("act_recibe", "", request).strip()
                veedor = val.val_vacio("act_veedor","",request).strip()

                inventario = request.form.getlist("act_inventario[]")

                if entrega != "" and recibe != "" and veedor != "":

                    if len(inventario) > 0:

                        if entrega != recibe:
                            dir_act = "actas_"+session["tipo"]

                            existe = db[dir_act].find_one({"$and": [{'entrega': entrega}, {'recibe': recibe} ,{'veedor':veedor}, {'estado':'Pendiente'}]})

                            if existe:
                                return jsonify({"message": "Acta Pendiente para revisión N° "+str(existe["numero"])}), 404
                            else:

                                secuencia = 1
                                
                                ultimo = db[dir_act].aggregate([
                                    {"$match": {"numero": {"$regex": f"^{sys_anio}-\\d+-TMP$"}}},# solo TMP
                                    {"$addFields": {"secuencia_int": {"$toInt": {"$arrayElemAt": [{"$split": ["$numero", "-"]}, 1]}}}},
                                    {"$sort": {"secuencia_int": -1}},
                                    {"$limit": 1}
                                ])

                                ultimo = next(ultimo, None)
                                
                                if ultimo:
                                    cod_acta = str(ultimo["numero"]).split('-')
                                    anio = int(cod_acta[0])
                                    if anio == sys_anio:
                                        secuencia = int(cod_acta[1]) + 1

                                num_acta = f"{sys_anio}-{secuencia}-TMP"

                                dir_inv = "inventario_"+session["tipo"]
                                dir_cat = "categorias_"+session["tipo"]
                                dir_mar = "marcas_"+session["tipo"]
                                dir_mod = "modelos_"+session["tipo"]

                                inventario = [ObjectId(id_str) for id_str in inventario]

                                productos = list(db[dir_inv].aggregate([
                                    {"$match":  {"_id": {"$in": inventario}}},
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
                                ]))

                                cedulas = [entrega, recibe, veedor]
                                servidores = obtener_servidores(cedulas)

                                servidores_dict = {servidor['cedula']: servidor for servidor in servidores}

                                serv_entrega = servidores_dict.get(entrega)
                                serv_recibe = servidores_dict.get(recibe)
                                serv_veedor = servidores_dict.get(veedor)
                                
                                acta = Acta(num_acta, productos,serv_entrega,serv_recibe,serv_veedor,"Pendiente",session)
                                acta.crear_acta()
                                _id = db[dir_act].insert_one(
                                    acta.obtener_acta()).inserted_id
                                hist.guardar_historial(
                                    "CORRECTO", "CREAR", 'ACTA N° "'+str(num_acta)+'" CON ID "'+str(_id)+'" CREADA CORRECTAMENTE')
                                return jsonify({"message": "Acta Creada Correctamente"}), 200
                        else:
                            return jsonify({"message": "El que Entrega debe ser Diferente al que Recibe"}), 404
                    else:
                        return jsonify({"message": "Debes seleccionar almenos un producto a entregar"}), 404
                else:
                    return jsonify({"message": "Información Incompleta"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL CREAR EL ACTA PARA "'+recibe+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Crear el acta"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500

def ver_actas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):
                
                dir_act = "actas_"+session["tipo"]
                actas = db[dir_act].aggregate([
                    {"$addFields": {
                        "fecha_acta":{ "$dateToString":{"format":"%Y-%m-%d %H:%M:%S", "date":"$fecha_creacion"}},
                        "fecha_aprobacion":{ "$dateToString":{"format":"%Y-%m-%d %H:%M:%S", "date":"$fecha_aprobacion"}}
                    }},
                    {
                        "$project": {
                            "numero": 1,
                            "estado": 1,
                            "entrega.nombres": 1,
                            "recibe.nombres": 1,
                            "fecha_acta": 1,
                            "fecha_aprobacion": 1
                        }
                    },
                    {"$sort": {"fecha_acta": -1}}
                ])

                data = {"data": list(actas)}

                return json.dumps(data, default=str), 200
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODAS LAS ACTAS - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todas las actas"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def aprobar_actas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id", "", request).strip()
                numero = val.val_vacio("numero", "", request).strip()
                
                dir_inv = "inventario_"+session["tipo"]
                dir_act = "actas_"+session["tipo"]
                
                existe = db[dir_act].find_one({"_id": ObjectId(id)})

                if existe:
                    
                    secuencia = 1
                            
                    ultimo = db[dir_act].aggregate([
                        {"$match": {"numero": {"$regex": f"^{sys_anio}-\\d+(-[^T].*|)$"}}}, #que no sean TMP
                        {"$addFields": {"secuencia_int": {"$toInt": {"$arrayElemAt": [{"$split": ["$numero", "-"]}, 1]}}}},
                        {"$sort": {"secuencia_int": -1}},
                        {"$limit": 1}
                    ])

                    ultimo = next(ultimo, None)
                            
                    if ultimo:
                        cod_acta = str(ultimo["numero"]).split('-')
                        anio = int(cod_acta[0])
                        if anio == sys_anio:
                            secuencia = int(cod_acta[1]) + 1

                    num_acta = f"{sys_anio}-{secuencia}"

                    ids_inventario = [item["_id"] for item in existe["inventario"]]
                
                    db[dir_act].update_one({"_id": ObjectId(id)},{"$set":{"numero":num_acta,"estado":"Aprobado", "fecha_aprobacion":datetime.now()}})
                    
                    db[dir_inv].update_many({"_id": {"$in": ids_inventario}}, {"$set": {"custodio": existe["recibe"]["cedula"]}})

                    hist.guardar_historial(
                        "CORRECTO", "APROBADO", 'ACTA N° "'+str(numero)+'" CON ID "'+str(id)+'" APROBADA CORRECTAMENTE')
                    return jsonify({"message": "Acta Aprobada Correctamente"}), 200
                   
                else:
                    return jsonify({"message": "Acta NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "APROBAR", 'ERROR AL APROBAR EL ACTA N° "'+str(numero)+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Aprobar el acta"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500


def del_actas(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id", "", request).strip()
                numero = val.val_vacio("numero", "", request).strip()
                dir_act = "actas_"+session["tipo"]
                
                existe = db[dir_act].find_one({"_id": ObjectId(id)})

                if existe:
                        
                    db[dir_act].delete_one({"_id": ObjectId(id)})
                    hist.guardar_historial(
                        "CORRECTO", "ELIMINAR", 'ACTA N° "'+str(numero)+'" CON ID "'+str(id)+'" ELIMINADA CORRECTAMENTE')
                    return jsonify({"message": "Acta Eliminada Correctamente"}), 200
                   
                else:
                    return jsonify({"message": "Acta NO Existente"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "ELIMINAR", 'ERROR AL ELIMINAR EL ACTA N° "'+str(numero)+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al Eliminar el acta"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
