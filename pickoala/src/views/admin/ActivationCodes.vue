<template>
  <div class="activation-codes">
    <div class="page-header">
      <h2>{{ $t('admin.activation.title') }}</h2>
      <button class="generate-btn" @click="showGenerateModal = true">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
        {{ $t('admin.activation.generate') }}
      </button>
    </div>

    <!-- Stats or Filters could go here -->
    <div class="filters">
        <div class="filter-group">
            <label>{{ $t('admin.activation.status') }}:</label>
            <select v-model="filterStatus" @change="fetchCodes(1)">
                <option value="">{{ $t('common.all') }}</option>
                <option value="unused">{{ $t('admin.activation.unused') }}</option>
                <option value="used">{{ $t('admin.activation.used') }}</option>
            </select>
        </div>
    </div>

    <div class="table-container" v-loading="loading">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>{{ $t('admin.activation.code') }}</th>
            <th>{{ $t('admin.activation.duration') }}</th>
            <th>{{ $t('admin.activation.status') }}</th>
            <th>{{ $t('admin.activation.created') }}</th>
            <th>{{ $t('admin.activation.usedBy') }}</th>
            <th>{{ $t('admin.activation.usedAt') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="code in codes" :key="code.id">
            <td>{{ code.id }}</td>
            <td class="code-cell">
                <span class="code-text">{{ code.code }}</span>
                <button class="copy-btn" @click="copyCode(code.code)" :title="$t('common.copy')">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                        <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
                    </svg>
                </button>
            </td>
            <td>{{ code.duration_days }} {{ $t('common.days') }}</td>
            <td>
              <span class="status-badge" :class="code.status">
                {{ code.status === 'unused' ? $t('admin.activation.unused') : $t('admin.activation.used') }}
              </span>
            </td>
            <td>{{ formatDate(code.created_at) }}</td>
            <td>{{ code.used_by_username || '-' }}</td>
            <td>{{ code.used_at ? formatDate(code.used_at) : '-' }}</td>
            <td>
              <button class="delete-btn" @click="deleteCode(code.id)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </td>
          </tr>
          <tr v-if="codes.length === 0">
            <td colspan="8" class="empty-state">{{ $t('common.noData') }}</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="total > 0">
      <button :disabled="currentPage === 1" @click="fetchCodes(currentPage - 1)">&lt;</button>
      <span>{{ currentPage }} / {{ Math.ceil(total / perPage) }}</span>
      <button :disabled="currentPage * perPage >= total" @click="fetchCodes(currentPage + 1)">&gt;</button>
    </div>

    <!-- Generate Modal -->
    <div v-if="showGenerateModal" class="modal-overlay" @click.self="showGenerateModal = false">
      <div class="modal-content">
        <h3>{{ $t('admin.activation.generateTitle') }}</h3>
        
        <div class="form-group">
          <label>{{ $t('admin.activation.count') }}</label>
          <input type="number" v-model.number="generateForm.count" min="1" max="100">
        </div>
        
        <div class="form-group">
          <label>{{ $t('admin.activation.durationDays') }}</label>
          <input type="number" v-model.number="generateForm.duration_days" min="1">
        </div>

        <div class="form-group">
            <label>{{ $t('admin.activation.prefix') }}</label>
            <input type="text" v-model="generateForm.prefix" placeholder="VIP">
        </div>
        
        <div class="modal-actions">
          <button class="cancel-btn" @click="showGenerateModal = false">{{ $t('common.cancel') }}</button>
          <button class="confirm-btn" @click="handleGenerate" :disabled="generating">
            {{ generating ? $t('common.processing') : $t('common.confirm') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// State
const codes = ref([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(20)
const loading = ref(false)
const filterStatus = ref('')

const showGenerateModal = ref(false)
const generating = ref(false)
const generateForm = ref({
  count: 10,
  duration_days: 30,
  prefix: 'VIP'
})

const fetchCodes = async (page = 1) => {
  loading.value = true
  try {
    const res = await api.get('/admin/activation/list', {
      params: {
        page,
        per_page: perPage.value,
        status: filterStatus.value || undefined
      }
    })
    codes.value = res.data.items
    total.value = res.data.total
    currentPage.value = page
  } catch (error) {
    ElMessage.error(t('error.loadFailed'))
  } finally {
    loading.value = false
  }
}

const handleGenerate = async () => {
    if (generateForm.value.count < 1 || generateForm.value.duration_days < 1) {
        ElMessage.warning(t('admin.activation.invalidParams'))
        return
    }

    generating.value = true
    try {
        await api.post('/admin/activation/generate', generateForm.value)
        ElMessage.success(t('admin.activation.generateSuccess'))
        showGenerateModal.value = false
        fetchCodes(1)
    } catch (error) {
        ElMessage.error(error.response?.data?.detail || t('error.operationFailed'))
    } finally {
        generating.value = false
    }
}

const deleteCode = async (id) => {
    try {
        await ElMessageBox.confirm(
            t('admin.activation.deleteConfirm'),
            t('common.warning'),
            { confirmButtonText: t('common.confirm'), cancelButtonText: t('common.cancel'), type: 'warning' }
        )
        
        await api.delete(`/admin/activation/${id}`)
        ElMessage.success(t('common.deleteSuccess'))
        fetchCodes(currentPage.value)
    } catch (e) {
        // Cancelled or error
    }
}

const copyCode = (code) => {
    navigator.clipboard.writeText(code).then(() => {
        ElMessage.success(t('common.copySuccess'))
    })
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  fetchCodes()
})
</script>

<style scoped lang="scss">
.activation-codes {
  padding: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  h2 {
    margin: 0;
    font-size: 24px;
    color: var(--text-primary);
  }
}

.generate-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  background: var(--accent-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s;
  
  &:hover {
    background: var(--accent-hover);
  }
}

.filters {
    margin-bottom: 20px;
}

.filter-group {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 14px;
    color: var(--text-secondary);
    
    select {
        padding: 6px 12px;
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        background: var(--bg-card);
        color: var(--text-primary);
        outline: none;
        
        &:focus {
            border-color: var(--accent-primary);
        }
    }
}

.table-container {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  
  th, td {
    padding: 16px;
    text-align: left;
    border-bottom: 1px solid var(--border-light);
  }
  
  th {
    font-weight: 600;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    font-size: 13px;
    text-transform: uppercase;
  }
  
  td {
    color: var(--text-primary);
    font-size: 14px;
  }
  
  tr:last-child td {
    border-bottom: none;
  }
}

.code-cell {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .code-text {
        font-family: monospace;
        font-weight: 600;
        letter-spacing: 1px;
    }
    
    .copy-btn {
        background: none;
        border: none;
        color: var(--text-tertiary);
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
        display: flex;
        
        &:hover {
            color: var(--accent-primary);
            background: var(--bg-secondary);
        }
    }
}

.status-badge {
    padding: 4px 8px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 500;
    
    &.unused {
        background: rgba(16, 185, 129, 0.1);
        color: #10B981;
    }
    
    &.used {
        background: rgba(107, 114, 128, 0.1);
        color: #6B7280;
    }
}

.delete-btn {
  background: none;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 6px;
  border-radius: 6px;
  transition: all 0.2s;
  
  &:hover {
    background: rgba(239, 68, 68, 0.1);
  }
}

.empty-state {
  text-align: center;
  color: var(--text-tertiary);
  padding: 32px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-top: 24px;
  
  button {
    padding: 8px 16px;
    background: var(--bg-card);
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    cursor: pointer;
    color: var(--text-primary);
    
    &:disabled {
      opacity: 0.5;
      cursor: not-allowed;
    }
    
    &:hover:not(:disabled) {
      border-color: var(--accent-primary);
      color: var(--accent-primary);
    }
  }
}

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
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-card);
  padding: 32px;
  border-radius: var(--radius-lg);
  width: 90%;
  max-width: 400px;
  box-shadow: var(--shadow-xl);
  border: 1px solid var(--border-light);
  
  h3 {
    margin: 0 0 24px;
    color: var(--text-primary);
  }
}

.form-group {
  margin-bottom: 20px;
  
  label {
    display: block;
    margin-bottom: 8px;
    font-size: 14px;
    color: var(--text-secondary);
  }
  
  input {
    width: 100%;
    padding: 10px;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    background: var(--bg-secondary);
    color: var(--text-primary);
    font-size: 14px;
    
    &:focus {
      border-color: var(--accent-primary);
      outline: none;
    }
  }
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 32px;
  
  button {
    padding: 10px 20px;
    border-radius: var(--radius-md);
    font-weight: 500;
    cursor: pointer;
    border: none;
    
    &.cancel-btn {
      background: var(--bg-secondary);
      color: var(--text-secondary);
      
      &:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
      }
    }
    
    &.confirm-btn {
      background: var(--accent-primary);
      color: white;
      
      &:hover {
        background: var(--accent-hover);
      }
      
      &:disabled {
        opacity: 0.7;
        cursor: not-allowed;
      }
    }
  }
}
</style>
