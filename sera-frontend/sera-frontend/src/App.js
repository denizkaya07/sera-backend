import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./App.css";

const API = "http://127.0.0.1:8000";

// ─── Token Yönetimi (sessionStorage — XSS'e karşı localStorage'dan daha güvenli) ───
const getToken = () => sessionStorage.getItem("token");
const saveToken = (t) => sessionStorage.setItem("token", t);
const clearToken = () => sessionStorage.removeItem("token");

// ─── Korumalı Rota (Protected Route) ───────────────────────────────────────────────
const ProtectedRoute = ({ children }) => {
  return getToken() ? children : <Navigate to="/" replace />;
};

// ─── Ana App ────────────────────────────────────────────────────────────────────────
function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Auth />} />
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

// ─── Auth (Login + Register) ────────────────────────────────────────────────────────
const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    if (getToken()) navigate("/dashboard", { replace: true });
  }, [navigate]);

  const doLogin = async (u, p) => {
    const res = await fetch(`${API}/api/token/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: u, password: p }),
    });
    const data = await res.json();
    if (data.access) {
      saveToken(data.access);
      navigate("/dashboard", { replace: true });
      return true;
    }
    return false;
  };

  const handleLogin = async () => {
    setError("");
    setLoading(true);
    try {
      const ok = await doLogin(username, password);
      if (!ok) setError("Kullanıcı adı veya şifre hatalı.");
    } catch {
      setError("Sunucuya bağlanılamadı.");
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    setError("");
    setLoading(true);
    try {
      const res = await fetch(`${API}/api/users/register/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      const data = await res.json();
      if (data.error) { setError(data.error); return; }
      // Kayıt başarılı → otomatik giriş
      const ok = await doLogin(username, password);
      if (!ok) setError("Kayıt başarılı fakat giriş yapılamadı.");
    } catch {
      setError("Sunucuya bağlanılamadı.");
    } finally {
      setLoading(false);
    }
  };

  const handleKey = (e) => {
    if (e.key === "Enter") isLogin ? handleLogin() : handleRegister();
  };

  return (
    <div className="container">
      <div className="card">
        <h2>{isLogin ? "Giriş Yap" : "Kayıt Ol"}</h2>

        <input
          placeholder="Kullanıcı adı"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          onKeyDown={handleKey}
          autoComplete="username"
        />
        <input
          placeholder="Şifre"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={handleKey}
          autoComplete={isLogin ? "current-password" : "new-password"}
        />

        {error && <p className="error">{error}</p>}

        <button
          onClick={isLogin ? handleLogin : handleRegister}
          disabled={loading || !username || !password}
        >
          {loading ? "Yükleniyor..." : isLogin ? "Giriş Yap" : "Kayıt Ol"}
        </button>

        <p
          className="toggle"
          onClick={() => { setIsLogin(!isLogin); setError(""); }}
        >
          {isLogin ? "Hesabın yok mu? Kayıt ol" : "Zaten hesabın var mı? Giriş yap"}
        </p>
      </div>
    </div>
  );
};

// ─── Dashboard ──────────────────────────────────────────────────────────────────────
const Dashboard = () => {
  const [user, setUser] = useState("");
  const [prescriptions, setPrescriptions] = useState([]);
  const [loadingData, setLoadingData] = useState(true);
  const [fetchError, setFetchError] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    const token = getToken();

    const fetchProfile = fetch(`${API}/api/users/profile/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((res) => {
      if (res.status === 401) { handleLogout(); return; }
      return res.json();
    }).then((data) => {
      if (data?.user) setUser(data.user);
    });

    const fetchPrescriptions = fetch(`${API}/api/prescriptions/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((res) => {
      if (res.status === 401) { handleLogout(); return; }
      return res.json();
    }).then((data) => {
      if (Array.isArray(data)) {
        setPrescriptions(data);
      } else {
        setFetchError("Reçeteler yüklenemedi.");
      }
    });

    Promise.all([fetchProfile, fetchPrescriptions])
      .catch(() => setFetchError("Sunucuya bağlanılamadı."))
      .finally(() => setLoadingData(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleLogout = () => {
    clearToken();
    navigate("/", { replace: true });
  };

  return (
    <div className="container dashboard-container">
      <div className="card dashboard-card">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          {user && <p className="welcome">Hoşgeldin, <strong>{user}</strong></p>}
          <button className="logout-btn" onClick={handleLogout}>Çıkış Yap</button>
        </div>

        <hr />

        <h3>Reçetelerim</h3>

        {loadingData && <p className="muted">Yükleniyor...</p>}
        {fetchError && <p className="error">{fetchError}</p>}

        {!loadingData && !fetchError && prescriptions.length === 0 && (
          <p className="muted">Henüz reçete yok.</p>
        )}

        <div className="prescription-list">
          {prescriptions.map((p) => (
            <div key={p.id} className="prescription-item">
              <strong>{p.title}</strong>
              {p.description && <p>{p.description}</p>}
              <span className="prescription-date">
                {new Date(p.created_at).toLocaleDateString("tr-TR")}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default App;
