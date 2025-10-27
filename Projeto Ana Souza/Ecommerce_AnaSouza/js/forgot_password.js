function enviarCodigoRecuperacao(e) {
    e.preventDefault(); // impede o envio
    var txtEmail = document.getElementById('usuario_email').value;
    console.log(txtEmail); // mostra no console do navegador
    alert("Email enviado para: " + txtEmail); // mostra um alerta
}
