
$('#reportesModal').on('show.bs.modal', function (event) {

    let form = document.getElementById("form_reportes");
    form.reset();

    $.ajax({

        url: '/inventario/ver_servidores',
        type: 'POST',
        data: { s_validar: "false" },

        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(servidor => {

                output += '<option value=' + servidor._id + '>' + servidor.nombres + '</option>';

            });

            $("#rpt_cmb_custodio").html(output);

            output = "";

        }

    });


    $.ajax({

        url: '/inventario/ver_categorias',
        type: 'POST',
        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(categoria => {

                output += '<option value=' + categoria._id + '>' + categoria.nombre + '</option>';

            });

            data_categorias = response.data

            $("#rpt_cmb_categoria").html(output);

            output = "";

        }

    });


    $.ajax({

        url: '/inventario/ver_marcas',
        type: 'POST',
        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(marca => {

                output += '<option value=' + marca._id + '>' + marca.nombre + '</option>';

            });

            $("#rpt_cmb_marca").html(output);

            output = "";

        }

    });

});

$('#form_reportes').submit(function (e) {

    e.preventDefault();

    var custodio = document.getElementById("rpt_cmb_custodio").value
    var categoria = document.getElementById("rpt_cmb_categoria").value
    var marca = document.getElementById("rpt_cmb_marca").value
    var modelo = document.getElementById("rpt_cmb_modelo").value
    var estado = document.getElementById("rpt_cmb_estado").value

    var parametros = [];

    // Agregar los parámetros solo si tienen un valor válido
    if (custodio) {
        parametros.push("custodio=" + encodeURIComponent(custodio));
    }
    if (categoria) {
        parametros.push("categoria=" + encodeURIComponent(categoria));
    }
    if (marca) {
        parametros.push("marca=" + encodeURIComponent(marca));
    }
    if (modelo) {
        parametros.push("modelo=" + encodeURIComponent(modelo));
    }
    if (estado) {
        parametros.push("estado=" + encodeURIComponent(estado));
    }

    var url = "/rpt/inventario?" + parametros.join("&");

    window.open(url, "_blank");

});

$("#rpt_cmb_marca").on("change", function (e) {

    var marca = document.getElementById("rpt_cmb_marca").value
    updateModelos_rpt(marca);

})

function updateModelos_rpt(marca_prod) {

    var output = '<option disabled selected value="">Selecciona</option>';

    $("#rpt_cmb_modelo").html(output);

    $.ajax({

        url: '/inventario/ver_modelos',
        type: 'POST',
        data: { marca: marca_prod },
        success: function (response) {


            response = JSON.parse(response)

            response.data.forEach(modelo => {

                output += '<option value=' + modelo._id + '>' + modelo.nombre + '</option>';

            });

            $("#rpt_cmb_modelo").html(output);

            output = "";

        }

    });
}