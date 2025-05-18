// Script pour le widget flottant du chatbot
document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM pour le widget
    const chatbotFab = document.getElementById('chatbot-fab');
    const chatbotWidget = document.getElementById('chatbot-widget');
    const widgetMessages = document.getElementById('widget-messages');
    const widgetInput = document.getElementById('widget-input');
    const widgetSend = document.getElementById('widget-send');
    
    // Vérifier si tous les éléments existent
    if (chatbotFab && chatbotWidget && widgetMessages && widgetInput && widgetSend) {
        // Ouvrir/fermer le widget quand on clique sur le bouton flottant
        chatbotFab.addEventListener('click', function() {
            chatbotWidget.classList.toggle('active');
            
            // Si le widget est ouvert, mettre le focus sur le champ de saisie
            if (chatbotWidget.classList.contains('active')) {
                widgetInput.focus();
            }
        });
        
        // Fermer le widget quand on clique sur le bouton de fermeture
        const closeButton = document.querySelector('.widget-close');
        if (closeButton) {
            closeButton.addEventListener('click', function() {
                chatbotWidget.classList.remove('active');
            });
        }
        
        // Ajuster automatiquement la hauteur du textarea
        widgetInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight > 80 ? '80px' : this.scrollHeight + 'px');
        });
        
        // Envoyer un message quand l'utilisateur clique sur le bouton d'envoi
        widgetSend.addEventListener('click', function() {
            sendWidgetMessage();
        });
        
        // Envoyer un message quand l'utilisateur appuie sur Entrée (sans Shift)
        widgetInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendWidgetMessage();
            }
        });
        
        // Fonction pour envoyer un message via le widget
        function sendWidgetMessage() {
            const message = widgetInput.value.trim();
            if (message === '') return;
            
            // Ajouter le message de l'utilisateur à la conversation
            addWidgetMessage(message, 'user');
            
            // Vider le champ de saisie et réinitialiser sa hauteur
            widgetInput.value = '';
            widgetInput.style.height = 'auto';
            
            // Afficher l'indicateur de typing
            showWidgetTypingIndicator();
            
            // Envoyer la requête au serveur
            fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: message }),
            })
            .then(response => response.json())
            .then(data => {
                // Masquer l'indicateur de typing
                hideWidgetTypingIndicator();
                
                // Ajouter la réponse du chatbot à la conversation
                if (data.response) {
                    addWidgetMessage(data.response, 'bot');
                } else if (data.error) {
                    addWidgetMessage("Désolé, une erreur s'est produite. Veuillez réessayer.", 'bot');
                    console.error('Erreur:', data.error);
                }
            })
            .catch(error => {
                // Masquer l'indicateur de typing en cas d'erreur
                hideWidgetTypingIndicator();
                
                // Afficher un message d'erreur à l'utilisateur
                addWidgetMessage("Désolé, je ne peux pas répondre pour le moment. Veuillez réessayer plus tard.", 'bot');
                console.error('Erreur:', error);
            });
        }
        
        // Fonction pour ajouter un message à la conversation du widget
        function addWidgetMessage(content, sender) {
            // Créer les éléments HTML pour le message
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}`;
            
            const messageContent = document.createElement('div');
            messageContent.className = 'message-content';
            
            const messageText = document.createElement('p');
            // Si le message vient du bot, on peut avoir du HTML (comme des <br>)
            if (sender === 'bot') {
                messageText.innerHTML = content;
            } else {
                messageText.textContent = content;
            }
            
            messageContent.appendChild(messageText);
            
            const messageTime = document.createElement('div');
            messageTime.className = 'message-time';
            messageTime.textContent = formatTime(new Date());
            
            messageDiv.appendChild(messageContent);
            messageDiv.appendChild(messageTime);
            
            // Ajouter le message à la conversation
            widgetMessages.appendChild(messageDiv);
            
            // Faire défiler la conversation vers le bas
            widgetMessages.scrollTop = widgetMessages.scrollHeight;
        }
        
        // Fonction pour afficher l'indicateur de typing dans le widget
        function showWidgetTypingIndicator() {
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot typing-message';
            typingDiv.id = 'widget-typing-indicator';
            
            const typingContent = document.createElement('div');
            typingContent.className = 'typing-indicator';
            
            for (let i = 0; i < 3; i++) {
                const dot = document.createElement('span');
                typingContent.appendChild(dot);
            }
            
            typingDiv.appendChild(typingContent);
            widgetMessages.appendChild(typingDiv);
            
            // Faire défiler la conversation vers le bas
            widgetMessages.scrollTop = widgetMessages.scrollHeight;
        }
        
        // Fonction pour masquer l'indicateur de typing dans le widget
        function hideWidgetTypingIndicator() {
            const typingIndicator = document.getElementById('widget-typing-indicator');
            if (typingIndicator) {
                typingIndicator.remove();
            }
        }
        
        // Fonction pour formater l'heure
        function formatTime(date) {
            const hours = date.getHours().toString().padStart(2, '0');
            const minutes = date.getMinutes().toString().padStart(2, '0');
            return `${hours}:${minutes}`;
        }
    }
});