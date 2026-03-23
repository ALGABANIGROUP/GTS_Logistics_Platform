// Role Model
export class Role {
    constructor(data = {}) {
        this.id = data.id || `role_${Date.now()}`
        this.name = data.name || ''
        this.description = data.description || ''
        this.type = data.type || 'custom' // system, business, custom
        this.permissions = data.permissions || []
        this.color = data.color || this.generateColor()
        this.level = data.level || 0 // Numeric level (0-100)
        this.is_default = data.is_default || false
        this.can_be_edited = data.can_be_edited !== undefined ? data.can_be_edited : true
        this.can_be_deleted = data.can_be_deleted !== undefined ? data.can_be_deleted : true
        this.user_count = data.user_count || 0
        this.created_at = data.created_at || new Date().toISOString()
        this.updated_at = data.updated_at || new Date().toISOString()
        this.created_by = data.created_by || null
    }

    generateColor() {
        const colors = [
            '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444',
            '#06B6D4', '#84CC16', '#EC4899', '#6366F1', '#14B8A6'
        ]
        return colors[Math.floor(Math.random() * colors.length)]
    }

    hasPermission(permissionId) {
        if (this.permissions.includes('*')) {
            return true
        }
        return this.permissions.includes(permissionId)
    }

    hasAnyPermission(permissionIds) {
        if (this.permissions.includes('*')) {
            return true
        }
        return permissionIds.some(perm => this.permissions.includes(perm))
    }

    hasAllPermissions(permissionIds) {
        if (this.permissions.includes('*')) {
            return true
        }
        return permissionIds.every(perm => this.permissions.includes(perm))
    }

    // Add permission
    addPermission(permissionId) {
        if (!this.permissions.includes(permissionId)) {
            this.permissions.push(permissionId)
            this.updated_at = new Date().toISOString()
        }
    }

    // Remove permission
    removePermission(permissionId) {
        const index = this.permissions.indexOf(permissionId)
        if (index > -1) {
            this.permissions.splice(index, 1)
            this.updated_at = new Date().toISOString()
        }
    }

    // Get permission level info
    getPermissionLevel() {
        if (this.permissions.includes('*')) return 'full'
        if (this.permissions.length > 20) return 'high'
        if (this.permissions.length > 10) return 'medium'
        if (this.permissions.length > 0) return 'low'
        return 'none'
    }
}

// Permission Model
export class Permission {
    constructor(data = {}) {
        this.id = data.id || ''
        this.name = data.name || ''
        this.description = data.description || ''
        this.module = data.module || ''
        this.category = data.category || ''
        this.is_dangerous = data.is_dangerous || false
        this.requires_approval = data.requires_approval || false
        this.created_at = data.created_at || new Date().toISOString()
    }
}
