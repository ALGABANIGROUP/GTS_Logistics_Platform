import React, { createContext, useCallback, useContext, useEffect, useMemo, useRef } from "react";

const UiActionsContext = createContext({
  emitRefresh: () => false,
  subscribe: () => () => {},
});

export const UiActionsProvider = ({ children }) => {
  const listenersRef = useRef(new Set());

  const subscribe = useCallback((handler) => {
    if (typeof handler !== "function") {
      return () => {};
    }
    listenersRef.current.add(handler);
    return () => listenersRef.current.delete(handler);
  }, []);

  const emitRefresh = useCallback(() => {
    const listeners = Array.from(listenersRef.current);
    if (!listeners.length) return false;
    listeners.forEach((handler) => {
      try {
        handler();
      } catch {
        // ignore refresh handler errors
      }
    });
    return true;
  }, []);

  const value = useMemo(
    () => ({
      emitRefresh,
      subscribe,
    }),
    [emitRefresh, subscribe]
  );

  return <UiActionsContext.Provider value={value}>{children}</UiActionsContext.Provider>;
};

export const useUiActions = () => useContext(UiActionsContext);

export const useRefreshSubscription = (handler) => {
  const { subscribe } = useUiActions();

  useEffect(() => {
    return subscribe(handler);
  }, [subscribe, handler]);
};
