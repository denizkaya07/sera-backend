import React, { useState, useEffect } from "react";
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import "./App.css";

const API = "http://127.0.0.1:8000";
const getToken = () => sessionStorage.getItem("token");
const getRole = () => sessionStorage.getItem("role");
const saveToken = (t) => sessionStorage.setItem("token", t);
const saveRole = (r) => sessionStorage.setItem("role", r);
const clearSession = () => { sessionStorage.removeItem("token"); sessionStorage.removeItem("role"); };

const ProtectedRoute = ({ children }) => getToken() ? children : <Navigate to="/" replace />;

const ROLE_LABELS = { farmer: "Ciftci", engineer: "Muhendis", dealer: "Bayi", producer: "Uretici Firma" };
const ROLE_COLORS = { dealer: "#3182ce", engineer: "#38a169", producer: "#dd6b20", farmer: "#805ad5" };
const EMPTY_FARM = { name: '', isletme_tipi: 'sera', il: '', ilce: '', mahalle: '', sera_tipi: '', buyukluk: '', urun_tipi: '', urun_cesidi: '' };

// PDF blob getir (ortak yardımcı)
const fetchPrescriptionBlob = async (prescriptionId) => {
  const token = getToken();
  const res = await fetch(`${API}/api/prescriptions/${prescriptionId}/pdf/`, {
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!res.ok) throw new Error('PDF olusturulamadi.');
  return res.blob();
};

// PDF indir
const downloadPrescriptionPDF = async (prescriptionId, title) => {
  try {
    const blob = await fetchPrescriptionBlob(prescriptionId);
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `recete_${prescriptionId}_${(title || 'recete').replace(/\s+/g, '_')}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (err) {
    alert(err.message || 'PDF indirilemedi.');
  }
};

// WhatsApp ile paylaş (Web Share API — telefonda çalışır)
const shareViaWhatsApp = async (prescriptionId, title) => {
  try {
    const blob = await fetchPrescriptionBlob(prescriptionId);
    const fileName = `recete_${prescriptionId}_${(title || 'recete').replace(/\s+/g, '_')}.pdf`;
    const file = new File([blob], fileName, { type: 'application/pdf' });

    // Telefon / tablet: Web Share API dosya paylaşımı destekleniyorsa
    if (navigator.share && navigator.canShare && navigator.canShare({ files: [file] })) {
      await navigator.share({ title, files: [file] });
    } else {
      // Masaüstü: dosyayı indir, WhatsApp Web'i aç
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = fileName;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      setTimeout(() => {
        window.open(
          `https://web.whatsapp.com/`,
          '_blank'
        );
        alert('PDF indirildi. WhatsApp Web acildi — dosyayi surukleyip birakin veya atasman olarak gonderin.');
      }, 800);
    }
  } catch (err) {
    if (err.name !== 'AbortError') alert(err.message || 'Paylasim basarisiz.');
  }
};
const EMPTY_ITEM = { sira: 1, uygulama_tipi: 'sulamayla', product: '', urun_adi: '', doz: '', not_field: '' };
const EMPTY_PRODUCT = { name: '', urun_tipi: 'ilac', etken_madde: '', doz: '', kullanim_amaci: '', uretici: '', ozellikler: '' };

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Auth />} />
        <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

const Auth = () => {
  const [isLogin, setIsLogin] = useState(true);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState("farmer");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => { if (getToken()) navigate("/dashboard", { replace: true }); }, [navigate]);

  const doLogin = async (u, p) => {
    const res = await fetch(`${API}/api/token/`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: u, password: p }),
    });
    const data = await res.json();
    if (data.access) {
      saveToken(data.access);
      const profile = await fetch(`${API}/api/users/profile/`, { headers: { Authorization: `Bearer ${data.access}` } }).then(r => r.json());
      saveRole(profile.role || '');
      navigate("/dashboard", { replace: true });
      return true;
    }
    return false;
  };

  const handleLogin = async () => {
    setError(""); setLoading(true);
    try { const ok = await doLogin(username, password); if (!ok) setError("Kullanici adi veya sifre hatali."); }
    catch { setError("Sunucuya baglanılamadi."); } finally { setLoading(false); }
  };

  const handleRegister = async () => {
    setError(""); setLoading(true);
    try {
      const res = await fetch(`${API}/api/users/register/`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password, role }),
      });
      const data = await res.json();
      if (data.error) { setError(data.error); return; }
      await doLogin(username, password);
    } catch { setError("Sunucuya baglanılamadi."); } finally { setLoading(false); }
  };

  return (
    <div className="container">
      <div className="card">
        <h2>{isLogin ? "Giris Yap" : "Kayit Ol"}</h2>
        <input placeholder="Kullanici adi" value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        <input placeholder="Sifre" type="password" value={password} onChange={(e) => setPassword(e.target.value)} autoComplete={isLogin ? "current-password" : "new-password"} />
        {!isLogin && (
          <select value={role} onChange={(e) => setRole(e.target.value)}>
            <option value="farmer">Ciftci</option>
            <option value="engineer">Muhendis</option>
            <option value="dealer">Bayi</option>
            <option value="producer">Uretici Firma</option>
          </select>
        )}
        {error && <p className="error">{error}</p>}
        <button onClick={isLogin ? handleLogin : handleRegister} disabled={loading || !username || !password}>
          {loading ? "Yukleniyor..." : isLogin ? "Giris Yap" : "Kayit Ol"}
        </button>
        <p className="toggle" onClick={() => { setIsLogin(!isLogin); setError(""); }}>
          {isLogin ? "Hesabin yok mu? Kayit ol" : "Zaten hesabin var mi? Giris yap"}
        </p>
      </div>
    </div>
  );
};

const FarmForm = ({ onSave, onCancel }) => {
  const [form, setForm] = useState(EMPTY_FARM);
  const [error, setError] = useState("");
  const set = (k, v) => setForm({ ...form, [k]: v });

  const handleSave = async () => {
    if (!form.name.trim()) { setError("Isletme adi zorunludur."); return; }
    const token = getToken();
    const res = await fetch(`${API}/api/farms/`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    if (data.id) onSave(data);
    else setError("Kaydedilemedi.");
  };

  return (
    <div className="farm-form-card">
      <h3>Yeni Isletme Ekle</h3>
      <div className="form-grid">
        <div className="form-group"><label>Isletme Adi *</label><input value={form.name} onChange={(e) => set('name', e.target.value)} /></div>
        <div className="form-group"><label>Isletme Tipi</label>
          <select value={form.isletme_tipi} onChange={(e) => set('isletme_tipi', e.target.value)}>
            <option value="sera">Sera</option><option value="bahce">Bahce</option>
            <option value="tarla">Tarla</option><option value="fidelik">Fidelik</option><option value="diger">Diger</option>
          </select>
        </div>
        <div className="form-group"><label>Il</label><input value={form.il} onChange={(e) => set('il', e.target.value)} /></div>
        <div className="form-group"><label>Ilce</label><input value={form.ilce} onChange={(e) => set('ilce', e.target.value)} /></div>
        <div className="form-group"><label>Mahalle</label><input value={form.mahalle} onChange={(e) => set('mahalle', e.target.value)} /></div>
        <div className="form-group"><label>Buyukluk (m2)</label><input type="number" value={form.buyukluk} onChange={(e) => set('buyukluk', e.target.value)} /></div>
        {form.isletme_tipi === 'sera' && (
          <div className="form-group"><label>Sera Tipi</label>
            <select value={form.sera_tipi} onChange={(e) => set('sera_tipi', e.target.value)}>
              <option value="">Secin</option><option value="cam">Cam Sera</option>
              <option value="plastik">Plastik Sera</option><option value="polykarbon">Polykarbon Sera</option><option value="diger">Diger</option>
            </select>
          </div>
        )}
        <div className="form-group"><label>Urun Tipi</label>
          <select value={form.urun_tipi} onChange={(e) => set('urun_tipi', e.target.value)}>
            <option value="">Secin</option><option value="domates">Domates</option><option value="biber">Biber</option>
            <option value="salatalik">Salatalik</option><option value="patlican">Patlican</option><option value="marul">Marul</option><option value="diger">Diger</option>
          </select>
        </div>
        <div className="form-group"><label>Urun Cesidi</label><input value={form.urun_cesidi} onChange={(e) => set('urun_cesidi', e.target.value)} /></div>
      </div>
      {error && <p className="error">{error}</p>}
      <div className="form-buttons">
        <button onClick={handleSave}>Kaydet</button>
        <button className="cancel-btn" onClick={onCancel}>Iptal</button>
      </div>
    </div>
  );
};

const FarmCard = ({ farm, onDelete, onClick }) => (
  <div className="farm-card" onClick={onClick} style={onClick ? {cursor:'pointer'} : {}}>
    <div className="farm-card-header">
      <strong>{farm.name}</strong>
      <span className="farm-type-badge">{farm.isletme_tipi}</span>
      {onDelete && <button className="delete-btn" onClick={(e) => { e.stopPropagation(); onDelete(farm.id); }}>Sil</button>}
    </div>
    <div className="farm-card-details">
      {(farm.il || farm.ilce || farm.mahalle) && <span>Konum: {[farm.mahalle, farm.ilce, farm.il].filter(Boolean).join(', ')}</span>}
      {farm.buyukluk && <span>Alan: {farm.buyukluk} m2</span>}
      {farm.urun_tipi && <span>Urun: {farm.urun_tipi}{farm.urun_cesidi ? ` (${farm.urun_cesidi})` : ''}</span>}
    </div>
  </div>
);

const TODAY = new Date().toISOString().split('T')[0];
const emptyItem = () => ({ urun_adi: '', doz: '', sera_toplam: '', uygulama_tipi: '', not_field: '', product: '' });
const emptySession = (sira) => ({ sira, tarih: TODAY, items: [emptyItem()] });

const PrescriptionForm = ({ farm, onSave, onCancel }) => {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [sessions, setSessions] = useState([emptySession(1)]);
  const [products, setProducts] = useState([]);
  const [error, setError] = useState("");
  const token = getToken();

  // DB'den ürünleri çek
  useEffect(() => {
    fetch(`${API}/api/products/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json())
      .then(data => { if (Array.isArray(data)) setProducts(data); });
  }, [token]);

  // Session güncelle
  const updateSession = (si, key, val) => {
    const updated = [...sessions];
    updated[si] = { ...updated[si], [key]: val };
    setSessions(updated);
  };

  // Sera toplamı hesapla (ml/da cinsinden dozaj × alan)
  const calcSeraToplam = (dozVal, buyukluk) => {
    const doz = parseFloat(dozVal);
    if (!isNaN(doz) && doz > 0 && buyukluk) {
      return (doz * buyukluk / 1000).toFixed(2) + ' ml';
    }
    return null;
  };

  // Item güncelle
  const updateItem = (si, ii, key, val) => {
    const updated = [...sessions];
    updated[si].items[ii] = { ...updated[si].items[ii], [key]: val };

    // Dozaj değişince sera_toplam otomatik hesapla
    if (key === 'doz') {
      const toplam = calcSeraToplam(val, farm.buyukluk);
      if (toplam) updated[si].items[ii].sera_toplam = toplam;
    }

    // İlaç/Gübre adı DB'deki ürünle eşleşince önerilen dozu doldur
    if (key === 'urun_adi') {
      const matched = products.find(p => p.name.toLowerCase() === val.toLowerCase());
      if (matched) {
        updated[si].items[ii].product = matched.id;
        // Önerilen doz sadece alan boşsa ya da başka üründen doluysa doldur
        if (matched.doz) {
          updated[si].items[ii].doz = matched.doz;
          const toplam = calcSeraToplam(matched.doz, farm.buyukluk);
          if (toplam) updated[si].items[ii].sera_toplam = toplam;
        }
      } else {
        // Elle yazılmış, product id'yi temizle
        updated[si].items[ii].product = '';
      }
    }

    setSessions(updated);
  };

  // Ürün seçilince (dropdown'dan) tüm alanları doldur
  const selectProduct = (si, ii, productId) => {
    const p = products.find(pr => pr.id === parseInt(productId));
    if (!p) return;
    const updated = [...sessions];
    updated[si].items[ii] = {
      ...updated[si].items[ii],
      product: p.id,
      urun_adi: p.name,
      doz: p.doz || updated[si].items[ii].doz,
    };
    const toplam = calcSeraToplam(p.doz, farm.buyukluk);
    if (toplam) updated[si].items[ii].sera_toplam = toplam;
    setSessions(updated);
  };

  const addSession = () => setSessions([...sessions, emptySession(sessions.length + 1)]);
  const removeSession = (si) => setSessions(sessions.filter((_, i) => i !== si).map((s, i) => ({ ...s, sira: i + 1 })));

  const addItem = (si) => {
    const updated = [...sessions];
    updated[si].items.push(emptyItem());
    setSessions(updated);
  };
  const removeItem = (si, ii) => {
    const updated = [...sessions];
    updated[si].items = updated[si].items.filter((_, i) => i !== ii);
    setSessions(updated);
  };

  const handleSave = async () => {
    if (!title.trim()) { setError("Recete basligi zorunludur."); return; }
    const payload = {
      title, description, farm: farm.id,
      sessions: sessions.map((s, si) => ({
        sira: si + 1,
        tarih: s.tarih || null,
        items: s.items.map((item, ii) => ({
          sira: ii + 1,
          urun_adi: item.urun_adi,
          doz: item.doz,
          sera_toplam: item.sera_toplam,
          uygulama_tipi: item.uygulama_tipi,
          not_field: item.not_field,
          product: item.product ? parseInt(item.product) : null,
        })),
      })),
    };
    const res = await fetch(`${API}/api/prescriptions/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (data.id) onSave(data);
    else setError(JSON.stringify(data));
  };

  return (
    <div className="prescription-form-card">
      <h3>Recete Yaz — {farm.name}</h3>
      <div className="form-grid" style={{ marginBottom: 16 }}>
        <div className="form-group">
          <label>Recete Basligi *</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Ornek: Agustos Gubre Programi" />
        </div>
        <div className="form-group">
          <label>Aciklama</label>
          <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Opsiyonel" />
        </div>
      </div>

      {sessions.map((session, si) => (
        <div key={si} className="session-block">
          <div className="session-header">
            <span className="session-title">{session.sira}. Sulama</span>
            {farm.buyukluk && <span className="session-alan">🌿 {farm.buyukluk} m²</span>}
            <input
              type="date"
              className="session-date-input"
              value={session.tarih}
              onChange={(e) => updateSession(si, 'tarih', e.target.value)}
            />
            <button className="add-ilac-btn" onClick={() => addItem(si)}>+ Ilac Ekle</button>
            {sessions.length > 1 && (
              <button className="remove-session-btn" onClick={() => removeSession(si)}>Kaldir</button>
            )}
          </div>

          <div className="session-table-wrapper">
            <table className="session-table">
              <thead>
                <tr>
                  <th>Ilac / Gubre Adi</th>
                  <th>Dozaj (ml/da)</th>
                  <th>Sera Toplaminа {farm.buyukluk ? `(${farm.buyukluk} m²)` : ''}</th>
                  <th>Uygulama</th>
                  <th>Not</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {session.items.map((item, ii) => (
                  <tr key={ii}>
                    <td className="ilac-cell">
                      {/* DB'den hızlı seçim */}
                      <select
                        className="tbl-select product-quick-select"
                        value={item.product || ''}
                        onChange={(e) => selectProduct(si, ii, e.target.value)}
                      >
                        <option value="">— DB'den sec —</option>
                        {products.map(p => (
                          <option key={p.id} value={p.id}>
                            [{p.urun_tipi === 'ilac' ? 'Ilac' : p.urun_tipi === 'gubre' ? 'Gubre' : 'Diger'}] {p.name}
                          </option>
                        ))}
                      </select>
                      {/* Ya da elle yaz */}
                      <input
                        className="tbl-input"
                        placeholder="Veya ilac / gubre adi yazin..."
                        value={item.urun_adi}
                        onChange={(e) => updateItem(si, ii, 'urun_adi', e.target.value)}
                      />
                      {/* Seçilen ürün bilgisi */}
                      {item.product && (() => {
                        const p = products.find(pr => pr.id === parseInt(item.product));
                        return p && p.etken_madde ? (
                          <span className="product-hint">⚗ {p.etken_madde}</span>
                        ) : null;
                      })()}
                    </td>
                    <td>
                      <input
                        className="tbl-input"
                        placeholder="Ornek: 150"
                        value={item.doz}
                        onChange={(e) => updateItem(si, ii, 'doz', e.target.value)}
                      />
                      {item.product && (() => {
                        const p = products.find(pr => pr.id === parseInt(item.product));
                        return p && p.doz ? (
                          <span className="product-hint">Onerilen: {p.doz}</span>
                        ) : null;
                      })()}
                    </td>
                    <td>
                      <input
                        className="tbl-input sera-toplam-input"
                        placeholder={farm.buyukluk ? 'Dozaj girince otomatik hesaplanir' : 'Sera Toplaminа'}
                        value={item.sera_toplam}
                        onChange={(e) => updateItem(si, ii, 'sera_toplam', e.target.value)}
                      />
                    </td>
                    <td>
                      <select
                        className="tbl-select"
                        value={item.uygulama_tipi}
                        onChange={(e) => updateItem(si, ii, 'uygulama_tipi', e.target.value)}
                      >
                        <option value=""></option>
                        <option value="yapraktan">Yapraktan</option>
                        <option value="damla_sulama">Damla Sulama</option>
                        <option value="sulamayla">Sulamayla</option>
                        <option value="topraktan">Topraktan</option>
                        <option value="yagmurlama">Yagmurlama</option>
                      </select>
                    </td>
                    <td>
                      <input
                        className="tbl-input"
                        placeholder="Not..."
                        value={item.not_field}
                        onChange={(e) => updateItem(si, ii, 'not_field', e.target.value)}
                      />
                    </td>
                    <td>
                      {session.items.length > 1 && (
                        <button className="sil-btn" onClick={() => removeItem(si, ii)}>Sil</button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ))}

      <button className="add-session-btn" onClick={addSession}>+ Sulama Ekle</button>
      {error && <p className="error">{error}</p>}
      <div className="form-buttons" style={{ marginTop: 16 }}>
        <button onClick={handleSave}>Receteyi Kaydet</button>
        <button className="cancel-btn" onClick={onCancel}>Iptal</button>
      </div>
    </div>
  );
};

const FarmDetail = ({ farm, onBack, canWrite }) => {
  const [prescriptions, setPrescriptions] = useState([]);
  const [notes, setNotes] = useState([]);
  const [newNote, setNewNote] = useState("");
  const [showForm, setShowForm] = useState(false);
  const [loading, setLoading] = useState(true);
  const token = getToken();

  useEffect(() => {
    Promise.all([
      fetch(`${API}/api/prescriptions/?farm_id=${farm.id}`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/farm-notes/?farm_id=${farm.id}`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
    ]).then(([presc, noteData]) => {
      if (Array.isArray(presc)) setPrescriptions(presc);
      if (Array.isArray(noteData)) setNotes(noteData);
    }).finally(() => setLoading(false));
  }, [farm.id, token]);

  const handleAddNote = async () => {
    if (!newNote.trim()) return;
    const res = await fetch(`${API}/api/farm-notes/`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ farm: farm.id, content: newNote }),
    });
    const data = await res.json();
    if (data.id) { setNotes([...notes, data]); setNewNote(""); }
  };

  return (
    <div>
      <button className="back-btn" onClick={onBack}>← Geri</button>
      <div className="farm-detail-header">
        <h2>{farm.name}</h2>
        <span className="farm-type-badge">{farm.isletme_tipi}</span>
      </div>
      <div className="farm-card-details" style={{marginBottom:'16px'}}>
        {(farm.il || farm.ilce || farm.mahalle) && <span>Konum: {[farm.mahalle, farm.ilce, farm.il].filter(Boolean).join(', ')}</span>}
        {farm.buyukluk && <span>Alan: {farm.buyukluk} m2</span>}
        {farm.urun_tipi && <span>Urun: {farm.urun_tipi}{farm.urun_cesidi ? ` (${farm.urun_cesidi})` : ''}</span>}
      </div>
      {canWrite && (
        <div style={{marginBottom:'16px'}}>
          {!showForm
            ? <button className="add-btn" onClick={() => setShowForm(true)}>+ Recete Yaz</button>
            : <PrescriptionForm farm={farm} onSave={(p) => { setPrescriptions([...prescriptions, p]); setShowForm(false); }} onCancel={() => setShowForm(false)} />
          }
        </div>
      )}
      <h3>Receteler</h3>
      {loading && <p className="muted">Yukleniyor...</p>}
      {!loading && prescriptions.length === 0 && <p className="muted">Henuz recete yok.</p>}
      {prescriptions.map(p => (
        <div key={p.id} className="prescription-detail-card">
          <div className="prescription-detail-header">
            <strong>{p.title}</strong>
            <span className="prescription-date">{new Date(p.created_at).toLocaleDateString("tr-TR")}</span>
            <span className="muted" style={{fontSize:'12px'}}>Yazan: {p.created_by_username}</span>
            <button className="pdf-btn" title="PDF olarak indir" onClick={() => downloadPrescriptionPDF(p.id, p.title)}>⬇ PDF</button>
            <button className="wa-btn" title="WhatsApp ile paylas" onClick={() => shareViaWhatsApp(p.id, p.title)}>📤 WA</button>
          </div>
          {p.description && <p style={{fontSize:'13px', color:'#555', margin:'4px 0'}}>{p.description}</p>}

          {/* Yeni format: sessions */}
          {p.sessions && p.sessions.length > 0 && p.sessions.map(session => (
            <div key={session.id} className="session-view-block">
              <div className="session-view-header">
                <span>{session.sira}. Sulama</span>
                {session.tarih && <span className="session-view-date">{new Date(session.tarih).toLocaleDateString("tr-TR")}</span>}
              </div>
              <table className="session-view-table">
                <thead>
                  <tr><th>Ilac / Gubre Adi</th><th>Dozaj (ml/da)</th><th>Sera Toplaminа</th><th>Uygulama</th><th>Not</th></tr>
                </thead>
                <tbody>
                  {session.items && session.items.map(item => (
                    <tr key={item.id}>
                      <td>{item.product_name || item.urun_adi || '-'}</td>
                      <td>{item.doz || '-'}</td>
                      <td>{item.sera_toplam || '-'}</td>
                      <td>{item.uygulama_tipi || '-'}</td>
                      <td>{item.not_field || ''}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ))}

          {/* Eski format: doğrudan items */}
          {(!p.sessions || p.sessions.length === 0) && p.items && p.items.map(item => (
            <div key={item.id} className="prescription-item-display">
              <span className="item-num">{item.sira}.</span>
              <span className="item-type">{item.uygulama_tipi}</span>
              <span className="item-product">{item.product_name || item.urun_adi}</span>
              {item.doz && <span className="item-doz">— {item.doz}</span>}
              {item.not_field && <span className="item-note">{item.not_field}</span>}
            </div>
          ))}
        </div>
      ))}
      <h3 style={{marginTop:'24px'}}>Notlar</h3>
      {notes.length === 0 && <p className="muted">Henuz not yok.</p>}
      {notes.map(note => (
        <div key={note.id} className="note-item">
          <p>{note.content}</p>
          <span className="note-meta">{note.author_username} — {new Date(note.created_at).toLocaleDateString("tr-TR")}</span>
        </div>
      ))}
      {canWrite && (
        <div className="note-input">
          <textarea placeholder="Not ekle..." value={newNote} onChange={(e) => setNewNote(e.target.value)} rows={2} />
          <button className="add-note-btn" onClick={handleAddNote}>Not Ekle</button>
        </div>
      )}
    </div>
  );
};

const CustomerFarms = () => {
  const [permissions, setPermissions] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [loading, setLoading] = useState(true);
  const token = getToken();

  useEffect(() => {
    fetch(`${API}/api/farm-permissions/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(data => { if (Array.isArray(data)) setPermissions(data); })
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) return <p className="muted">Yukleniyor...</p>;

  if (selectedFarm) {
    return <FarmDetail farm={selectedFarm} onBack={() => setSelectedFarm(null)} canWrite={true} />;
  }

  if (permissions.length === 0) return <p className="muted">Henuz kabul edilmis isletme izni yok.</p>;

  const grouped = permissions.reduce((acc, perm) => {
    const key = perm.farmer_username;
    if (!acc[key]) acc[key] = [];
    acc[key].push(perm);
    return acc;
  }, {});

  return (
    <div>
      {Object.entries(grouped).map(([farmer, perms]) => (
        <div key={farmer} className="customer-group">
          <div className="customer-group-header">
            <strong>{farmer}</strong>
            <span className="role-badge">Ciftci</span>
          </div>
          <div className="farm-list">
            {perms.map(perm => (
              <div key={perm.id} className="farm-card clickable" onClick={() => setSelectedFarm({ id: perm.farm, name: perm.farm_name, isletme_tipi: '', owner: farmer })}>
                <div className="farm-card-header">
                  <strong>{perm.farm_name}</strong>
                  <span className="farm-type-badge">{perm.year} yili</span>
                  <span className="open-btn">Ac →</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
};

const InvitationPanel = () => {
  const [searchUsername, setSearchUsername] = useState("");
  const [searchResult, setSearchResult] = useState(null);
  const [searchError, setSearchError] = useState("");
  const [message, setMessage] = useState("");
  const [sentInvitations, setSentInvitations] = useState([]);
  const [successMsg, setSuccessMsg] = useState("");
  const token = getToken();

  useEffect(() => {
    fetch(`${API}/api/invitations/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(data => { if (Array.isArray(data)) setSentInvitations(data); });
  }, [token]);

  const handleSearch = async () => {
    setSearchError(""); setSearchResult(null);
    if (!searchUsername.trim()) return;
    const res = await fetch(`${API}/api/invitations/search_farmer/?username=${searchUsername}`, { headers: { Authorization: `Bearer ${token}` } });
    const data = await res.json();
    if (data.error) setSearchError(data.error);
    else setSearchResult(data);
  };

  const handleInvite = async () => {
    if (!searchResult) return;
    const res = await fetch(`${API}/api/invitations/`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ receiver: searchResult.id, message }),
    });
    const data = await res.json();
    if (data.id) {
      setSuccessMsg(`${searchResult.username} adli ciftciye davet gonderildi.`);
      setSentInvitations([...sentInvitations, data]);
      setSearchResult(null); setSearchUsername(""); setMessage("");
    } else {
      setSearchError(data.receiver?.[0] || data.non_field_errors?.[0] || "Davet gonderilemedi.");
    }
  };

  const statusColor = { pending: "#d69e2e", accepted: "#38a169", rejected: "#e53e3e" };
  const statusLabel = { pending: "Bekliyor", accepted: "Kabul Edildi", rejected: "Reddedildi" };

  return (
    <div>
      <h3>Ciftci Ara</h3>
      <div className="search-bar">
        <input placeholder="Ciftci kullanici adi" value={searchUsername} onChange={(e) => setSearchUsername(e.target.value)} onKeyDown={(e) => e.key === "Enter" && handleSearch()} />
        <button onClick={handleSearch}>Ara</button>
      </div>
      {searchError && <p className="error">{searchError}</p>}
      {successMsg && <p className="success">{successMsg}</p>}
      {searchResult && (
        <div className="search-result">
          <strong>{searchResult.username}</strong> <span className="role-badge">Ciftci</span>
          <textarea placeholder="Mesaj (opsiyonel)" value={message} onChange={(e) => setMessage(e.target.value)} rows={2} />
          <button className="invite-btn" onClick={handleInvite}>Davet Gonder</button>
        </div>
      )}
      {sentInvitations.length > 0 && (
        <>
          <h3 style={{marginTop:'24px'}}>Gonderilen Davetler</h3>
          {sentInvitations.map(inv => (
            <div key={inv.id} className="invitation-card">
              <div className="inv-header">
                <strong>{inv.receiver_username}</strong>
                <span className="inv-status" style={{color: statusColor[inv.status]}}>{statusLabel[inv.status]}</span>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
};

const ReceivedInvitations = ({ farms }) => {
  const [invitations, setInvitations] = useState([]);
  const [selectedFarms, setSelectedFarms] = useState({});
  const [messages, setMessages] = useState({});
  const token = getToken();

  useEffect(() => {
    fetch(`${API}/api/invitations/received/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(data => { if (Array.isArray(data)) setInvitations(data); });
  }, [token]);

  const toggleFarm = (invId, farmId) => {
    const current = selectedFarms[invId] || [];
    const updated = current.includes(farmId) ? current.filter(id => id !== farmId) : [...current, farmId];
    setSelectedFarms({ ...selectedFarms, [invId]: updated });
  };

  const handleAccept = async (invId) => {
    const farmIds = selectedFarms[invId] || [];
    if (farmIds.length === 0) { setMessages({ ...messages, [invId]: "En az bir isletme secmelisiniz." }); return; }
    const res = await fetch(`${API}/api/invitations/${invId}/accept/`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify({ farm_ids: farmIds }),
    });
    const data = await res.json();
    if (data.message) {
      setMessages({ ...messages, [invId]: "Davet kabul edildi." });
      setInvitations(invitations.filter(inv => inv.id !== invId));
    } else {
      setMessages({ ...messages, [invId]: data.error || "Hata olustu." });
    }
  };

  const handleReject = async (invId) => {
    await fetch(`${API}/api/invitations/${invId}/reject/`, { method: "POST", headers: { Authorization: `Bearer ${token}` } });
    setInvitations(invitations.filter(inv => inv.id !== invId));
  };

  if (invitations.length === 0) return <p className="muted">Bekleyen davet yok.</p>;

  return (
    <div>
      {invitations.map(inv => (
        <div key={inv.id} className="invitation-card received">
          <div className="inv-header">
            <strong>{inv.sender_username}</strong>
            <span className="role-badge" style={{background: ROLE_COLORS[inv.sender_role] || '#718096'}}>
              {ROLE_LABELS[inv.sender_role] || inv.sender_role}
            </span>
          </div>
          {inv.message && <p className="inv-message">{inv.message}</p>}
          <p className="muted" style={{fontSize:'13px'}}>Hangi isletmelerinizi paylasmak istiyorsunuz?</p>
          <div className="farm-checkboxes">
            {farms.length === 0 && <p className="muted">Once isletme ekleyin.</p>}
            {farms.map(farm => (
              <label key={farm.id} className="farm-checkbox">
                <input type="checkbox" checked={(selectedFarms[inv.id] || []).includes(farm.id)} onChange={() => toggleFarm(inv.id, farm.id)} />
                {farm.name} ({farm.isletme_tipi})
              </label>
            ))}
          </div>
          {messages[inv.id] && <p className={messages[inv.id].includes("kabul") ? "success" : "error"}>{messages[inv.id]}</p>}
          <div className="form-buttons">
            <button onClick={() => handleAccept(inv.id)}>Kabul Et</button>
            <button className="cancel-btn" onClick={() => handleReject(inv.id)}>Reddet</button>
          </div>
        </div>
      ))}
    </div>
  );
};

// ─── ÜRÜN YÖNETİMİ ───────────────────────────────────────────────────────────
const ProductManager = () => {
  const [products, setProducts] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState(EMPTY_PRODUCT);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const token = getToken();
  const currentRole = getRole();

  useEffect(() => {
    fetch(`${API}/api/products/`, { headers: { Authorization: `Bearer ${token}` } })
      .then(r => r.json()).then(data => { if (Array.isArray(data)) setProducts(data); })
      .finally(() => setLoading(false));
  }, [token]);

  const set = (k, v) => setForm({ ...form, [k]: v });

  const handleSave = async () => {
    if (!form.name.trim()) { setError("Urun adi zorunludur."); return; }
    const res = await fetch(`${API}/api/products/`, {
      method: "POST", headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
      body: JSON.stringify(form),
    });
    const data = await res.json();
    if (data.id) {
      setProducts([...products, data]);
      setForm(EMPTY_PRODUCT);
      setShowForm(false);
      setError("");
    } else {
      setError(JSON.stringify(data));
    }
  };

  const handleDelete = async (id) => {
    const res = await fetch(`${API}/api/products/${id}/`, {
      method: "DELETE", headers: { Authorization: `Bearer ${token}` },
    });
    if (res.ok) setProducts(products.filter(p => p.id !== id));
  };

  const myProducts = products.filter(p => p.added_by_username === sessionStorage.getItem('username'));
  const roleColor = ROLE_COLORS[currentRole] || '#718096';

  return (
    <div>
      <button className="add-btn" onClick={() => setShowForm(!showForm)}>
        {showForm ? 'Iptal' : '+ Yeni Urun Ekle'}
      </button>

      {showForm && (
        <div className="farm-form-card">
          <h3>Yeni Urun Ekle</h3>
          <div className="form-grid">
            <div className="form-group"><label>Urun Adi *</label><input value={form.name} onChange={(e) => set('name', e.target.value)} /></div>
            <div className="form-group"><label>Urun Tipi</label>
              <select value={form.urun_tipi} onChange={(e) => set('urun_tipi', e.target.value)}>
                <option value="ilac">Ilac</option>
                <option value="gubre">Gubre</option>
                <option value="diger">Diger</option>
              </select>
            </div>
            <div className="form-group"><label>Etken Madde</label><input value={form.etken_madde} onChange={(e) => set('etken_madde', e.target.value)} /></div>
            <div className="form-group"><label>Doz</label><input value={form.doz} onChange={(e) => set('doz', e.target.value)} placeholder="Ornek: 2 lt/100 lt su" /></div>
            <div className="form-group" style={{gridColumn:'1/-1'}}><label>Kullanim Amaci</label><input value={form.kullanim_amaci} onChange={(e) => set('kullanim_amaci', e.target.value)} /></div>
            <div className="form-group"><label>Uretici</label><input value={form.uretici} onChange={(e) => set('uretici', e.target.value)} /></div>
            <div className="form-group" style={{gridColumn:'1/-1'}}><label>Ozellikler</label><textarea value={form.ozellikler} onChange={(e) => set('ozellikler', e.target.value)} rows={2} /></div>
          </div>
          {error && <p className="error">{error}</p>}
          <div className="form-buttons">
            <button onClick={handleSave}>Kaydet</button>
            <button className="cancel-btn" onClick={() => { setShowForm(false); setError(""); }}>Iptal</button>
          </div>
        </div>
      )}

      <h3 style={{marginTop:'16px'}}>Tum Urunler</h3>
      {loading && <p className="muted">Yukleniyor...</p>}
      {!loading && products.length === 0 && <p className="muted">Henuz urun yok.</p>}
      {products.map(p => (
        <div key={p.id} className="product-card" style={{borderLeftColor: ROLE_COLORS[p.added_by_role] || '#718096'}}>
          <div className="product-header">
            <strong>{p.name}</strong>
            <span className="product-type-badge">{p.urun_tipi}</span>
            {p.added_by_username && (
              <span className="product-owner" style={{color: ROLE_COLORS[p.added_by_role] || '#718096'}}>
                {p.added_by_username}
              </span>
            )}
            {p.added_by_username === sessionStorage.getItem('currentUser') && (
              <button className="delete-btn" onClick={() => handleDelete(p.id)}>Sil</button>
            )}
          </div>
          {p.etken_madde && <p className="product-detail"><strong>Etken Madde:</strong> {p.etken_madde}</p>}
          {p.doz && <p className="product-detail"><strong>Doz:</strong> {p.doz}</p>}
          {p.kullanim_amaci && <p className="product-detail">{p.kullanim_amaci}</p>}
        </div>
      ))}
    </div>
  );
};

const Dashboard = () => {
  const [user, setUser] = useState("");
  const [roleLabel, setRoleLabel] = useState("");
  const [prescriptions, setPrescriptions] = useState([]);
  const [farms, setFarms] = useState([]);
  const [selectedFarm, setSelectedFarm] = useState(null);
  const [loadingData, setLoadingData] = useState(true);
  const [fetchError, setFetchError] = useState("");
  const [activeTab, setActiveTab] = useState("farms");
  const [showForm, setShowForm] = useState(false);
  const navigate = useNavigate();

  const currentRole = getRole();
  const isFarmer = currentRole === 'farmer';
  const isDealer = currentRole === 'dealer';
  const isEngineer = currentRole === 'engineer';
  const isProducer = currentRole === 'producer';

  const handleLogout = () => { clearSession(); navigate("/", { replace: true }); };

  useEffect(() => {
    const token = getToken();
    if (!token) { handleLogout(); return; }

    let defaultTab = 'farms';
    if (isDealer || isEngineer) defaultTab = 'customers';
    if (isProducer) defaultTab = 'products';
    setActiveTab(defaultTab);

    Promise.all([
      fetch(`${API}/api/users/profile/`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      fetch(`${API}/api/prescriptions/`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json()),
      ...(isFarmer ? [fetch(`${API}/api/farms/`, { headers: { Authorization: `Bearer ${token}` } }).then(r => r.json())] : [Promise.resolve([])]),
    ]).then(([profile, presc, farmsData]) => {
      if (profile?.user) {
        setUser(profile.user);
        sessionStorage.setItem('currentUser', profile.user);
      }
      if (profile?.role) setRoleLabel(ROLE_LABELS[profile.role] || profile.role);
      if (Array.isArray(presc)) setPrescriptions(presc);
      if (Array.isArray(farmsData)) setFarms(farmsData);
    }).catch(() => setFetchError("Sunucuya baglanılamadi."))
      .finally(() => setLoadingData(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const handleDeleteFarm = async (id) => {
    const token = getToken();
    await fetch(`${API}/api/farms/${id}/`, { method: "DELETE", headers: { Authorization: `Bearer ${token}` } });
    setFarms(farms.filter((f) => f.id !== id));
  };

  const tabs = [
    ...(isFarmer ? [{ key: 'farms', label: 'Isletmelerim' }] : []),
    ...(isDealer || isEngineer ? [{ key: 'customers', label: 'Musterilerim' }] : []),
    ...(isProducer || isDealer || isEngineer ? [{ key: 'products', label: 'Urunler' }] : []),
    { key: 'prescriptions', label: 'Recetelerim' },
    ...(isDealer || isEngineer ? [{ key: 'invitations', label: 'Davetler' }] : []),
    ...(isFarmer ? [{ key: 'received', label: 'Gelen Davetler' }] : []),
  ];

  return (
    <div className="container dashboard-container">
      <div className="card dashboard-card">
        <div className="dashboard-header">
          <h1>Dashboard</h1>
          {user && (
            <p className="welcome">
              Hosgeldin, <strong>{user}</strong>
              {roleLabel && <span className="role-badge" style={{background: ROLE_COLORS[currentRole] || '#667eea'}}>{roleLabel}</span>}
            </p>
          )}
          <button className="logout-btn" onClick={handleLogout}>Cikis Yap</button>
        </div>

        <div className="tabs">
          {tabs.map(t => (
            <button key={t.key} className={activeTab === t.key ? "tab active" : "tab"}
              onClick={() => { setActiveTab(t.key); setSelectedFarm(null); }}>
              {t.label}
            </button>
          ))}
        </div>

        {loadingData && <p className="muted">Yukleniyor...</p>}
        {fetchError && <p className="error">{fetchError}</p>}

        {activeTab === "farms" && isFarmer && !loadingData && (
          selectedFarm
            ? <FarmDetail farm={selectedFarm} onBack={() => setSelectedFarm(null)} canWrite={false} />
            : <>
                {!showForm && <button className="add-btn" onClick={() => setShowForm(true)}>+ Yeni Isletme Ekle</button>}
                {showForm && <FarmForm onSave={(farm) => { setFarms([...farms, farm]); setShowForm(false); }} onCancel={() => setShowForm(false)} />}
                {farms.length === 0 && !showForm && <p className="muted">Henuz isletme yok.</p>}
                <div className="farm-list">{farms.map((f) => <FarmCard key={f.id} farm={f} onDelete={handleDeleteFarm} onClick={() => setSelectedFarm(f)} />)}</div>
              </>
        )}

        {activeTab === "customers" && (isDealer || isEngineer) && <CustomerFarms />}
        {activeTab === "products" && (isProducer || isDealer || isEngineer) && <ProductManager />}

        {activeTab === "prescriptions" && !loadingData && (
          <>
            {prescriptions.length === 0 && <p className="muted">Henuz recete yok.</p>}
            <div className="prescription-list">
              {prescriptions.map((p) => (
                <div key={p.id} className="prescription-detail-card">
                  <div className="prescription-detail-header">
                    <strong>{p.title}</strong>
                    {p.farm_name && <span className="muted" style={{fontSize:'12px'}}>— {p.farm_name}</span>}
                    <span className="prescription-date">{new Date(p.created_at).toLocaleDateString("tr-TR")}</span>
                    <button className="pdf-btn" title="PDF olarak indir" onClick={() => downloadPrescriptionPDF(p.id, p.title)}>⬇ PDF</button>
                    <button className="wa-btn" title="WhatsApp ile paylas" onClick={() => shareViaWhatsApp(p.id, p.title)}>📤 WA</button>
                  </div>
                  {p.items && p.items.map(item => (
                    <div key={item.id} className="prescription-item-display">
                      <span className="item-num">{item.sira}.</span>
                      <span className="item-type">{item.uygulama_tipi}</span>
                      <span className="item-product">{item.product_name || item.urun_adi}</span>
                      {item.doz && <span className="item-doz">— {item.doz}</span>}
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </>
        )}

        {activeTab === "invitations" && (isDealer || isEngineer) && <InvitationPanel />}
        {activeTab === "received" && isFarmer && <ReceivedInvitations farms={farms} />}
      </div>
    </div>
  );
};

export default App;
