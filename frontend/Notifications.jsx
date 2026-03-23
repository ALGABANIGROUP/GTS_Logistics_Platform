import React, { useEffect, useState } from "react";
import axios from "axios";

const Notifications = () => {
  const [notifications, setNotifications] = useState([]);

  const fetchNotifications = async () => {
    const res = await axios.get("/notifications/");
    setNotifications(res.data);
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  return (
    <div className="p-4 max-w-2xl mx-auto">
      <h2 className="text-xl font-bold mb-4">Notifications</h2>
      <ul className="space-y-3">
        {notifications.map((note) => (
          <li key={note.id} className="p-3 rounded bg-yellow-100 border">
            <p className="font-medium">{note.message}</p>
            <p className="text-sm text-gray-600">
              Created: {new Date(note.created_at).toLocaleString()}
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Notifications;