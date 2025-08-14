from flask import render_template, jsonify, session
from datetime import datetime
from controllers.validateCtl import Validaciones as val
from bson.objectid import ObjectId
from database.mongoDb import MongoDb
import controllers.historyCtl as hist

db = MongoDb().db()

def inicio():
    return render_template('/views/index.html')


def del_foto(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                id = val.val_vacio("id","",request)
                tipo = val.val_vacio("tipo","",request)
                existe = None

                if tipo == "inventarios":
                    existe = db["inventario" +"_"+session["tipo"]].find_one({"_id": ObjectId(id)})
                else:
                    existe = db[tipo].find_one({"_id": ObjectId(id)})

                if existe:
                    if existe["url_foto"] != "":
                        path = ("public/"+tipo+"/"+existe["url_foto"])
                        val.del_archivo(path)
                        db[tipo].update_one({"_id": ObjectId(id)}, { "$set": {"url_foto": ""}})
                    return jsonify({"message": "Imagen Eliminada Correctamente"}), 200
                else:
                    return jsonify({"message": "El Recurso No existe"}), 404
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "CREAR", 'ERROR AL ELIMINAR LA IMAGEN DE TIPO "'+tipo+'" CON ID "'+id+'" - "'+str(e)+'"')
            return jsonify({"message": "Error al eliminar la imagen"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
