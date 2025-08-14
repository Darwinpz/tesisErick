
$(document).ready(function () {

    $('#v-pills-usuarios-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_usuarios')) {

            var table = $('#table_usuarios').DataTable({
                "ajax": {
                    "url": "/inventario/ver_usuarios",
                    "method": "post",
                },
                "columns": [
                    { "data": "_id" },
                    { "data": "servidor.cedula" },
                    { "data": "usuario" },
                    { "data": "servidor.nombres" },
                    { "data": "area.abreviatura" },
                    { "data": "rol" },
                    { "data": "estado" },
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-usuarios mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-usuarios mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 30, //para que se filtren por 30
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [30, 35, 40, 45, 50]
            });

            $("#btn-refresh-usuarios").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_usuarios tbody').on('click', '.btn-eliminar-usuarios', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el usuario: ' + data.servidor.nombres + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_usuarios',
                        type: 'POST',
                        data: { cedula: data.servidor.cedula }

                    }).done(function () {

                        $('#table_usuarios').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_usuarios tbody').on('click', '.btn-editar-usuarios', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#usuarioModal').modal("show");

                let form = document.getElementById("form_usuario");

                document.getElementById("usuarioModalLabel").innerHTML = "<b>Editar Usuario</b>"

                document.getElementById("save-usuario").style = "display:none"
                document.getElementById("edit-usuario").style = "display:visible"

                document.getElementById("u_nombre").value = data.usuario
                document.getElementById("u_estado").value = data.estado
                document.getElementById("u_rol").value = data.rol
                document.getElementById("u_clave").value = data.clave
                document.getElementById("u_rep_clave").value = data.clave

                var combo = document.getElementById("u_cmb_servidor")
                combo.setAttribute("disabled", "true");
                combo.style = "display:none"

                var servidor = document.getElementById("u_servidor")
                servidor.style = "display:visible"
                servidor.value = data.servidor.nombres

                document.getElementById("u_cedula").value = data.cedula

                form.setAttribute("action", "/inventario/edit_usuario")

            });

        }
    })

});



$('#usuarioModal').on('show.bs.modal', function (event) {

    let form = document.getElementById("form_usuario");
    let mensaje = document.getElementById("mensaje_usuario");

    mensaje.innerText = ""

    document.getElementById("usuarioModalLabel").innerHTML = "<b>Agregar Usuario</b>"

    document.getElementById("save-usuario").style = "display:visible"
    document.getElementById("edit-usuario").style = "display:none"

    var combo = document.getElementById("u_cmb_servidor")
    combo.removeAttribute("disabled");
    combo.style = "display:visible"

    var servidor = document.getElementById("u_servidor")
    servidor.style = "display:none"
    servidor.value = ""
    document.getElementById("u_cedula").value = ""

    form.reset();

    $.ajax({

        url: '/inventario/ver_servidores',
        type: 'POST',
        data: { s_validar: "true" },

        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(servidor => {

                output += '<option value=' + servidor.cedula + '>' + servidor.nombres + '</option>';

            });

            $("#u_cmb_servidor").html(output);

            output = "";

        }

    });

    form.setAttribute("action", "/inventario/save_usuarios")

});



$('#form_usuario').submit(function (e) {

    e.preventDefault();

    var form = $('#form_usuario')[0];

    let mensaje = document.getElementById("mensaje_usuario");

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

        if (e.message != "Usuario Actualizado Correctamente") {

            form.reset();
            $('#usuarioModal').modal("hide");

        }

        $('#table_usuarios').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });


});



$('.btn_ver_clave').click(function (e) {

    e.preventDefault();

    let $this = $(this);

    var padre = $this.prev('input');
    var hijo = $this[0].getElementsByTagName("i")[0];

    switch (padre.attr("type")) {

        case "text":

            padre.attr("type", "password");
            hijo.classList.add("fa-eye-slash");
            hijo.classList.remove("fa-eye")
            break

        case "password":
            padre.attr("type", "text");
            hijo.classList.add("fa-eye");
            hijo.classList.remove("fa-eye-slash")
            break;
    }

});