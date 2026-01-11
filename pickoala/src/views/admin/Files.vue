<template>
  <div class="admin-page">
    <h2 class="admin-page__title">{{ $t('admin.files') }}</h2>
    
    <div class="filter-bar">
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="search" type="text" :placeholder="$t('admin.searchFilename')" @keyup.enter="loadFiles" />
      </div>
      
      <!-- User Filter Tag -->
      <div v-if="userIdFilter" class="filter-tag">
        <span>{{ $t('admin.user') }}: {{ userFilterName }}</span>
        <button class="filter-tag__close" @click="clearUserFilter">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
    </div>
    
    <div class="table-card">
      <div v-if="loading" class="loading">
        <div class="loading__spinner"></div>
      </div>
      
      <table v-else class="data-table">
        <thead>
          <tr>
            <th style="width: 50px"></th>
            <th>{{ $t('admin.filename') }}</th>
            <th>{{ $t('admin.user') }}</th>
            <th>{{ $t('common.size') }}</th>
            <th>{{ $t('admin.downloadCount') }}</th>
            <th>{{ $t('admin.uploadTime') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="file in files" :key="file.id">
            <td class="file-icon-cell">
               <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path>
                  <polyline points="13 2 13 9 20 9"></polyline>
               </svg>
            </td>
            <td class="cell-primary">
              <div class="image-name">{{ file.original_filename }}</div>
              <div class="file-meta-sm">{{ file.filename }}</div>
            </td>
            <td>
              <a 
                v-if="file.user_id" 
                href="javascript:;" 
                class="user-link" 
                @click="filterByUser(file.user_id, file.username)"
                :title="$t('admin.filterByUser')"
              >
                {{ file.username }}
              </a>
              <span v-else class="text-muted">{{ $t('admin.guest') }}</span>
            </td>
            <td class="cell-muted">{{ formatSize(file.file_size) }}</td>
            <td class="cell-muted">{{ file.download_count }}</td>
            <td class="cell-muted">{{ formatDate(file.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button class="action-btn action-btn--danger" @click="deleteFile(file)" :title="$t('common.delete')">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="files.length === 0">
            <td colspan="7" class="empty-cell">{{ $t('common.noData') }}</td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="total > pageSize" class="table-pagination">
        <span class="table-pagination__info">{{ $t('admin.totalItems', { count: total }) }}</span>
        <div class="table-pagination__btns">
          <button :disabled="page <= 1" @click="page--; loadFiles()">{{ $t('common.prev') }}</button>
          <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
          <button :disabled="page >= Math.ceil(total / pageSize)" @click="page++; loadFiles()">{{ $t('common.next') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { useSiteStore } from '@/stores/site'
import { formatDateTime } from '@/utils/timezone'

const { t } = useI18n()
const siteStore = useSiteStore()

const files = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const search = ref('')
const userIdFilter = ref(null)
const userFilterName = ref('')

const loadFiles = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, file_type: 'other' }
    if (search.value) params.search = search.value
    if (userIdFilter.value) params.user_id = userIdFilter.value
    
    const response = await api.get('/admin/files', { params })
    files.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Error loading files:', error)
    ElMessage.error(t('error.loadFailed'))
  } finally {
    loading.value = false
  }
}

const filterByUser = (userId, username) => {
  userIdFilter.value = userId
  userFilterName.value = username
  page.value = 1
  loadFiles()
}

const clearUserFilter = () => {
  userIdFilter.value = null
  userFilterName.value = ''
  page.value = 1
  loadFiles()
}

const deleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
        t('files.deleteConfirm'), 
        t('admin.deleteConfirm'), 
        { type: 'warning' }
    )
    await api.delete(`/admin/files/${file.id}`)
    ElMessage.success(t('common.success'))
    loadFiles()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const formatSize = (bytes) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1048576) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1048576).toFixed(1) + ' MB'
}

const formatDate = (date) => {
  return formatDateTime(date, siteStore.timezone())
}

onMounted(() => {
  loadFiles()
})
</script>

<style lang="scss" scoped>
.admin-page {
  &__title {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 24px;
  }
}

.filter-bar {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  align-items: center;
}

.filter-tag {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--bg-tertiary);
  border-radius: var(--radius-md);
  font-size: 13px;
  color: var(--text-primary);
  
  &__close {
    display: flex;
    align-items: center;
    background: none;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 2px;
    border-radius: 50%;
    
    &:hover {
      background: rgba(0,0,0,0.1);
      color: var(--text-primary);
    }
  }
}

.user-link {
  color: var(--accent-primary);
  text-decoration: none;
  font-weight: 500;
  
  &:hover {
    text-decoration: underline;
  }
}

.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 12px;
  background: var(--bg-card);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
  
  svg { color: var(--text-tertiary); flex-shrink: 0; }
  
  input {
    width: 200px;
    padding: 10px 0;
    font-size: 14px;
    color: var(--text-primary);
    background: transparent;
    border: none;
    
    &::placeholder { color: var(--text-tertiary); }
    &:focus { outline: none; }
  }
}

.table-card {
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-neu-flat);
  overflow: hidden;
}

.loading {
  display: flex;
  justify-content: center;
  padding: 60px;
  
  &__spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--border-light);
    border-top-color: var(--text-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin { to { transform: rotate(360deg); } }

.data-table {
  width: 100%;
  border-collapse: collapse;
  th, td { padding: 12px 16px; text-align: left; font-size: 13px; }
  th { background: var(--bg-secondary); color: var(--text-secondary); font-weight: 600; }
  td { border-top: 1px solid var(--border-light); color: var(--text-secondary); vertical-align: middle; }
  .cell-primary { color: var(--text-primary); font-weight: 500; }
  .cell-muted { color: var(--text-tertiary); }
  .empty-cell { text-align: center; padding: 40px; color: var(--text-tertiary); }
  
  .image-name { max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
  .file-meta-sm { font-size: 11px; color: var(--text-tertiary); font-weight: 400; }
  
  tbody tr:hover { background: var(--bg-secondary); }
}

.file-icon-cell { color: var(--text-tertiary); }

.action-btns { display: flex; gap: 4px; }
.action-btn {
  width: 28px; height: 28px; display: flex; align-items: center; justify-content: center;
  background: var(--bg-secondary); border: none; border-radius: var(--radius-sm);
  color: var(--text-secondary); cursor: pointer; transition: all 0.15s;
  &:hover { background: var(--bg-tertiary); color: var(--text-primary); }
  &--danger:hover { background: var(--accent-danger-bg); color: var(--accent-danger); }
}

.table-pagination {
  display: flex; justify-content: space-between; align-items: center; padding: 16px; border-top: 1px solid var(--border-light);
  &__info { font-size: 13px; color: var(--text-tertiary); }
  &__btns {
    display: flex; align-items: center; gap: 12px;
    button {
      padding: 6px 12px; font-size: 13px; background: var(--bg-secondary); border: none; border-radius: var(--radius-sm);
      color: var(--text-primary); cursor: pointer;
      &:hover:not(:disabled) { background: var(--bg-tertiary); }
      &:disabled { opacity: 0.4; cursor: not-allowed; }
    }
    span { font-size: 13px; color: var(--text-secondary); }
  }
}
</style>
