// Chatbot functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatToggle = document.getElementById('chat-toggle');
    const chatbox = document.getElementById('chatbox');
    const chatClose = document.getElementById('chat-close');
    const sendBtn = document.getElementById('send-btn');
    const userMessageInput = document.getElementById('user-message');
    const chatMessages = document.getElementById('chat-messages');
    const chatMode = document.body && document.body.dataset ? (document.body.dataset.chatMode || 'widget') : 'widget';

    const suggestions = [
        'Latest headlines',
        'Politics news',
        'Technology updates',
        'Search: economy',
        'How can I contact you?'
    ];

    function setExpanded(isOpen) {
        if (chatToggle) {
            chatToggle.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        }
    }

    function toggleChat(forceOpen = null) {
        if (!chatbox || chatMode === 'page') return;

        const shouldOpen = forceOpen === null ? !chatbox.classList.contains('active') : forceOpen;
        chatbox.classList.toggle('active', shouldOpen);
        setExpanded(shouldOpen);

        if (shouldOpen && userMessageInput) {
            userMessageInput.focus();
            if (chatMessages && chatMessages.children.length === 0) {
                showWelcomeMessage();
            }
        }
    }

    function showWelcomeMessage() {
        if (!chatMessages) return;

        const welcomeDiv = document.createElement('div');
        welcomeDiv.className = 'welcome-message';
        welcomeDiv.innerHTML = `
            <div class="welcome-title">Need a quick headline?</div>
            <div class="welcome-text">Ask me for the latest stories, browse a category, or search a topic.</div>
            <div class="welcome-chips">
                ${suggestions.map((suggestion) => `
                    <button class="chat-chip" data-prompt="${suggestion}">${suggestion}</button>
                `).join('')}
            </div>
        `;

        chatMessages.appendChild(welcomeDiv);
    }

    function closeChat() {
        if (!chatbox || chatMode === 'page') return;
        chatbox.classList.remove('active');
        setExpanded(false);
    }

    function appendLinks(messageDiv, links) {
        const linksWrap = document.createElement('div');
        linksWrap.className = 'chat-links';

        links.forEach((link) => {
            const anchor = document.createElement('a');
            anchor.className = 'chat-link';
            anchor.href = link.url || '#';
            anchor.setAttribute('aria-label', link.title || 'Article link');

            const title = document.createElement('span');
            title.className = 'chat-link-title';
            title.textContent = link.title || 'Read article';

            const meta = document.createElement('span');
            meta.className = 'chat-link-meta';
            const category = link.category ? link.category : 'News';
            const published = link.published ? link.published : '';
            meta.textContent = published ? `${category} - ${published}` : category;

            anchor.appendChild(title);
            anchor.appendChild(meta);
            linksWrap.appendChild(anchor);
        });

        messageDiv.appendChild(linksWrap);
    }

    function addMessage(text, sender, links = null) {
        if (!chatMessages) return;
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        messageDiv.textContent = text;

        if (sender.includes('bot') && Array.isArray(links) && links.length) {
            appendLinks(messageDiv, links);
        }

        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function showTypingIndicator() {
        if (!chatMessages) return;
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

    function hideTypingIndicator() {
        const typingIndicator = document.getElementById('typing-indicator');
        if (typingIndicator) {
            typingIndicator.remove();
        }
    }

    function removeWelcomeMessage() {
        const welcomeMsg = chatMessages ? chatMessages.querySelector('.welcome-message') : null;
        if (welcomeMsg) {
            welcomeMsg.remove();
        }
    }

    function hydrateHistory() {
        if (!chatMessages) return;
        const historyScript = document.getElementById('chat-history');
        if (!historyScript) return;
        try {
            const history = JSON.parse(historyScript.textContent);
            if (Array.isArray(history)) {
                history.forEach((item) => {
                    const role = item.role === 'user' ? 'user' : 'bot';
                    addMessage(item.content || '', role);
                });
            }
        } catch (err) {
            console.warn('Failed to load chat history', err);
        }
    }
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

    async function sendMessage(forcedMessage = null) {
        if (!userMessageInput) return;
        const message = (forcedMessage || userMessageInput.value).trim();

        if (message === '') {
            return;
        }

        removeWelcomeMessage();
        addMessage(message, 'user');

        userMessageInput.value = '';
        sendBtn.disabled = true;
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
            hideTypingIndicator();

            if (response.ok && data.reply) {
                addMessage(data.reply, 'bot', data.links);
            } else {
                addMessage('Sorry, I could not process your request.', 'bot error');
            }
        } catch (error) {
            console.error('Error:', error);
            hideTypingIndicator();
            addMessage('Sorry, there was an error connecting to the server. Please try again.', 'bot error');
        } finally {
            sendBtn.disabled = true;
            if (userMessageInput.value.trim() !== '') {
                sendBtn.disabled = false;
            }
            userMessageInput.focus();
        }
    }

    if (chatToggle) {
        chatToggle.addEventListener('click', function() {
            toggleChat();
        });
    }

    if (chatClose) {
        chatClose.addEventListener('click', closeChat);
    }

    if (sendBtn) {
        sendBtn.addEventListener('click', function() {
            sendMessage();
        });
    }

    if (userMessageInput) {
        userMessageInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                sendMessage();
            }
        });

        userMessageInput.addEventListener('input', function() {
            sendBtn.disabled = this.value.trim() === '';
        });
    }

    if (chatMessages) {
        chatMessages.addEventListener('click', function(e) {
            const chip = e.target.closest('.chat-chip');
            if (chip) {
                sendMessage(chip.dataset.prompt);
            }
        });
    }

    document.addEventListener('click', function(e) {
        if (!chatbox || !chatToggle) return;
        if (chatbox.classList.contains('active') && !chatbox.contains(e.target) && !chatToggle.contains(e.target)) {
            closeChat();
        }
    });

    if (chatbox) {
        chatbox.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    if (chatMode === 'page') {
        if (chatbox) {
            chatbox.classList.add('active');
        }
        if (chatToggle) {
            chatToggle.style.display = 'none';
        }
    }

    hydrateHistory();

    if (chatMode === 'page' && chatMessages && chatMessages.children.length === 0) {
        showWelcomeMessage();
    }

    setExpanded(chatMode === 'page');
});










