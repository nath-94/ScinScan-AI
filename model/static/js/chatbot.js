document.addEventListener('DOMContentLoaded', function() {
    // Éléments du DOM pour le chatbot principal (page dédiée)
    const chatbotMessages = document.getElementById('chatbot-messages');
    const userInput = document.getElementById('user-inputa');
    const sendButton = document.getElementById('send-button');
    
    // Éléments du DOM pour le widget flottant
    const chatbotFab = document.getElementById('chatbot-fab');
    const chatbotWidget = document.getElementById('chatbot-widget');
    const widgetClose = document.querySelector('.widget-close');
    const widgetMessages = document.getElementById('widget-messages');
    const widgetInput = document.getElementById('widget-input');
    const widgetSend = document.getElementById('widget-send');

    // ===== FONCTIONS COMMUNES =====
    
    // Formater l'heure actuelle (pour les messages)
    function formatTime(date) {
        const hours = date.getHours().toString().padStart(2, '0');
        const minutes = date.getMinutes().toString().padStart(2, '0');
        return `${hours}:${minutes}`;
    }
    
    // Fonction pour créer un indicateur de typing
    function createTypingIndicator(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return null;
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message bot typing-message';
        typingDiv.id = containerId + '-typing-indicator';
        
        const typingContent = document.createElement('div');
        typingContent.className = 'typing-indicator';
        
        for (let i = 0; i < 3; i++) {
            const dot = document.createElement('span');
            typingContent.appendChild(dot);
        }
        
        typingDiv.appendChild(typingContent);
        container.appendChild(typingDiv);
        
        // Faire défiler vers le bas
        container.scrollTop = container.scrollHeight;
        
        return typingDiv;
    }
    
    // Fonction pour supprimer l'indicateur de typing
    function removeTypingIndicator(containerId) {
        const typingIndicator = document.getElementById(containerId + '-typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }
    
    // Fonction pour envoyer un message au serveur et traiter la réponse
    function sendToServer(message, callback) {
        fetch('/api/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message }),
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Erreur réseau: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                callback(null, data.error);
            } else if (data.response) {
                callback(data.response, null);
            } else {
                callback(null, "Réponse du serveur invalide");
            }
        })
        .catch(error => {
            console.error('Erreur:', error);
            callback(null, "Une erreur est survenue. Veuillez réessayer.");
        });
    }
    
    // Fonction pour ajouter un message à un conteneur
    function addMessage(container, content, sender) {
        if (!container) return;
        
        // Créer les éléments du message
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
        
        // Ajouter le message au conteneur
        container.appendChild(messageDiv);
        
        // Faire défiler vers le bas
        container.scrollTop = container.scrollHeight;
    }
    
    // ===== GESTIONNAIRE DU WIDGET =====
    
    // Ouvrir/fermer le widget quand on clique sur le bouton flottant
    if (chatbotFab) {
        chatbotFab.addEventListener('click', function() {
            chatbotWidget.classList.toggle('active');
            
            // Si le widget est ouvert, mettre le focus sur le champ de saisie
            if (chatbotWidget.classList.contains('active')) {
                if (widgetInput) {
                    widgetInput.focus();
                }
            }
        });
    }
    
    // Fermer le widget quand on clique sur le bouton de fermeture
    if (widgetClose) {
        widgetClose.addEventListener('click', function() {
            chatbotWidget.classList.remove('active');
        });
    }
    
    // Ajuster automatiquement la hauteur du textarea du widget
    if (widgetInput) {
        widgetInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight > 100 ? '100px' : this.scrollHeight + 'px');
        });
        
        // Envoyer un message quand on appuie sur Entrée (sans Shift)
        widgetInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendWidgetMessage();
            }
        });
    }
    
    // Envoyer un message quand on clique sur le bouton d'envoi du widget
    if (widgetSend) {
        widgetSend.addEventListener('click', function() {
            sendWidgetMessage();
        });
    }
    
    // Fonction pour envoyer un message depuis le widget
    function sendWidgetMessage() {
        if (!widgetInput || !widgetMessages) return;
        
        const message = widgetInput.value.trim();
        if (message === '') return;
        
        // Ajouter le message de l'utilisateur au widget
        addMessage(widgetMessages, message, 'user');
        
        // Vider le champ de saisie et réinitialiser sa hauteur
        widgetInput.value = '';
        widgetInput.style.height = 'auto';
        
        // Afficher l'indicateur de typing
        createTypingIndicator('widget-messages');
        
        // Envoyer le message au serveur
        sendToServer(message, function(response, error) {
            // Supprimer l'indicateur de typing
            removeTypingIndicator('widget-messages');
            
            // Afficher la réponse ou l'erreur
            if (response) {
                addMessage(widgetMessages, response, 'bot');
            } else if (error) {
                addMessage(widgetMessages, "Désolé, une erreur s'est produite: " + error, 'bot');
            }
        });
    }
    
    // ===== GESTIONNAIRE DE LA PAGE CHATBOT =====
    
    // Configuration pour la page dédiée au chatbot
    if (userInput && sendButton && chatbotMessages) {
        // Ajuster automatiquement la hauteur du textarea
        userInput.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = (this.scrollHeight > 100 ? '100px' : this.scrollHeight + 'px');
        });
        
        // Envoyer un message quand l'utilisateur clique sur le bouton d'envoi
        sendButton.addEventListener('click', function() {
            sendPageMessage();
        });
        
        // Envoyer un message quand l'utilisateur appuie sur Entrée (sans Shift)
        userInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendPageMessage();
            }
        });
        
        // Fonction pour envoyer un message depuis la page
        function sendPageMessage() {
            const message = userInput.value.trim();
            if (message === '') return;
            
            // Ajouter le message de l'utilisateur à la conversation
            addMessage(chatbotMessages, message, 'user');
            
            // Vider le champ de saisie et réinitialiser sa hauteur
            userInput.value = '';
            userInput.style.height = 'auto';
            
            // Afficher l'indicateur de typing
            createTypingIndicator('chatbot-messages');
            
            // Envoyer le message au serveur
            sendToServer(message, function(response, error) {
                // Supprimer l'indicateur de typing
                removeTypingIndicator('chatbot-messages');
                
                // Afficher la réponse ou l'erreur
                if (response) {
                    addMessage(chatbotMessages, response, 'bot');
                } else if (error) {
                    addMessage(chatbotMessages, "Désolé, une erreur s'est produite: " + error, 'bot');
                }
            });
        }
        
        // Fonction pour envoyer une suggestion
        window.sendSuggestion = function(element) {
            if (element && element.textContent) {
                userInput.value = element.textContent;
                sendPageMessage();
            }
        };
    }
});