document.addEventListener('DOMContentLoaded', () => {

    function atualizarQuantidade(id, quantidade) {
        fetch(`/update_cart/${id}/${quantidade}`, { method: 'POST' })
        .then(res => res.json())
        .then(data => {
            // Atualiza input com nova quantidade
            document.querySelector(`input[data-id="${id}"]`).value = quantidade;

            // Atualiza subtotal do item
            document.querySelector(`#subtotal-${id}`).textContent = "R$ " + data.subtotal.toFixed(2);

            // Atualiza total do carrinho
            document.querySelector("#subtotal-geral").textContent = "R$ " + data.subtotal.toFixed(2);
            document.querySelector("#total-geral").textContent = "R$ " + data.total.toFixed(2);
        });
    }

    // Botão +
    document.querySelectorAll('.quantity-right-plus').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const input = document.querySelector(`input[data-id="${id}"]`);
            let quantidade = parseInt(input.value);
            quantidade++;  // incrementa
            atualizarQuantidade(id, quantidade);
        });
    });

    // Botão -
    document.querySelectorAll('.quantity-left-minus').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const input = document.querySelector(`input[data-id="${id}"]`);
            let quantidade = parseInt(input.value);
            quantidade--;  // decrementa
            if (quantidade < 1) quantidade = 0;  // opcional: remove do carrinho
            atualizarQuantidade(id, quantidade);
        });
    });

});
