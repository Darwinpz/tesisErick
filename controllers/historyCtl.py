from flask import jsonify,session
from models.History import History
from database.mongoDb import MongoDb
from controllers.validateCtl import Validaciones as val
import json
db = MongoDb().db()


def guardar_historial(tipo, accion, mensaje):
    history = History(tipo, accion, mensaje, session)
    db.history.insert_one(history.obtener_history())


def ver_history(request):

    if request.method == 'POST':

        try:

            if val.validar_session(session):

                if val.validar_admin(session):
                    #histories = db.history.find()

                    histories = db.history.aggregate([
                            {"$addFields": {
                                "fecha_accion":{ "$dateToString":{"format":"%d/%m/%Y %H:%M:%S", "date":"$fecha_accion"}}
                            }},
                            {
                                "$sort": {"fecha_accion":-1}
                            }
                        ])
                    
                    data = {"data": list(histories)}

                    return json.dumps(data, default=str), 200
                else:
                    return jsonify({"message": "Debes ser Administrador"}), 401
            else:
                return jsonify({"message": "Debes iniciar sesión"}), 403
        except Exception as e:
            guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR TODO EL HISTORIAL - "'+str(e)+'"')
            return jsonify({"message": "Error al Visualizar todo el historial"}), 404
    else:
        return jsonify({"message": "Petición Incorrecta"}), 500
