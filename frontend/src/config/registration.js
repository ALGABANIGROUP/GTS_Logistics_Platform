const parseBool = (value) => {
  if (typeof value !== "string") return false;
  return ["1", "true", "yes", "on"].includes(value.toLowerCase());
};

const normalize = (value) => {
  if (typeof value !== "string") return "";
  return value.trim();
};

const formatLongDate = (value) => {
  const normalized = normalize(value);
  if (!normalized) return "";
  const parsed = new Date(normalized);
  if (Number.isNaN(parsed.getTime())) {
    return normalized;
  }
  return new Intl.DateTimeFormat("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  }).format(parsed);
};

const registrationDisabled = parseBool(
  import.meta.env.VITE_REGISTRATION_DISABLED
);
const registrationReopenRaw = normalize(
  import.meta.env.VITE_REGISTRATION_REOPEN_DATE
);
const registrationReopenLabel = formatLongDate(registrationReopenRaw);
const registrationContactEmail =
  normalize(import.meta.env.VITE_REGISTRATION_CONTACT_EMAIL) ||
  "admin@gabanilogistics.com";
const registrationNotice =
  normalize(import.meta.env.VITE_REGISTRATION_NOTICE) ||
  "Registration is paused while we run the platform privately until August 9, 2026.";

export const registrationStatus = {
  disabled: registrationDisabled,
  reopenRaw: registrationReopenRaw,
  reopenLabel: registrationReopenLabel,
  contactEmail: registrationContactEmail,
  notice: registrationNotice,
};

export const REGISTRATION_DISABLED_FLAG = registrationDisabled;
export const REGISTRATION_NOTICE_TEXT = registrationNotice;
export const REGISTRATION_CONTACT = registrationContactEmail;
export const REGISTRATION_REOPEN_LABEL = registrationReopenLabel;
