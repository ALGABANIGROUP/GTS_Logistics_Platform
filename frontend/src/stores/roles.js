import { defineStore } from 'pinia'
import { Role, Permission } from '@/models/Role'
import * as rolesAPI from '@/api/roles'

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
