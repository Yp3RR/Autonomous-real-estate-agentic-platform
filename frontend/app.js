const API_URL = "http://localhost:8000";
const sessionId = crypto.randomUUID();

const messagesEl = document.getElementById("messages");
const inputEl = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(role, text) {
  const div = document.createElement("div");
  div.style.cssText = `
    padding: 10px 14px;
    border-radius: 6px;
    max-width: 80%;
    font-size: 0.92rem;
    line-height: 1.5;
    ${role === "user"
      ? "align-self: flex-end; background: #c9a84c; color: #1a1a1a;"
      : "align-self: flex-start; background: #2a2a2a; color: #f0ece0;"}
  `;
  div.innerHTML = marked.parse(text);
  messagesEl.appendChild(div);
  messagesEl.scrollTop = messagesEl.scrollHeight;
}

async function sendMessage() {
  const message = inputEl.value.trim();
  if (!message) return;

  addMessage("user", message);
  inputEl.value = "";

  try {
    const res = await fetch(`${API_URL}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ session_id: sessionId, message }),
    });
    const data = await res.json();
    addMessage("agent", data.response);
  } catch (err) {
    addMessage("agent", "Something went wrong. Is the backend running?");
  }
}

addMessage("agent", `
**Northstar One — 3 BHK Options**

We have two configurations:

- **3 BHK + 3T** — ₹1.75 Cr onwards
- **3 BHK + Servant Room** — ₹2.10 Cr onwards

### Payment Plan
- Booking: 10%
- On possession: 10%

Are you interested in self-use or investment?
`);

sendBtn.addEventListener("click", sendMessage);
inputEl.addEventListener("keydown", (e) => {
  if (e.key === "Enter") sendMessage();
});