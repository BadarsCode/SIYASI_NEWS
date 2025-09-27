// Toggle Chat Window
document.getElementById("chat-toggle").addEventListener("click", () => {
  const chatbot = document.getElementById("chatbot");
  chatbot.style.display =
    chatbot.style.display === "flex" ? "none" : "flex";
});

// Send Message
document.getElementById("chat-send").addEventListener("click", async () => {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (!message) return;

  const chatBody = document.getElementById("chat-body");
  chatBody.innerHTML += `<div><b>You:</b> ${message}</div>`;
  input.value = "";

  try {
    const response = await fetch("/chatbot-api/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });

    const data = await response.json();
    chatBody.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
  } catch (error) {
    chatBody.innerHTML += `<div><b>Bot:</b> Sorry, I couldn’t connect.</div>`;
  }

  chatBody.scrollTop = chatBody.scrollHeight;
});

// Optional: Press Enter to Send
document.getElementById("chat-input").addEventListener("keypress", (e) => {
  if (e.key === "Enter") {
    document.getElementById("chat-send").click();
  }
});
