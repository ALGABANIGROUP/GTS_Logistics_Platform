// frontend/src/utils/authStorage.js
// Simplified version - stores tokens in localStorage for persistence across tabs and reloads

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const SAVED_EMAIL_KEY = 'gts_saved_email';
const CONTEXT_KEYS = ['auth_context', 'user', 'entitlements'];

const getLocalStorage = () =>
    typeof window !== "undefined" ? window.localStorage : null;
const getSessionStorage = () =>
    typeof window !== "undefined" ? window.sessionStorage : null;

/**
 * Write authentication token to localStorage.
 */
export const writeAuthToken = (token) => {
    const storage = getLocalStorage();
    if (!storage || !token) return;
    try {
        storage.setItem(ACCESS_TOKEN_KEY, token);
    } catch (e) {
        console.warn("Failed to write auth token:", e);
    }
};

/**
 * Read authentication token from localStorage.
 */
export const readAuthToken = () => {
    const storage = getLocalStorage();
    if (!storage) return null;
    try {
        return storage.getItem(ACCESS_TOKEN_KEY);
    } catch (e) {
        console.warn("Failed to read auth token:", e);
        return null;
    }
};

/**
 * Write refresh token to localStorage.
 */
export const writeRefreshToken = (token) => {
    const storage = getLocalStorage();
    if (!storage || !token) return;
    try {
        storage.setItem(REFRESH_TOKEN_KEY, token);
    } catch (e) {
        console.warn("Failed to write refresh token:", e);
    }
};

/**
 * Read refresh token from localStorage.
 */
export const readRefreshToken = () => {
    const storage = getLocalStorage();
    if (!storage) return null;
    try {
        return storage.getItem(REFRESH_TOKEN_KEY);
    } catch (e) {
        console.warn("Failed to read refresh token:", e);
        return null;
    }
};

/**
 * Clear all authentication data from localStorage.
 */
export const clearAuthCache = () => {
    const storage = getLocalStorage();
    const session = getSessionStorage();
    try {
        storage?.removeItem(ACCESS_TOKEN_KEY);
        storage?.removeItem(REFRESH_TOKEN_KEY);
        CONTEXT_KEYS.forEach((key) => {
            storage?.removeItem(key);
            session?.removeItem(key);
        });
        // Optional: clear saved email as well
        // storage.removeItem(SAVED_EMAIL_KEY);
    } catch (e) {
        console.warn("Failed to clear auth cache:", e);
    }
};

/**
 * Save email for "Remember me" functionality.
 */
export const saveSavedEmail = (email) => {
    const storage = getLocalStorage();
    if (!storage) return;
    try {
        storage.setItem(SAVED_EMAIL_KEY, email);
    } catch (e) {
        console.warn("Failed to save email:", e);
    }
};

/**
 * Read saved email from localStorage.
 */
export const readSavedEmail = () => {
    const storage = getLocalStorage();
    if (!storage) return null;
    try {
        return storage.getItem(SAVED_EMAIL_KEY);
    } catch (e) {
        console.warn("Failed to read saved email:", e);
        return null;
    }
};
