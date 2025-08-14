$(document).ready(function () {

    $('#v-pills-marcas-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_marcas')) {

            var table = $('#table_marcas').DataTable({
                "ajax": {
                    "url": "/inventario/ver_marcas",
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-marcas mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-marcas mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 10, //para que se filtren por 5
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [10, 15, 20, 25]
            });

            $("#btn-refresh-marcas").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_marcas tbody').on('click', '.btn-eliminar-marcas', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar la marca: ' + data.nombre + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_marcas',
                        type: 'POST',
                        data: { id: data._id, nombre: data.nombre }

                    }).done(function () {

                        $('#table_marcas').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_marcas tbody').on('click', '.btn-editar-marcas', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#marcaModal').modal("show");

                let form = document.getElementById("form_marca");

                document.getElementById("marcaModalLabel").innerHTML = "<b>Editar Marca</b>"

                document.getElementById("save-marca").style = "display:none"
                document.getElementById("edit-marca").style = "display:visible"

                document.getElementById("mar_nombre").value = data.nombre

                document.getElementById("mar_codigo").value = data._id

                form.setAttribute("action", "/inventario/edit_marca")

            });

        }
    })

});


$('#marcaModal').on('show.bs.modal', function (event) {


    let form = document.getElementById("form_marca");
    let mensaje = document.getElementById("mensaje_marca");

    mensaje.innerText = ""

    document.getElementById("marcaModalLabel").innerHTML = "<b>Agregar Marca</b>"

    document.getElementById("save-marca").style = "display:visible"
    document.getElementById("edit-marca").style = "display:none"

    form.setAttribute("action", "/inventario/save_marcas")

    form.reset();

});

$('#form_marca').submit(function (e) {

    e.preventDefault();

    var form = $('#form_marca')[0];

    let mensaje = document.getElementById("mensaje_marca");

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

        if (e.message != "Marca Actualizada Correctamente") {

            form.reset();
            $('#marcaModal').modal("hide");

        }

        $('#table_marcas').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });

});

