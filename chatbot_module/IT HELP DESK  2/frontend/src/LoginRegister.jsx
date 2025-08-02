import { useState } from "react";
import { useAuth } from "./AuthContext";
import { useNavigate } from "react-router-dom";
import "./index.css";
import botGif from "./assets/bot.gif";

function LoginRegister() {
  const [username, setUsername] = useState("");
  const navigate = useNavigate();

  
  const [error, setError] = useState("");

  const handleLogin = async () => {
    setError("");
    try {
      const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username }),
      });

      const data = await response.json();
      if (response.ok) {
        localStorage.setItem("token", data.token);
        navigate("/chat");
      } else {
        setError(data.error || "Login failed.");
      }
    } catch (err) {
      console.error("Login error:", err);
      setError("Network error or server not responding.");
    }
  };
  const handleKeyDown = (e) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

 
  return (
    <div className="login-page">
      <div className="login-container">
        <div className="bot-side">
          <img src={botGif} alt="Echo Bot" className="bot-image" />
        </div>

        <div className="form-side">
          <h2 className="brand-title">Echo AI</h2>
          <div className="login-form">

            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            
            <button onClick={handleLogin}>Login</button>
            {error && <p className="error-text">{error}</p>}
          </div>
        </div>
      </div>
    </div>
  );
}

export default LoginRegister;
