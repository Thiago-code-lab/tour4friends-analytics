// chat.js
document.addEventListener('DOMContentLoaded', function() {
    
    // 1. Cria o HTML do chat
    const chatHtml = `
        <div id="chat-bolha">💬</div>
        <div id="chat-janela">
            <div class="chat-header">
                <span>Tour4Friends Bot</span>
                <button id="chat-fecha">X</button>
            </div>
            <div class="chat-body" id="chat-body"> 
                <div class="msg bot">
                    <p>Olá! 👋<br>Posso ajudar com dúvidas sobre o Caminho de Santiago?</p>
                </div>
            </div>
            <div class="chat-footer">
                <input type="text" id="chat-input" placeholder="Digite sua dúvida...">
                <button id="chat-envia">➤</button>
            </div>
        </div>
    `;

    // 2. Adiciona o HTML ao body
    document.body.insertAdjacentHTML('beforeend', chatHtml);

    // 3. Pega as referências dos elementos
    const bolha = document.getElementById('chat-bolha');
    const janela = document.getElementById('chat-janela');
    const botaoFechar = document.getElementById('chat-fecha');
    const botaoEnviar = document.getElementById('chat-envia');
    const inputMsg = document.getElementById('chat-input');
    const chatBody = document.getElementById('chat-body');

    // 4. Funções de clique (Abrir/Fechar)
    function toggleChat() {
        janela.classList.toggle('aberto');
    }
    bolha.addEventListener('click', toggleChat);
    botaoFechar.addEventListener('click', toggleChat);


    async function enviarMensagem() {
        const pergunta = inputMsg.value.trim();
        if (!pergunta) return; 

        adicionarMensagem(pergunta, 'user');
        inputMsg.value = ""; 

        try {

        const response = await fetch('http://127.0.0.1:5000/perguntar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ pergunta: pergunta }) 
            });

            if (!response.ok) {
                throw new Error('Erro na resposta do servidor.');
            }

            const data = await response.json();
            const respostaBot = data.resposta;

            // 3. Adiciona a resposta do bot visualmente
            adicionarMensagem(respostaBot, 'bot');

        } catch (error) {
            console.error("Erro ao chamar a API:", error);
            adicionarMensagem("Desculpe, estou com problemas de conexão no momento.", 'bot');
        }
    }

    // Adiciona evento ao clicar no botão ENVIAR
    botaoEnviar.addEventListener('click', function(e) {
        e.preventDefault(); // Evita recarregar a página se estiver num form
        enviarMensagem();
    });

    // Adiciona evento ao apertar "Enter" no teclado
    inputMsg.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            enviarMensagem();
        }
    });

    function adicionarMensagem(texto, tipo) {
        const divMsg = document.createElement('div');
        divMsg.classList.add('msg', tipo);
        divMsg.innerHTML = `<p>${texto}</p>`;
        
        chatBody.appendChild(divMsg);
        

        chatBody.scrollTop = chatBody.scrollHeight;
    }
});