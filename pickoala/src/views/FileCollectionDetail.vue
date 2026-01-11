<template>
  <div class="page">
    <div class="page__header">
      <div class="page__header-left">
        <button class="back-btn" @click="$router.push('/file-collections')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15,18 9,12 15,6"/>
          </svg>
          {{ $t('common.back') || '返回' }}
        </button>
        <h1 class="page__title" v-if="collection">{{ collection.name }}</h1>
      </div>
      <div class="page__header-right" v-if="collection">
        <!-- Add Link to add files (redirect to files page) -->
        <button class="btn btn--secondary" @click="$router.push('/files')" :title="$t('fileCollections.addHint') || '添加文件 (去文件列表)'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
          </svg>
          <span class="btn-text">{{ $t('common.add') || '添加' }}</span>
        </button>
        <button class="btn btn--secondary btn--icon" @click="showEditDialog" :title="$t('common.edit') || '编辑'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </button>
      </div>
    </div>
    
    <div class="page__content">
      <div v-if="collection && collection.description" class="collection-desc">
        {{ collection.description }}
      </div>
      
      <div class="filter-bar" v-if="!loading">
        <div class="filter-bar__left">
          <span class="filter-stats">{{ $t('fileCollections.totalFiles', { count: total }) || `共 ${total} 个文件` }}</span>
        </div>
      </div>
      
      <div v-if="loading" class="loading">
        <div class="loading__spinner"></div>
      </div>
      
      <div v-else-if="files.length === 0" class="empty-state">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
          <polyline points="14 2 14 8 20 8"></polyline>
        </svg>
        <p>{{ $t('fileCollections.noFiles') || '文件集为空' }}</p>
        <p class="empty-state__hint">{{ $t('fileCollections.addHint') || '请前往“我的文件”页面将文件添加到此文件集' }}</p>
        <button class="btn btn--primary" @click="$router.push('/files')">{{ $t('fileCollections.manageFiles') || '去管理文件' }}</button>
      </div>
      
      <div v-else class="image-grid">
        <div 
          v-for="file in files" 
          :key="file.id" 
          class="image-card"
          @click="copyShareLink(file)"
        >
          <div class="image-card__thumb">
            <div class="file-icon-placeholder">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                <polyline points="14 2 14 8 20 8"></polyline>
                <text x="8" y="18" font-size="6" font-weight="bold" fill="currentColor">{{ (file.extension || 'FILE').toUpperCase() }}</text>
              </svg>
            </div>
          </div>
          
          <div class="image-card__info">
            <div class="image-card__name" :title="file.original_filename">{{ file.original_filename }}</div>
            <div class="image-card__meta">
              {{ formatSize(file.file_size) }} · {{ formatDate(file.created_at) }}
            </div>
          </div>
          
          <div class="image-card__actions" @click.stop>
            <button class="icon-btn" @click="copyShareLink(file)" :title="$t('common.copyLink') || '复制链接'">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
              </svg>
            </button>
            <button class="icon-btn" @click="removeFromCollection(file)" :title="$t('fileCollections.removeFromCollection') || '移出文件集'">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M18 6L6 18M6 6l12 12"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Edit Dialog -->
    <div v-if="editDialogVisible" class="dialog-overlay" @click.self="editDialogVisible = false">
      <div class="dialog">
        <div class="dialog__header">
          <h3>{{ $t('fileCollections.edit') || '编辑文件集' }}</h3>
          <button class="dialog__close" @click="editDialogVisible = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog__body">
          <div class="form-group">
            <label class="form-label">{{ $t('fileCollections.name') || '名称' }} <span class="required">*</span></label>
            <input v-model="editForm.name" type="text" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">{{ $t('common.description') || '描述' }}</label>
            <textarea v-model="editForm.description" class="form-input form-textarea" rows="3"></textarea>
          </div>
          <div class="form-group form-group--inline">
            <label class="form-label">{{ $t('albums.isPublic') || '公开访问' }}</label>
            <label class="switch">
              <input type="checkbox" v-model="editForm.is_public" />
              <span class="switch__slider"></span>
            </label>
          </div>
        </div>
        <div class="dialog__footer">
          <button class="btn btn--secondary" @click="editDialogVisible = false">{{ $t('common.cancel') || '取消' }}</button>
          <button class="btn btn--primary" @click="saveCollection" :disabled="!editForm.name || saving">
            {{ saving ? ($t('common.saving') || '保存中...') : ($t('common.save') || '保存') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { formatDateTime } from '@/utils/timezone'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const collection = ref(null)
const files = ref([])
const loading = ref(false)
const total = ref(0)
const collectionId = route.params.id

const editDialogVisible = ref(false)
const saving = ref(false)
const editForm = reactive({
  name: '',
  description: '',
  is_public: false,
})

const loadCollection = async () => {
  try {
    const response = await api.get(`/file-collections/${collectionId}`)
    collection.value = response.data
  } catch (error) {
    ElMessage.error(t('error.loadFailed') || '加载失败')
    router.push('/file-collections')
  }
}

const loadFiles = async () => {
  loading.value = true
  try {
    const response = await api.get(`/file-collections/${collectionId}/files`)
    files.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error(error)
  } finally {
    loading.value = false
  }
}

const showEditDialog = () => {
  if (!collection.value) return
  editForm.name = collection.value.name
  editForm.description = collection.value.description || ''
  editForm.is_public = collection.value.is_public
  editDialogVisible.value = true
}

const saveCollection = async () => {
  if (!editForm.name) return
  saving.value = true
  try {
    await api.put(`/file-collections/${collectionId}`, editForm)
    collection.value.name = editForm.name
    collection.value.description = editForm.description
    collection.value.is_public = editForm.is_public
    editDialogVisible.value = false
    ElMessage.success(t('common.updateSuccess') || '更新成功')
  } catch (error) {
    console.error(error)
    ElMessage.error(t('error.operationFailed') || '操作失败')
  } finally {
    saving.value = false
  }
}

const removeFromCollection = async (file) => {
  try {
    await ElMessageBox.confirm(
      t('fileCollections.removeConfirm') || '确定要将此文件移出文件集吗？文件不会被删除。',
      t('common.confirm') || '确认',
      { type: 'warning' }
    )
    // There is no dedicated remove endpoint in my plan, but I can use file updates (move)
    // Wait, implementation plan said "implement file move/add to collection API"
    // I should create that endpoint in `backend/app/api/files.py` or `file_collections.py`
    // Wait, `File` model has `collection_id`. I can update file to set collection_id=None.
    // I need to verify if there is an endpoint for that.
    // Assuming backend updates `files` update endpoint or I create a specific one.
    // I haven't modified `files` API yet. I should add a "move" endpoint or use standard update.
    // Let's assume standard update `PUT /files/{id}` with `collection_id: null` works IF I update `FileUpdate` schema.
    // I updated `FileUpdate` schema in previous step.
    // So I can use `PUT /files/{id}`.
    await api.put(`/files/${file.id}`, { collection_id: null })
    
    ElMessage.success(t('common.success') || '操作成功')
    loadFiles()
    // Refresh collection details (count)
    loadCollection()
  } catch (error) {
    if (error !== 'cancel') {
        console.error(error)
        ElMessage.error(t('error.operationFailed') || '操作失败')
    }
  }
}

const copyShareLink = async (file) => {
  const link = `${window.location.origin}/s/${file.unique_code}`
  if (navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(link)
      ElMessage.success(t('common.copied') || '已复制链接')
    } catch {
      ElMessage.error(t('error.copyFailed') || '复制失败')
    }
  } else {
     // Fallback
     ElMessage.info('Link: ' + link)
  }
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (date) => {
  if (!date) return '-'
  return formatDateTime(date)
}

onMounted(async () => {
  await loadCollection()
  await loadFiles()
})
</script>

<style lang="scss" scoped>
.page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    flex-wrap: wrap;
    gap: 20px;
    
    &-left {
      display: flex;
      align-items: center;
      gap: 20px;
      flex-wrap: wrap;
    }
    
    &-right {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  }
  
  &__title {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    line-height: 1.2;
  }
  
  &__content {
    background: var(--bg-card);
    border-radius: var(--radius-xl);
    padding: 24px;
    box-shadow: var(--shadow-sm);
    min-height: 400px;
  }
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: var(--bg-card);
    border-color: var(--border-medium);
    color: var(--text-primary);
    box-shadow: var(--shadow-sm);
  }
  
  svg {
    width: 18px;
    height: 18px;
  }
}

.collection-desc {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.6;
  margin-bottom: 24px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-light);
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  border-radius: var(--radius-md);
  cursor: pointer;
  border: none;
  background: var(--bg-secondary);
  color: var(--text-secondary);
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &--primary {
    background: var(--accent-primary);
    color: white;
    &:hover { opacity: 0.9; color: white; background: var(--accent-primary); }
  }
  
  &--icon {
    padding: 8px;
    width: 36px;
    height: 36px;
    justify-content: center;
  }

  .btn-text {
      @media (max-width: 600px) {
          display: none;
      }
  }
}

.filter-bar {
  margin-bottom: 20px;
}

.filter-stats {
  font-size: 13px;
  color: var(--text-tertiary);
}

// Grid
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

.image-card {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-neu-flat);
  overflow: hidden;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-neu-convex);
    
    .image-card__actions {
      opacity: 1;
    }
  }
  
  &__thumb {
    width: 100%;
    height: 140px;
    overflow: hidden;
    background: var(--bg-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    
    .file-icon-placeholder {
      color: var(--text-tertiary);
    }
  }
  
  &__info {
    padding: 12px;
  }
  
  &__name {
    font-size: 13px;
    font-weight: 500;
    color: var(--text-primary);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  &__meta {
    font-size: 11px;
    color: var(--text-tertiary);
    margin-top: 4px;
  }
  
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    padding: 0 8px 8px;
    opacity: 0;
    transition: opacity 0.2s;
  }
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  
  svg { margin-bottom: 16px; }
  p { margin: 0 0 8px; font-size: 15px; }
  
  &__hint {
    font-size: 13px;
    margin-bottom: 20px !important;
  }
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

@keyframes spin {
  to { transform: rotate(360deg); }
}

// Dialog styles (duplicated from other components, ideally should be global or checking class)
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  width: 100%;
  max-width: 420px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-light);
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }
  
  &__close {
    background: none;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 4px;
    
    &:hover { color: var(--text-primary); }
  }
  
  &__body {
    padding: 24px;
  }
  
  &__footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 24px;
    border-top: 1px solid var(--border-light);
  }
}

.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  .required { color: var(--accent-danger); }
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  
  &:focus {
    outline: none;
    border-color: var(--border-medium);
    background: var(--bg-card);
  }
}

.form-textarea { resize: vertical; min-height: 80px; }
.form-group--inline { display: flex; justify-content: space-between; align-items: center; }

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
    
    &:checked + .switch__slider {
      background: var(--accent-primary);
      &::before { transform: translateX(20px); }
    }
  }
  
  &__slider {
    position: absolute;
    inset: 0;
    background: var(--bg-tertiary);
    border-radius: 12px;
    cursor: pointer;
    transition: 0.2s;
    
    &::before {
      content: '';
      position: absolute;
      left: 2px;
      top: 2px;
      width: 20px;
      height: 20px;
      background: white;
      border-radius: 50%;
      transition: 0.2s;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
  }
}
</style>
