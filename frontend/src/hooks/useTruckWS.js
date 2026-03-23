// E:\GTS Logistics\frontend\src\hooks\useTruckWS.js
import { useEffect, useRef, useState } from "react";
import { connectTruckLocationsWS } from "../utils/wsClient";

export function useTruckWS() {
  const wsRef = useRef(null);
  const [positions, setPositions] = useState([]);

  useEffect(() => {
    wsRef.current = connectTruckLocationsWS({
      onMessage: (msg) => {
        if (msg.type === "truck_positions" && Array.isArray(msg.data)) {
          setPositions(msg.data);
        }
      },
    });
    return () => {
      try {
        wsRef.current && wsRef.current.close();
      } catch (error) {
        void error;
      }
    };
  }, []);

  return { positions };
}
