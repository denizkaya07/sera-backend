import React, { useState } from "react";

function Login({ setToken }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    const res = await fetch("http://127.0.0.1:8000/api/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ username, password }),
    });

    const data = await res.json();
    console.log(data);

    if (data.access) {
      setToken(data.access);
    } else {
      alert("Login hatalı");
    }
  };

  return (
    <div>
      <h2>Login</h2>
      <input placeholder="username" onChange={(e) => setUsername(e.target.value)} />
      <br />
      <input placeholder="password" type="password" onChange={(e) => setPassword(e.target.value)} />
      <br />
      <button onClick={handleLogin}>Giriş Yap</button>
    </div>
  );
}

export default Login;