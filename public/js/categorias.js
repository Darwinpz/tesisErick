$(document).ready(function () {

    $('#v-pills-categorias-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_categorias')) {

            var table = $('#table_categorias').DataTable({
                "ajax": {
                    "url": "/inventario/ver_categorias",
                    "method": "post"
                },
                "columns": [
                    { "data": "_id" },
                    { "data": "nombre" },
                    { "data": "items.codigo" },
                    { "data": "items.serie" },
                    { "data": "items.mod_marc" },
                    { "data": "items.ip_mac" },
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-categorias mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-categorias mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 10, //para que se filtren por 5
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [10, 15, 20, 25]
            });

            $("#btn-refresh-categorias").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_categorias tbody').on('click', '.btn-eliminar-categorias', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar la Categoria: ' + data.nombre + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_categorias',
                        type: 'POST',
                        data: { id: data._id, nombre: data.nombre }

                    }).done(function () {

                        $('#table_categorias').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_categorias tbody').on('click', '.btn-editar-categorias', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#categoriaModal').modal("show");

                let form = document.getElementById("form_categoria");

                document.getElementById("categoriaModalLabel").innerHTML = "<b>Editar Categoria</b>"

                document.getElementById("save-categoria").style = "display:none"
                document.getElementById("edit-categoria").style = "display:visible"

                document.getElementById("cat_nombre").value = data.nombre

                if (data.items.codigo == "on") {
                    document.getElementById("cat_cod").setAttribute("checked", "true")
                } else {
                    document.getElementById("cat_cod").removeAttribute("checked")
                }

                if (data.items.serie == "on") {
                    document.getElementById("cat_serie").setAttribute("checked", "true")
                } else {
                    document.getElementById("cat_serie").removeAttribute("checked")
                }

                if (data.items.mod_marc == "on") {
                    document.getElementById("cat_mod_marc").setAttribute("checked", "true")
                } else {
                    document.getElementById("cat_mod_marc").removeAttribute("checked")
                }

                if (data.items.ip_mac == "on") {
                    document.getElementById("cat_ip_mac").setAttribute("checked", "true")
                } else {
                    document.getElementById("cat_ip_mac").removeAttribute("checked")
                }

                document.getElementById("cat_codigo").value = data._id

                form.setAttribute("action", "/inventario/edit_categoria")

            });

        }
    })

});


$('#categoriaModal').on('show.bs.modal', function (event) {

    let form = document.getElementById("form_categoria");
    let mensaje = document.getElementById("mensaje_categoria");

    mensaje.innerText = ""

    document.getElementById("categoriaModalLabel").innerHTML = "<b>Agregar Categoria</b>"

    document.getElementById("save-categoria").style = "display:visible"
    document.getElementById("edit-categoria").style = "display:none"


    document.getElementById("cat_cod").removeAttribute("checked")
    document.getElementById("cat_serie").removeAttribute("checked")
    document.getElementById("cat_mod_marc").removeAttribute("checked")
    document.getElementById("cat_ip_mac").removeAttribute("checked")

    form.setAttribute("action", "/inventario/save_categorias")

    form.reset();

});


$('#form_categoria').submit(function (e) {

    e.preventDefault();

    var form = $('#form_categoria')[0];

    let mensaje = document.getElementById("mensaje_categoria");

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

        if (e.message != "Categoria Actualizada Correctamente") {

            form.reset();
            $('#categoriaModal').modal("hide");

        }

        $('#table_categorias').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });


});
