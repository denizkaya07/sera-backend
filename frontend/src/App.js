import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate
} from "react-router-dom";
import "./App.css";

function App() {
  const [token, setToken] = useState("");

  useEffect(() => {
    const savedToken = localStorage.getItem("token");
    if (savedToken) setToken(savedToken);
  }, []);

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Auth setToken={setToken} />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute token={token}>
              <Dashboard setToken={setToken} />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  );
}

const ProtectedRoute = ({ token, children }) => {
  return token ? children : <Navigate to="/" />;
};

//////////////////////////////
// 🎨 AUTH UI (LOGIN + REGISTER)
//////////////////////////////
const Auth = ({ setToken }) => {
  const [isLogin, setIsLogin] = useState(true);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const login = async () => {
    const res = await fetch("http://127.0.0.1:8000/api/token/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (data.access) {
      localStorage.setItem("token", data.access);
      setToken(data.access);
      window.location.href = "/dashboard";
    } else {
      alert("Hatalı giriş ❌");
    }
  };

  const register = async () => {
    const res = await fetch("http://127.0.0.1:8000/api/users/register/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    const data = await res.json();

    if (data.error) {
      alert(data.error);
      return;
    }

    alert("Kayıt başarılı 🎉");
    await login();
  };

  return (
    <div className="container">
      <div className="card">
        <h2>{isLogin ? "Giriş Yap" : "Kayıt Ol"}</h2>

        <input
          placeholder="Kullanıcı adı"
          onChange={(e) => setUsername(e.target.value)}
        />

        <input
          placeholder="Şifre"
          type="password"
          onChange={(e) => setPassword(e.target.value)}
        />

        <button onClick={isLogin ? login : register}>
          {isLogin ? "Giriş Yap" : "Kayıt Ol"}
        </button>

        <p onClick={() => setIsLogin(!isLogin)} className="toggle">
          {isLogin
            ? "Hesabın yok mu? Kayıt ol"
            : "Zaten hesabın var mı? Giriş yap"}
        </p>
      </div>
    </div>
  );
};

//////////////////////////////
// 🔐 DASHBOARD
//////////////////////////////
const Dashboard = ({ setToken }) => {
  const [user, setUser] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("token");

    fetch("http://127.0.0.1:8000/api/users/profile/", {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
      .then(res => res.json())
      .then(data => setUser(data.user));
  }, []);

  const logout = () => {
    localStorage.removeItem("token");
    setToken("");
    window.location.href = "/";
  };

  return (
    <div className="container">
      <div className="card">
        <h1>Dashboard 🔐</h1>
        <h3>Hoşgeldin: {user}</h3>
        <button onClick={logout}>Çıkış Yap</button>
      </div>
    </div>
  );
};

export default App;