// frontend/src/pages/DriverManagement.jsx

import { useEffect, useState, useRef } from "react";
import alertSound from "../assets/alert_critical.wav";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";

const DriverManagement = () => {
  const [alerts, setAlerts] = useState([]);
  const audioRef = useRef(null);

  useEffect(() => {
    const ws = new WebSocket("ws://127.0.0.1:8000/ws/drivers/alerts");

    ws.onmessage = (event) => {
      const alert = JSON.parse(event.data);
      setAlerts((prev) => [alert, ...prev]);
      if (audioRef.current) audioRef.current.play();

      toast.error(`🚚 Driver Alert: ${alert.message}`, {
        position: "top-right",
        autoClose: 5000,
      });
    };

    return () => ws.close();
  }, []);

  return (
    <div className="p-6">
      <ToastContainer />
      <audio ref={audioRef} src={alertSound} preload="auto" />

      <h2 className="text-2xl font-bold mb-4">🚛 Driver Management</h2>

      {alerts.length === 0 ? (
        <p>No driver alerts.</p>
      ) : (
        <ul className="space-y-3">
          {alerts.map((alert, index) => (
            <li key={index} className="bg-white shadow p-3 rounded">
              <p className="text-gray-800">{alert.message}</p>
              <p className="text-sm text-gray-500">{new Date(alert.timestamp).toLocaleString()}</p>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default DriverManagement;
