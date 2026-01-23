function message_error(obj){
    var html = '<ul style="text-align: left;">';
    $.each(obj, function (key, value){
        console.log(key)
        console.log(value)
        html += '<li>'+key+': '+value+'</li>'; 
    });
    html+='</lu>';
    Swal.fire({
        title:'Error',
        html: html,
        icon: 'error'
    });
}

function cargando(){
    Swal.fire({
        title: 'Procesando...',
        html: 'Por favor espera mientras procesamos sus datos.',
        allowOutsideClick: false, // Evitar que se cierre al hacer clic fuera
        showConfirmButton: false, // No mostrar botón de confirmación
        didOpen: () => {
            Swal.showLoading();
        }
    });
}

function copytoken(token, listUrl){
    Swal.fire({
        title: 'Token Generado',
        text: 'Tu token ha sido generado exitosamente. Puedes copiarlo a continuación.',
        input: 'text',
        inputValue: token,
        showCancelButton: true,
        confirmButtonText: 'Copiar al Portapapeles',
        cancelButtonText: 'Cerrar',
        didOpen: () => {
            const input = Swal.getInput();
            input.select(); // Selecciona el texto para que sea más fácil copiar
        },
        preConfirm: () => {
            const input = Swal.getInput();
            input.select();
            document.execCommand('copy');
            Swal.fire('Copiado!', 'El token ha sido copiado al portapapeles.', 'success').then(() => {
                // Redirecciona después de copiar
                window.location.href = listUrl;
            });
        }
    });
}