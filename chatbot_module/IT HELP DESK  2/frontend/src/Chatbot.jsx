import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "./AuthContext";
import "./index.css";

function Chatbot() {
  const authToken = localStorage.getItem("token");
  const navigate = useNavigate();

  const [userMessage, setUserMessage] = useState("");
  const [messages, setMessages] = useState([]);
  const [sessionId, setSessionId] = useState(() => crypto.randomUUID());
  const [typing, setTyping] = useState(false);
  const [quickReplies, setQuickReplies] = useState([
    "Regarding password",
    "Regarding tickets",
    "Contact IT Support",
    "Any other issue"
  ]);
  const [showSubReplies, setShowSubReplies] = useState([]);

  const handleLogout = () => {
    localStorage.removeItem("token");
    navigate("/");
  };

  useEffect(() => {
    if (authToken) {
      fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: "hi",
        }),
      })
        .then((res) => res.json())
        .then((data) => {
          setMessages([
            { role: "assistant", content: "Hi, how can I help you today?" },
            { role: "assistant", content: "Please choose an option below:" },
          ]);
        });
    }
  }, [authToken]);

  const handleQuickReply = (option) => {
    if (option === "Regarding password") {
      setShowSubReplies([
        "Reset Password",
        "Forgot your Password",
        "Change my password",
        "Password reset link expired",
        "Account locked after password attempts"
      ]);
    } else if (option === "Regarding tickets") {
      setShowSubReplies([
        "My ticket number",
        "My ticket status",
        "How long will it take to resolve my ticket?",
        "Raise a new ticket",
        "Reopen closed ticket",
        "Update my existing ticket"
      ]);
    } else if (option === "Contact IT Support") {
      setShowSubReplies(["Email: it-support@echobyte.com", "Phone: +1 (800) 555-1234"]);
    } else if (option === "Any other issue") {
      setShowSubReplies(["Please explain your issue."]);
    } else {
      sendMessage(option);
    }
  };

  const sendMessage = async (msg) => {
    if (!msg.trim()) return;

    const newMessages = [...messages, { role: "user", content: msg }];
    setMessages(newMessages);
    setUserMessage("");
    setTyping(true);

    try {
      const res = await fetch("http://127.0.0.1:5000/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${authToken}`,
        },
        body: JSON.stringify({
          session_id: sessionId,
          user_message: msg,
        }),
      });

      const data = await res.json();
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: data.response },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Error: Something went wrong." },
      ]);
    } finally {
      setTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      sendMessage(userMessage);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <button className="logout-button" onClick={handleLogout}>
          Logout
        </button>
      </div>

      <div className="messages">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message ${msg.role}`}>
            {msg.content}
          </div>
        ))}
        {typing && (
          <div className="message assistant">
            Typing...
          </div>
        )}
      </div>

      {showSubReplies.length > 0 && (
        <div className="quick-replies">
          {showSubReplies.map((opt, i) =>
            opt.startsWith("Email:") || opt.startsWith("Phone:") ? (
              <div key={i} className="info-text">{opt}</div>
            ) : (
              <button key={i} onClick={() => sendMessage(opt)}>
                {opt}
              </button>
            )
          )}
        </div>
      )}

      {quickReplies.length > 0 && (
        <div className="quick-replies">
          {quickReplies.map((option, i) => (
            <button key={i} onClick={() => handleQuickReply(option)}>
              {option}
            </button>
          ))}
        </div>
      )}

      <div className="input-container">
        <input
          type="text"
          placeholder="Type your message..."
          value={userMessage}
          onChange={(e) => setUserMessage(e.target.value)}
          onKeyDown={handleKeyDown}
        />
        <button onClick={() => sendMessage(userMessage)}>Send</button>
      </div>
    </div>
  );
}

export default Chatbot;
