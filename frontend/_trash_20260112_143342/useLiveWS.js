// src/hooks/useLiveWS.js
import { useEffect, useMemo, useState } from "react";
import { getWSClient } from "../utils/wsClient";

export default function useLiveWS(channels = []) {
    const client = useMemo(() => getWSClient(), []);
    const [lastMessage, setLastMessage] = useState(null);

    useEffect(() => {
        client.connect();
        const offMsg = client.onMessage((msg) => setLastMessage(msg));

        const unsubs = (channels || []).map((ch) => client.subscribe(ch));
        return () => {
            offMsg();
            unsubs.forEach((u) => u && u());
            // Do NOT disconnect here globally; keep one app-level connection.
        };
    }, [client, JSON.stringify(channels)]);

    return { client, lastMessage };
}
