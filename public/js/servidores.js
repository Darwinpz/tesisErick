var data_serv

$(document).ready(function () {

    $('#v-pills-servidores-tab').on('shown.bs.tab', function () {
        if (!$.fn.DataTable.isDataTable('#table_servidores')) {

            var table = $('#table_servidores').DataTable({
                "ajax": {
                    "url": "/inventario/ver_servidores",
                    "method": "post",
                    "data": { s_validar: "" },
                },
                "columns": [
                    { "data": "_id" },
                    { "data": "cedula" },
                    { "data": "nombres" },
                    { "data": "area.abreviatura" },
                    { "data": "cargo.nombre" },
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
                        "defaultContent": '<a type="button" class="btn btn-primary btn-editar-servidores mb-1" ><i class="fas fa-edit"></i></a> <a type="button" class="btn btn-danger btn-eliminar-servidores mb-1"><i class="fas fa-trash"></i></a>',
                    }
                ],
                "pagingType": "full_numbers", //con esto salen los botones de primero anterior siguiente ultimo y los numeros de pagina
                "pageLength": 30, //para que se filtren por 30
                "language": {
                    "url": "/js/Spanish.json" //Para que salga en español
                },
                "lengthMenu": [30, 35, 40, 45, 50]
            });

            $("#btn-refresh-servidores").on('click', function () {

                table.clear().draw();
                table.ajax.reload();
            
            });

            $('#table_servidores tbody').on('click', '.btn-eliminar-servidores', function () {

                var data = table.row($(this).parents('tr')).data();

                const response = confirm('¿Estas seguro de eliminar el servidor: ' + data.nombres + '?');

                if (response) {

                    $.ajax({

                        url: '/inventario/del_servidores',
                        type: 'POST',
                        data: { cedula: data.cedula }

                    }).done(function () {

                        $('#table_servidores').DataTable().ajax.reload();

                    }).fail(function (e) {
                        alert("Error: " + e.responseJSON.message);
                    });

                }

            });


            $('#table_servidores tbody').on('click', '.btn-editar-servidores', function () {
                var data = table.row($(this).parents('tr')).data();

                $('#servidorModal').modal("show");

                let form = document.getElementById("form_servidor");

                document.getElementById("servidorModalLabel").innerHTML = "<b>Editar Servidor</b>"

                document.getElementById("save-servidor").style = "display:none"
                document.getElementById("edit-servidor").style = "display:visible"
                document.getElementById("carnet-servidor").style = "display:visible"
                document.getElementById("carnet-servidor").href = "/carnet/"+data._id

                document.getElementById("s_cedula").value = data.cedula
                document.getElementById("s_ciudadano").value = data.nombres
                document.getElementById("s_cmb_estado").value = data.estado
                document.getElementById("s_cmb_jefe").value = data.jefe
                document.getElementById("s_correo").value = data.correo

                if (data.url_foto != "") {

                    document.getElementById("img_servidor").src = "/servidores/" + data.url_foto

                    var btn_borrar = document.createElement("span")
                    btn_borrar.className = "btn btn-danger d-flex justify-content-center mt-2"
                    btn_borrar.innerText = "Eliminar Foto"
                    btn_borrar.id = "btn-borrar-foto-servidor"
                    document.getElementById("foto-servidor").appendChild(btn_borrar)

                    $('#btn-borrar-foto-servidor').on('click', function () {

                        const response = confirm('¿Estas seguro de eliminar la Imagen?');

                        if (response) {

                            $.ajax({

                                url: '/del_foto',
                                type: 'POST',
                                data: { id: data._id, tipo: "servidores" }

                            }).done(function () {

                                document.getElementById("img_servidor").src = "/img/perfil.jpg"
                                document.getElementById("btn-borrar-foto-servidor").remove()
                                data_serv.url_foto = ""

                            }).fail(function (e) {
                                alert("Error: " + e.responseJSON.message);
                            });

                        }

                    })

                } else {
                    document.getElementById("img_servidor").src = "/img/perfil.jpg"

                    if (document.getElementById("btn-borrar-foto-servidor") != undefined) {

                        document.getElementById("btn-borrar-foto-servidor").remove()

                    }

                }


                data_serv = data

                form.setAttribute("action", "/inventario/edit_servidor")


            });

        }
    })

});


$('#servidorModal').on('show.bs.modal', function (event) {


    let form = document.getElementById("form_servidor");
    let mensaje = document.getElementById("mensaje_servidor");
    let mensaje_buscador = document.getElementById("mensaje_serv_buscador");

    document.getElementById("img_servidor").src = "/img/perfil.jpg"

    document.getElementById("save-servidor").style = "display:visible"
    document.getElementById("edit-servidor").style = "display:none"
    document.getElementById("carnet-servidor").style = "display:none"
    document.getElementById("carnet-servidor").href = ""

    mensaje.innerText = ""
    mensaje_buscador.innerText = ""

    document.getElementById("servidorModalLabel").innerHTML = "<b>Agregar Servidor</b>"

    if (document.getElementById("btn-borrar-foto-servidor") != undefined) {

        document.getElementById("btn-borrar-foto-servidor").remove()

    }

    form.reset();

    $.ajax({

        url: '/inventario/ver_areas',
        type: 'POST',
        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(area => {

                output += '<option value=' + area._id + '>' + area.abreviatura + '</option>';

            });

            $("#s_cmb_area").html(output);

            if (data_serv) {

                document.getElementById("s_cmb_area").value = data_serv.area._id

            }

            output = "";

        }

    });

    $.ajax({

        url: '/inventario/ver_cargos',
        type: 'POST',
        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(cargo => {

                output += '<option value=' + cargo._id + '>' + cargo.nombre + '</option>';

            });

            $("#s_cmb_cargo").html(output);

            if (data_serv) {

                document.getElementById("s_cmb_cargo").value = data_serv.cargo._id

            }

            output = "";

        }

    });

    $.ajax({

        url: '/inventario/ver_modalidades',
        type: 'POST',
        success: function (response) {

            var output = '<option disabled selected value="">Selecciona</option>';

            response = JSON.parse(response)

            response.data.forEach(cargo => {

                output += '<option value=' + cargo._id + '>' + cargo.nombre + '</option>';

            });

            $("#s_cmb_modalidad").html(output);

            if (data_serv) {

                document.getElementById("s_cmb_modalidad").value = data_serv.modalidad._id

            }

            output = "";

        }

    });

    data_serv = null


    form.setAttribute("action", "/inventario/save_servidores")

});

$("#s_cedula").on("input", function (e) {

    cedula = $(this).val()

    let mensaje = document.getElementById("mensaje_serv_buscador");

    if (cedula != "" && cedula.length == 10) {

        if (validarCedulaEcuatoriana(cedula)) {

            mensaje.innerText = "Correcto";
            mensaje.style = "color:green;";

        }else{
            mensaje.innerText = "No válida";
            mensaje.style = "color:red;";
        }
        
    } else {

        mensaje.innerText = "Debe tener almenos 10 digitos";
        mensaje.style = "color:red;";

    }

})

function validarCedulaEcuatoriana(cedula) {
    // Eliminar espacios y caracteres no numéricos
    const cedulaLimpia = cedula.replace(/\D/g, '');
    
    // Verificar longitud (debe tener 10 dígitos)
    if (cedulaLimpia.length !== 10) {
        return false;
    }
    
    // Verificar que los primeros dos dígitos correspondan a una provincia válida (01-24)
    const provincia = parseInt(cedulaLimpia.substring(0, 2));
    if (provincia < 1 || provincia > 24) {
        return false;
    }
    
    // Verificar tercer dígito (debe ser menor a 6)
    const tercerDigito = parseInt(cedulaLimpia.charAt(2));
    if (tercerDigito > 5) {
        return false;
    }
    
    // Algoritmo de validación (módulo 10)
    const coeficientes = [2, 1, 2, 1, 2, 1, 2, 1, 2];
    const verificador = parseInt(cedulaLimpia.charAt(9));
    let suma = 0;
    
    for (let i = 0; i < 9; i++) {
        let valor = parseInt(cedulaLimpia.charAt(i)) * coeficientes[i];
        if (valor >= 10) {
            valor = valor - 9;
        }
        suma += valor;
    }
    
    const resultado = (suma % 10 === 0) ? 0 : 10 - (suma % 10);
    
    // El dígito verificador debe coincidir con el resultado
    return resultado === verificador;
}

$('#form_servidor').submit(function (e) {

    e.preventDefault();

    var form = $('#form_servidor')[0];

    let mensaje = document.getElementById("mensaje_servidor");

    mensaje.innerHTML = '<i class="fa fa-spinner fa-spin" style="color:gray"></i>'

    $.ajax({

        url: form.getAttribute("action"),
        type: 'POST',
        data: new FormData(form),
        enctype: 'multipart/form-data',
        processData: false,
        contentType: false,
        cache: false,

    }).done(function (e) {

        mensaje.innerText = e.message;
        mensaje.style = "color:green;";

        if (e.message != "Servidor Actualizado Correctamente") {

            form.reset();
            document.getElementById("img_servidor").src = "/img/perfil.jpg"
            $('#servidorModal').modal("hide");

        }

        $('#table_servidores').DataTable().ajax.reload();

    }).fail(function (e) {

        mensaje.innerText = e.responseJSON.message;
        mensaje.style = "color:red;";

    });

});
