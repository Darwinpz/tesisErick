var data_inventario
var data_categorias

$(document).ready(function () {

    $('#v-pills-inventario-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_inventarios')) {

            var table = $('#table_inventarios').DataTable({
                "ajax": {
                    "url": "/inventario/ver_inventarios",
                    "method": "post"
                },
                "columns": [
                    { "data": "_id" },
                    {
                        "data": "codigo",
                        "render": function (d, t, r) {
                            return (r.codigo == "") ? "N/A" : r.codigo
                        }
                    },
                    {
                        "data": "serie",
                        "render": function (d, t, r) {
                            return (r.serie == "") ? "N/A" : r.serie
                        }
                    },
                    { "data": "categoria.nombre" },
                    { "data": "nombre" },
                    { "data": "marca.nombre", },
                    { "data": "modelo.nombre" },
                    { "data": "estado" },
                    { "data": "servidor.nombres" },
                    { "data": null }
                ],
                "createdRow": function (row, data, index) {
                    if (data.estado == "OPERATIVO") {
                        $(row).addClass("text-success fw-bold")
                    }
                    if (data.estado == "REGULAR") {
                        $(row).addClass("text-warning fw-bold")
                    }
                    if (data.estado == "BAJA") {
                        $(row).addClass("text-danger fw-bold")
                    }
                },
                "columnDefs": [
                    {
                        target: 0,
                        visible: false,
                        searchable: false,
                    },
                    {
                        "targets": -1,
                        "data": null,
                        "render": function (data, type, row) {
                            return `<a type="button" class="btn btn-primary btn-editar-inventarios mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-inventarios mb-1"><i class="fas fa-trash"></i></a>`
                        }
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 30, //para que se filtren por 30
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [30, 35, 40, 45, 50]
            });
            
            $("#btn-refresh-inventarios").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_inventarios tbody').on('click', '.btn-eliminar-inventarios', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el Inventario: ' + data.nombre + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_inventarios',
                        type: 'POST',
                        data: { id: data._id }

                    }).done(function () {

                        $('#table_inventarios').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_inventarios tbody').on('click', '.btn-editar-inventarios', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#inventarioModal').modal("show");

                let form = document.getElementById("form_inventario");

                document.getElementById("inventarioModalLabel").innerHTML = "<b>Editar Inventario</b>"

                document.getElementById("save-inventario").style = "display:none"
                document.getElementById("edit-inventario").style = "display:visible"

                document.getElementById("i_nombre").value = data.nombre
                document.getElementById("i_cmb_estado").value = data.estado
                document.getElementById("i_descripcion").value = data.descripcion
                document.getElementById("i_precio").value = data.precio
                document.getElementById("i_cmb_categoria").value = data.categoria

                document.getElementById("i_id").value = data._id

                document.getElementById("i_cta_contable").value = data.cta_contable
                document.getElementById("i_codigo").value = data.codigo
                document.getElementById("i_serie").value = data.serie
                //document.getElementById("i_cmb_marca").value = data.marca
                //document.getElementById("i_cmb_modelo").value = data.modelo
                document.getElementById("i_ip").value = data.ip
                document.getElementById("i_mac").value = data.mac

                document.getElementById("i_cmb_adquisicion").value = data.adquisicion

                clearopcciones();

                for (var i = 0; i < data.items.length; i++) {

                    crear_opciones(i, data.items[i])

                }

                if (data.url_foto != "") {

                    document.getElementById("img_inventario").src = "/inventarios/" + data.url_foto

                    var btn_borrar = document.createElement("span")
                    btn_borrar.className = "btn btn-danger d-flex justify-content-center mt-2"
                    btn_borrar.innerText = "Eliminar Foto"
                    btn_borrar.id = "btn-borrar-foto-inventario"
                    document.getElementById("foto-inventario").appendChild(btn_borrar)

                    $('#btn-borrar-foto-inventario').on('click', function () {

                        const response = confirm('¿Estas seguro de eliminar la Imagen?');

                        if (response) {

                            $.ajax({

                                url: '/del_foto',
                                type: 'POST',
                                data: { id: data._id, tipo: "inventarios" }

                            }).done(function () {

                                document.getElementById("img_inventario").src = "/img/caja.png"
                                document.getElementById("btn-borrar-foto-inventario").remove()
                                data_inventario.url_foto = ""

                            }).fail(function (e) {
                                alert("Error: " + e.responseJSON.message);
                            });

                        }

                    })

                } else {
                    document.getElementById("img_inventario").src = "/img/caja.png"

                    if (document.getElementById("btn-borrar-foto-inventario") != undefined) {

                        document.getElementById("btn-borrar-foto-inventario").remove()

                    }

                }

                data_inventario = data

                form.setAttribute("action", "/inventario/edit_inventario")

            });

        }
    })

});


$('#inventarioModal').on('show.bs.modal', function (event) {

    let form = document.getElementById("form_inventario");
    let mensaje = document.getElementById("mensaje_inventario");

    document.getElementById("img_inventario").src = "/img/caja.png"

    document.getElementById("save-inventario").style = "display:visible"
    document.getElementById("edit-inventario").style = "display:none"

    mensaje.innerText = ""

    document.getElementById("inventarioModalLabel").innerHTML = "<b>Agregar Inventario</b>"

    if (document.getElementById("btn-borrar-foto-inventario") != undefined) {

        document.getElementById("btn-borrar-foto-inventario").remove()

    }

    clearopcciones();
    nuevo();

    form.reset();

    form.setAttribute("action", "/inventario/save_inventario")

    $.ajax({

        url: '/inventario/ver_servidores',
        type: 'POST',
        data: { s_validar: "false" },

        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(servidor => {

                output += '<option value=' + servidor.cedula + '>' + servidor.nombres + '</option>';

            });

            $("#i_cmb_custodio").html(output);

            if (data_inventario) {

                document.getElementById("i_cmb_custodio").value = data_inventario.custodio

            }

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

            $("#i_cmb_categoria").html(output);

            if (data_inventario) {

                document.getElementById("i_cmb_categoria").value = data_inventario.categoria._id

                val_categorias(data_inventario.categoria.items)
            }

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

            $("#i_cmb_marca").html(output);

            if (data_inventario) {

                if (data_inventario.marca._id != null) {
                    document.getElementById("i_cmb_marca").value = data_inventario.marca._id
                    updateModelos(data_inventario.marca._id, data_inventario.modelo._id)
                }
            }

            output = "";

        }

    });

    data_inventario = null

});

function val_categorias(items) {

    if (items.codigo == "on") {
        document.getElementById("i_codigo").removeAttribute("readonly")
    } else {
        document.getElementById("i_codigo").setAttribute("readonly", "true")
    }

    if (items.serie == "on") {
        document.getElementById("i_serie").removeAttribute("readonly")
    } else {
        document.getElementById("i_serie").setAttribute("readonly", "true")
    }

    if (items.mod_marc == "on") {
        document.getElementById("i_cmb_modelo").disabled = false
        document.getElementById("i_cmb_marca").disabled = false
    } else {
        document.getElementById("i_cmb_modelo").disabled = true
        document.getElementById("i_cmb_marca").disabled = true
    }

    if (items.ip_mac == "on") {
        document.getElementById("i_ip").removeAttribute("readonly")
        document.getElementById("i_mac").removeAttribute("readonly")
    } else {
        document.getElementById("i_ip").setAttribute("readonly", "true")
        document.getElementById("i_mac").setAttribute("readonly", "true")
    }
}


function nuevo() {

    document.getElementById("i_cmb_modelo").disabled = true
    document.getElementById("i_cmb_marca").disabled = true
    document.getElementById("i_ip").setAttribute("readonly", "true")
    document.getElementById("i_mac").setAttribute("readonly", "true")
    document.getElementById("i_serie").setAttribute("readonly", "true")
    document.getElementById("i_codigo").setAttribute("readonly", "true")

}

$("#i_cmb_categoria").on("change", function (e) {

    var id_categoria = document.getElementById("i_cmb_categoria").value

    let categoria = data_categorias.find(o => o._id === id_categoria);

    val_categorias(categoria.items)


    document.getElementById("i_ip").value = ""
    document.getElementById("i_mac").value = ""
    document.getElementById("i_codigo").value = ""
    document.getElementById("i_serie").value = ""
    document.getElementById("i_cmb_marca").value = ""
    document.getElementById("i_cmb_modelo").value = ""
    var reset_modelo = '<option disabled selected value="">Selecciona</option>'
    $("#i_cmb_modelo").html(reset_modelo);
    document.getElementById("i_nombre").value = ""


});

$("#i_cmb_marca").on("change", function (e) {

    var marca = document.getElementById("i_cmb_marca").value
    updateModelos(marca, "");

})

function updateModelos(marca_prod, modelo_seleccionado) {

    var output = '<option disabled selected value="">Selecciona</option>';

    $("#i_cmb_modelo").html(output);

    $.ajax({

        url: '/inventario/ver_modelos',
        type: 'POST',
        data: { marca: marca_prod },
        success: function (response) {


            response = JSON.parse(response)

            response.data.forEach(modelo => {

                output += '<option value=' + modelo._id + '>' + modelo.nombre + '</option>';

            });

            $("#i_cmb_modelo").html(output);

            if (modelo_seleccionado != "") {

                document.getElementById("i_cmb_modelo").value = modelo_seleccionado

            }

            output = "";

        }

    });
}

$('#form_inventario').submit(function (e) {

    e.preventDefault();

    var form = $('#form_inventario')[0];

    let mensaje = document.getElementById("mensaje_inventario");

    mensaje.innerHTML = '<i class="fa fa-spinner fa-spin" style="color:gray"></i>'

    $.ajax({

        url: form.getAttribute("action"),
        type: 'POST',
        data: new FormData(form),
        processData: false,
        contentType: false,
        cache: false

    }).done(function (e) {

        mensaje.innerText = e.message;
        mensaje.style = "color:green;";

        if (e.message != "Inventario Actualizado Correctamente") {

            form.reset();
            document.getElementById("img_inventario").src = "/img/caja.png"
            $('#inventarioModal').modal("hide");

        }

        $('#table_inventarios').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });


});


function addopciones() {

    var count = document.getElementById("items").childElementCount

    count = count - 1;

    if (count <= 4) {

        crear_opciones(count, null)

    }

}

function clearopcciones() {

    document.querySelectorAll(".items").forEach(e => e.remove())

}

function crear_opciones(count, objeto) {

    var btn_eliminar = document.createElement("span")
    btn_eliminar.className = "btn btn-danger d-flex justify-content-center"
    btn_eliminar.innerHTML = "<i class='fas fa-trash'></i>"
    btn_eliminar.style = "border-radius:50%; position:absolute; height:25px; width:3px"
    btn_eliminar.setAttribute("onclick", "delopciones(" + count + ")");

    var row = document.createElement("div");
    row.className = "row mb-2 items"
    row.id = "prod_" + count

    var col_pieza = document.createElement("div");
    col_pieza.className = "col-lg-3 col-md-12 col-sm-12 mb-1 mt-1";

    var col_serie = document.createElement("div");
    col_serie.className = "col-lg-3 col-md-12 col-sm-12 mb-1 mt-1";

    var col_modelo = document.createElement("div");
    col_modelo.className = "col-lg-3 col-md-12 col-sm-12 mb-1 mt-1";

    var col_detalle = document.createElement("div");
    col_detalle.className = "col-lg-3 col-md-12 col-sm-12 mb-1 mt-1";

    var input_pieza = document.createElement("input");
    input_pieza.type = "text"
    input_pieza.placeholder = "Pieza Interna"
    input_pieza.className = "form-control"
    input_pieza.name = "pieza[]"
    input_pieza.required = true;
    input_pieza.value = (objeto != null) ? objeto.pieza : ""

    var input_serie = document.createElement("input");
    input_serie.type = "text"
    input_serie.placeholder = "Serie"
    input_serie.className = "form-control"
    input_serie.name = "serie[]"
    input_serie.required = true;
    input_serie.value = (objeto != null) ? objeto.serie : ""

    var input_modelo = document.createElement("input");
    input_modelo.type = "text"
    input_modelo.placeholder = "Modelo"
    input_modelo.className = "form-control"
    input_modelo.name = "modelo[]"
    input_modelo.required = true;
    input_modelo.value = (objeto != null) ? objeto.modelo : ""

    var input_detalle = document.createElement("input");
    input_detalle.type = "text"
    input_detalle.placeholder = "Detalle"
    input_detalle.className = "form-control"
    input_detalle.name = "detalle[]"
    input_detalle.required = true;
    input_detalle.value = (objeto != null) ? objeto.detalle : ""

    col_pieza.appendChild(input_pieza)
    col_serie.appendChild(input_serie)
    col_modelo.appendChild(input_modelo)
    col_detalle.appendChild(input_detalle)

    row.appendChild(btn_eliminar)
    row.appendChild(col_pieza)
    row.appendChild(col_serie)
    row.appendChild(col_modelo)
    row.appendChild(col_detalle)

    document.getElementById("items").appendChild(row)

}


function delopciones(id) {

    document.getElementById("prod_" + id).remove();

}