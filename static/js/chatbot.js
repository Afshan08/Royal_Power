
document.addEventListener('DOMContentLoaded', () => {
    const toggleBtn = document.getElementById('chat-toggle-btn');
    const closeBtn = document.getElementById('close-chat');
    const chatWindow = document.getElementById('chat-window');
    const chatInput = document.getElementById('chat-input');
    const sendBtn = document.getElementById('send-btn');
    const messagesContainer = document.getElementById('chat-messages');

    if (!toggleBtn || !chatWindow) return;

    // Toggle Chat visibility with animation classes
    function toggleChat() {
        if (chatWindow.classList.contains('hidden')) {
            chatWindow.classList.remove('hidden');
            // Small delay to allow display:block to apply before opacity transition
            setTimeout(() => {
                chatWindow.classList.remove('opacity-0', 'translate-y-4');
                chatWindow.classList.add('opacity-100', 'translate-y-0');
            }, 10);
        } else {
            chatWindow.classList.remove('opacity-100', 'translate-y-0');
            chatWindow.classList.add('opacity-0', 'translate-y-4');
            setTimeout(() => {
                chatWindow.classList.add('hidden');
            }, 300);
        }
    }

    toggleBtn.addEventListener('click', toggleChat);
    closeBtn.addEventListener('click', toggleChat);

    function addMessage(text, isUser = false) {
        const div = document.createElement('div');
        div.className = `flex items-start gap-2 max-w-[85%] ${isUser ? 'ml-auto flex-row-reverse' : ''}`;

        const avatar = isUser ?
            `<div class="w-6 h-6 rounded-full bg-royal-red flex-shrink-0 flex items-center justify-center mt-1 text-white text-xs"><i class="fa-solid fa-user"></i></div>` :
            `<div class="w-6 h-6 rounded-full bg-royal-black flex-shrink-0 flex items-center justify-center mt-1"><i class="fa-solid fa-robot text-[10px] text-royal-gold"></i></div>`;

        const bubbleStyle = isUser ?
            `bg-royal-red text-white rounded-2xl rounded-tr-none shadow-md` :
            `bg-white text-gray-700 rounded-2xl rounded-tl-none shadow-sm border border-gray-100`;

        div.innerHTML = `
            ${avatar}
            <div class="${bubbleStyle} p-3 text-sm">
                ${text}
            </div>
        `;

        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    function addTypingIndicator() {
        const id = 'typing-' + Date.now();
        const div = document.createElement('div');
        div.id = id;
        div.className = 'flex items-start gap-2 max-w-[85%]';
        div.innerHTML = `
            <div class="w-6 h-6 rounded-full bg-royal-black flex-shrink-0 flex items-center justify-center mt-1"><i class="fa-solid fa-robot text-[10px] text-royal-gold"></i></div>
            <div class="bg-white p-3 rounded-2xl rounded-tl-none shadow-sm border border-gray-100 flex gap-1">
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce"></span>
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.2s"></span>
                <span class="w-1.5 h-1.5 bg-gray-400 rounded-full animate-bounce" style="animation-delay: 0.4s"></span>
            </div>
        `;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
        return id;
    }

    function sendMessage() {
        const text = chatInput.value.trim();
        if (!text) return;

        addMessage(text, true);
        chatInput.value = '';

        const typingId = addTypingIndicator();

        fetch('/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: text })
        })
            .then(res => res.json())
            .then(data => {
                document.getElementById(typingId)?.remove();
                addMessage(data.response);
            })
            .catch(err => {
                document.getElementById(typingId)?.remove();
                addMessage("Sorry, I'm having trouble connecting to the server.");
                console.error(err);
            });
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
});
