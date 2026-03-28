import React, { useEffect, useState, useCallback } from "react";

function Dashboard({ token }) {
  const [prescriptions, setPrescriptions] = useState([]);

  const fetchData = useCallback(async () => {
    const res = await fetch("http://127.0.0.1:8000/api/prescriptions/", {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    const data = await res.json();
    setPrescriptions(data);
  }, [token]); // 🔥 önemli

  useEffect(() => {
    fetchData();
  }, [fetchData]); // 🔥 artık stabil

  return (
    <div>
      <h2>Reçeteler</h2>

      {prescriptions.map((p) => (
        <div key={p.id}>
          <b>{p.title}</b> - {p.description}
        </div>
      ))}
    </div>
  );
}

export default Dashboard;