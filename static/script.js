// script.js

document.addEventListener('DOMContentLoaded', () => {
    const chatbox = document.getElementById('chatbox');
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user_input');

    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const message = userInput.value.trim();
        if (message) {
            addMessage('user', message);
            fetchResponse(message);
            userInput.value = '';
        }
    });

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);

        const textSpan = document.createElement('div');
        textSpan.classList.add('text');
        textSpan.innerText = text;

        messageDiv.appendChild(textSpan);
        chatbox.appendChild(messageDiv);
        chatbox.scrollTop = chatbox.scrollHeight;
    }

    function fetchResponse(message) {
        fetch('/get_response', {
            method: 'POST',
            body: new URLSearchParams(`user_input=${encodeURIComponent(message)}`),
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
        })
        .then(response => response.json())
        .then(data => {
            addMessage('bot', data.bot_response);
        })
        .catch(error => {
            console.error('Error:', error);
            addMessage('bot', "Sorry, I couldn't process your request.");
        });
    }
});
