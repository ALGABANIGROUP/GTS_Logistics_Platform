// frontend/src/hooks/useWS.ts
import { useEffect, useRef } from "react";
import { getWSClient } from "../utils/wsClient";

type Handler = (payload: any) => void;

export function useWS(channels: string[] | string, handler: Handler) {
  const saved = useRef<Handler>(handler);
  useEffect(() => { saved.current = handler; }, [handler]);

  useEffect(() => {
    const wsClient = getWSClient();
    const list = Array.isArray(channels) ? channels : [channels];
    const cleanups = list.map((ch) =>
      wsClient.subscribe(ch, (msg) => saved.current?.(msg))
    );
    // ensure connection
    wsClient.connect();
    return () => { cleanups.forEach((fn) => fn && fn()); };
  }, [Array.isArray(channels) ? channels.join("|") : channels]);
}
