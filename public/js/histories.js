$(document).ready(function () {

    $('#v-pills-histories-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_histories')) {

            var table = $('#table_histories').DataTable({
                "ajax": {
                    "url": "/inventario/ver_histories",
                    "method": "post"
                },
                "ordering": false,
                "columns": [
                    { "data": "_id" },
                    { "data": "tipo" },
                    { "data": "mensaje" },
                    { "data": "cedula" },
                    { "data": "rol" },
                    { "data": "fecha_accion" },
                    { "data": null }
                ],
                "createdRow": function (row, data, index) {
                    if (data.tipo == "CORRECTO") {
                        $(row).addClass("text-success fw-bold")
                    } else {
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-ver-histories" ><i class="fas fa-eye"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 30, //para que se filtren por 30
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [30, 35, 40, 45, 50]
            });

            $('#table_histories tbody').on('click', '.btn-ver-histories', function () {
                var data = table.row($(this).parents('tr')).data();

                document.getElementById("hist_tipo").innerText = data.tipo
                document.getElementById("hist_accion").innerText = data.accion
                document.getElementById("hist_fecha").innerText = data.fecha_accion
                document.getElementById("hist_ip").innerText = data.ip
                document.getElementById("hist_cedula").innerText = data.cedula
                document.getElementById("hist_nombre").innerText = data.nombre
                document.getElementById("hist_mensaje").value = data.mensaje
                document.getElementById("hist_tipo_user").innerText = data.tipo_user
                document.getElementById("hist_rol").innerText = data.rol

                $('#historyModal').modal("show");

            });

            $("#btn-refresh-history").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

        }
    })

});
