from flask import Flask, request, render_template
from dotenv import load_dotenv
import controllers.indexCtl as ini
import controllers.loginCtl as logi
import controllers.historyCtl as hist
import controllers.modeloCtl as mod
import controllers.marcaCtl as mar
import controllers.categoriaCtl as cat
import controllers.inventarioCtl as inv
import controllers.modalidadCtl as moda
import controllers.areaCtl as area
import controllers.servidorCtl as serv
import controllers.cargoCtl as cargo
import controllers.usuarioCtl as user
import controllers.actaCtl as act
import controllers.reportesCtl as rpt
import controllers.carnetCtl as crnt

import os

load_dotenv()

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = os.getenv("KEY")
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# -----RUTAS---------------------------------------------

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

@app.route('/', methods=['GET'])
def index():
    return ini.inicio()

@app.route('/preguntas', methods=['GET'])
def preguntas():
    return ini.preguntas()

@app.route('/contrato', methods=['GET'])
def contrato():
    return ini.contrato()

@app.route('/del_foto', methods=['POST'])
def index_del_foto():
    return ini.del_foto(request)

# ----PRINCIPAL----

@app.route('/inventario', methods=['GET', 'POST'])
def inv_login():
    return logi.login(request)


@app.route('/inventario/principal', methods=['GET'])
def inv_principal():
    return logi.principal()


@app.route('/inventario/salir')
def inv_salir():
    return logi.cerrar_sesion()


# ----- USUARIOS ---------

@app.route('/inventario/save_usuarios', methods=['POST'])
def upsi_save_usuarios():
    return user.save_usuarios(request)


@app.route('/inventario/ver_usuarios', methods=['POST'])
def upsi_ver_usuarios():
    return user.ver_usuarios(request)


@app.route('/inventario/edit_usuario', methods=['POST'])
def upsi_edit_usuario():
    return user.edit_usuarios(request)


@app.route('/inventario/del_usuarios', methods=['POST'])
def upsi_del_usuarios():
    return user.del_usuarios(request)

# ---- TRABAJADORES ---

@app.route('/inventario/save_servidores', methods=['POST'])
def upsi_save_servidores():
    return serv.save_servidores(request)


@app.route('/inventario/ver_servidores', methods=['POST'])
def upsi_ver_servidores():
    return serv.ver_servidores(request)


@app.route('/inventario/edit_servidor', methods=['POST'])
def upsi_edit_servidor():
    return serv.edit_servidores(request)


@app.route('/inventario/del_servidores', methods=['POST'])
def upsi_del_servidores():
    return serv.del_servidores(request)

# ------CATEGORIAS------

@app.route('/inventario/save_categorias', methods=['POST'])
def inv_save_categorias():
    return cat.save_categorias(request)


@app.route('/inventario/ver_categorias', methods=['POST'])
def inv_ver_categorias():
    return cat.ver_categorias(request)


@app.route('/inventario/edit_categoria', methods=['POST'])
def inv_edit_categorias():
    return cat.edit_categorias(request)


@app.route('/inventario/del_categorias', methods=['POST'])
def inv_del_categorias():
    return cat.del_categorias(request)

# -----MARCAS-----

@app.route('/inventario/save_marcas', methods=['POST'])
def inv_save_marcas():
    return mar.save_marcas(request)


@app.route('/inventario/ver_marcas', methods=['POST'])
def inv_ver_marcas():
    return mar.ver_marcas(request)


@app.route('/inventario/edit_marca', methods=['POST'])
def inv_edit_marcas():
    return mar.edit_marcas(request)


@app.route('/inventario/del_marcas', methods=['POST'])
def inv_del_marcas():
    return mar.del_marcas(request)


# ------MODELOS------

@app.route('/inventario/save_modelos', methods=['POST'])
def inv_save_modelos():
    return mod.save_modelos(request)


@app.route('/inventario/ver_modelos', methods=['POST'])
def inv_ver_modelos():
    return mod.ver_modelos(request)


@app.route('/inventario/edit_modelo', methods=['POST'])
def inv_edit_modelos():
    return mod.edit_modelos(request)


@app.route('/inventario/del_modelos', methods=['POST'])
def inv_del_modelos():
    return mod.del_modelos(request)

# ----- MODALIDADES -----

@app.route('/inventario/save_modalidades', methods=['POST'])
def upsi_save_modalidades():
    return moda.save_modalidades(request)


@app.route('/inventario/ver_modalidades', methods=['POST'])
def upsi_ver_modalidades():
    return moda.ver_modalidades(request)


@app.route('/inventario/edit_modalidad', methods=['POST'])
def upsi_edit_modalidades():
    return moda.edit_modalidades(request)


@app.route('/inventario/del_modalidades', methods=['POST'])
def upsi_del_modalidades():
    return moda.del_modalidades(request)

# ----- AREAS -----

@app.route('/inventario/save_areas', methods=['POST'])
def upsi_save_areas():
    return area.save_areas(request)


@app.route('/inventario/ver_areas', methods=['POST'])
def upsi_ver_areas():
    return area.ver_areas(request)


@app.route('/inventario/edit_area', methods=['POST'])
def upsi_edit_areas():
    return area.edit_areas(request)


@app.route('/inventario/del_areas', methods=['POST'])
def upsi_del_areas():
    return area.del_areas(request)

# ----- CARGOS -----

@app.route('/inventario/save_cargos', methods=['POST'])
def upsi_save_cargos():
    return cargo.save_cargos(request)


@app.route('/inventario/ver_cargos', methods=['POST'])
def upsi_ver_cargos():
    return cargo.ver_cargos(request)


@app.route('/inventario/edit_cargo', methods=['POST'])
def upsi_edit_cargos():
    return cargo.edit_cargos(request)


@app.route('/inventario/del_cargos', methods=['POST'])
def upsi_del_cargos():
    return cargo.del_cargos(request)


# ----- INVENTARIO ------
@app.route('/inventario/save_inventario', methods=['POST'])
def inv_save_inventario():
    return inv.save_inventario(request)


@app.route('/inventario/ver_inventarios', methods=['POST'])
def inv_ver_inventarios():
    return inv.ver_inventarios(request)

@app.route('/inventario/buscar_inventarios', methods=['POST'])
def inv_buscar_inventarios():
    return inv.buscar_inventarios(request)

@app.route('/inventario/edit_inventario', methods=['POST'])
def inv_edit_inventarios():
    return inv.edit_inventarios(request)


@app.route('/inventario/del_inventarios', methods=['POST'])
def inv_del_inventarios():
    return inv.del_inventarios(request)


# ------- ACTAS ---------

@app.route('/inventario/save_actas', methods=['POST'])
def act_save_actas():
    return act.save_actas(request)


@app.route('/inventario/ver_actas', methods=['POST'])
def act_ver_actas():
    return act.ver_actas(request)

@app.route('/inventario/aprobar_actas', methods=['POST'])
def act_aprobar_actas():
    return act.aprobar_actas(request)

@app.route('/inventario/del_actas', methods=['POST'])
def act_del_actas():
    return act.del_actas(request)

# ----REPORTES UPSIPTEEO----

@app.route('/rpt/usuarios', methods=['GET'])
def rpt_ver_usuarios():
    return rpt.ver_usuarios()


@app.route('/rpt/servidores', methods=['GET'])
def rpt_ver_servidores():
    return rpt.ver_servidores()


@app.route('/rpt/inventario', methods=['GET'])
def rpt_ver_inventario():
    return rpt.ver_inventario()

@app.route('/rpt/acta/<id>', methods=['GET'])
def rpt_ver_acta(id):
    return rpt.ver_acta(id)

# ---CARNETS---
@app.route('/carnet/<id>', methods=['GET'])
def crnt_ver_carnet_servidor(id):
    return crnt.ver_carnet(id)

@app.route('/carnets', methods=['GET'])
def crnt_ver_carnet_servidores():
    return crnt.ver_carnet()

#--- HISTORIES --
@app.route('/inventario/ver_histories', methods=['POST'])
def hist_ver_histories():
    return hist.ver_history(request)

# -----ERRORES---------------

@app.errorhandler(500)
def handle_500(e):
    return render_template('/views/errors/500.html'), 500


@app.errorhandler(401)
def handle_401(e):
    return render_template('/views/errors/401.html'), 401

@app.errorhandler(404)
def handle_404(e):
    return render_template('/views/errors/404.html'), 404


@app.errorhandler(403)
def handle_403(e):
    return render_template('/views/errors/403.html'), 403

# -----------------------------


if __name__ == '__main__':
    app.run(host=os.getenv("HOST"), port=os.getenv("PORT"))