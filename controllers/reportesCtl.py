from flask import make_response, session, abort,request
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.platypus.tables import Table, TableStyle, colors
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime, timedelta
import controllers.historyCtl as hist
from reportlab.lib import utils
from io import BytesIO
import locale
from bson.objectid import ObjectId
from database.mongoDb import MongoDb
from controllers.validateCtl import Validaciones as val

locale.setlocale(locale.LC_TIME, 'es_ES.utf8')

db = MongoDb().db()

imagen_logo = utils.ImageReader("./public/img/logo.jpg")

fecha = datetime.now().strftime("%d/%m/%Y - %H:%M:%S")

def dividir_texto(texto):
    contenido = texto.split()
    mitad = len(contenido)//2
    return (' '.join(contenido[:mitad]) +"\n"+ ' '.join(contenido[mitad:])).strip()

def table_usuarios():

    usuarios = db.usuarios.aggregate([
        {"$lookup": {"from": "servidores", "localField": "cedula",
                     "foreignField": "cedula", "as": "servidor"}},
        {"$unwind": "$servidor"},
        {"$project": {"servidor._id": 0}},
        {"$lookup": {"from": "areas", "localField": "servidor.area",
                    "foreignField": "_id", "as": "area"}},
        {"$unwind": "$area"}
    ])

    data = [
        ['Cédula', 'Usuario', 'Nombres', 'Tipo', 'Rol', 'Estado'],
    ]

    for user in usuarios:
        data.append([user["cedula"], user["usuario"], user["servidor"]
                    ["nombres"], user["area"]["abreviatura"], user["rol"], user["estado"]])

    return estilo_tabla(data)


def table_servidores():

    servidores = db.servidores.aggregate([
        {"$lookup": {"from": "cargos", "localField": "cargo",
                             "foreignField": "_id", "as": "cargo"}},
        {"$unwind": "$cargo"},
        {"$lookup": {"from": "areas", "localField": "area",
                             "foreignField": "_id", "as": "area"}},
        {"$unwind": "$area"},
        {"$lookup": {"from": "modalidades", "localField": "modalidad",
                             "foreignField": "_id", "as": "modalidad"}},
        {"$unwind": "$modalidad"},
    ])

    data = [
        ['Cédula', 'Nombres', 'Correo', 'Area', 'Jefe', 'Cargo', 'Estado'],
    ]
    
    
    for user in servidores:
        data.append([user["cedula"], user["nombres"], user["correo"],
                    user["area"]["abreviatura"],user["jefe"], dividir_texto(user["cargo"]["nombre"]), user["estado"]])

    return estilo_tabla(data)

def table_actas(acta):

    data = [
        ['Código', 'Cuenta', 'Serie','Categoria', 'Nombre', 'Marca','Modelo', 'Estado', 'Descripción'],
    ]

    for inv in acta["inventario"]:

        codigo = "N/A" if inv["codigo"].strip() == "" else inv["codigo"].strip()
        cta_contable = "N/A" if inv["cta_contable"].strip() == "" else inv["cta_contable"].strip()
        serie = "N/A" if inv["serie"].strip() == "" else inv["serie"].strip()
        modelo = "N/A" if inv["modelo"]["nombre"].strip() == "" else inv["modelo"]["nombre"].strip()
        marca = "N/A" if inv["marca"]["nombre"].strip() == "" else inv["marca"]["nombre"].strip()
        descripcion = "N/A" if inv["descripcion"].strip() == "" else inv["descripcion"].strip()

        data.append([codigo, cta_contable,serie, dividir_texto(inv["categoria"]["nombre"]), dividir_texto(inv["nombre"]), marca, modelo ,inv["estado"], dividir_texto(descripcion)])

    return estilo_tabla(data)

def table_inventario(id=None,categoria=None,marca=None,modelo=None,estado=None):

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
    
    match_conditions = {}
    
    if id:
        match_conditions["servidor._id"] = ObjectId(id)
    if categoria:
        match_conditions["categoria._id"] = ObjectId(categoria)
    if marca:
        match_conditions["marca._id"] = ObjectId(marca)
    if modelo:
        match_conditions["modelo._id"] = ObjectId(modelo)
    if estado:
        match_conditions["estado"] = str(estado).upper()

    if match_conditions:
        consulta.append({"$match": match_conditions})

    inventarios = db[dir_inv].aggregate(consulta)

    data = [
        ['Código', 'Cuenta', 'Serie', 'Categoria', 'Marca', 'Modelo', 'Estado', 'Descripción']
    ]

    if id is None:
        data[0].append('Custodio')

    for inv in inventarios:

        codigo = "N/A" if inv["codigo"].strip() == "" else inv["codigo"].strip()
        cta_contable = "N/A" if inv["cta_contable"].strip() == "" else inv["cta_contable"].strip()
        serie = "N/A" if inv["serie"].strip() == "" else inv["serie"].strip()
        modelo = "N/A" if inv["modelo"]["nombre"].strip() == "" else inv["modelo"]["nombre"].strip()
        marca = "N/A" if inv["marca"]["nombre"].strip() == "" else inv["marca"]["nombre"].strip()
        descripcion = "N/A" if inv["descripcion"].strip() == "" else inv["descripcion"].strip()

        fila = [codigo, cta_contable, serie, dividir_texto(inv["categoria"]["nombre"]), 
                dividir_texto(marca), dividir_texto(modelo), inv["estado"], dividir_texto(descripcion)]

        if id is None:
            fila.append(dividir_texto(inv["servidor"]["nombres"]))
        data.append(fila)

    return estilo_tabla_inventario(data,id)


def estilo_tabla(data):

    tabla = Table(data, repeatRows=1)
    # tabla = Table(data, rowHeights=30, repeatRows=1, colWidths=[
    #              25*mm, 25*mm, 70*mm, 25*mm, 25*mm, 20*mm])

    tabla.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))

    return tabla

def estilo_tabla_inventario(data, id):

    margins = 50  # Margen izquierdo y derecho (ajustar según sea necesario)
    table_width = A4[1] - 2 * margins
    num_columns = len(data[0])
    #col_widths = [table_width / num_columns] * num_columns
    col_widths = [50] + [table_width / (num_columns - 1)] * (num_columns - 1)
    
    header_style = ParagraphStyle(
        name="HeaderStyle",
        fontName="Times-Bold",
        fontSize=9,
        alignment=1,  # Centrar el texto
        textColor=colors.black
    )
    cell_style = ParagraphStyle(
        name="CellStyle",
        fontName="Times-Roman",
        fontSize=7,
        alignment=1,  # Alinear a la izquierda
        textColor=colors.black,
        wordWrap="CJK",  # Permitir ajuste de palabras
        spaceBefore=3,
        spaceAfter=3
    )

    # Convertir los datos en párrafos con el estilo adecuado
    formatted_data = []
    for i, row in enumerate(data):
        formatted_row = [Paragraph(str(cell), header_style if i == 0 else cell_style) for cell in row]
        formatted_data.append(formatted_row)

    tabla = Table(formatted_data, repeatRows=1, colWidths=col_widths)
    # tabla = Table(data, rowHeights=30, repeatRows=1, colWidths=[
    #              25*mm, 25*mm, 70*mm, 25*mm, 25*mm, 20*mm])

    base_style = [
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 5),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('TOPPADDING', (0, 1), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 3),
    ]

    # Determinar los tamaños de fuente según la condición
    font_sizes = (9, 7) #if id is not None else (8, 6)

    # Añadir tamaños de fuente específicos
    base_style.extend([
        ('FONTSIZE', (0, 0), (-1, 0), font_sizes[0]),
        ('FONTSIZE', (0, 1), (-1, -1), font_sizes[1]),
    ])

    # Aplicar estilo a la tabla
    tabla.setStyle(TableStyle(base_style))

    return tabla

def estilo_firmas(data):

    tabla = Table(data, repeatRows=0)
    # tabla = Table(data, rowHeights=30, repeatRows=1, colWidths=[
    #              25*mm, 25*mm, 70*mm, 25*mm, 25*mm, 20*mm])

    tabla.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Times-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 30),
        
        ('ALIGN', (0, 1), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 1), (-1, -1), 'Times-Roman'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('TOPPADDING', (0, 1), (-1, -1), 2),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 1),
        
        ('FONTNAME', (0, 3), (-1, 3), 'Times-Bold'),
        ('FONTSIZE', (0, 3), (-1, 3), 8),
        ('TOPPADDING', (0, 3), (-1, 3), 1),
        ('BOTTOMPADDING', (0, 3), (-1, 3), 0),

        ('FONTNAME', (0, 4), (-1, 4), 'Times-Bold'),
        ('FONTSIZE', (0, 4), (-1, 4), 8),        
        ('TOPPADDING', (0, 4), (-1, 4), 0),
        
    ]))

    return tabla

def titulo(texto):

    title = Paragraph(texto, style=ParagraphStyle(
        'Titulo', fontName="Times-Bold", fontSize=12, alignment=1, spaceAfter=14))
    return title

def cabecera_vertical_upsipteeo(canvas, doc):

    area = db.areas.find_one({"abreviatura":session["tipo"]})
    palabras = area["nombre"].split()
    mitad = len(palabras)//2
    linea1 = ' '.join(palabras[:mitad])
    linea2 = ' '.join(palabras[mitad:])

    canvas.saveState()
    canvas.drawImage(imagen_logo, 10*mm,
                     A4[1]-20*mm, width=30*mm, height=15*mm)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawString(40*mm, A4[1]-12*mm, linea1)
    canvas.drawString(40*mm, A4[1]-17*mm, linea2)
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(8*mm, 5*mm, "Generado el "+ fecha + " - "+area["abreviatura"])
    canvas.drawString(A4[0]-20*mm, 5*mm, "Página " + str(doc.page))
    canvas.restoreState()


def cabecera_horizontal_upsipteeo(canvas, doc):

    area = db.areas.find_one({"abreviatura":session["tipo"]})
    palabras = area["nombre"].split()
    mitad = len(palabras)//2
    linea1 = ' '.join(palabras[:mitad])
    linea2 = ' '.join(palabras[mitad:])
    
    canvas.saveState()
    canvas.drawImage(imagen_logo, 10*mm,
                     A4[0]-20*mm, width=30*mm, height=15*mm)
    canvas.setFont('Helvetica-Bold', 9)
    canvas.drawString(40*mm, A4[0]-12*mm, linea1)
    canvas.drawString(40*mm, A4[0]-17*mm, linea2)
    canvas.setFont("Times-Roman", 9)
    canvas.drawString(8*mm, 5*mm, "Generado el "+fecha + " - "+area["abreviatura"])
    canvas.drawString(A4[1]-20*mm, 5*mm, "Página " + str(doc.page))

    if doc.borrador:
        canvas.setFont("Helvetica", 40)
        canvas.setFillAlpha(0.3)
        canvas.setStrokeAlpha(0.3)
        canvas.rotate(90)
        canvas.drawString(65*mm, -A4[1]+10, "BORRADOR")
        canvas.drawString(65*mm, -13*mm, "BORRADOR")

    canvas.restoreState()


def construir(my_doc, buffer, elements, filename, cabecera):
    
    my_doc.build(elements, onFirstPage=cabecera,
                 onLaterPages=cabecera)

    pdf = buffer.getvalue()
    buffer.close()
    response = make_response(pdf)
    response.headers.set('Content-Type', 'application/pdf')
    response.headers.set('Content-Disposition', 'inline',
                         filename=filename)
    return response


def ver_usuarios():

    if val.validar_session(session):

        try:
            buffer = BytesIO()

            my_doc = SimpleDocTemplate(
                buffer, pagesize=A4, title="Reporte de usuarios")

            elements = []
            elements.append(titulo("Reporte de usuarios del sistema"))
            elements.append(table_usuarios())
    
            return construir(my_doc, buffer, elements, 'Reporte_Usuarios.pdf', cabecera_vertical_upsipteeo)
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR EL REPORTE DE USUARIOS - "'+str(e)+'"')
            abort(404)
    else:
        abort(403)


def ver_servidores():

    if val.validar_session(session):

        try:
            buffer = BytesIO()

            my_doc = SimpleDocTemplate(
                buffer, pagesize=(A4[1], A4[0]), title="Reporte de servidores")

            my_doc.borrador = False

            elements = []
            elements.append(titulo("Reporte de servidores"))
            elements.append(table_servidores())
            
            return construir(my_doc, buffer, elements, 'Reporte_Servidores.pdf', cabecera_horizontal_upsipteeo)
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR EL REPORTE DE SERVIDORES - "'+str(e)+'"')
            abort(404)
    else:
        abort(403)


def ver_inventario():

    if val.validar_session(session):

        try:

            id = request.args.get('custodio', None)
            categoria = request.args.get('categoria', None)
            marca = request.args.get('marca', None)
            modelo = request.args.get('modelo', None)
            estado = request.args.get('estado', None)

            buffer = BytesIO()

            nombres = ""
            cedula = ""

            if id is not None:
                custodio = db.servidores.find_one({"_id":ObjectId(id)},{"cedula": 1, "nombres": 1, "_id": 0})
                cedula = " - " + custodio["cedula"]
                nombres = " - " + custodio["nombres"]
                
            my_doc = SimpleDocTemplate(
                buffer, pagesize=(A4[1], A4[0]), title="Reporte de inventario " +cedula)

            my_doc.borrador = False
            
            elements = []
            
            elements.append(titulo("Reporte de inventario "+ nombres))
            elements.append(table_inventario(id,categoria,marca,modelo,estado))

            return construir(my_doc, buffer, elements, 'Reporte_Inventario.pdf' ,cabecera_horizontal_upsipteeo)
        except Exception as e:
            print(e)
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL VISUALIZAR EL REPORTE DE INVENTARIO - "'+str(e)+'"')
            abort(404)
    else:
        abort(403)

def ver_acta(id=None):

    if val.validar_session(session):

        try:
            buffer = BytesIO()

            my_doc = SimpleDocTemplate(
                buffer, pagesize=(A4[1], A4[0]), title="Acta de Entrega - Recepción")

            my_doc.borrador = True

            elements = []
            dir_act = "actas_"+session["tipo"]

            acta = db[dir_act].find_one({"_id":ObjectId(id)})

            if acta:
                
                fecha = acta["fecha_creacion"]

                if acta["estado"] == "Aprobado":
                    my_doc.borrador = False
                    fecha = acta["fecha_aprobacion"]
            
                elements.append(Paragraph("<b>Acta Nro. "+session["tipo"]+"-"+str(acta["numero"])+"</b>", style=ParagraphStyle(
                    'Num_acta', fontName="Times", alignment=2, fontSize=10, spaceAfter=5)))
                
                elements.append(Paragraph("<b>Machala, "+fecha.strftime("%d de %B de %Y - %H:%M:%S") +"</b>",
                                style=ParagraphStyle('Fecha', fontName="Times", alignment=2, fontSize=10, spaceAfter=5)))
                
                elements.append(titulo("Acta de Entrega - Recepción"))
            
                elements.append(Paragraph("En la Ciudad de Machala en las instalaciones de AvifaNet - El Oro "
                                      +", con fecha "+fecha.strftime("%d de %B de %Y")+", se procede a la suscripción del ACTA DE ENTREGA - RECEPCIÓN, entre "+acta["recibe"]["nombres"]
                                      +", "+acta["recibe"]["cargo"]["nombre"] +" de la "+ acta["recibe"]["area"]["nombre"] +", y por otra parte "+ acta["entrega"]["nombres"] 
                                      +", "+acta["entrega"]["cargo"]["nombre"] +" de la "+ acta["entrega"]["area"]["nombre"] +", entregando los siguientes activos y bienes de acuerdo al siguiente detalle:",
                    style=ParagraphStyle('Parrafo1', fontSize=10, fontName="Times", alignment=4, leading=15, spaceAfter=10)))

                elements.append(table_actas(acta))

                elements.append(Paragraph("''El daño, pérdida o destrucción del bien por negligencia comprobada "
                                        +"por su mal uso, no imputable al deterioro normal de las cosas, será responsabilidad del trabajador que lo tiene "
                                        +"a su cargo y de los trabajadores que de cualquier manera tienen acceso al bien''.",
                    style=ParagraphStyle('Parrafo2', fontSize=9, fontName="Times", alignment=4, leading=10, spaceAfter=14, spaceBefore=10)))

                elements.append(Paragraph("<b>Para constancia de lo actuado y en fé de conformidad y aceptación, se suscribe la presente acta en dos "
                                        +"ejemplares de igual tenor y efecto para las personas que intervienen en esta diligencia.</b>",
                    style=ParagraphStyle('Parrafo3', fontSize=9, fontName="Times", alignment=4, leading=10, spaceAfter=30, spaceBefore=10)))

                firmas = []
                firmas.append(["ENTREGA CONFORME", "RECIBE CONFORME","RESPONSABLE"])
                firmas.append([Paragraph("_"*35, style=ParagraphStyle('linea',alignment=1))] * 3)
                firmas.append([acta["entrega"]["nombres"], acta["recibe"]["nombres"], acta["veedor"]["nombres"]])
                firmas.append([acta["entrega"]["cargo"]["nombre"], acta["recibe"]["cargo"]["nombre"], acta["veedor"]["cargo"]["nombre"]])
                firmas.append([acta["entrega"]["area"]["abreviatura"], acta["recibe"]["area"]["abreviatura"], acta["veedor"]["area"]["abreviatura"]])

                elements.append(estilo_firmas(firmas))

                return construir(my_doc, buffer, elements,'Acta_Entrega_Recepcion_No_'+str(acta["numero"])+'.pdf',cabecera_horizontal_upsipteeo)
            else:
                abort(404)
        except Exception as e:
            hist.guardar_historial(
                "ERROR", "VISUALIZAR", 'ERROR AL APROBAR EL ACTA N° "'+str(acta["numero"])+'" CON ID "'+str(id)+'" - "'+str(e)+'"')
            abort(404)
    else:
        abort(403)
