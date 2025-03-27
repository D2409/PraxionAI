document.addEventListener("DOMContentLoaded", () => {
    const sendButton = document.getElementById("send");
    const inputField = document.getElementById("user-input");
    const messagesContainer = document.querySelector(".chatbox-messages");

    sendButton.addEventListener("click", () => {
        const userMessage = inputField.value.trim();

        if (userMessage === "") return;

        // Add user's message to the chatbox
        addMessage(userMessage, "user");

        // Clear input field
        inputField.value = "";

        // Send message to backend
        fetch("/chatbot", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({ message: userMessage }),
        })
            .then((response) => {
                if (!response.ok) throw new Error("Network error");
                return response.json();
            })
            .then((data) => {
                addMessage(data.response, "bot");
            })
            .catch((error) => {
                console.error("Error:", error);
                addMessage("Sorry, something went wrong.", "bot");
            });
    });

    function addMessage(text, sender) {
        const messageElement = document.createElement("div");
        messageElement.classList.add(sender === "user" ? "user-message" : "bot-message");
        messageElement.textContent = text;
        messagesContainer.appendChild(messageElement);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
});
