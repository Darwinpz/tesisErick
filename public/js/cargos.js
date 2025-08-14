$(document).ready(function () {

    $('#v-pills-cargos-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_cargos')) {

            var table = $('#table_cargos').DataTable({
                "ajax": {
                    "url": "/inventario/ver_cargos",
                    "method": "post"
                },
                "columns": [
                    { "data": "_id" },
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-cargos mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-cargos mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 10, //para que se filtren por 5
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [10, 15, 20, 25]
            });

            $("#btn-refresh-cargos").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_cargos tbody').on('click', '.btn-eliminar-cargos', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el cargo: ' + data.nombre + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_cargos',
                        type: 'POST',
                        data: { id: data._id, nombre: data.nombre }

                    }).done(function () {

                        $('#table_cargos').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_cargos tbody').on('click', '.btn-editar-cargos', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#cargoModal').modal("show");

                let form = document.getElementById("form_cargo");

                document.getElementById("cargoModalLabel").innerHTML = "<b>Editar Cargo</b>"

                document.getElementById("save-cargo").style = "display:none"
                document.getElementById("edit-cargo").style = "display:visible"

                document.getElementById("c_nombre").value = data.nombre

                document.getElementById("c_codigo").value = data._id

                form.setAttribute("action", "/inventario/edit_cargo")

            });

        }
    })

});


$('#cargoModal').on('show.bs.modal', function (event) {


    let form = document.getElementById("form_cargo");
    let mensaje = document.getElementById("mensaje_cargo");

    mensaje.innerText = ""

    document.getElementById("cargoModalLabel").innerHTML = "<b>Agregar Cargo</b>"

    document.getElementById("save-cargo").style = "display:visible"
    document.getElementById("edit-cargo").style = "display:none"

    form.setAttribute("action", "/inventario/save_cargos")

    form.reset();

});

$('#form_cargo').submit(function (e) {

    e.preventDefault();

    var form = $('#form_cargo')[0];

    let mensaje = document.getElementById("mensaje_cargo");

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

        if (e.message != "Cargo Actualizado Correctamente") {

            form.reset();
            $('#cargoModal').modal("hide");

        }

        $('#table_cargos').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });

});

