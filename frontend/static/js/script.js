const chatArea = document.getElementById('chat-area');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

// Event listener for send button
sendBtn.addEventListener('click', () => {
    const message = userInput.value.trim();
    if (message) {
        // Display user's message
        const userMessage = document.createElement('p');
        userMessage.className = 'user-message';
        userMessage.textContent = message;
        chatArea.appendChild(userMessage);

        // Display bot's response (demo)
        const botMessage = document.createElement('p');
        botMessage.className = 'bot-message';
        botMessage.textContent = "Thanks for your message. I'll get back to you shortly!";
        chatArea.appendChild(botMessage);

        // Scroll to the latest message
        chatArea.scrollTop = chatArea.scrollHeight;

        // Clear input field
        userInput.value = '';
    }
});

// Optional: Allow pressing "Enter" to send the message
userInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendBtn.click();
    }
});