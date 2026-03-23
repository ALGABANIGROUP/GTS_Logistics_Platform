export const isValidEmail = (email = "") => {
  const value = String(email).trim();
  if (!value) return false;
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
};

export const isStrongPassword = (password = "") => {
  const value = String(password);
  if (import.meta?.env?.DEV) {
    return value.length >= 6;
  }
  if (value.length < 8) return false;
  if (!/[A-Z]/.test(value)) return false;
  if (!/[0-9]/.test(value)) return false;
  return true;
};

export const normalizePhone = (phone = "") => {
  return String(phone).replace(/[^\d]/g, "");
};

export const isValidPhone = (phone = "") => {
  const normalized = normalizePhone(phone);
  return normalized.length >= 7;
};
