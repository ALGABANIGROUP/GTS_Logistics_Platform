<template>
  <div class="modal-overlay" @click.self="$emit('close')">
    <div class="modal-container">
      <div class="modal-header">
        <h2 class="modal-title">
          <i class="fas" :class="isEditing ? 'fa-edit' : 'fa-plus'"></i>
          {{ isEditing ? 'Edit Role' : 'Create New Role' }}
        </h2>
        <button @click="$emit('close')" class="modal-close">
          <i class="fas fa-times"></i>
        </button>
      </div>
      
      <form @submit.prevent="handleSubmit" class="role-form">
        <div class="form-section">
          <h3 class="section-title">Basic Information</h3>
          
          <div class="form-grid">
            <!-- Role Name -->
            <div class="form-group">
              <label for="roleName" class="form-label required">
                Role Name
              </label>
              <input
                type="text"
                id="roleName"
                v-model="form.name"
                required
                placeholder="Enter role name"
                class="form-input"
                :class="{ 'error': errors.name }"
              >
              <div v-if="errors.name" class="error-message">
                {{ errors.name }}
              </div>
            </div>
            
            <!-- Role ID -->
            <div class="form-group">
              <label for="roleId" class="form-label required">
                Role ID
              </label>
              <input
                type="text"
                id="roleId"
                v-model="form.id"
                required
                placeholder="e.g., admin, manager, etc."
                class="form-input"
                :class="{ 'error': errors.id }"
                :disabled="isEditing"
              >
              <div v-if="errors.id" class="error-message">
                {{ errors.id }}
              </div>
              <div class="form-hint">
                Used internally in the system, must be unique
              </div>
            </div>
          </div>
          
          <!-- Description -->
          <div class="form-group">
            <label for="roleDescription" class="form-label">
              Description
            </label>
            <textarea
              id="roleDescription"
              v-model="form.description"
              rows="3"
              placeholder="Brief description of the role and responsibilities"
              class="form-textarea"
            ></textarea>
          </div>
          
          <div class="form-grid">
            <!-- Role Type -->
            <div class="form-group">
              <label for="roleType" class="form-label required">
                Role Type
              </label>
              <select
                id="roleType"
                v-model="form.type"
                required
                class="form-select"
              >
                <option value="system">System</option>
                <option value="business">Business</option>
                <option value="custom">Custom</option>
              </select>
              <div class="form-hint">
                System: for system control, Business: for users, Custom: special use
              </div>
            </div>
            
            <!-- Role Level -->
            <div class="form-group">
              <label for="roleLevel" class="form-label required">
                Role Level
              </label>
              <input
                type="range"
                id="roleLevel"
                v-model="form.level"
                min="0"
                max="100"
                step="5"
                class="form-range"
              >
              <div class="range-value">
                <span class="value">{{ form.level }}</span>
                <div class="level-description">
                  <span v-if="form.level >= 80" class="high">High</span>
                  <span v-else-if="form.level >= 40" class="medium">Medium</span>
                  <span v-else class="low">Low</span>
                </div>
              </div>
              <div class="form-hint">
                Determines role priority in system (0-100)
              </div>
            </div>
          </div>
          
          <!-- Role Color -->
          <div class="form-group">
            <label class="form-label">Role Color</label>
            <div class="color-picker">
              <div 
                v-for="color in colorOptions"
                :key="color"
                class="color-option"
                :style="{ backgroundColor: color }"
                :class="{ selected: form.color === color }"
                @click="form.color = color"
              >
                <i v-if="form.color === color" class="fas fa-check"></i>
              </div>
              <input
                type="color"
                v-model="form.color"
                class="color-input"
              >
            </div>
          </div>
          
          <!-- Options -->
          <div class="form-group">
            <label class="form-label">Additional Options</label>
            <div class="form-options">
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="form.is_default"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                <span class="checkbox-text">Set as default role for new users</span>
              </label>
              
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="form.can_be_edited"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                <span class="checkbox-text">This role can be edited</span>
              </label>
              
              <label class="checkbox-label">
                <input
                  type="checkbox"
                  v-model="form.can_be_deleted"
                  class="checkbox-input"
                >
                <span class="checkbox-custom"></span>
                <span class="checkbox-text">This role can be deleted</span>
              </label>
            </div>
          </div>
        </div>
        
        <!-- Permissions Section -->
        <div class="form-section">
          <div class="section-header">
            <h3 class="section-title">Permissions</h3>
            <div class="section-actions">
              <button type="button" @click="selectAll" class="btn-link">
                Select All
              </button>
              <button type="button" @click="deselectAll" class="btn-link">
                Deselect All
              </button>
            </div>
          </div>
          
          <div class="permissions-container">
            <div class="modules-list">
              <div
                v-for="module in modules"
                :key="module.id"
                class="module-item"
                :class="{ active: activeModule === module.id }"
                @click="activeModule = module.id"
              >
                <div class="module-icon">
                  <i :class="module.icon"></i>
                </div>
                <div class="module-info">
                  <div class="module-name">{{ module.name }}</div>
                  <div class="module-count">
                    {{ getSelectedCount(module.id) }} / {{ module.permissions.length }}
                  </div>
                </div>
              </div>
            </div>
            
            <div class="permissions-list">
              <div v-if="activeModule" class="module-permissions">
                <div class="module-header">
                  <h4>{{ getModuleName(activeModule) }}</h4>
                  <div class="module-stats">
                    <span class="selected-count">
                      {{ getSelectedCount(activeModule) }} selected
                    </span>
                    <button
                      type="button"
                      @click="toggleModule(activeModule)"
                      class="btn-link"
                    >
                      {{ isModuleSelected(activeModule) ? 'Deselect All' : 'Select All' }}
                    </button>
                  </div>
                </div>
                
                <div class="permissions-grid">
                  <div
                    v-for="permission in getModulePermissions(activeModule)"
                    :key="permission.id"
                    class="permission-item"
                  >
                    <label class="checkbox-label permission-label">
                      <input
                        type="checkbox"
                        :value="permission.id"
                        v-model="form.permissions"
                        class="checkbox-input"
                      >
                      <span class="checkbox-custom"></span>
                      <div class="permission-info">
                        <div class="permission-name">{{ permission.name }}</div>
                        <div class="permission-description">
                          {{ permission.description }}
                        </div>
                      </div>
                    </label>
                    
                    <div class="permission-actions">
                      <span 
                        v-if="permission.is_dangerous" 
                        class="danger-badge"
                        title="Dangerous permission"
                      >
                        <i class="fas fa-exclamation-triangle"></i>
                      </span>
                    </div>
                  </div>
                </div>
              </div>
              
              <div v-else class="select-module">
                <i class="fas fa-key"></i>
                <p>Select a module from the list to view its permissions</p>
              </div>
            </div>
          </div>
          
          <div class="permissions-summary">
            <div class="summary-item">
              <span class="summary-label">Total Selected Permissions:</span>
              <span class="summary-value">{{ form.permissions.length }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Permission Level:</span>
              <span class="summary-value" :class="`level-${getPermissionLevel()}`">
                {{ getPermissionLevelName(getPermissionLevel()) }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Form Actions -->
        <div class="form-actions">
          <button type="button" @click="$emit('close')" class="btn-secondary">
            Cancel
          </button>
          <button type="submit" class="btn-primary" :disabled="submitting">
            <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
            {{ isEditing ? 'Update Role' : 'Create Role' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Role } from '@/models/Role'

const props = defineProps({
  role: Object
})

const emit = defineEmits(['save', 'close'])

// Form state
const form = ref({
  id: '',
  name: '',
  description: '',
  type: 'custom',
  permissions: [],
  color: '#3B82F6',
  level: 50,
  is_default: false,
  can_be_edited: true,
  can_be_deleted: true
})

const errors = ref({})
const submitting = ref(false)
const activeModule = ref('users')

// Options
const colorOptions = [
  '#3B82F6', '#10B981', '#8B5CF6', '#F59E0B', '#EF4444',
  '#06B6D4', '#84CC16', '#EC4899', '#6366F1', '#14B8A6'
]

// Permission modules
const modules = ref([
  {
    id: 'users',
    name: 'Users',
    icon: 'fas fa-users',
    permissions: [
      { id: 'users.view', name: 'View Users', description: 'View list of users', is_dangerous: false },
      { id: 'users.create', name: 'Create Users', description: 'Add new users', is_dangerous: false },
      { id: 'users.edit', name: 'Edit Users', description: 'Modify user data', is_dangerous: false },
      { id: 'users.delete', name: 'Delete Users', description: 'Remove users', is_dangerous: true },
      { id: 'users.impersonate', name: 'Impersonate', description: 'Login as another user', is_dangerous: true }
    ]
  },
  {
    id: 'roles',
    name: 'Roles',
    icon: 'fas fa-user-tag',
    permissions: [
      { id: 'roles.view', name: 'View Roles', description: 'View roles list', is_dangerous: false },
      { id: 'roles.create', name: 'Create Roles', description: 'Create new roles', is_dangerous: true },
      { id: 'roles.edit', name: 'Edit Roles', description: 'Modify role settings', is_dangerous: true },
      { id: 'roles.delete', name: 'Delete Roles', description: 'Remove roles', is_dangerous: true },
      { id: 'roles.assign', name: 'Assign Roles', description: 'Assign roles to users', is_dangerous: false }
    ]
  },
  {
    id: 'system',
    name: 'System',
    icon: 'fas fa-cogs',
    permissions: [
      { id: 'system.settings', name: 'System Settings', description: 'Modify system settings', is_dangerous: true },
      { id: 'system.logs', name: 'System Logs', description: 'View system logs', is_dangerous: true },
      { id: 'system.backup', name: 'Backup', description: 'Manage backups', is_dangerous: true },
      { id: 'system.updates', name: 'Updates', description: 'Manage updates', is_dangerous: true }
    ]
  }
])

// Computed
const isEditing = computed(() => !!props.role)

// Helper functions
const getModuleName = (moduleId) => {
  const module = modules.value.find(m => m.id === moduleId)
  return module ? module.name : moduleId
}

const getModulePermissions = (moduleId) => {
  const module = modules.value.find(m => m.id === moduleId)
  return module ? module.permissions : []
}

const getSelectedCount = (moduleId) => {
  const modulePermissions = getModulePermissions(moduleId).map(p => p.id)
  return form.value.permissions.filter(perm => modulePermissions.includes(perm)).length
}

const isModuleSelected = (moduleId) => {
  const modulePermissions = getModulePermissions(moduleId).map(p => p.id)
  const selected = form.value.permissions.filter(perm => modulePermissions.includes(perm))
  return selected.length === modulePermissions.length && modulePermissions.length > 0
}

const getPermissionLevel = () => {
  const count = form.value.permissions.length
  if (count > 20) return 'high'
  if (count > 10) return 'medium'
  if (count > 0) return 'low'
  return 'none'
}

const getPermissionLevelName = (level) => {
  const levels = {
    high: 'High',
    medium: 'Medium',
    low: 'Limited',
    none: 'No Permissions'
  }
  return levels[level] || level
}

// Event handlers
const selectAll = () => {
  const allPermissions = modules.value.flatMap(module => 
    module.permissions.map(p => p.id)
  )
  form.value.permissions = [...allPermissions]
}

const deselectAll = () => {
  form.value.permissions = []
}

const toggleModule = (moduleId) => {
  const modulePermissions = getModulePermissions(moduleId).map(p => p.id)
  
  if (isModuleSelected(moduleId)) {
    form.value.permissions = form.value.permissions.filter(
      perm => !modulePermissions.includes(perm)
    )
  } else {
    const newPermissions = [...form.value.permissions]
    modulePermissions.forEach(perm => {
      if (!newPermissions.includes(perm)) {
        newPermissions.push(perm)
      }
    })
    form.value.permissions = newPermissions
  }
}

const validateForm = () => {
  const errors = {}
  
  if (!form.value.name.trim()) {
    errors.name = 'Role name is required'
  }
  
  if (!form.value.id.trim()) {
    errors.id = 'Role ID is required'
  } else if (!/^[a-z0-9_]+$/.test(form.value.id)) {
    errors.id = 'Must contain only lowercase letters, numbers and underscores'
  }
  
  return errors
}

const handleSubmit = async () => {
  const validationErrors = validateForm()
  
  if (Object.keys(validationErrors).length > 0) {
    errors.value = validationErrors
    return
  }
  
  submitting.value = true
  
  try {
    const roleData = { ...form.value }
    emit('save', roleData)
  } catch (error) {
    console.error('Error saving role:', error)
  } finally {
    submitting.value = false
  }
}

// Watch and initialize
watch(() => props.role, (newRole) => {
  if (newRole) {
    form.value = { ...newRole }
  }
})

onMounted(() => {
  if (props.role) {
    form.value = { ...props.role }
  } else {
    form.value.id = `role_${Date.now()}`
  }
})
</script>

<style scoped>
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
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  overflow-y: auto;
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

.role-form {
  padding: 24px;
}

.form-section {
  margin-bottom: 32px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 2px solid #e2e8f0;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-weight: 500;
  color: #475569;
  margin-bottom: 8px;
}

.form-label.required::after {
  content: ' *';
  color: #ef4444;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 6px;
  font-size: 14px;
  font-family: inherit;
  transition: border-color 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.form-input.error {
  border-color: #ef4444;
}

.error-message {
  color: #ef4444;
  font-size: 13px;
  margin-top: 4px;
}

.form-hint {
  color: #94a3b8;
  font-size: 13px;
  margin-top: 4px;
}

/* Color Picker */
.color-picker {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
  align-items: center;
}

.color-option {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid transparent;
  transition: transform 0.2s;
}

.color-option:hover {
  transform: scale(1.1);
}

.color-option.selected {
  border-color: #1e293b;
}

.color-option .fa-check {
  color: white;
  font-size: 12px;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

.color-input {
  width: 32px;
  height: 32px;
  border: none;
  padding: 0;
  border-radius: 50%;
  cursor: pointer;
}

/* Range */
.form-range {
  width: 100%;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: #e2e8f0;
  border-radius: 3px;
  outline: none;
}

.form-range::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: #3b82f6;
  cursor: pointer;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.range-value {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 8px;
}

.range-value .value {
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
}

.level-description span {
  font-size: 14px;
  font-weight: 500;
  padding: 2px 8px;
  border-radius: 12px;
}

.level-description .high {
  background: #dcfce7;
  color: #166534;
}

.level-description .medium {
  background: #fef3c7;
  color: #92400e;
}

.level-description .low {
  background: #f3f4f6;
  color: #374151;
}

/* Checkboxes */
.form-options {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  user-select: none;
}

.checkbox-input {
  display: none;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #cbd5e1;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.checkbox-input:checked + .checkbox-custom {
  background: #3b82f6;
  border-color: #3b82f6;
}

.checkbox-input:checked + .checkbox-custom::after {
  content: '✓';
  color: white;
  font-size: 12px;
}

.checkbox-text {
  color: #475569;
  font-size: 14px;
}

/* Permissions */
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-actions {
  display: flex;
  gap: 16px;
}

.permissions-container {
  display: grid;
  grid-template-columns: 250px 1fr;
  gap: 20px;
  height: 400px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  overflow: hidden;
}

.modules-list {
  border-right: 1px solid #e2e8f0;
  overflow-y: auto;
  background: #f8fafc;
}

.module-item {
  padding: 16px;
  cursor: pointer;
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.2s;
  display: flex;
  align-items: center;
  gap: 12px;
}

.module-item:hover {
  background: #f1f5f9;
}

.module-item.active {
  background: #dbeafe;
  border-right: 3px solid #3b82f6;
}

.module-icon {
  width: 36px;
  height: 36px;
  background: white;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #475569;
}

.module-item.active .module-icon {
  background: #3b82f6;
  color: white;
}

.module-info {
  flex: 1;
}

.module-name {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 2px;
}

.module-count {
  font-size: 12px;
  color: #64748b;
}

.permissions-list {
  overflow-y: auto;
  padding: 20px;
}

.module-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #e2e8f0;
}

.module-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.module-stats {
  display: flex;
  align-items: center;
  gap: 16px;
}

.selected-count {
  font-size: 14px;
  color: #64748b;
}

.permissions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.permission-item {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  transition: border-color 0.2s;
}

.permission-item:hover {
  border-color: #cbd5e1;
}

.permission-label {
  flex: 1;
  margin: 0;
  align-items: flex-start;
}

.permission-info {
  flex: 1;
}

.permission-name {
  font-weight: 500;
  color: #1e293b;
  margin-bottom: 4px;
}

.permission-description {
  font-size: 13px;
  color: #64748b;
  line-height: 1.4;
}

.danger-badge {
  color: #ef4444;
  font-size: 14px;
}

.select-module {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #94a3b8;
}

.select-module i {
  font-size: 48px;
  margin-bottom: 16px;
}

.permissions-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-weight: 500;
  color: #475569;
}

.summary-value {
  font-weight: 600;
  color: #1e293b;
  font-size: 16px;
}

.summary-value.level-high {
  color: #166534;
}

.summary-value.level-medium {
  color: #92400e;
}

.summary-value.level-low {
  color: #374151;
}

/* Form Actions */
.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding-top: 24px;
  border-top: 1px solid #e2e8f0;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  padding: 12px 24px;
  border-radius: 6px;
  border: none;
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background 0.2s;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: #f1f5f9;
  color: #475569;
  padding: 12px 24px;
  border-radius: 6px;
  border: 1px solid #cbd5e1;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-link {
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  padding: 0;
}

.btn-link:hover {
  text-decoration: underline;
}
</style>
