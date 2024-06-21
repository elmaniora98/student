document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Empêche le formulaire de se soumettre normalement

        const userInput = document.getElementById('user-input').value.trim(); // Récupère le message de l'utilisateur

        // Vérifie si le message de l'utilisateur n'est pas vide
        if (userInput !== '') {
            sendMessageToServer(userInput); // Envoie le message à la vue Django pour traitement
        }
    });

    function sendMessageToServer(message) {
        const csrfToken = getCSRFToken(); // Récupère le jeton CSRF pour l'envoyer avec la requête

        const requestData = {
            'message': message,
            'csrfmiddlewaretoken': csrfToken
        };

        fetch('/chatbot/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(requestData)
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur lors de la requête au serveur Django');
            }
            return response.json();
        })
        .then(data => {
            // Traitez la réponse du serveur Django ici
            console.log('Réponse du serveur Django :', data);
            displayMessage(data.response, false);
        })
        .catch(error => {
            console.error('Erreur:', error);
            displayMessage('Une erreur s\'est produite lors de la communication avec le serveur.', false);
        });
    }

    function displayMessage(message, isUser) {
        const chatBox = document.getElementById('chat-box');
        const messageElement = document.createElement('div');
        messageElement.classList.add('message', isUser ? 'user-message' : 'bot-message');
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight; // Fait défiler la zone de chat vers le bas
    }

    // Fonction pour récupérer le jeton CSRF à partir des cookies
    function getCSRFToken() {
        const cookieValue = document.cookie.match('(^|;)\\s*csrftoken\\s*=\\s*([^;]+)');
        return cookieValue ? cookieValue.pop() : '';
    }
});
