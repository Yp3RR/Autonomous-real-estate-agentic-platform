const API_URL = "https://autonomous-real-estate-agentic-platform.onrender.com";
const sessionId = crypto.randomUUID();

const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Header scroll effect — transparent over hero, solid when scrolled
window.addEventListener("scroll", () => {
  document.getElementById("header").classList.toggle("scrolled", window.scrollY > 60);
});

function addMessage(role, text) {
  const div = document.createElement("div");
  div.className = role === "user" ? "msg-user" : "msg-agent";
  div.innerHTML = marked.parse(text);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function showTyping() {
  const el = document.createElement("div");
  el.className = "typing-indicator";
  el.id = "typing-indicator";
  el.innerHTML = "<span></span><span></span><span></span>";
  messagesEl.appendChild(el);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

function removeTyping() {
  const el = document.getElementById("typing-indicator");
  if (el) el.remove();
}

async function sendMessage() {
  const message = inputEl.value.trim();
  if (!message) return;

  addMessage("user", message);
  inputEl.value = "";
  sendBtn.disabled = true;
  showTyping();

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    const data = await res.json();
    removeTyping();
    addMessage("agent", data.response);
  } catch (err) {
    removeTyping();
    addMessage("agent", "Something went wrong. Please try again in a moment.");
  } finally {
    sendBtn.disabled = false;
    inputEl.focus();
  }
}

// Welcome message
addMessage(
  "agent",
  "Hi, I'm Dhruv — your personal advisor for Northstar One. " +
  "Whether you're looking to invest or find a home, I'm here to help. " +
  "What would you like to know?"
);

sendBtn.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) sendMessage();
});