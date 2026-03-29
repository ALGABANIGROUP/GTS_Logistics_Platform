const ACCESS_TOKEN_KEYS = ["access_token", "token", "gts_token", "authToken", "jwt"];
const REFRESH_TOKEN_KEYS = ["refresh_token", "refreshToken"];
const SESSION_KEYS = ["user", "auth_context"];

const getLocalStorage = () =>
  typeof window !== "undefined" ? window.localStorage : null;

const getSessionStorage = () =>
  typeof window !== "undefined" ? window.sessionStorage : null;

const clearLocalTokenCopies = () => {
  const ls = getLocalStorage();
  if (!ls) return;
  for (const key of ACCESS_TOKEN_KEYS) {
    ls.removeItem(key);
  }
  for (const key of REFRESH_TOKEN_KEYS) {
    ls.removeItem(key);
  }
};

const promoteTokenToSession = (token, targetKey) => {
  const ss = getSessionStorage();
  if (!ss || !token) {
    return token;
  }

  ss.setItem(targetKey, token);
  return token;
};

export function readAuthToken() {
  const ss = getSessionStorage();
  const ls = getLocalStorage();
  if (!ss && !ls) {
    return "";
  }

  try {
    const sessionPrimary = ss?.getItem("access_token");
    if (sessionPrimary) return sessionPrimary;

    for (const key of ACCESS_TOKEN_KEYS) {
      const sessionValue = ss?.getItem(key);
      if (sessionValue) {
        if (key !== "access_token") {
          ss?.setItem("access_token", sessionValue);
          ss?.removeItem(key);
        }
        return sessionValue;
      }
    }

    for (const key of ACCESS_TOKEN_KEYS) {
      const localValue = ls?.getItem(key);
      if (localValue) {
        promoteTokenToSession(localValue, "access_token");
        clearLocalTokenCopies();
        return localValue;
      }
    }
  } catch {
    // ignore
  }

  return "";
}

export function writeAuthToken(token) {
  const ss = getSessionStorage();
  if (!ss || !token) {
    return;
  }
  try {
    ss.setItem("access_token", token);
    clearLocalTokenCopies();
  } catch {
    // ignore
  }
}

export function readRefreshToken() {
  const ss = getSessionStorage();
  const ls = getLocalStorage();
  if (!ss && !ls) {
    return "";
  }

  try {
    for (const key of REFRESH_TOKEN_KEYS) {
      const sessionValue = ss?.getItem(key);
      if (sessionValue) {
        if (key !== "refresh_token") {
          ss?.setItem("refresh_token", sessionValue);
          ss?.removeItem(key);
        }
        return sessionValue;
      }
    }

    for (const key of REFRESH_TOKEN_KEYS) {
      const localValue = ls?.getItem(key);
      if (localValue) {
        promoteTokenToSession(localValue, "refresh_token");
        clearLocalTokenCopies();
        return localValue;
      }
    }
  } catch {
    // ignore
  }

  return "";
}

export function writeRefreshToken(token) {
  const ss = getSessionStorage();
  if (!ss || !token) {
    return;
  }
  try {
    ss.setItem("refresh_token", token);
    const ls = getLocalStorage();
    for (const key of REFRESH_TOKEN_KEYS) {
      ls?.removeItem(key);
    }
  } catch {
    // ignore
  }
}

export function clearAuthCache() {
  const ls = getLocalStorage();
  const ss = getSessionStorage();
  if (!ls && !ss) {
    return;
  }

  try {
    for (const key of ACCESS_TOKEN_KEYS) {
      ls?.removeItem(key);
      ss?.removeItem(key);
    }
    for (const key of REFRESH_TOKEN_KEYS) {
      ls?.removeItem(key);
      ss?.removeItem(key);
    }
    for (const key of SESSION_KEYS) {
      ls?.removeItem(key);
      ss?.removeItem(key);
    }
    ls?.removeItem("gts_user");
    ls?.removeItem("gts_user_profile");
  } catch {
    // ignore
  }

  if (typeof indexedDB !== "undefined" && indexedDB) {
    for (const dbName of ["gts-cache", "gts-auth-cache"]) {
      try {
        indexedDB.deleteDatabase(dbName);
      } catch {
        // ignore
      }
    }
  }
}
