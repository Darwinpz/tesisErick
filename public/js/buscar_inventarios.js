var countCheck = 0
let inventarioSeleccionado = new Set();

function limpiarContador(){
    countCheck = 0
    document.getElementById("countEntrega").innerText = `Entregar (${countCheck})`   
}

function buscarInventario() {
    
    if (!$.fn.DataTable.isDataTable('#table_buscar_inventarios')) {

        var tableInventario = $('#table_buscar_inventarios').DataTable({
            "ajax": {
                "url": "/inventario/buscar_inventarios",
                "method": "post",
                "data": function (d) {d.custodio = $('#act_cmb_entrega').val()}
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
                        return `<input type="checkbox" value="${row._id}" class="btn-check-inventario" name="act_inventario[]" readonly>`;
                    }
                }
            ],
            "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
            "pageLength": 5, //para que se filtren por 30
            "language": {
                "url": "/js/Spanish.json" //Para que salga en español
            },
            "lengthMenu": [5, 10, 25, 50, 100]
        });

        $("#act_cmb_entrega").on("change", function (e) {
            tableInventario.ajax.reload(null, false);
            limpiarContador()
        })

        
        $('#actaModal').on('hidden.bs.modal', function (e) {
            tableInventario.clear().draw()
            limpiarContador()
        })

        $('#table_buscar_inventarios tbody').on('change', '.btn-check-inventario', function (e) {
            
            let isChecked = $(this).prop('checked');
            
            countCheck += isChecked ? 1 : -1;

            isChecked ? inventarioSeleccionado.add(e.target.value) : inventarioSeleccionado.delete(e.target.value);
        
            $(this).closest('tr').find('input[type="checkbox"]').prop('readonly', !isChecked);
            document.getElementById("countEntrega").innerText = `Entregar (${countCheck})`
            
        })


    }

}
