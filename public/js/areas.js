$(document).ready(function () {

    $('#v-pills-areas-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_areas')) {
            
            var table = $('#table_areas').DataTable({
                "ajax": {
                    "url": "/inventario/ver_areas",
                    "method": "post"
                },
                "columns": [
                    { "data": "_id" },
                    { "data": "abreviatura" },
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-areas mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-areas mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 30, //para que se filtren por 30
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [30, 35, 40, 45, 50]
            });

            $("#btn-refresh-areas").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_areas tbody').on('click', '.btn-eliminar-areas', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el área: ' + data.abreviatura + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_areas',
                        type: 'POST',
                        data: { id: data._id, abreviatura: data.abreviatura }

                    }).done(function () {

                        $('#table_areas').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_areas tbody').on('click', '.btn-editar-areas', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#areaModal').modal("show");

                let form = document.getElementById("form_area");

                document.getElementById("areaModalLabel").innerHTML = "<b>Editar Area</b>"

                document.getElementById("save-area").style = "display:none"
                document.getElementById("edit-area").style = "display:visible"

                document.getElementById("a_abreviatura").value = data.abreviatura
                document.getElementById("a_nombre").innerText = data.nombre

                document.getElementById("a_codigo").value = data._id

                form.setAttribute("action", "/inventario/edit_area")

            });

        }
    })

});



$('#areaModal').on('show.bs.modal', function (event) {

    let form = document.getElementById("form_area");
    let mensaje = document.getElementById("mensaje_area");

    mensaje.innerText = ""

    document.getElementById("a_nombre").innerText = ""

    document.getElementById("areaModalLabel").innerHTML = "<b>Agregar Area</b>"

    document.getElementById("save-area").style = "display:visible"
    document.getElementById("edit-area").style = "display:none"

    form.setAttribute("action", "/inventario/save_areas")

    form.reset();

});


$('#form_area').submit(function (e) {

    e.preventDefault();

    var form = $('#form_area')[0];

    let mensaje = document.getElementById("mensaje_area");

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

        if (e.message != "Area Actualizada Correctamente") {

            form.reset();
            $('#areaModal').modal("hide");

        }

        $('#table_areas').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });


});
