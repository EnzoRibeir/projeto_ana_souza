function notificar(popup, titulo, mensagem, icone, caminho) {
    if (popup) {
        popupSwal.fire({ 
            title: `${titulo}`
            , text: `${mensagem}`
            , icon: `${icone}` 
        }).then(() => { 
            if (caminho) { window.location.href = `${caminho}`; }            
        }) 
    } else {
        toastSwal.fire({
            title: `${titulo}`
            , text: `${mensagem}`
            , icon: `${icone}` 
        });
    }
}

function visualizarSenha(id_campo) {
    var campo_senha = document.getElementById(id_campo);
    var botao_visualizar = document.querySelector('.olho-senha');

    if (campo_senha.type === 'password') {
        campo_senha.type = 'text';
        botao_visualizar.classList.replace('fa-eye-slash', 'fa-eye');
    } else {
        campo_senha.type = 'password';
        botao_visualizar.classList.replace('fa-eye', 'fa-eye-slash');
    }    
}

function impedirColagem(e) { // Impede que o usuário cole conteúdos em um determinado campo. EXEMPLO: Campo de confirmação de e-mail e senha.
    e.preventDefault();
    var clipboardData = e.clipboardData || window.clipboardData;
    clipboardData.setData('text', '');
}

/***** Máscaras para campos (pode ser usada em outras telas) *****/
function aplicarMascaraCPF(campo) {
    campo.value = campo.value.replace(/[^0-9.-]/g, ''); // Remove letras e mantém apenas números, ponto (.) e hífen (-).
    $(`#${campo.id}`).mask("000.000.000-00");
}

function aplicarMascaraRG(campo) {
    campo.value = campo.value.replace(/[^A-Z0-9.-]/g, ''); // Remove caracteres que não são letras maiúsculas nem números.
    $(`#${campo.id}`).mask("00.000.000-0");
}

function validarRG(rg) {
    rg = rg.replace(/[.-]/g, ''); // Remove os pontos (.) e o hífen (-).

    if (rg === "000000000") {
        return false;
    }

    if (rg.length < 8 || /^(.)\1+$/.test(rg)) { // Verifica se o RG tem menos de 8 dígitos (considerando RGs sem DV) e se não é uma sequência repetida qualquer.
        return false; 
    }

    return true;
}

function aplicarMascaraTelefone(campo) {
    $(`#${campo.id}`).mask("(00) 00000-0000");
}
/*****/

/***** Validações *****/
function validarCaracteresEspeciais(texto) {
    return /[`!@#$%^&*()_+\-=\[\]{};':"\\|,.<>\/?~]/.test(texto);
}

function validarComparacaoCampos(id_campo, id_campo_confirmacao, id_feedback, mensagem) {
    var campo = document.getElementById(id_campo);
    var campo_confirmacao = document.getElementById(id_campo_confirmacao);

    var div_feedback = document.getElementById(id_feedback);

    campo.value !== campo_confirmacao.value ? exibirFeedback(campo, div_feedback, mensagem) : limparFeedback(div_feedback);
}

function validarCriteriosSenha(id_campo, id_feedback) {
    var campo = document.getElementById(id_campo);
    var div_feedback = document.getElementById(id_feedback);

    !/^(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*()-_+=])[A-Za-z\d!@#$%^&*()-_+=]{10,}$/.test(campo.value) ? exibirFeedback(campo, div_feedback, 'Esta senha não atende aos critérios de segurança.') : limparFeedback(div_feedback);
}

function validarNome(id_campo, id_feedback) {
    var campo = document.getElementById(id_campo);
    var div_feedback = document.getElementById(id_feedback);

    if (campo.value.length < 2) {
        exibirFeedback(campo, div_feedback, 'Nome inválido. Informe-o corretamente.')
    } else if (validarCaracteresEspeciais(campo.value)) {
        exibirFeedback(campo, div_feedback, 'Não são permitidos caracteres especiais. Informe um nome válido.');
        campo.value = '';
    } else {
        limparFeedback(div_feedback);
    }    
}

function validarDataNascimento(id_campo, id_feedback) {
    var campo = document.getElementById(id_campo);
    var div_feedback = document.getElementById(id_feedback);

    var dtNasc = new Date(campo.value)
        , mesNasc = dtNasc.getMonth() + 1 // Dado que os meses aqui são índices, começando por 0, acrescentei +1
        , dtAtual = new Date()
        , mesAtual = dtAtual.getMonth() + 1
        , idade = dtAtual.getFullYear() - dtNasc.getFullYear();
    
    if (mesAtual < mesNasc || (mesAtual === mesNasc && dtAtual.getDate() < dtNasc.getDate())) { idade--; }

    idade < 18 ? exibirFeedback(campo, div_feedback, 'É necessário ser maior de idade para realizar o cadastro.') : limparFeedback(div_feedback);    
}

function validarCPF(id_campo, id_feedback) {
    var campo = document.getElementById(id_campo);
    var div_feedback = document.getElementById(id_feedback);

    var cpf = campo.value.replace(/[.-]/g, ''); // Remove os pontos (.) e o hífen (-), mantendo apenas números para realizar as operações de validação.

    if (cpf == "00000000000") {
        exibirFeedback(campo, div_feedback, 'Informe um CPF válido.');
        return;
    }

    if (cpf.length !== 11 || /^(.)\1+$/.test(cpf)) { // Verifica se o CPF tem 11 dígitos e se não é uma sequência repetida qualquer.
        exibirFeedback(campo, div_feedback, 'Informe um CPF válido.');
        return; 
    }
    
    var soma;
    var resto;
    soma = 0;

    for (i = 1; i <= 9; i++) {
        soma = soma + parseInt(cpf.substring(i - 1, i)) * (11 - i); 
    }

    resto = (soma * 10) % 11;
    if ((resto == 10) || (resto == 11)) { 
        resto = 0; 
    }
    if (resto != parseInt(cpf.substring(9, 10))) {
        exibirFeedback(campo, div_feedback, 'Informe um CPF válido.');
        return;
    }

    soma = 0;
    for (i = 1; i <= 10; i++) { 
        soma = soma + parseInt(cpf.substring(i - 1, i)) * (12 - i); 
    }

    resto = (soma * 10) % 11;
    if ((resto == 10) || (resto == 11)) {
        resto = 0;        
    }
    if (resto != parseInt(cpf.substring(10, 11) )) {
        exibirFeedback(campo, div_feedback, 'Informe um CPF válido.');
        return;
    }

    limparFeedback(div_feedback);
}

function validarEmail(id_campo, id_feedback) {
    var campo = document.getElementById(id_campo);
    var div_feedback = document.getElementById(id_feedback);

    !/^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?:\.[a-zA-Z]{2,})?$/.test(campo.value) ? exibirFeedback(campo, div_feedback, 'Informe um e-mail válido.') : limparFeedback(div_feedback);
}
/*****/

/***** Feedback *****/
function exibirFeedback(campo, div_feedback, mensagem) {
    div_feedback.style.display = 'block';
    div_feedback.innerHTML = `<strong>${mensagem}</strong>`;

    //campo.focus();
}

function limparFeedback(div_feedback) {
    div_feedback.innerHTML = '';
    div_feedback.style.display = 'none';
}

function verificarFeedbackInvalido(id_form) {
    var formulario = document.getElementById(id_form);
    var feedbacks = formulario.querySelectorAll(".invalid-feedback");
    
    for (let i = 0; i < feedbacks.length; i++) {
        if (feedbacks[i].textContent.trim() !== "") {
            return true;
        }
    }
    
    return false;
}

function confirmarFormulario(event, id_form, caminho_action) {
    event.preventDefault();

    if (verificarFeedbackInvalido(id_form)) {
        notificar(false, "Verifique as suas informações", "Um ou mais dados informados não são válidos.", "error", "");
        return;
    } else {
        var formulario = document.getElementById(id_form);
        formulario.action = caminho_action;
        formulario.submit();    
    }
}