// Chatbot functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatToggle = document.getElementById('chat-toggle');
    const chatbox = document.getElementById('chatbox');
    const chatClose = document.getElementById('chat-close');
    const sendBtn = document.getElementById('send-btn');
    const userMessageInput = document.getElementById('user-message');
    const chatMessages = document.getElementById('chat-messages');

    // Toggle chat window
    function toggleChat() {
        chatbox.classList.toggle('active');
        if (chatbox.classList.contains('active')) {
            userMessageInput.focus();
            // Show welcome message if no messages exist
            if (chatMessages.children.length === 0) {
                showWelcomeMessage();
            }
        }
    }

    // Show welcome message
    function showWelcomeMessage() {
        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <h4>👋 Welcome to News Chat!</h4>
            <p>Ask me anything about our news or how to navigate the site.</p>
        `;
        chatMessages.appendChild(welcomeDiv);
    }

    // Close chat window
    function closeChat() {
        chatbox.classList.remove('active');
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        
        // Auto-scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Show typing indicator
    function showTypingIndicator() {
        const typingDiv = document.createElement('div');
        typingDiv.className = 'typing-indicator active';
        typingDiv.id = 'typing-indicator';
        typingDiv.innerHTML = `
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
            <span class="typing-dot"></span>
        `;
        chatMessages.appendChild(typingDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    // Hide typing indicator
    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    // Get CSRF token from cookie
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Send message to backend
    async function sendMessage() {
        const message = userMessageInput.value.trim();
        
        if (message === '') {
            return;
        }

        // Remove welcome message if exists
        const welcomeMsg = chatMessages.querySelector('.welcome-message');
        if (welcomeMsg) {
            welcomeMsg.remove();
        }

        // Add user message to chat
        addMessage(message, 'user');
        
        // Clear input and disable send button
        userMessageInput.value = '';
        sendBtn.disabled = true;
        
        // Show typing indicator
        showTypingIndicator();

        try {
            const response = await fetch('/api/chatbot/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ message: message })
            });

            const data = await response.json();
            
            // Hide typing indicator
            hideTypingIndicator();
            
            // Add bot response
            if (data.reply) {
                addMessage(data.reply, 'bot');
            } else {
                addMessage('Sorry, I could not process your request.', 'bot error');
            }
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessage('Sorry, there was an error connecting to the server. Please try again.', 'bot error');
        } finally {
            sendBtn.disabled = false;
            userMessageInput.focus();
        }
    }

    // Event listeners
    if (chatToggle) {
        chatToggle.addEventListener('click', toggleChat);
    }

    if (chatClose) {
        chatClose.addEventListener('click', closeChat);
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', sendMessage);
    }

    if (userMessageInput) {
        // Send message on Enter key
        userMessageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });

        // Enable/disable send button based on input
        userMessageInput.addEventListener('input', function() {
            sendBtn.disabled = this.value.trim() === '';
        });
    }

    // Close chat when clicking outside
    document.addEventListener('click', function(e) {
        if (chatbox.classList.contains('active') && 
            !chatbox.contains(e.target) && 
            !chatToggle.contains(e.target)) {
            closeChat();
        }
    });

    // Prevent chat from closing when clicking inside
    if (chatbox) {
        chatbox.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }
});