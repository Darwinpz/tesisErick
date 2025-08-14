from flask import render_template, session, redirect, url_for, abort
from database.mongoDb import MongoDb
import controllers.historyCtl as hist
from bson.objectid import ObjectId
from controllers.validateCtl import Validaciones as val
import controllers.encryptCtl as ctl_encrypt
import os

db = MongoDb().db()

def cerrar_sesion():
    if val.validar_session(session):
        hist.guardar_historial(
            "CORRECTO", "SALIR", 'CIERRE DE SESIÓN CON ÉXITO - CÉDULA: "'+session["cedula"]+'"')
        session.pop('ip', None)
        session.pop('id', None)
        session.pop('cedula', None)
        session.pop('nombre', None)
        session.pop('tipo', None)
        session.pop('rol', None)
        return redirect(url_for('inv_login'))
    else:
        abort(403)


def principal():
    if val.validar_session(session):
        return render_template('/views/inventario/principal.html', session=session)
    else:
        return redirect(url_for('inv_login'))


def login(request):

    alerts = {"tipo": "", "message": ""}

    try:

        if request.method == 'GET':
            if val.validar_session(session):
                return redirect(url_for("inv_principal"))
            else:
                return render_template('/views/inventario/login.html')
        else:

            nom_usuario = val.val_vacio("usuario","",request)
            clave = val.val_vacio("clave","",request)

            if nom_usuario == os.getenv("USER_ADMIN") and clave == os.getenv("PWD_ADMIN"):
                session["ip"] = request.environ['REMOTE_ADDR']
                session["id"] = ObjectId().__str__()
                session["cedula"] = "0000000000"
                session["nombre"] = "SUPER-ADMIN"
                session["tipo"] = "AFIVANET"
                session["rol"] = "Super-Admin"

                hist.guardar_historial(
                    "CORRECTO", "INGRESO", 'INGRESO CON ÉXITO AL SISTEMA - SUPER-ADMIN: "'+session["cedula"]+'"')

                return redirect(url_for("inv_principal"))

            usuario = list(db.usuarios.aggregate([
                {"$lookup": {"from": "servidores", "localField": "cedula",
                             "foreignField": "cedula", "as": "servidor"}},
                {"$unwind": "$servidor"},
                {"$project": {"servidor._id": 0}},
                {"$match": {"$or": [{"servidor.cedula": nom_usuario}, {"usuario": nom_usuario}, {
                    "servidor.correo": nom_usuario}]}},
                {"$lookup": {"from": "areas", "localField": "servidor.area",
                             "foreignField": "_id", "as": "area"}},
                {"$unwind": "$area"},
            ]))

            if len(usuario) > 0:

                usuario = usuario[0]

                if clave == ctl_encrypt.decrypt(usuario["clave"]):

                    if usuario["estado"] == "ACTIVO":
                        session["ip"] = request.environ['REMOTE_ADDR']
                        session["id"] = str(usuario["_id"])
                        session["cedula"] = usuario["servidor"]["cedula"]
                        session["nombre"] = usuario["servidor"]["nombres"]
                        session["tipo"] = usuario["area"]["abreviatura"]
                        session["rol"] = usuario["rol"]

                        hist.guardar_historial(
                            "CORRECTO", "INGRESO", 'INGRESO CON ÉXITO AL SISTEMA - CÉDULA: "'+session["cedula"]+'"')

                        return redirect(url_for("inv_principal"))
                    else:
                        alerts["tipo"] = "danger"
                        alerts["message"] = "Usuario Inactivo o No existe"
                        return render_template('/views/inventario/login.html', alert=alerts)
                else:
                    alerts["tipo"] = "danger"
                    alerts["message"] = "Clave incorrecta"
                    return render_template('/views/inventario/login.html', alert=alerts)
            else:
                alerts["tipo"] = "danger"
                alerts["message"] = "Usuario incorrecto"
                return render_template('/views/inventario/login.html', alert=alerts)
    except Exception as e:
        alerts["tipo"] = "danger"
        alerts["message"] = str(e)
        hist.guardar_historial(
            "ERROR", "INGRESO", 'ERROR DE INGRESO AL SISTEMA - "'+str(e)+'"')
        abort(500)
