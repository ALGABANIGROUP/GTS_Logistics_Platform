<template>
  <div class="role-management-container">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-content">
        <h1 class="page-title">
          <i class="fas fa-user-tag"></i>
          Role & Permission Management
        </h1>
        <div class="header-stats">
          <div class="stat-item">
            <span class="stat-value">{{ stats.total }}</span>
            <span class="stat-label">Total Roles</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.system }}</span>
            <span class="stat-label">System</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.business }}</span>
            <span class="stat-label">Business</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ stats.default }}</span>
            <span class="stat-label">Default</span>
          </div>
        </div>
      </div>
      
      <div class="header-actions">
        <button @click="exportRoles" class="btn-secondary">
          <i class="fas fa-download"></i>
          Export
        </button>
        <button @click="showImportDialog = true" class="btn-secondary">
          <i class="fas fa-upload"></i>
          Import
        </button>
        <button @click="showCreateRole" class="btn-primary">
          <i class="fas fa-plus"></i>
          Create New Role
        </button>
      </div>
    </div>
    
    <!-- Toolbar -->
    <div class="toolbar">
      <!-- Search -->
      <div class="search-container">
        <i class="fas fa-search"></i>
        <input 
          v-model="searchQuery"
          @input="searchRoles"
          placeholder="Search for a role..."
          class="search-input"
        >
      </div>
      
      <!-- Filters -->
      <div class="filters">
        <div class="filter-group">
          <label>Type:</label>
          <select v-model="filters.type" @change="applyFilters">
            <option value="">All</option>
            <option value="system">System</option>
            <option value="business">Business</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Status:</label>
          <select v-model="filters.status" @change="applyFilters">
            <option value="">All</option>
            <option value="default">Default</option>
            <option value="custom">Custom</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Users:</label>
          <select v-model="filters.users" @change="applyFilters">
            <option value="">All</option>
            <option value="with_users">With Users</option>
            <option value="without_users">Without Users</option>
          </select>
        </div>
        
        <button @click="resetFilters" class="btn-link">
          <i class="fas fa-times"></i>
          Clear Filters
        </button>
      </div>
    </div>
    
    <!-- Roles Grid -->
    <div class="roles-grid" v-if="!loading">
      <div 
        v-for="role in filteredRoles"
        :key="role.id"
        class="role-card"
        :style="{ borderLeftColor: role.color }"
        @click="viewRole(role)"
      >
        <!-- Card Header -->
        <div class="role-card-header">
          <div class="role-info">
            <h3 class="role-name">{{ role.name }}</h3>
            <div class="role-meta">
              <span class="role-type" :style="{ backgroundColor: role.color }">
                {{ getRoleTypeName(role.type) }}
              </span>
              <span v-if="role.is_default" class="role-default">
                <i class="fas fa-star"></i> Default
              </span>
              <span class="role-level">
                Level: {{ role.level }}
              </span>
            </div>
          </div>
          
          <div class="role-users">
            <i class="fas fa-users"></i>
            <span class="user-count">{{ role.user_count }}</span>
          </div>
        </div>
        
        <!-- Role Description -->
        <p class="role-description">{{ role.description }}</p>
        
        <!-- Permissions -->
        <div class="role-permissions">
          <div class="permissions-header">
            <span class="permissions-count">
              {{ role.permissions.length }} permissions
            </span>
            <span class="permissions-level" :class="`level-${role.getPermissionLevel()}`">
              {{ getPermissionLevelName(role.getPermissionLevel()) }}
            </span>
          </div>
          
          <div class="permissions-preview">
            <span 
              v-for="perm in getPermissionPreview(role.permissions)" 
              :key="perm"
              class="permission-tag"
            >
              {{ perm }}
            </span>
            <span v-if="role.permissions.length > 3" class="more-permissions">
              +{{ role.permissions.length - 3 }} more
            </span>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="role-actions">
          <button 
            @click.stop="editRole(role)"
            class="btn-action"
            :disabled="!role.can_be_edited"
            :title="role.can_be_edited ? 'Edit Role' : 'This role cannot be edited'"
          >
            <i class="fas fa-edit"></i>
            Edit
          </button>
          
          <button 
            @click.stop="duplicateRole(role)"
            class="btn-action"
            title="Duplicate Role"
          >
            <i class="fas fa-copy"></i>
            Copy
          </button>
          
          <button 
            @click.stop="assignUsers(role)"
            class="btn-action"
          >
            <i class="fas fa-user-plus"></i>
            Assign
          </button>
          
          <div class="dropdown">
            <button class="btn-action more-actions">
              <i class="fas fa-ellipsis-v"></i>
            </button>
            <div class="dropdown-content">
              <a @click.stop="viewPermissions(role)" class="dropdown-item">
                <i class="fas fa-key"></i>
                View Permissions
              </a>
              <a @click.stop="exportRole(role)" class="dropdown-item">
                <i class="fas fa-download"></i>
                Export Role
              </a>
              <div class="dropdown-divider"></div>
              <a 
                @click.stop="deleteRole(role)"
                class="dropdown-item danger"
                :class="{ disabled: !role.can_be_deleted }"
              >
                <i class="fas fa-trash"></i>
                Delete
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading" class="loading-state">
      <i class="fas fa-spinner fa-spin"></i>
      <p>Loading roles...</p>
    </div>
    
    <!-- Empty State -->
    <div v-if="!loading && filteredRoles.length === 0" class="empty-state">
      <i class="fas fa-user-tag"></i>
      <p>No roles to display</p>
      <button @click="showCreateRole" class="btn-primary">
        <i class="fas fa-plus"></i>
        Create First Role
      </button>
    </div>
    
    <!-- Modals -->
    <RoleForm 
      v-if="showRoleForm"
      :role="selectedRole"
      @save="handleRoleSave"
      @close="closeRoleForm"
    />
    
    <!-- Delete Confirmation -->
    <div v-if="roleToDelete" class="modal-overlay" @click.self="roleToDelete = null">
      <div class="modal-container confirmation-modal">
        <div class="modal-header">
          <h2 class="modal-title">
            <i class="fas fa-exclamation-triangle text-red-500"></i>
            Delete Role
          </h2>
          <button @click="roleToDelete = null" class="modal-close">
            <i class="fas fa-times"></i>
          </button>
        </div>
        
        <div class="modal-body">
          <p class="confirmation-message">
            Are you sure you want to delete the role <strong>{{ roleToDelete.name }}</strong>?
          </p>
          <p class="warning-message">
            This action cannot be undone.
          </p>
        </div>
        
        <div class="modal-footer">
          <button @click="roleToDelete = null" class="btn-secondary">
            Cancel
          </button>
          <button @click="confirmDeleteRole" class="btn-danger">
            <i class="fas fa-trash"></i>
            Delete Role
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRolesStore } from '@/stores/roles'
import RoleForm from './RoleForm.vue'

// Store
const rolesStore = useRolesStore()

// State
const searchQuery = ref('')
const filters = ref({
  type: '',
  status: '',
  users: ''
})
const showRoleForm = ref(false)
const roleToDelete = ref(null)
const showImportDialog = ref(false)
const selectedRole = ref(null)

// Computed
const loading = computed(() => rolesStore.loading)
const allRoles = computed(() => rolesStore.roles)
const stats = computed(() => {
  const roles = allRoles.value
  return {
    total: roles.length,
    system: roles.filter(r => r.type === 'system').length,
    business: roles.filter(r => r.type === 'business').length,
    custom: roles.filter(r => r.type === 'custom').length,
    default: roles.filter(r => r.is_default).length,
    with_users: roles.filter(r => r.user_count > 0).length,
    without_users: roles.filter(r => r.user_count === 0).length
  }
})

// Filtered roles
const filteredRoles = computed(() => {
  let results = allRoles.value
  
  // Text search
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    results = results.filter(role =>
      role.name.toLowerCase().includes(query) ||
      role.description.toLowerCase().includes(query) ||
      role.id.toLowerCase().includes(query)
    )
  }
  
  // Type filter
  if (filters.value.type) {
    results = results.filter(role => role.type === filters.value.type)
  }
  
  // Status filter
  if (filters.value.status === 'default') {
    results = results.filter(role => role.is_default)
  } else if (filters.value.status === 'custom') {
    results = results.filter(role => !role.is_default)
  }
  
  // Users filter
  if (filters.value.users === 'with_users') {
    results = results.filter(role => role.user_count > 0)
  } else if (filters.value.users === 'without_users') {
    results = results.filter(role => role.user_count === 0)
  }
  
  return results.sort((a, b) => b.level - a.level)
})

// Helper functions
const getRoleTypeName = (type) => {
  const types = {
    system: 'System',
    business: 'Business',
    custom: 'Custom'
  }
  return types[type] || type
}

const getPermissionLevelName = (level) => {
  const levels = {
    full: 'Full Access',
    high: 'High',
    medium: 'Medium',
    low: 'Limited',
    none: 'No Permissions'
  }
  return levels[level] || level
}

const getPermissionPreview = (permissions) => {
  return permissions.slice(0, 3).map(perm => {
    const parts = perm.split('.')
    return parts[1] || parts[0]
  })
}

// Event handlers
const searchRoles = () => {
  // Search with debounce in real implementation
}

const applyFilters = () => {
  // Apply filters
}

const resetFilters = () => {
  filters.value = {
    type: '',
    status: '',
    users: ''
  }
  searchQuery.value = ''
}

const showCreateRole = () => {
  selectedRole.value = null
  showRoleForm.value = true
}

const viewRole = (role) => {
  console.log('View role:', role)
}

const editRole = (role) => {
  if (role.can_be_edited) {
    selectedRole.value = role
    showRoleForm.value = true
  }
}

const duplicateRole = async (role) => {
  try {
    const newName = prompt('Enter new role name:', `${role.name} (Copy)`)
    if (newName) {
      await rolesStore.duplicateRole(role.id, newName)
      alert('Role duplicated successfully')
    }
  } catch (error) {
    alert(`Error: ${error.message}`)
  }
}

const assignUsers = (role) => {
  console.log('Assign users to:', role)
}

const viewPermissions = (role) => {
  console.log('View permissions for:', role)
}

const exportRole = (role) => {
  const dataStr = JSON.stringify(role, null, 2)
  const blob = new Blob([dataStr], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `role_${role.id}_${new Date().toISOString().split('T')[0]}.json`
  link.click()
}

const deleteRole = (role) => {
  if (role.can_be_deleted) {
    roleToDelete.value = role
  } else {
    alert('This role cannot be deleted')
  }
}

const confirmDeleteRole = async () => {
  try {
    await rolesStore.deleteRole(roleToDelete.value.id)
    alert('Role deleted successfully')
    roleToDelete.value = null
  } catch (error) {
    alert(`Error: ${error.message}`)
  }
}

const handleRoleSave = async (roleData) => {
  try {
    if (roleData.id && rolesStore.getRoleById(roleData.id)) {
      await rolesStore.updateRole(roleData.id, roleData)
    } else {
      await rolesStore.createRole(roleData)
    }
    closeRoleForm()
    alert('Role saved successfully')
  } catch (error) {
    alert(`Error: ${error.message}`)
  }
}

const closeRoleForm = () => {
  showRoleForm.value = false
  selectedRole.value = null
}

const exportRoles = () => {
  rolesStore.exportRoles('json')
}

// Lifecycle
onMounted(() => {
  rolesStore.fetchRoles()
})
</script>

<style scoped>
.role-management-container {
  padding: 24px;
  background: #f8fafc;
  min-height: 100vh;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.header-content {
  flex: 1;
}

.page-title {
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.header-stats {
  display: flex;
  gap: 24px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.stat-value {
  font-size: 24px;
  font-weight: 700;
  color: #3b82f6;
}

.stat-label {
  font-size: 14px;
  color: #64748b;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* Toolbar */
.toolbar {
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.search-container {
  position: relative;
  max-width: 400px;
}

.search-container .fa-search {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
}

.search-input {
  width: 100%;
  padding: 10px 40px 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-group label {
  font-weight: 500;
  color: #475569;
  white-space: nowrap;
}

.filter-group select {
  padding: 6px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: white;
  min-width: 120px;
}

/* Roles Grid */
.roles-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 20px;
}

.role-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  border-left: 4px solid;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.role-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.role-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.role-info {
  flex: 1;
}

.role-name {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 8px;
}

.role-meta {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.role-type {
  padding: 2px 8px;
  border-radius: 12px;
  color: white;
  font-size: 12px;
  font-weight: 500;
}

.role-default {
  padding: 2px 8px;
  border-radius: 12px;
  background: #fef3c7;
  color: #92400e;
  font-size: 12px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 4px;
}

.role-level {
  padding: 2px 8px;
  border-radius: 12px;
  background: #dbeafe;
  color: #1e40af;
  font-size: 12px;
  font-weight: 500;
}

.role-users {
  display: flex;
  align-items: center;
  gap: 6px;
  color: #64748b;
}

.user-count {
  font-weight: 600;
  color: #475569;
}

.role-description {
  color: #64748b;
  font-size: 14px;
  line-height: 1.5;
  margin: 0;
}

/* Permissions */
.role-permissions {
  background: #f8fafc;
  padding: 12px;
  border-radius: 6px;
}

.permissions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.permissions-count {
  font-size: 14px;
  color: #64748b;
}

.permissions-level {
  font-size: 12px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
}

.permissions-level.level-full {
  background: #dcfce7;
  color: #166534;
}

.permissions-level.level-high {
  background: #dbeafe;
  color: #1e40af;
}

.permissions-level.level-medium {
  background: #fef3c7;
  color: #92400e;
}

.permissions-level.level-low {
  background: #f3f4f6;
  color: #374151;
}

.permissions-level.level-none {
  background: #f3f4f6;
  color: #6b7280;
}

.permissions-preview {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.permission-tag {
  padding: 4px 8px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 4px;
  font-size: 12px;
  color: #475569;
}

.more-permissions {
  font-size: 12px;
  color: #94a3b8;
}

/* Actions */
.role-actions {
  display: flex;
  gap: 8px;
  margin-top: auto;
}

.btn-action {
  padding: 8px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 4px;
  background: white;
  color: #475569;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.2s;
}

.btn-action:hover {
  background: #f1f5f9;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dropdown {
  position: relative;
}

.dropdown-content {
  display: none;
  position: absolute;
  left: 0;
  background: white;
  min-width: 180px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  border-radius: 6px;
  z-index: 100;
  border: 1px solid #e2e8f0;
}

.dropdown:hover .dropdown-content {
  display: block;
}

.dropdown-item {
  padding: 10px 16px;
  display: flex;
  align-items: center;
  gap: 8px;
  color: #475569;
  text-decoration: none;
  cursor: pointer;
  transition: background 0.2s;
}

.dropdown-item:hover {
  background: #f8fafc;
}

.dropdown-item.danger {
  color: #ef4444;
}

.dropdown-item.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dropdown-divider {
  height: 1px;
  background: #e2e8f0;
  margin: 4px 0;
}

/* States */
.loading-state,
.empty-state {
  padding: 48px;
  text-align: center;
  color: #64748b;
}

.loading-state i {
  font-size: 32px;
  margin-bottom: 16px;
  color: #3b82f6;
}

.empty-state i {
  font-size: 48px;
  margin-bottom: 16px;
  color: #cbd5e1;
}

/* Buttons */
.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  padding: 10px 20px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-link {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.btn-link:hover {
  color: #475569;
}

.btn-danger {
  background: #ef4444;
  color: white;
  padding: 10px 20px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  transition: background 0.2s;
}

.btn-danger:hover {
  background: #dc2626;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 100%;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-title {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: #1e293b;
  display: flex;
  align-items: center;
  gap: 12px;
}

.modal-close {
  background: none;
  border: none;
  font-size: 20px;
  color: #94a3b8;
  cursor: pointer;
  padding: 8px;
  border-radius: 4px;
}

.modal-close:hover {
  background: #f1f5f9;
}

.modal-body {
  padding: 24px;
}

.confirmation-message {
  font-size: 16px;
  color: #475569;
  margin-bottom: 12px;
}

.warning-message {
  font-size: 14px;
  color: #ef4444;
  padding: 12px;
  background: #fef2f2;
  border-radius: 6px;
  border: 1px solid #fee2e2;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 24px;
  border-top: 1px solid #e2e8f0;
}

/* Responsive */
@media (max-width: 768px) {
  .roles-grid {
    grid-template-columns: 1fr;
  }
  
  .page-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
  
  .filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    justify-content: space-between;
  }
}
</style>
