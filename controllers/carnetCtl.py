from flask import make_response, session, abort
from database.mongoDb import MongoDb
from controllers.validateCtl import Validaciones as val
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A6
import controllers.historyCtl as hist
from io import BytesIO
from reportlab.lib import utils
from reportlab.lib.styles import ParagraphStyle
from bson.objectid import ObjectId

db = MongoDb().db()

RUTA_IMAGEN_SERVIDOR = []

imagen_perfil = utils.ImageReader("./public/img/perfil.jpg")
imagen_logo = utils.ImageReader("./public/img/logo.jpg")

def dividir_texto(texto):
    contenido = texto.split()
    mitad = len(contenido) // 2
    return (' '.join(contenido[:mitad]) + "<br/>" + ' '.join(contenido[mitad:])).strip()

def construir(my_doc, buffer, elements, filename, cabecera):
    my_doc.build(elements, onFirstPage=cabecera, onLaterPages=cabecera)
    pdf = buffer.getvalue()
    buffer.close()
    response = make_response(pdf)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'inline', filename=filename)
    return response

def cabecera_vertical_upsipteeo(canvas, doc):
    page_index = doc.page - 1
    if page_index < len(RUTA_IMAGEN_SERVIDOR):
        imagen = RUTA_IMAGEN_SERVIDOR[page_index]
    else:
        imagen = ""

    canvas.saveState()
    canvas.drawImage(imagen_logo, 14*mm, A6[1]-35*mm, width=76*mm, height=32*mm)
    canvas.setLineWidth(1)
    canvas.line(3*mm, A6[1] - 34*mm, A6[0] - 3*mm, A6[1] - 34*mm)

    x = 33*mm
    y = A6[1]-85*mm
    width = 40*mm
    height = 45*mm
    radius = 5

    if imagen != "":
        imagen_servidor = utils.ImageReader(imagen) 
        canvas.drawImage(imagen_servidor, x, y, width=width, height=height)
    else:
        canvas.drawImage(imagen_perfil, x, y, width=width, height=height)

    canvas.setLineWidth(1)
    canvas.setStrokeColorRGB(0, 0, 0)
    canvas.roundRect(x, y, width, height, radius)

    canvas.setFont('Helvetica-Bold', 10)
    canvas.setLineWidth(1)
    canvas.setStrokeColorRGB(0, 0, 0)
    canvas.rect(3*mm, 3*mm, A6[0] - 6*mm, A6[1] - 6*mm)

    canvas.restoreState()

def ver_carnet(id=None):
    if not val.validar_session(session):
        abort(403)

    try:
        consulta = [
            {"$lookup": {"from": "cargos", "localField": "cargo",
                         "foreignField": "_id", "as": "cargo"}},
            {"$unwind": "$cargo"},
            {"$lookup": {"from": "areas", "localField": "area",
                         "foreignField": "_id", "as": "area"}},
            {"$unwind": "$area"},
            {"$lookup": {"from": "modalidades", "localField": "modalidad",
                         "foreignField": "_id", "as": "modalidad"}},
            {"$unwind": "$modalidad"}
        ]
        
        if id is not None:
            consulta.insert(1, {"$match": {'_id': ObjectId(id)}})
        else:
            consulta.insert(1, {"$match": {'estado': 'ACTIVO'}})

        servidores = list(db.servidores.aggregate(consulta))

        if not servidores:
            abort(404)

        RUTA_IMAGEN_SERVIDOR.clear()

        buffer = BytesIO()
        my_doc = SimpleDocTemplate(buffer, pagesize=A6, title="Carnet")
        elements = []

        for servidor in servidores:
            # Espacio grande para que empiece debajo de la foto
            elements.append(Spacer(1, 170))  # Ajustar este valor si es necesario

            # Nombre
            table_data_nombre = [[Paragraph(
                "<b>" + dividir_texto(servidor["nombres"]) + "</b>",
                style=ParagraphStyle('Nombres', fontSize=14, alignment=1,leading=15, spaceBefore=5, spaceAfter=5)
            )]]
            table_nombre = Table(table_data_nombre, colWidths=200)
            table_nombre.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table_nombre)

            # Cédula
            elements.append(Paragraph(
                "<b>C.I: " + servidor["cedula"] + "</b>",
                style=ParagraphStyle('Cedula', fontSize=13, alignment=1, spaceBefore=5, spaceAfter=5)
            ))

            # Cargo
            table_data_cargo = [[Paragraph(
                "<b>" + servidor["cargo"]["nombre"] +" - "+servidor["area"]["nombre"] + "</b>",
                style=ParagraphStyle('Cargo', fontSize=11, alignment=1, spaceBefore=5, spaceAfter=5)
            )]]
            table_cargo = Table(table_data_cargo, colWidths=250)
            table_cargo.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(table_cargo)

            # Guardar imagen
            if servidor["url_foto"] != "":
                RUTA_IMAGEN_SERVIDOR.append("./public/servidores/" + servidor["url_foto"])
            else:
                RUTA_IMAGEN_SERVIDOR.append("")

        return construir(my_doc, buffer, elements, 'carnet.pdf', cabecera_vertical_upsipteeo)

    except Exception as e:
        hist.guardar_historial(
            "ERROR", "VISUALIZAR", f'ERROR AL VISUALIZAR LOS CARNET - "{str(e)}"'
        )
        abort(404)
