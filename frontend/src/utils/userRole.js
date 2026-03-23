const ROLE_KEYS = ["effective_role", "role", "db_role", "token_role"];
const ADMIN_ROLES = ["admin", "system_admin", "super_admin", "owner"];
const SUPER_ADMIN_ROLES = ["super_admin", "owner"];

export function normalizeUserRole(role) {
  return String(role || "").toLowerCase().trim();
}

export function getUserRole(user) {
  const u = user || {};
  for (const key of ROLE_KEYS) {
    const value = u[key];
    if (value) {
      return normalizeUserRole(value);
    }
  }
  return "";
}

export function isAdminRole(role) {
  return ADMIN_ROLES.includes(normalizeUserRole(role));
}

export function isSuperAdminRole(role) {
  return SUPER_ADMIN_ROLES.includes(normalizeUserRole(role));
}

export function hasRequiredRole(userRole, allowedRoles = []) {
  const normalizedUserRole = normalizeUserRole(userRole);
  const normalizedAllowedRoles = allowedRoles.map(normalizeUserRole).filter(Boolean);

  if (!normalizedAllowedRoles.length) {
    return true;
  }

  if (normalizedAllowedRoles.includes(normalizedUserRole)) {
    return true;
  }

  if (isSuperAdminRole(normalizedUserRole)) {
    return normalizedAllowedRoles.some((role) => isAdminRole(role));
  }

  if (normalizedUserRole === "system_admin") {
    return normalizedAllowedRoles.includes("admin") || normalizedAllowedRoles.includes("system_admin");
  }

  return false;
}
