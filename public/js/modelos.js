var data_mod

$(document).ready(function () {

    $('#v-pills-modelos-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_modelos')) {

            var table = $('#table_modelos').DataTable({
                "ajax": {
                    "url": "/inventario/ver_modelos",
                    "method": "post",
                    "data": { marca: "" },
                },
                "columns": [
                    { "data": "_id" },
                    { "data": "marca.nombre" },
                    { "data": "nombre" },
                    { "data": null }
                ],
                "columnDefs": [
                    {
                        target: 0,
                        visible: false,
                        searchable: false,
                    },
                    {
                        "targets": -1,
                        "data": null,
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-modelos mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-modelos mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 10, //para que se filtren por 5
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [10, 15, 20, 25]
            });

            $("#btn-refresh-modelos").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_modelos tbody').on('click', '.btn-eliminar-modelos', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el modelo: ' + data.nombre + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_modelos',
                        type: 'POST',
                        data: { id: data._id, nombre: data.nombre }

                    }).done(function () {

                        $('#table_modelos').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_modelos tbody').on('click', '.btn-editar-modelos', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#modeloModal').modal("show");

                let form = document.getElementById("form_modelo");

                document.getElementById("modeloModalLabel").innerHTML = "<b>Editar Modelo</b>"

                document.getElementById("save-modelo").style = "display:none"
                document.getElementById("edit-modelo").style = "display:visible"

                document.getElementById("mod_nombre").value = data.nombre

                document.getElementById("mod_codigo").value = data._id

                form.setAttribute("action", "/inventario/edit_modelo")

                data_mod = data

            });

        }
    })

});


$('#modeloModal').on('show.bs.modal', function (event) {


    let form = document.getElementById("form_modelo");
    let mensaje = document.getElementById("mensaje_modelo");

    mensaje.innerText = ""

    document.getElementById("modeloModalLabel").innerHTML = "<b>Agregar Modelo</b>"

    document.getElementById("save-modelo").style = "display:visible"
    document.getElementById("edit-modelo").style = "display:none"

    form.setAttribute("action", "/inventario/save_modelos")

    form.reset();

    $.ajax({

        url: '/inventario/ver_marcas',
        type: 'POST',
        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(marca => {

                output += '<option value=' + marca._id + '>' + marca.nombre + '</option>';

            });

            $("#mod_cmb_marca").html(output);

            if (data_mod) {

                document.getElementById("mod_cmb_marca").value = data_mod.marca._id

            }

            output = "";

        }

    });

    data_mod = null

});

$('#form_modelo').submit(function (e) {

    e.preventDefault();

    var form = $('#form_modelo')[0];

    let mensaje = document.getElementById("mensaje_modelo");

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

        if (e.message != "Modelo Actualizado Correctamente") {

            form.reset();
            $('#modeloModal').modal("hide");

        }

        $('#table_modelos').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });

});

