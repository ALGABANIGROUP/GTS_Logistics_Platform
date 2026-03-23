import { useState, useEffect } from "react";
import { API_BASE_URL, WS_BASE_URL } from "../config/env";

const Notifications = () => {
    const [notifications, setNotifications] = useState([]);

    useEffect(() => {
        const fetchNotifications = async () => {
            try {
                const response = await fetch(`${API_BASE_URL}/notifications`);
                const data = await response.json();
                setNotifications(data.notifications);
            } catch (error) {
                console.error("Error fetching notifications:", error);
            }
        };

        fetchNotifications();

        // WebSocket for real-time updates
        const ws = new WebSocket(WS_BASE_URL);

        ws.onmessage = (event) => {
            const newNotification = JSON.parse(event.data);
            setNotifications((prev) => [newNotification, ...prev]);
        };

        return () => ws.close();
    }, []);

    return (
        <div className="notifications">
            <h3>Notifications</h3>
            <ul>
                {notifications.map((notif, index) => (
                    <li key={index}>{notif.message}</li>
                ))}
            </ul>
        </div>
    );
};

export default Notifications;
