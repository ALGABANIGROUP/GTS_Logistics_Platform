import { useState, useEffect, useCallback } from 'react';

export const useWebSocket = () => {
    const [socket, setSocket] = useState(null);
    const [data, setData] = useState(null);
    const [connected, setConnected] = useState(false);

    const connectWebSocket = useCallback((url) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.close();
        }
        const ws = new WebSocket(url);
        ws.onopen = () => {
            console.log('✅ WebSocket connected to TMS');
            setConnected(true);
            setSocket(ws);
        };
        ws.onmessage = (event) => {
            try {
                const parsedData = JSON.parse(event.data);
                setData(parsedData);
            } catch (err) {
                console.error('Error parsing WebSocket data:', err);
            }
        };
        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            setConnected(false);
        };
        ws.onclose = () => {
            console.log('WebSocket disconnected');
            setConnected(false);
        };
        return ws;
    }, [socket]);

    const disconnectWebSocket = useCallback(() => {
        if (socket) {
            socket.close();
            setSocket(null);
            setConnected(false);
        }
    }, [socket]);

    const sendData = useCallback((data) => {
        if (socket && socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify(data));
            return true;
        }
        return false;
    }, [socket]);

    useEffect(() => {
        return () => {
            disconnectWebSocket();
        };
    }, [disconnectWebSocket]);

    return {
        socket,
        data,
        connected,
        connectWebSocket,
        disconnectWebSocket,
        sendData
    };
};
