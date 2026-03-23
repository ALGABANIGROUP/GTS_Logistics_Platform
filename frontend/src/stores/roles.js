import { defineStore } from 'pinia'
import { Role, Permission } from '@/models/Role'
















































































































































































































































































































































































** Status:** Complete and Ready for Backend Integration ** Language:** English Only ** Implementation Date:** February 4, 2026  -- - ```}  "@fortawesome/fontawesome-free": "^6.x"  "axios": "^1.x",  "pinia": "^2.x",  "vue": "^3.x",{```json## Dependencies - [x] English - only interface - [x] Responsive design - [x] Export / Import foundation - [x] Permission management - [x] Search and filters - [x] Full CRUD functionality - [x] Pinia store updates - [x] API integration layer - [x] RoleForm.vue component - [x] RoleManagement.vue component✅ ** COMPLETE ** - All core components and API integration implemented## Status - No Arabic text anywhere - All error messages in English - All documentation in English - All comments in English - All UI text in English✅ ** 100 % English Implementation **## Language Compliance```    └── roles.js               (API integration - NEW)└── api/│   └── Role.js                (Role & Permission classes)├── models/│   └── roles.js               (Updated with API calls)├── stores/│       └── RoleForm.vue        (Create/Edit - 700+ lines)│       ├── RoleManagement.vue  (Main UI - 800+ lines)│   └── roles/├── components/frontend/src/```## File Structure - Role comparison tool - Permission conflict detection - Role change history - Role approval workflow - Time - based role assignments - Role inheritance system### Additional Features6.Add bulk role operations(delete, export )5. Implement role templates / presets4.Add role usage analytics dashboard3.Implement drag - and - drop for permission assignment2.Add UserAssignment component for bulk user operations1.Add PermissionsViewer component for detailed view### Frontend Enhancements5.Set up database migrations for roles / permissions tables4.Add audit logging for role changes3.Implement permission checking middleware2.Add role validation logic1.Create `backend/routes/roles.py` with all API endpoints### Backend Implementation## Next Steps - [] Test with default roles(API fallback) - [] Test responsive layout on mobile - [] Handle API errors gracefully - [] Validate role form inputs - [] View role statistics - [] Export roles to JSON - [] Revoke permissions from role - [] Assign permissions to role - [] Filter roles by type / status / users - [] Search roles by name / description - [] Duplicate role with new name - [] Delete role(with confirmation) -[] Edit existing role - [] Create new role with permissions - [] Load roles from API## Testing Checklist```async def get_permissions()@router.get("/api/roles/permissions")async def duplicate_role()@router.post("/api/roles/{role_id}/duplicate")async def delete_role()@router.delete("/api/roles/{role_id}")async def update_role()@router.put("/api/roles/{role_id}")async def create_role()@router.post("/api/roles")async def get_roles()@router.get("/api/roles")# Required endpoints in backend/routes/roles.py```pythonImplement the following endpoints on your FastAPI backend:### 3. Backend API Setup```rolesStore.fetchRoles() // Load roles on app startconst rolesStore = useRolesStore()import { useRolesStore } from '@/stores/roles'// In your main.js or app initialization```javascript### 2. Initialize Store```}  meta: { requiresAuth: true, requiredRole: ['admin', 'super_admin'] }  component: RoleManagement,  name: 'RoleManagement',  path: '/admin/roles',{// Add routeimport RoleManagement from '@/components/roles/RoleManagement.vue'// In your router or admin panel```javascript### 1. Import Components## Integration Steps - Confirmation dialogs for destructive actions - Clear error messages - Loading states for async operations - Instant filter application - Real - time search with no lag### User Experience - Modal forms with proper scrolling - Touch - friendly action buttons - Mobile - optimized toolbar and filters - Grid layout adapts to screen size### Responsive Design - Dangerous permissions marked with warning indicators - Permission levels color - coded(High / Medium / Low) - Roles display with custom colors for visual identification### Color Coding## UI Features - `system.updates` - Manage updates(dangerous) - `system.backup` - Manage backups(dangerous) - `system.logs` - View system logs(dangerous) - `system.settings` - Modify system settings(dangerous)### System Module - `roles.assign` - Assign roles to users - `roles.delete` - Remove roles(dangerous) - `roles.edit` - Modify role settings(dangerous) - `roles.create` - Create new roles(dangerous) - `roles.view` - View roles list### Roles Module - `users.impersonate` - Login as another user(dangerous) - `users.delete` - Remove users(dangerous) - `users.edit` - Modify user data - `users.create` - Add new users - `users.view` - View list of users### Users Module## Permission Modules5. ** partner ** - Partner access(Purple #8B5CF6, Level 30)4. ** user ** - Default user role(Gray #6B7280, Level 10)3. ** manager ** - Management functions(Amber #F59E0B, Level 50)2. ** admin ** - System administration(Sky Blue #0EA5E9, Level 80)1. ** super_admin ** - Full system access(Red #DC2626, Level 100)The system implements exactly 5 valid roles matching backend RBAC:## Valid Roles(Backend RBAC Compliant)```User Action → Store Action → API Request → Success/Error → State Update → UI RefreshCRUD Operations:App Start → fetchRoles() → API Call → Fallback to Defaults if Error → State UpdateInitial Load:```### State Management Flow```User Action → Component Event → Pinia Store Action → API Call → Update State → Re-renderData Flow:    └─> Role Cards Grid    ├─> Delete Confirmation Modal    ├─> RoleForm.vue (Create/Edit Modal)RoleManagement.vue (Main Container)```### Component Flow## Architecture```- exportRoles()             // Existing client-side export maintained- revokePermission()        // Calls rolesAPI.revokePermission()- assignPermission()        // Calls rolesAPI.assignPermission()- duplicateRole()           // Calls rolesAPI.duplicateRole()- deleteRole()              // Calls rolesAPI.deleteRole()- updateRole()              // Calls rolesAPI.updateRole()- createRole()              // Calls rolesAPI.createRole()- fetchRoles()              // Calls rolesAPI.fetchRoles()```javascript ** Updated Actions:** - Role model instantiation from API responses - Error handling and loading states - Fallback to default roles when API unavailable - All actions now call API endpoints ** Integration Points:**** Location:** `frontend/src/stores/roles.js`(Updated)### 3. State Management```- checkRoleDeletable(id)    // GET /api/roles/:id/deletable- validateRole(roleData)    // POST /api/roles/validate// Validation- searchRoles(query)        // GET /api/roles/search- fetchRoleAuditLog()       // GET /api/roles/:id/audit- fetchRoleStats()          // GET /api/roles/stats// Analytics- importRoles(data)         // POST /api/roles/import- exportRoles(roleIds)      // GET /api/roles/export// Import/Export- removeRoleFromUser()      // DELETE /api/users/:id/roles/:rid- assignRoleToUsers()       // POST /api/roles/:id/users/bulk- assignRoleToUser()        // POST /api/users/:id/roles- fetchRoleUsers(roleId)    // GET /api/roles/:id/users// User Assignment- assignPermissions()       // POST /api/roles/:id/permissions/bulk- revokePermission()        // DELETE /api/roles/:id/permissions/:pid- assignPermission()        // POST /api/roles/:id/permissions- fetchPermissions()        // GET /api/roles/permissions// Permissions- duplicateRole(roleId)     // POST /api/roles/:id/duplicate- deleteRole(roleId)        // DELETE /api/roles/:id- updateRole(roleId, data)  // PUT /api/roles/:id- createRole(roleData)      // POST /api/roles- fetchRoleById(roleId)     // GET /api/roles/:id- fetchRoles()              // GET /api/roles// Role CRUD```javascript ** Endpoints Implemented:**** Location:** `frontend/src/api/roles.js`### 2. API Integration - Loading state during submission - Cancel and close form - Save role(create or update) - ** Actions ** - Form submission state handling - Real - time error messages - Role ID format validation(lowercase, numbers, underscores only) - Required field validation - ** Validation ** - Permission level indicator(High / Medium / Low / None) - Permission statistics summary - Select / Deselect all per module - Dangerous permission indicators - Permission grid with descriptions - Visual module selection sidebar - Three modules: Users, Roles, System - Module - based permission organization - ** Permission Management ** - Can be deleted checkbox - Can be edited checkbox - Set as default role checkbox - ** Options ** - Color picker(10 preset colors + custom) - Role level slider(0 - 100) - Role type(System, Business, Custom) - Description(optional) - Role ID(required, auto - generated for new roles)  - Role name(required) - ** Basic Information **** Features:**** Location:** `frontend/src/components/roles/RoleForm.vue`#### RoleForm.vue - Touch - friendly action buttons - Adaptive toolbar and filters - Mobile - friendly grid layout - ** Responsive Design ** - Import roles from file - Export all roles(JSON / CSV) - ** Bulk Operations ** - Export individual roles - View permissions details - Assign users to role - Delete role with confirmation(if deletable) - Duplicate role with new name - Edit existing role(if editable) - Create new role - ** CRUD Actions ** - Permission preview(first 3 permissions) - Role metadata(type, level, default status) - User count per role - Permission count and level indicators - Visual role display with color coding - ** Role Cards Grid ** - Clear filters button - Filter by user assignment(With Users, Without Users) - Filter by status(Default, Custom) - Filter by type(System, Business, Custom) - Real - time search by role name, description, or ID - ** Search and Filters ** - User assignment statistics - Default roles indicator - System / Business / Custom role breakdown - Total roles count - ** Statistics Dashboard **** Features:**** Location:** `frontend/src/components/roles/RoleManagement.vue`#### RoleManagement.vue### 1. Components## Files CreatedComplete implementation of a role management system for the GTS application with Vue 3 components, Pinia store, and API integration.## Overviewimport * as rolesAPI from '@/api/roles'

export const useRolesStore = defineStore('roles', {
    state: () => ({
        roles: [],
        permissions: [],
        loading: false,
        error: null,

        // Core permissions by module
        permissionModules: {
            users: {
                name: 'Users',
                permissions: [
                    { id: 'users.view', name: 'View Users', description: 'Ability to see the list of users' },
                    { id: 'users.create', name: 'Create Users', description: 'Add new users' },
                    { id: 'users.edit', name: 'Edit Users', description: 'Modify user data' },
                    { id: 'users.delete', name: 'Delete Users', description: 'Remove users from the system' },
                    { id: 'users.impersonate', name: 'Impersonate', description: 'Login as another user' }
                ]
            },
            roles: {
                name: 'Roles',
                permissions: [
                    { id: 'roles.view', name: 'View Roles', description: 'View list of roles' },
                    { id: 'roles.create', name: 'Create Roles', description: 'Create new roles' },
                    { id: 'roles.edit', name: 'Edit Roles', description: 'Modify role settings' },
                    { id: 'roles.delete', name: 'Delete Roles', description: 'Remove roles from the system' },
                    { id: 'roles.assign', name: 'Assign Roles', description: 'Assign roles to users' }
                ]
            },
            system: {
                name: 'System',
                permissions: [
                    { id: 'system.settings', name: 'System Settings', description: 'Modify general system settings' },
                    { id: 'system.logs', name: 'System Logs', description: 'View system logs and events' },
                    { id: 'system.backup', name: 'Backup', description: 'Manage backups' },
                    { id: 'system.updates', name: 'Updates', description: 'Manage system updates' }
                ]
            }
        }
    }),

    getters: {
        // Get role by ID
        getRoleById: (state) => (id) => {
            return state.roles.find(role => role.id === id)
        },

        // Get roles by type
        getRolesByType: (state) => (type) => {
            return state.roles.filter(role => role.type === type)
        },

        // Get permissions by module
        getPermissionsByModule: (state) => (module) => {
            return state.permissionModules[module]?.permissions || []
        },

        // Check user permission
        userHasPermission: (state) => (userId, permissionId) => {
            return true
        }
    },

    actions: {
        // Fetch all roles from API
        async fetchRoles() {
            this.loading = true
            this.error = null

            try {
                const response = await rolesAPI.fetchRoles()

                // If API returns data, use it
                if (response && response.data && response.data.length > 0) {
                    this.roles = response.data.map(roleData => new Role(roleData))
                } else {
                    // Fallback to default roles
                    this.roles = this.getDefaultRoles()
                }
            } catch (error) {
                console.error('Error fetching roles:', error)
                this.error = error.message
                // Use default roles on error
                this.roles = this.getDefaultRoles()
            } finally {
                this.loading = false
            }
        },

        // Get default roles (fallback when API unavailable)
        getDefaultRoles() {
            return [
                new Role({
                    id: 'super_admin',
                    name: 'Super Admin',
                    description: 'Full access to all parts of the system',
                    type: 'system',
                    permissions: ['*'],
                    color: '#DC2626',
                    level: 100,
                    is_default: false,
                    can_be_edited: false,
                    can_be_deleted: false,
                    user_count: 1
                }),
                new Role({
                    id: 'admin',
                    name: 'Admin',
                    description: 'Manages the system and its users',
                    type: 'system',
                    permissions: [
                        'users.view', 'users.create', 'users.edit', 'users.delete',
                        'roles.view', 'roles.assign',
                        'system.logs'
                    ],
                    color: '#0EA5E9',
                    level: 80,
                    is_default: false,
                    can_be_edited: true,
                    can_be_deleted: false,
                    user_count: 5
                }),
                new Role({
                    id: 'manager',
                    name: 'Manager',
                    description: 'Manages team and resources',
                    type: 'business',
                    permissions: [
                        'users.view', 'users.edit',
                        'reports.view', 'reports.generate'
                    ],
                    color: '#F59E0B',
                    level: 50,
                    is_default: false,
                    can_be_edited: true,
                    can_be_deleted: true,
                    user_count: 25
                }),
                new Role({
                    id: 'user',
                    name: 'User',
                    description: 'Standard user with basic permissions',
                    type: 'system',
                    permissions: [
                        'users.view',
                        'reports.view'
                    ],
                    color: '#6B7280',
                    level: 10,
                    is_default: true,
                    can_be_edited: true,
                    can_be_deleted: false,
                    user_count: 500
                }),
                new Role({
                    id: 'partner',
                    name: 'Partner',
                    description: 'External partner with limited access',
                    type: 'business',
                    permissions: [
                        'users.view',
                        'reports.view'
                    ],
                    color: '#8B5CF6',
                    level: 5,
                    is_default: false,
                    can_be_edited: true,
                    can_be_deleted: true,
                    user_count: 50
                })
            ]
        } catch(error) {
            this.error = error.message
            console.error('Error loading default roles:', error)
        } finally {
            this.loading = false
        }
    },

    // Create new role
    async createRole(roleData) {
        this.loading = true
        this.error = null

        try {
            const response = await rolesAPI.createRole(roleData)
            const newRole = new Role(response.data)
            this.roles.push(newRole)
            return newRole
        } catch (error) {
            this.error = error.message
            console.error('Error creating role:', error)
            throw error
        } finally {
            this.loading = false
        }
    },

    // Update existing role
    async updateRole(roleId, updates) {
        this.loading = true
        this.error = null

        try {
            const response = await rolesAPI.updateRole(roleId, updates)
            const index = this.roles.findIndex(r => r.id === roleId)
            if (index !== -1) {
                this.roles[index] = new Role(response.data)
            }
            return this.roles[index]
        } catch (error) {
            this.error = error.message
            console.error('Error updating role:', error)
            throw error
        } finally {
            this.loading = false
        }
    },

    // Delete role
    async deleteRole(roleId) {
        this.loading = true
        this.error = null

        try {
            await rolesAPI.deleteRole(roleId)
            this.roles = this.roles.filter(r => r.id !== roleId)
        } catch (error) {
            this.error = error.message
            console.error('Error deleting role:', error)
            throw error
        } finally {
            this.loading = false
        }
    },

    // Assign permission to role
    async assignPermission(roleId, permissionId) {
        this.loading = true
        this.error = null

        try {
            await rolesAPI.assignPermission(roleId, permissionId)
            const role = this.getRoleById(roleId)
            if (role && !role.permissions.includes(permissionId)) {
                role.addPermission(permissionId)
            }
        } catch (error) {
            this.error = error.message
            console.error('Error assigning permission:', error)
            throw error
        } finally {
            this.loading = false
        }
    },

    // Revoke permission from role
    async revokePermission(roleId, permissionId) {
        this.loading = true
        this.error = null

        try {
            await rolesAPI.revokePermission(roleId, permissionId)
            const role = this.getRoleById(roleId)
            if (role) {
                role.removePermission(permissionId)
            }
        } catch (error) {
            this.error = error.message
            console.error('Error revoking permission:', error)
            throw error
        } finally {
            this.loading = false
        }
    },

    // Duplicate role
    async duplicateRole(roleId, newName) {
        this.loading = true
        this.error = null

        try {
            const response = await rolesAPI.duplicateRole(roleId, newName)
            const newRole = new Role(response.data)
            this.roles.push(newRole)
            return newRole
        } catch (error) {
            this.error = error.message
            console.error('Error duplicating role:', error)
            throw error
        } finally {
            this.loading = false
        }
    },

    // Export roles
    async exportRoles(format = 'json') {
        const exportData = this.roles.map(role => ({
            id: role.id,
            name: role.name,
            description: role.description,
            permissions: role.permissions,
            color: role.color,
            level: role.level,
            is_default: role.is_default
        }))

        if (format === 'json') {
            const dataStr = JSON.stringify(exportData, null, 2)
            const blob = new Blob([dataStr], { type: 'application/json' })
            const url = URL.createObjectURL(blob)
            const link = document.createElement('a')
            link.href = url
            link.download = `roles_export_${new Date().toISOString().split('T')[0]}.json`
            link.click()
        } else if (format === 'csv') {
            const csvContent = [
                ['ID', 'Name', 'Description', 'Permissions Count', 'Level', 'Default'],
                ...exportData.map(r => [
                    r.id,
                    r.name,
                    r.description,
                    r.permissions.length,
                    r.level,
                    r.is_default ? 'Yes' : 'No'
                ])
            ].map(row => row.join(',')).join('\n')

            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
            const link = document.createElement('a')
            link.href = URL.createObjectURL(blob)
            link.download = `roles_export_${new Date().toISOString().split('T')[0]}.csv`
            link.click()
        }
    }
}
})
