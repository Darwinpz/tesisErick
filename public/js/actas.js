
$(document).ready(function () {

    $('#v-pills-actas-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_actas')) {

            var table = $('#table_actas').DataTable({
                "ajax": {
                    "url": "/inventario/ver_actas",
                    "method": "post"
                },
                "ordering": false,
                "columns": [
                    { "data": "_id" },
                    { "data": "numero" },
                    { "data": "estado" },
                    { "data": "entrega.nombres" },
                    { "data": "recibe.nombres" },
                    { "data": "fecha_acta" },
                    { "data": "fecha_aprobacion" },
                    {
                        "data": null,
                        render: function (data, type, row) {
                            var html_estado = (data["estado"] === "Pendiente") ? '<a type="button" class="btn btn-success btn-aprobar-actas mb-1"><i class="fas fa-check"></i></a>' : '';

                            return '<a type="button" target="_blank" href="/rpt/acta/' + data["_id"] + '" class="btn btn-primary btn-ver-actas mb-1" ><i class="fas fa-eye"></i></a> ' + html_estado + ' <a type="button" class="btn btn-danger btn-eliminar-actas mb-1"><i class="fas fa-trash"></i></a>';
                        },
                        "targets": -1
                    }
                ],
                "createdRow": function (row, data, index) {
                    if (data.estado == "Pendiente") {
                        $(row).addClass("text-warning fw-bold")
                    } else {
                        $(row).addClass("text-success fw-bold")
                    }

                },
                "columnDefs": [
                    {
                        target: 0,
                        visible: false,
                        searchable: false,
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 10, //para que se filtren por 5
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [10, 15, 20, 25]
            });

            $("#btn-refresh-actas").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_actas tbody').on('click', '.btn-eliminar-actas', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el acta N° ' + data.numero + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_actas',
                        type: 'POST',
                        data: { id: data._id, numero: data.numero }

                    }).done(function () {

                        $('#table_actas').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });

            $('#table_actas tbody').on('click', '.btn-aprobar-actas', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de aprobar el acta N° ' + data.numero + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/aprobar_actas',
                        type: 'POST',
                        data: { id: data._id, numero: data.numero }

                    }).done(function () {

                        $('#table_actas').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });
        }

    })

});


$('#actaModal').on('show.bs.modal', function (event) {


    let form = document.getElementById("form_acta");
    let mensaje = document.getElementById("mensaje_acta");

    mensaje.innerText = ""

    document.getElementById("actaModalLabel").innerHTML = "<b>Crear Acta</b>"

    document.getElementById("save-acta").style = "display:visible"
    document.getElementById("print-acta").style = "display:none"
    document.getElementById("print-acta").href = ""

    form.reset();

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

            $("#act_cmb_entrega").html(output);

            output = "";

        }

    });

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

            $("#act_cmb_recibe").html(output);

            output = "";

        }

    });

    $.ajax({

        url: '/inventario/ver_servidores',
        type: 'POST',
        data: { s_validar: "AFIVANET" },

        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(servidor => {

                output += '<option value=' + servidor.cedula + '>' + servidor.nombres + '</option>';

            });

            $("#act_cmb_veedor").html(output);

            output = "";

        }

    });

    buscarInventario()

    form.setAttribute("action", "/inventario/save_actas")

});


$('#form_acta').submit(function (e) {

    e.preventDefault();

    inventarioSeleccionado.forEach(id => {
        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "act_inventario[]";
        input.value = id;
        input.classList.add("inventario-hidden");
        this.appendChild(input);
    });

    var form = $('#form_acta')[0];

    let mensaje = document.getElementById("mensaje_acta");

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

        inventarioSeleccionado.clear();
        $('.inventario-hidden').remove();

        form.reset();
        $('#actaModal').modal("hide");

        $('#table_actas').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });


});