async function sendMessage() {
    const input = document.getElementById("userInput");
    const message = input.value.trim();
    if (!message) return;

    const chatBox = document.getElementById("chatBox");

    // Show user message
    const userMsg = document.createElement("div");
    userMsg.className = "msg user";
    userMsg.innerText = message;
    chatBox.appendChild(userMsg);
    chatBox.scrollTop = chatBox.scrollHeight;
    input.value = "";

    try {
        const response = await fetch("http://localhost:5000/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: message })
        });

        const data = await response.json();

        const botMsg = document.createElement("div");
        botMsg.className = "msg bot";
        botMsg.innerText = data.response || "Sorry, I couldn't understand that.";
        chatBox.appendChild(botMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
    } catch (err) {
        const errorMsg = document.createElement("div");
        errorMsg.className = "msg bot";
        errorMsg.innerText = "Error contacting the bot. Make sure the backend is running.";
        chatBox.appendChild(errorMsg);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
}

// Show chat on button click
function showChat() {
    document.querySelector(".homepage").style.display = "none"; // Hide homepage
    document.getElementById("chatContainer").classList.remove("hidden"); // Show chat
}

// close chat
function closeChat() {
    document.getElementById("chatContainer").classList.add("hidden");
    document.querySelector(".homepage").style.display = "block";
}

