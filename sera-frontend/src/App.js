useEffect(() => {
    const token = getToken();
    if (!token) {
      handleLogout();
      return;
    }

    const fetchProfile = fetch(`${API}/api/users/profile/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((res) => {
      if (res.status === 401) return;
      return res.json();
    }).then((data) => {
      if (data?.user) setUser(data.user);
    });

    const fetchPrescriptions = fetch(`${API}/api/prescriptions/`, {
      headers: { Authorization: `Bearer ${token}` },
    }).then((res) => {
      if (res.status === 401) return;
      return res.json();
    }).then((data) => {
      if (Array.isArray(data)) setPrescriptions(data);
      else setFetchError("Reçeteler yüklenemedi.");
    });

    Promise.all([fetchProfile, fetchPrescriptions])
      .catch(() => setFetchError("Sunucuya bağlanılamadı."))
      .finally(() => setLoadingData(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps