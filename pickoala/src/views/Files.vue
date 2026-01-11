<template>
  <div class="page" ref="pageContainer">
    <div class="page__header">
      <div class="header-left">
        <h1 class="page__title">{{ $t('nav.files') || '我的文件' }}</h1>
        <button class="btn btn--secondary btn--small" @click="$router.push('/file-collections')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          {{ $t('fileCollections.myCollections') || '我的文件集' }}
        </button>
      </div>
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="search-icon">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input 
          type="text" 
          v-model="searchQuery" 
          :placeholder="$t('common.search') || '搜索...'" 
          class="search-input"
          @input="handleSearch"
        />
      </div>
      <div class="page__header-actions">
        <button 
          v-if="!batchMode && files.length > 0" 
          class="header-btn" 
          @click="enterBatchMode"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          {{ $t('images.batchManage') || '批量管理' }}
        </button>
        <button class="header-btn header-btn--primary" @click="uploadInput.click()">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17,8 12,3 7,8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          {{ $t('common.upload') }}
        </button>
        <input 
          type="file" 
          ref="uploadInput" 
          style="display: none" 
          @change="handleUpload"
        />
      </div>
    </div>
    
    <!-- Batch Mode Toolbar -->
    <div v-if="batchMode" class="batch-toolbar">
      <div class="batch-toolbar__left">
        <label class="checkbox-wrapper">
          <input 
            type="checkbox" 
            :checked="isAllSelected" 
            :indeterminate="isPartialSelected"
            @change="toggleSelectAll"
          />
          <span class="checkbox-label">{{ $t('images.selectAll') || '全选' }}</span>
        </label>
        <span class="batch-toolbar__count">
          {{ $t('images.selectedCount', { count: selectedIds.length }) || `已选 ${selectedIds.length} 项` }}
        </span>
      </div>
      <div class="batch-toolbar__right">
        <button 
          class="batch-btn" 
          :disabled="selectedIds.length === 0"
          @click="showCollectionDialog(selectedIds)"
        >
          {{ $t('fileCollections.addToCollection') || '加入文件集' }}
        </button>
        <button 
          class="batch-btn batch-btn--danger" 
          :disabled="selectedIds.length === 0"
          @click="batchDelete"
        >
          {{ $t('images.batchDelete') || '批量删除' }}
        </button>
        <button class="batch-btn batch-btn--cancel" @click="exitBatchMode">
          {{ $t('common.cancel') }}
        </button>
      </div>
    </div>
    
    <!-- Loading State -->
    <div v-if="loading && displayItems.length === 0" class="loading-state">
      <div class="loading__spinner"></div>
    </div>
    
    <!-- Empty State -->
    <div v-else-if="displayItems.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
        <polyline points="14 2 14 8 20 8"></polyline>
      </svg>
      <p>{{ $t('files.noFiles') || '暂无文件' }}</p>
      <button class="btn btn--primary" @click="uploadInput.click()">{{ $t('common.uploadFirst') || '上传第一个文件' }}</button>
    </div>
    
    <div v-else class="image-grid">
      <div 
        v-for="item in displayItems" 
        :key="item.uniqueKey" 
        class="image-card"
        :class="{ 
          'image-card--selected': item.type === 'file' && selectedIds.includes(item.id),
          'image-card--folder': item.type === 'folder'
        }"
        @click="handleCardClick(item)"
      >
        <!-- Batch mode checkbox (Files only) -->
        <div v-if="batchMode && item.type === 'file'" class="image-card__checkbox" @click.stop>
          <input 
            type="checkbox" 
            :checked="selectedIds.includes(item.id)"
            @change="toggleSelect(item.id)"
          />
        </div>
        
        <!-- Thumbnail/Icon -->
        <div class="image-card__thumb">
          <!-- Folder Icon -->
          <div v-if="item.type === 'folder'" class="folder-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="currentColor" class="folder-svg">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <!-- File Icon/Preview -->
          <div v-else class="file-icon-placeholder">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
              <polyline points="14 2 14 8 20 8"></polyline>
              <text x="8" y="18" font-size="6" font-weight="bold" fill="currentColor">{{ item.extension?.toUpperCase() || 'FILE' }}</text>
            </svg>
          </div>
        </div>
        
        <div class="image-card__info">
          <div class="image-card__name" :title="item.name || item.original_filename">
            {{ item.name || item.original_filename }}
          </div>
          
          <!-- Folder Meta -->
          <div v-if="item.type === 'folder'" class="image-card__meta">
             {{ $t('fileCollections.fileCount', { count: item.file_count || 0 }) || (item.file_count || 0) + ' files' }}
          </div>
          
          <!-- File Meta -->
          <div v-else class="image-card__meta">
            {{ formatSize(item.file_size) }} · {{ formatDate(item.created_at) }}
            <span v-if="item.download_limit" class="image-card__limit">
              (剩{{ item.download_limit - item.download_count }})
            </span>
          </div>
        </div>
        
        <!-- Actions (Files Only) -->
        <div v-if="!batchMode && item.type === 'file'" class="image-card__actions" @click.stop>
          <button class="icon-btn" @click="showCollectionDialog([item.id])" :title="$t('fileCollections.addToCollection') || '加入文件集'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 5v14M5 12h14"/>
            </svg>
          </button>
          <button class="icon-btn" @click="copyShareLink(item)" :title="$t('common.copyLink') || '复制分享链接'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
            </svg>
          </button>
          <button class="icon-btn icon-btn--danger" @click="deleteFile(item)" :title="$t('common.delete')">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Add to Collection Dialog -->
    <div v-if="collectionDialogVisible" class="dialog-overlay" @click.self="collectionDialogVisible = false">
      <div class="dialog">
        <div class="dialog__header">
          <h3>{{ $t('fileCollections.addToCollection') || '添加到文件集' }}</h3>
          <button class="dialog__close" @click="collectionDialogVisible = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog__body">
          <div v-if="collectionsLoading" class="loading-spinner-wrapper">
            <div class="loading__spinner"></div>
          </div>
          <div v-else-if="collections.length === 0" class="empty-collections">
            <p>{{ $t('fileCollections.noCollections') || '暂无文件集' }}</p>
            <button class="btn btn--small btn--primary" @click="$router.push('/file-collections')">
              {{ $t('fileCollections.create') || '去创建' }}
            </button>
          </div>
          <div v-else class="collection-list">
            <div 
              v-for="col in collections" 
              :key="col.id" 
              class="collection-item"
              :class="{ 'collection-item--selected': selectedCollectionId === col.id }"
              @click="selectedCollectionId = col.id"
            >
              <div class="collection-item__icon">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
                  <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
                </svg>
              </div>
              <div class="collection-item__info">
                <div class="collection-item__name">{{ col.name }}</div>
                <div class="collection-item__count">{{ col.file_count || 0 }} files</div>
              </div>
              <div v-if="selectedCollectionId === col.id" class="collection-item__check">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="20 6 9 17 4 12"/>
                </svg>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog__footer">
          <button class="btn btn--secondary" @click="collectionDialogVisible = false">{{ $t('common.cancel') || '取消' }}</button>
          <button class="btn btn--primary" @click="confirmAddToCollection" :disabled="!selectedCollectionId || submitting">
            {{ submitting ? ($t('common.processing') || '处理中...') : ($t('common.confirm') || '确定') }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { formatDateTime } from '@/utils/timezone'

const { t } = useI18n()
const files = ref([])
const loading = ref(false)
const uploadInput = ref(null)

// Batch mode state
const batchMode = ref(false)
const selectedIds = ref([])

// Collection Dialog State
const collectionDialogVisible = ref(false)
const collections = ref([])
const collectionsLoading = ref(false)
const selectedCollectionId = ref(null)
const filesToAddToCollection = ref([])
const submitting = ref(false)

const isAllSelected = computed(() => {
  return files.value.length > 0 && selectedIds.value.length === files.value.length
})

const isPartialSelected = computed(() => {
  return selectedIds.value.length > 0 && selectedIds.value.length < files.value.length
})

const router = useRouter()
const folderCollections = ref([])
const searchQuery = ref('')
const displayItems = computed(() => {
  const folders = folderCollections.value.map(c => ({ ...c, type: 'folder', uniqueKey: 'folder-' + c.id }))
  const fileItems = files.value.map(f => ({ ...f, type: 'file', uniqueKey: 'file-' + f.id }))
  return [...folders, ...fileItems]
})

const loadFiles = async () => {
  loading.value = true
  try {
    const params = {
      type: 'other'
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    } else {
      params.uncategorized = true
    }

    const [filesRes, colsRes] = await Promise.all([
      api.get('/files', { params }),
      !searchQuery.value ? api.get('/file-collections') : Promise.resolve({ data: { items: [] } })
    ])

    files.value = filesRes.data
    folderCollections.value = colsRes.data.items || []
  } catch (err) {
    ElMessage.error(t('error.loadFailed') || '加载失败')
  } finally {
    loading.value = false
  }
}

// Debounce search
let searchTimeout
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadFiles()
  }, 300)
}

const handleCardClick = (item) => {
  if (item.type === 'folder') {
    router.push(`/file-collections/${item.id}`)
    return
  }
  
  if (batchMode.value) {
    toggleSelect(item.id)
  } else {
    copyShareLink(item)
  }
}

const handleUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  const loadingMsg = ElMessage({
    type: 'loading',
    message: t('common.uploading') || '上传中...',
    duration: 0
  })
  
  try {
    await api.post('/files/upload', formData)
    ElMessage.success(t('common.uploadSuccess') || '上传成功')
    loadFiles()
  } catch (err) {
    ElMessage.error(err.response?.data?.detail || t('error.uploadFailed') || '上传失败')
  } finally {
    loadingMsg.close()
    e.target.value = ''
  }
}

const deleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
      t('files.deleteConfirm') || '确定要删除这个文件吗？',
      t('common.confirm'),
      { type: 'warning' }
      )
    await api.delete(`/files/${file.id}`)
    ElMessage.success(t('common.deleteSuccess') || '删除成功')
    loadFiles()
  } catch (err) {
    if (err !== 'cancel') {
      ElMessage.error(t('error.deleteFailed') || '删除失败')
    }
  }
}

const copyShareLink = async (file) => {
  const link = `${window.location.origin}/s/${file.unique_code}`
  
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(link)
      ElMessage.success(t('common.copied') || '链接已复制')
      return
    } catch (err) {
      console.error('Clipboard API failed', err)
    }
  }

  const textArea = document.createElement("textarea")
  textArea.value = link
  textArea.style.position = "fixed"
  textArea.style.left = "-9999px"
  textArea.style.top = "0"
  document.body.appendChild(textArea)
  textArea.focus()
  textArea.select()
  
  try {
    const successful = document.execCommand('copy')
    if (successful) {
      ElMessage.success(t('common.copied') || '链接已复制')
    } else {
      throw new Error('execCommand failed')
    }
  } catch (err) {
    ElMessage.error(t('error.copyFailed') || '复制失败')
  }

  document.body.removeChild(textArea)
}

// Batch functions
const enterBatchMode = () => {
  batchMode.value = true
  selectedIds.value = []
}

const exitBatchMode = () => {
  batchMode.value = false
  selectedIds.value = []
}

const toggleSelect = (fileId) => {
  const index = selectedIds.value.indexOf(fileId)
  if (index === -1) {
    selectedIds.value.push(fileId)
  } else {
    selectedIds.value.splice(index, 1)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = files.value.map(f => f.id)
  }
}

const batchDelete = async () => {
  if (selectedIds.value.length === 0) return
  
  try {
    await ElMessageBox.confirm(
      t('files.batchDeleteConfirm', { count: selectedIds.value.length }) || `确定要删除选中的 ${selectedIds.value.length} 个文件吗？`,
      t('common.confirm'),
      { type: 'warning' }
    )
    
    // Call delete APi sequentially or batch if supported. 
    // Backend doesn't have batch delete for files yet, so we loop.
    // IMPROVEMENT: Add batch delete endpoint to backend later.
    // For now: Loop UI logic
    const loadingMsg = ElMessage({
      type: 'loading',
      message: t('common.processing') || '处理中...',
      duration: 0
    })

    try {
      await Promise.all(selectedIds.value.map(id => api.delete(`/files/${id}`)))
      ElMessage.success(t('common.deleteSuccess') || '删除成功')
      selectedIds.value = []
      exitBatchMode()
      loadFiles()
    } catch(err) {
      ElMessage.error(t('error.deleteFailed') || '部分删除失败')
    } finally {
      loadingMsg.close()
    }
    
  } catch (error) {
    if (error !== 'cancel') {
        console.error(error)
    }
  }
}

// Collection Logic
const loadCollections = async () => {
  collectionsLoading.value = true
  try {
    const response = await api.get('/file-collections')
    collections.value = response.data.items || []
  } catch (error) {
    console.error(error)
    ElMessage.error(t('error.loadFailed') || '加载失败')
  } finally {
    collectionsLoading.value = false
  }
}

const showCollectionDialog = async (ids) => {
  filesToAddToCollection.value = ids
  selectedCollectionId.value = null
  collectionDialogVisible.value = true
  await loadCollections()
}

const confirmAddToCollection = async () => {
  if (!selectedCollectionId.value || filesToAddToCollection.value.length === 0) return
  
  submitting.value = true
  try {
    // Adding to collection = moving file to collection.
    // Using PUT /files/{id} with collection_id
    await Promise.all(filesToAddToCollection.value.map(id => 
      api.put(`/files/${id}`, { collection_id: selectedCollectionId.value })
    ))
    
    ElMessage.success(t('common.success') || '操作成功')
    collectionDialogVisible.value = false
    exitBatchMode() // Exit batch mode if active
    loadFiles() // Refresh list (maybe show collection name later?)
  } catch (error) {
    console.error(error)
    ElMessage.error(t('error.operationFailed') || '操作失败')
  } finally {
    submitting.value = false
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

onMounted(() => {
  loadFiles()
})
</script>

<style lang="scss" scoped>
.page {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  padding: 24px 20px;
  box-sizing: border-box;
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    gap: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border-light);

    .header-left {
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
    letter-spacing: -0.5px;
  }

  &__header-actions {
    display: flex;
    align-items: center;
    gap: 12px;
  }
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 300px;
  margin-left: auto;
  margin-right: 16px;
  
  .search-input {
    width: 100%;
    padding: 8px 12px 8px 36px;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    background: var(--bg-card);
    color: var(--text-primary);
    font-size: 14px;
    
    &:focus {
      outline: none;
      border-color: var(--accent-primary);
      box-shadow: 0 0 0 2px var(--accent-primary-alpha);
    }
  }
  
  .search-icon {
    position: absolute;
    left: 10px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-tertiary);
    pointer-events: none;
  }
}

.folder-icon {
  color: var(--accent-primary);
  opacity: 0.8;
  display: flex;
  align-items: center;
  justify-content: center;
  
  svg {
    width: 64px;
    height: 64px;
  }
}

.image-card--folder {
  &:hover {
    .folder-icon {
      opacity: 1;
      transform: scale(1.05);
      transition: all 0.2s;
    }
  }
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &--primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
    
    &:hover {
      background: var(--accent-primary-hover);
      color: var(--text-inverse);
    }
  }
}

.btn--small {
    padding: 6px 12px;
    font-size: 13px;
}

// Batch Toolbar (Copied patterns)
.batch-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 24px;
  background: var(--bg-secondary);
  border-radius: var(--radius-lg);
  margin-bottom: 24px;
  animation: slideDown 0.3s ease;
  
  &__left, &__right {
    display: flex;
    align-items: center;
    gap: 16px;
  }
  
  &__count {
    font-size: 14px;
    color: var(--text-secondary);
    font-weight: 500;
  }
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  
  input[type="checkbox"] {
    width: 18px;
    height: 18px;
    accent-color: var(--accent-primary);
    cursor: pointer;
  }
}

.checkbox-label {
  font-size: 14px;
  color: var(--text-primary);
}

.batch-btn {
  padding: 6px 16px;
  font-size: 14px;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-card);
  color: var(--text-primary);
  
  &:hover { background: var(--bg-tertiary); }
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &--danger {
    background: var(--accent-danger-bg);
    color: var(--accent-danger);
    &:hover:not(:disabled) { background: var(--accent-danger); color: white; }
  }
  
  &--cancel {
    color: var(--text-tertiary);
    background: transparent;
    &:hover { color: var(--text-primary); background: transparent; }
  }
}

// Grid Layout
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 16px;
}

// Card Style
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
  
  &--selected {
    outline: 2px solid var(--accent-primary);
    outline-offset: -2px;
  }
  
  &__checkbox {
    position: absolute;
    top: 8px;
    left: 8px;
    z-index: 10;
    
    input[type="checkbox"] {
      width: 20px;
      height: 20px;
      cursor: pointer;
      accent-color: var(--accent-primary);
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
  
  &__limit {
    color: var(--warning);
    margin-left: 4px;
  }
  
  &__actions {
    display: flex;
    justify-content: flex-end;
    gap: 4px;
    padding: 0 8px 8px;
    opacity: 0; // Hidden by default, shown on hover
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
  transition: all 0.15s;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &--danger:hover {
    background: var(--accent-danger-bg);
    color: var(--accent-danger);
  }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 0;
  color: var(--text-secondary);
  gap: 16px;
  
  p {
    margin-bottom: 16px;
  }
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  
  &--primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
    &:hover { opacity: 0.9; }
  }
  
  &--secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    &:hover { background: var(--bg-tertiary); }
  }
}

@keyframes slideDown {
  from { transform: translateY(-10px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

// Dialog styles
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
  display: flex;
  flex-direction: column;
  max-height: 80vh;
  
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
    overflow-y: auto;
  }
  
  &__footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 24px;
    border-top: 1px solid var(--border-light);
  }
}

.loading-spinner-wrapper {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.loading__spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-light);
  border-top-color: var(--text-primary);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin { to { transform: rotate(360deg); } }

.empty-collections {
  text-align: center;
  padding: 40px 0;
  color: var(--text-secondary);
  p { margin-bottom: 12px; }
}

.collection-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.collection-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  border: 1px solid transparent;
  
  &:hover {
    background: var(--bg-secondary);
  }
  
  &--selected {
    background: var(--bg-secondary);
    border-color: var(--accent-primary);
  }
  
  &__icon {
    width: 40px;
    height: 40px;
    background: var(--bg-tertiary);
    border-radius: var(--radius-md);
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-secondary);
  }
  
  &__info {
    flex: 1;
  }
  
  &__name {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-primary);
  }
  
  &__count {
    font-size: 12px;
    color: var(--text-tertiary);
  }
  
  &__check {
    color: var(--accent-primary);
  }
}
</style>
