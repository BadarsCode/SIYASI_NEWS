const chatBtn = document.getElementById("chatbot-btn");
  const chatBox = document.getElementById("chatbot-box");
  const closeChat = document.getElementById("close-chat");
  const sendBtn = document.getElementById("send-btn");
  const messages = document.getElementById("chatbot-messages");

  chatBtn.onclick = () => chatBox.classList.toggle("hidden");
  closeChat.onclick = () => chatBox.classList.add("hidden");

  sendBtn.onclick = sendMessage;
  document.getElementById("chatbot-text").addEventListener("keypress", function(e) {
    if (e.key === "Enter") sendMessage();
  });

  function sendMessage() {
    const input = document.getElementById("chatbot-text");
    const msg = input.value.trim();
    if (!msg) return;

    // User message
    messages.innerHTML += `<div class='msg-user'>👤 ${msg}</div>`;
    input.value = "";

    // Send to Django backend
    fetch("/chatbot/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken")
      },
      body: JSON.stringify({message: msg})
    })
    .then(res => res.json())
    .then(data => {
      messages.innerHTML += `<div class='msg-bot'>🤖 ${data.reply}</div>`;
      messages.scrollTop = messages.scrollHeight;
    });
  }

  function getCookie(name) {
    let value = `; ${document.cookie}`;
    let parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(";").shift();
  }