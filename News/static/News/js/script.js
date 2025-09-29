const toggleBtn = document.getElementById("chat-toggle");
//const chatbox = document.getElementById("chatbox");
const sendBtn = document.getElementById("send-btn");
const userInput = document.getElementById("user-message");
const messagesDiv = document.getElementById("chat-messages");

  // Toggle chatbot visibility
  // toggleBtn.addEventListener("click", () => {
  //   chatbox.style.display = chatbox.style.display === "none" ? "flex" : "none";
  // });
function chat_window(){
  var chatbox = document.getElementById('chatbox');
  if (chatbox.style.display==="none"){
    chatbox.style.display='block';
  } else {
    chatbox.style.display='none';
  }
    
  }

  // Send message
  async function sendMessage() {
    const message = userInput.value.trim();
    if (!message) return;

    // Show user message
    messagesDiv.innerHTML += `<div><b>You:</b> ${message}</div>`;
    userInput.value = "";

    // Send to Django
    const response = await fetch("/chatbot/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": "{{ csrf_token }}",
      },
      body: JSON.stringify({ message }),
    });

    const data = await response.json();
    if (data.reply) {
      messagesDiv.innerHTML += `<div><b>Bot:</b> ${data.reply}</div>`;
    } else {
      messagesDiv.innerHTML += `<div><b>Bot:</b> Error!</div>`;
    }

    messagesDiv.scrollTop = messagesDiv.scrollHeight;
  }

  sendBtn.addEventListener("click", sendMessage);
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendMessage();
  });



// function myFunction() {
//   var x = document.getElementById("myDIV");
//   if (x.style.display === "none"){
//     x.style.display = "block";
//   } else  {
//     x.style.display= "none";
//   }
// }