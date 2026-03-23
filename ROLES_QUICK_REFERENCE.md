# GTS Role System Reference
**Quick Reference for Developers**

## ✅ Valid Roles (Backend RBAC)
Source: `backend/security/rbac.py`

### Internal Hierarchy (Low → High)
```
user → manager → admin → super_admin
```

### All Valid Roles
1. **user** - Default role, lowest privileges
2. **manager** - Can manage teams/resources
3. **admin** - Administrator with elevated access
4. **super_admin** - Highest privilege internal role
5. **partner** - Special domain role (not in hierarchy)

---

## ❌ Invalid Roles (DO NOT USE)
- ❌ `owner` - Use `super_admin` instead
- ❌ `system_admin` - Not in RBAC system
- ❌ `shipper` - This is a user_type, not a role
- ❌ `carrier` - This is a user_type, not a role
- ❌ `broker` - This is a user_type, not a role
- ❌ `system_administrator_bot` - Not a user role
- ❌ `finance` - Not a standard role
- ❌ `operations_manager` - Not a standard role
- ❌ `subscription_user` - Not a standard role
- ❌ `guest` - Not a standard role

---

## Frontend Usage Examples

### Role Display
```javascript
const ROLE_DISPLAY = {
  super_admin: "Super Admin",
  admin: "Administrator",
  manager: "Manager",
  user: "User",
  partner: "Partner",
};
```

### Admin Check (Correct)
```javascript
// ✅ Correct - matches backend hierarchy
const isAdmin = ["admin", "super_admin"].includes(role);

// ❌ Wrong - includes invalid roles
const isAdmin = ["admin", "system_admin", "super_admin", "owner"].includes(role);
```

### Super Admin Check (Correct)
```javascript
// ✅ Correct - only super_admin
const isSuperAdmin = role === "super_admin";

// ❌ Wrong - includes non-existent owner
const isSuperAdmin = role === "super_admin" || role === "owner";
```

### RequireAuth Component
```javascript
// ✅ Correct - uses valid roles
<RequireAuth roles={["admin", "super_admin"]}>
  <AdminContent />
</RequireAuth>

// ❌ Wrong - includes invalid roles
<RequireAuth roles={["admin", "system_admin", "super_admin", "owner"]}>
  <AdminContent />
</RequireAuth>
```

---

## Backend RBAC Functions

### normalize_role(role)
Normalizes role string and applies aliases
```python
normalize_role("super-admin")  # → "super_admin"
normalize_role("administrator")  # → "admin"
normalize_role("ops")  # → "manager"
```

### has_required_role(user_role, required_roles)
Checks if user has required role (with hierarchy expansion)
```python
has_required_role("super_admin", ["admin"])  # → True (hierarchy)
has_required_role("admin", ["admin"])  # → True (exact match)
has_required_role("manager", ["admin"])  # → False (lower privilege)
has_required_role("user", ["admin"])  # → False (lower privilege)
has_required_role("partner", ["admin"])  # → False (different domain)
```

### expand_required_roles(required)
Expands roles with hierarchy
```python
expand_required_roles(["admin"])  
# → {"admin", "super_admin"}

expand_required_roles(["manager"])  
# → {"manager", "admin", "super_admin"}

expand_required_roles(["user"])  
# → {"user", "manager", "admin", "super_admin"}

expand_required_roles(["partner"])  
# → {"partner"}  # Partner is isolated
```

---

## Database Schema

### users.role Column
- **Type**: VARCHAR(50)
- **Nullable**: False
- **Default**: "user"
- **Valid Values**: user, manager, admin, super_admin, partner

### Migration Checklist
- ✅ All existing users have valid roles
- ✅ No "owner" values in database (convert to "super_admin")
- ✅ No "system_admin" values (convert to "admin" or "super_admin")
- ✅ No user_type values in role column (shipper/carrier/broker)

---

## Common Mistakes to Avoid

### ❌ Mixing user_type with role
```javascript
// WRONG - user_type is NOT the same as role
const role = user.user_type;  // Could be "shipper"
```

### ❌ Using non-existent roles
```javascript
// WRONG - "owner" doesn't exist in RBAC
if (role === "owner") { ... }
```

### ❌ Not using hierarchy expansion
```javascript
// WRONG - super_admin should have admin access
if (role === "admin") {
  // super_admin users won't have access!
}

// CORRECT - use backend RBAC or check both
if (role === "admin" || role === "super_admin") {
  // Both admin and super_admin have access
}
```

---

## Role Aliases (Backend Only)
Backend automatically normalizes these:
- `superadmin` → `super_admin`
- `super-admin` → `super_admin`
- `administrator` → `admin`
- `ops` → `manager`

**Note**: Frontend should use canonical names only.

---

## Updated Files
1. ✅ `frontend/src/pages/admin/AdminUsers.jsx` - ROLE_DISPLAY updated
2. ✅ `frontend/src/pages/admin/AdminPanel.jsx` - isAdmin/isSuperAdmin fixed
3. ✅ `frontend/src/stores/useEntitlements.js` - isSuperAdmin fixed
4. ✅ `frontend/src/pages/UserSettings.jsx` - role display and checks fixed
5. ✅ `frontend/src/pages/Emails.jsx` - isAdmin check fixed

---

## Testing Checklist

### Frontend Tests
- [ ] Admin users page shows only 5 roles in dropdown
- [ ] Role filter works with all 5 roles
- [ ] Role badges display correct colors
- [ ] Create user with each role succeeds
- [ ] Edit user role succeeds
- [ ] No "owner" or "system_admin" appears anywhere

### Backend Tests
- [ ] User with role "super_admin" can access admin endpoints
- [ ] User with role "admin" can access admin endpoints
- [ ] User with role "manager" gets 403 on admin endpoints
- [ ] User with role "partner" has separate access scope
- [ ] Role normalization works (aliases converted)

### Integration Tests
- [ ] Login as super_admin → can access /admin/users
- [ ] Login as admin → can access /admin/users
- [ ] Login as manager → gets redirected from /admin/users
- [ ] Role hierarchy expansion works in RBAC
- [ ] Partner role isolated from internal hierarchy

---

## Support
For questions about roles, refer to:
- Backend: `backend/security/rbac.py`
- Documentation: `ROLES_VERIFICATION.md`
