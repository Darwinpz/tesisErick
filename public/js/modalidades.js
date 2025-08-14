$(document).ready(function () {

    $('#v-pills-modalidades-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_modalidades')) {

            var table = $('#table_modalidades').DataTable({
                "ajax": {
                    "url": "/inventario/ver_modalidades",
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
                        searchable: true,
                    },
                    {
                        "targets": -1,
                        "data": null,
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-modalidades mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-modalidades mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 10, //para que se filtren por 5
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [10, 15, 20, 25]
            });

            $("#btn-refresh-modalidades").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_modalidades tbody').on('click', '.btn-eliminar-modalidades', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar la Modalidad: ' + data.nombre + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_modalidades',
                        type: 'POST',
                        data: { id: data._id, nombre: data.nombre }

                    }).done(function () {

                        $('#table_modalidades').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_modalidades tbody').on('click', '.btn-editar-modalidades', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#modalidadModal').modal("show");

                let form = document.getElementById("form_modalidad");

                document.getElementById("modalidadModalLabel").innerHTML = "<b>Editar Modalidad</b>"

                document.getElementById("save-modalidad").style = "display:none"
                document.getElementById("edit-modalidad").style = "display:visible"

                document.getElementById("m_nombre").value = data.nombre

                document.getElementById("m_codigo").value = data._id

                form.setAttribute("action", "/inventario/edit_modalidad")

            });
        }
    })

});


$('#modalidadModal').on('show.bs.modal', function (event) {


    let form = document.getElementById("form_modalidad");
    let mensaje = document.getElementById("mensaje_modalidad");

    mensaje.innerText = ""

    document.getElementById("modalidadModalLabel").innerHTML = "<b>Agregar Modalidad</b>"

    document.getElementById("save-modalidad").style = "display:visible"
    document.getElementById("edit-modalidad").style = "display:none"

    form.setAttribute("action", "/inventario/save_modalidades")

    form.reset();

});

$('#form_modalidad').submit(function (e) {

    e.preventDefault();

    var form = $('#form_modalidad')[0];

    let mensaje = document.getElementById("mensaje_modalidad");

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

        if (e.message != "Modalidad Actualizada Correctamente") {

            form.reset();
            $('#modalidadModal').modal("hide");

        }

        $('#table_modalidades').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });

});

