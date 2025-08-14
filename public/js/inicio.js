
$(document).ready(function () {

    infoDashboard();

    $('#v-pills-inicio-tab').on('shown.bs.tab', function () {

        infoDashboard();

    })

})

// Calcular y mostrar porcentajes
function formatPercent(value, total) {
    return total > 0 ? ((value / total) * 100).toFixed(2) : '0.00';
}

function infoDashboard(){

    $.ajax({

        url: '/inventario/ver_info',
        type: 'POST',
        success: function (response) {

            response = JSON.parse(response)

            // 1. Obtener datos de la respuesta
            const data = response.data;
            const total = parseFloat(data.total) || 0;

            // 2. Actualizar valores absolutos
            document.getElementById("ini_total_inv").textContent = total.toLocaleString();
            document.getElementById("ini_operativo_inv").textContent = data.operativo.toLocaleString();
            document.getElementById("ini_regular_inv").textContent = data.regular.toLocaleString();
            document.getElementById("ini_baja_inv").textContent = data.baja.toLocaleString();

            document.getElementById("ini_porcentaje_inv_operativo").textContent = 
            `${formatPercent(data.operativo, total)}% del total`;

            document.getElementById("ini_porcentaje_inv_regular").textContent = 
            `${formatPercent(data.regular, total)}% del total`;

            document.getElementById("ini_porcentaje_inv_baja").textContent = 
            `${formatPercent(data.baja, total)}% del total`;

        }

    });

}