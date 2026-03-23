/**
 * Roles API Integration
 * Handles all HTTP requests related to role management
 */

import api from './axios'

// Base endpoint
const ROLES_ENDPOINT = '/api/roles'

/**
 * Fetch all roles
 * @returns {Promise} List of all roles
 */
export const fetchRoles = async () => {
    try {
        const response = await api.get(ROLES_ENDPOINT)
        return response.data
    } catch (error) {
        console.error('Error fetching roles:', error)
        throw error
    }
}

/**
 * Fetch a single role by ID
 * @param {string} roleId - Role ID
 * @returns {Promise} Role data
 */
export const fetchRoleById = async (roleId) => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/${roleId}`)
        return response.data
    } catch (error) {
        console.error(`Error fetching role ${roleId}:`, error)
        throw error
    }
}

/**
 * Create a new role
 * @param {Object} roleData - Role data
 * @returns {Promise} Created role
 */
export const createRole = async (roleData) => {
    try {
        const response = await api.post(ROLES_ENDPOINT, roleData)
        return response.data
    } catch (error) {
        console.error('Error creating role:', error)
        throw error
    }
}

/**
 * Update an existing role
 * @param {string} roleId - Role ID
 * @param {Object} roleData - Updated role data
 * @returns {Promise} Updated role
 */
export const updateRole = async (roleId, roleData) => {
    try {
        const response = await api.put(`${ROLES_ENDPOINT}/${roleId}`, roleData)
        return response.data
    } catch (error) {
        console.error(`Error updating role ${roleId}:`, error)
        throw error
    }
}

/**
 * Delete a role
 * @param {string} roleId - Role ID
 * @returns {Promise} Deletion confirmation
 */
export const deleteRole = async (roleId) => {
    try {
        const response = await api.delete(`${ROLES_ENDPOINT}/${roleId}`)
        return response.data
    } catch (error) {
        console.error(`Error deleting role ${roleId}:`, error)
        throw error
    }
}

/**
 * Duplicate a role
 * @param {string} roleId - Role ID to duplicate
 * @param {string} newName - New role name
 * @returns {Promise} Created role
 */
export const duplicateRole = async (roleId, newName) => {
    try {
        const response = await api.post(`${ROLES_ENDPOINT}/${roleId}/duplicate`, {
            name: newName
        })
        return response.data
    } catch (error) {
        console.error(`Error duplicating role ${roleId}:`, error)
        throw error
    }
}

/**
 * Fetch all permissions
 * @returns {Promise} List of all available permissions
 */
export const fetchPermissions = async () => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/permissions`)
        return response.data
    } catch (error) {
        console.error('Error fetching permissions:', error)
        throw error
    }
}

/**
 * Assign a permission to a role
 * @param {string} roleId - Role ID
 * @param {string} permissionId - Permission ID
 * @returns {Promise} Updated role
 */
export const assignPermission = async (roleId, permissionId) => {
    try {
        const response = await api.post(`${ROLES_ENDPOINT}/${roleId}/permissions`, {
            permission_id: permissionId
        })
        return response.data
    } catch (error) {
        console.error(`Error assigning permission to role ${roleId}:`, error)
        throw error
    }
}

/**
 * Revoke a permission from a role
 * @param {string} roleId - Role ID
 * @param {string} permissionId - Permission ID
 * @returns {Promise} Updated role
 */
export const revokePermission = async (roleId, permissionId) => {
    try {
        const response = await api.delete(`${ROLES_ENDPOINT}/${roleId}/permissions/${permissionId}`)
        return response.data
    } catch (error) {
        console.error(`Error revoking permission from role ${roleId}:`, error)
        throw error
    }
}

/**
 * Assign multiple permissions to a role
 * @param {string} roleId - Role ID
 * @param {Array<string>} permissionIds - Array of permission IDs
 * @returns {Promise} Updated role
 */
export const assignPermissions = async (roleId, permissionIds) => {
    try {
        const response = await api.post(`${ROLES_ENDPOINT}/${roleId}/permissions/bulk`, {
            permission_ids: permissionIds
        })
        return response.data
    } catch (error) {
        console.error(`Error assigning permissions to role ${roleId}:`, error)
        throw error
    }
}

/**
 * Get all users with a specific role
 * @param {string} roleId - Role ID
 * @returns {Promise} List of users
 */
export const fetchRoleUsers = async (roleId) => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/${roleId}/users`)
        return response.data
    } catch (error) {
        console.error(`Error fetching users for role ${roleId}:`, error)
        throw error
    }
}

/**
 * Assign a role to a user
 * @param {string} userId - User ID
 * @param {string} roleId - Role ID
 * @returns {Promise} Updated user
 */
export const assignRoleToUser = async (userId, roleId) => {
    try {
        const response = await api.post(`/api/users/${userId}/roles`, {
            role_id: roleId
        })
        return response.data
    } catch (error) {
        console.error(`Error assigning role to user ${userId}:`, error)
        throw error
    }
}

/**
 * Assign a role to multiple users
 * @param {Array<string>} userIds - Array of user IDs
 * @param {string} roleId - Role ID
 * @returns {Promise} Assignment results
 */
export const assignRoleToUsers = async (userIds, roleId) => {
    try {
        const response = await api.post(`${ROLES_ENDPOINT}/${roleId}/users/bulk`, {
            user_ids: userIds
        })
        return response.data
    } catch (error) {
        console.error(`Error assigning role to users:`, error)
        throw error
    }
}

/**
 * Remove a role from a user
 * @param {string} userId - User ID
 * @param {string} roleId - Role ID
 * @returns {Promise} Updated user
 */
export const removeRoleFromUser = async (userId, roleId) => {
    try {
        const response = await api.delete(`/api/users/${userId}/roles/${roleId}`)
        return response.data
    } catch (error) {
        console.error(`Error removing role from user ${userId}:`, error)
        throw error
    }
}

/**
 * Export roles to JSON
 * @param {Array<string>} roleIds - Array of role IDs to export (empty = all)
 * @returns {Promise} Export data
 */
export const exportRoles = async (roleIds = []) => {
    try {
        const params = roleIds.length > 0 ? { role_ids: roleIds.join(',') } : {}
        const response = await api.get(`${ROLES_ENDPOINT}/export`, { params })
        return response.data
    } catch (error) {
        console.error('Error exporting roles:', error)
        throw error
    }
}

/**
 * Import roles from JSON
 * @param {Object} rolesData - Roles data to import
 * @returns {Promise} Import results
 */
export const importRoles = async (rolesData) => {
    try {
        const response = await api.post(`${ROLES_ENDPOINT}/import`, rolesData)
        return response.data
    } catch (error) {
        console.error('Error importing roles:', error)
        throw error
    }
}

/**
 * Get role statistics
 * @returns {Promise} Role statistics
 */
export const fetchRoleStats = async () => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/stats`)
        return response.data
    } catch (error) {
        console.error('Error fetching role statistics:', error)
        throw error
    }
}

/**
 * Get role audit log
 * @param {string} roleId - Role ID
 * @param {Object} options - Query options (page, limit, etc.)
 * @returns {Promise} Audit log entries
 */
export const fetchRoleAuditLog = async (roleId, options = {}) => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/${roleId}/audit`, {
            params: options
        })
        return response.data
    } catch (error) {
        console.error(`Error fetching audit log for role ${roleId}:`, error)
        throw error
    }
}

/**
 * Validate role data before creation/update
 * @param {Object} roleData - Role data to validate
 * @returns {Promise} Validation results
 */
export const validateRole = async (roleData) => {
    try {
        const response = await api.post(`${ROLES_ENDPOINT}/validate`, roleData)
        return response.data
    } catch (error) {
        console.error('Error validating role:', error)
        throw error
    }
}

/**
 * Check if a role can be deleted
 * @param {string} roleId - Role ID
 * @returns {Promise} Deletion eligibility info
 */
export const checkRoleDeletable = async (roleId) => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/${roleId}/deletable`)
        return response.data
    } catch (error) {
        console.error(`Error checking if role ${roleId} can be deleted:`, error)
        throw error
    }
}

/**
 * Search roles by query
 * @param {string} query - Search query
 * @param {Object} filters - Search filters
 * @returns {Promise} Search results
 */
export const searchRoles = async (query, filters = {}) => {
    try {
        const response = await api.get(`${ROLES_ENDPOINT}/search`, {
            params: { q: query, ...filters }
        })
        return response.data
    } catch (error) {
        console.error('Error searching roles:', error)
        throw error
    }
}

export default {
    fetchRoles,
    fetchRoleById,
    createRole,
    updateRole,
    deleteRole,
    duplicateRole,
    fetchPermissions,
    assignPermission,
    revokePermission,
    assignPermissions,
    fetchRoleUsers,
    assignRoleToUser,
    assignRoleToUsers,
    removeRoleFromUser,
    exportRoles,
    importRoles,
    fetchRoleStats,
    fetchRoleAuditLog,
    validateRole,
    checkRoleDeletable,
    searchRoles
}
