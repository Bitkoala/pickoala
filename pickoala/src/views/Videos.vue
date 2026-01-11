<template>
  <div class="page" ref="pageContainer">
    <div class="page__header">
      <h1 class="page__title">{{ $t('nav.videos') || '我的视频' }}</h1>
      <div class="page__header-actions">
        <!-- Search Box -->
        <div class="search-box">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="11" cy="11" r="8"></circle>
            <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
          </svg>
          <input 
            v-model="searchQuery" 
            :placeholder="$t('common.search') || '搜索视频...'" 
            @input="handleSearch"
          />
        </div>

        <button 
          v-if="!batchMode" 
          class="header-btn" 
          @click="enterBatchMode"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/>
            <rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/>
          </svg>
          {{ $t('images.batchManage') || '批量管理' }}
        </button>
        <button class="header-btn header-btn--primary" @click="$router.push('/')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17,8 12,3 7,8"/><line x1="12" y1="3" x2="12" y2="15"/>
          </svg>
          {{ $t('common.upload') || '上传' }}
        </button>
        <button class="header-btn" @click="$router.push('/video-collections')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
          {{ $t('nav.collections') || '文件夹' }}
        </button>
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
          class="batch-btn batch-btn--danger" 
          :disabled="selectedIds.length === 0"
          @click="batchDelete"
        >
          {{ $t('images.batchDelete') || '批量删除' }}
        </button>
        <button class="batch-btn batch-btn--cancel" @click="exitBatchMode">
          {{ $t('common.cancel') || '取消' }}
        </button>
      </div>
    </div>
    
    <div class="filter-bar">
      <!-- Search Box moved to header -->
      <span v-if="files.length > 0" class="filter-stats">
        {{ $t('common.total') || '共' }} {{ files.length }}
      </span>
    </div>
    
    <!-- Video Grid -->
    <div v-if="loading" class="image-grid">
      <div v-for="i in 8" :key="i" class="image-card" style="box-shadow: none; cursor: default; background: transparent">
        <el-skeleton animated>
          <template #template>
             <el-skeleton-item variant="image" style="width: 100%; aspect-ratio: 16/9; border-radius: 8px" />
             <div style="padding: 10px 0">
               <el-skeleton-item variant="text" style="width: 60%" />
               <el-skeleton-item variant="text" style="width: 40%; margin-top: 5px" />
             </div>
          </template>
        </el-skeleton>
      </div>
    </div>
    
    <div v-else-if="files.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
        <line x1="7" y1="2" x2="7" y2="22"></line>
        <line x1="17" y1="2" x2="17" y2="22"></line>
        <line x1="2" y1="12" x2="22" y2="12"></line>
      </svg>
      <p>{{ $t('files.noVideos') || '暂无视频' }}</p>
      <button class="btn btn--primary" @click="$router.push('/')">{{ $t('common.uploadFirst') || '去上传' }}</button>
    </div>
    
    <div v-else class="image-grid">
      <div 
        v-for="file in files" 
        :key="file.id" 
        class="image-card"
        :class="{ 'image-card--selected': selectedIds.includes(file.id) }"
        @click="handleCardClick(file)"
      >
        <!-- Batch mode checkbox -->
        <div v-if="batchMode" class="image-card__checkbox" @click.stop>
          <input 
            type="checkbox" 
            :checked="selectedIds.includes(file.id)"
            @change="toggleSelect(file.id)"
          />
        </div>
        
        <div class="image-card__thumb">
          <!-- Thumbnail Image -->
          <img 
            v-if="file.thumbnail_url" 
            :src="getThumbnailUrl(file)" 
            class="video-thumb-img"
            loading="lazy"
          />
          <!-- Placeholder Icon if no thumbnail -->
          <div v-else class="file-icon-placeholder">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
               <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
               <line x1="7" y1="2" x2="7" y2="22"></line>
               <line x1="17" y1="2" x2="17" y2="22"></line>
               <line x1="2" y1="12" x2="22" y2="12"></line>
            </svg>
          </div>
          
          <!-- Play Overlay Icon -->
          <div class="play-overlay">
            <div class="play-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor" stroke="none">
                <path d="M8 5v14l11-7z" />
              </svg>
            </div>
          </div>
        </div>
        
        <div class="image-card__info">
          <div class="image-card__name" :title="file.original_filename">{{ file.original_filename }}</div>
          <div class="image-card__meta">
            {{ formatSize(file.file_size) }} · {{ formatDate(file.created_at) }}
          </div>
        </div>
        
        <div v-if="!batchMode" class="image-card__actions" @click.stop>
          <button class="icon-btn" @click="copyShareLink(file)" :title="$t('common.copyLink') || '复制链接'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
              <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
            </svg>
          </button>
          <button class="icon-btn icon-btn--danger" @click="deleteFile(file)" :title="$t('common.delete') || '删除'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Video Player Modal -->
    <VideoPlayerModal 
      v-model:visible="playerVisible"
      :video="currentVideo"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { formatDateTime } from '@/utils/timezone'
import VideoPlayerModal from '@/components/VideoPlayerModal.vue'

const { t } = useI18n()
const router = useRouter()
const files = ref([])
const loading = ref(false)
const searchQuery = ref('')
const playerVisible = ref(false)
const currentVideo = ref(null)

// Batch mode state
const batchMode = ref(false)
const selectedIds = ref([])

const isAllSelected = computed(() => {
  return files.value.length > 0 && selectedIds.value.length === files.value.length
})

const isPartialSelected = computed(() => {
  return selectedIds.value.length > 0 && selectedIds.value.length < files.value.length
})

const loadFiles = async () => {
  loading.value = true
  try {
    const params = { type: 'video' }
    if (searchQuery.value) params.search = searchQuery.value
    
    const response = await api.get('/files', { params })
    files.value = response.data
  } catch (error) {
    ElMessage.error(t('error.loadFailed') || '加载失败')
  } finally {
    loading.value = false
  }
}

// Search debounce
let searchTimeout
const handleSearch = () => {
  clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadFiles()
  }, 300)
}

const getThumbnailUrl = (file) => {
  if (file.thumbnail_url) {
    return file.thumbnail_url
  }
  return ''
}

const handleCardClick = (file) => {
  if (batchMode.value) {
    toggleSelect(file.id)
  } else {
    playVideo(file)
  }
}

const playVideo = (file) => {
  currentVideo.value = file
  playerVisible.value = true
}

// Batch Functions
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
      t('images.batchDeleteConfirm', { count: selectedIds.value.length }) || `确定要删除这 ${selectedIds.value.length} 个视频吗？`,
      t('common.confirm') || '确认',
      { type: 'warning' }
    )
    
    // Batch delete via API loop or specific endpoint if available
    // Currently backend supports DELETE /images with params, but for /files we might have to loop or use similar params
    // Files API mostly supports DELETE /files/{id}
    // We can loop for now, or check if we updated file deletion to batch.
    // Assuming loop for simplicity unless I see batch endpoint.
    // The images endpoint supports batch. Files endpoint typically assumes single.
    // I'll loop.
    
    // Actually better to do: Promise.all
    await Promise.all(selectedIds.value.map(id => api.delete(`/files/${id}`)))
    
    ElMessage.success(t('common.deleteSuccess') || '删除成功')
    
    exitBatchMode()
    loadFiles()
  } catch (error) {
    if (error !== 'cancel') {
      console.error(error)
      ElMessage.error(t('error.deleteFailed') || '删除失败')
    }
  }
}

const deleteFile = async (file) => {
  try {
    await ElMessageBox.confirm(
      t('common.deleteConfirm') || '确定要删除此文件吗？此操作无法撤销。',
      t('common.warning'),
      { type: 'warning' }
    )
    await api.delete(`/files/${file.id}`)
    ElMessage.success(t('common.deleteSuccess') || '删除成功')
    
    files.value = files.value.filter(f => f.id !== file.id)
  } catch (e) {
    if (e !== 'cancel') {
        console.error(e)
        ElMessage.error(t('error.deleteFailed') || '删除失败')
    }
  }
}

const copyShareLink = async (file) => {
  const link = `${window.location.origin}/s/${file.unique_code}`
  try {
    await navigator.clipboard.writeText(link)
    ElMessage.success(t('common.copied') || '链接已复制')
  } catch {
    ElMessage.error(t('error.copyFailed') || '复制失败')
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
// Inherit variables from theme
.page {
  padding: 32px 48px;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

.page__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page__title {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}

.page__header-actions {
  display: flex;
  gap: 12px;
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  font-weight: 500;
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    background: var(--bg-tertiary);
  }
  
  &--primary {
    background: var(--accent-primary);
    color: white;
    
    &:hover {
      background: var(--accent-primary-hover);
      box-shadow: 0 4px 12px var(--accent-primary-alpha);
    }
  }
}

// Batch Toolbar (Floating)
.batch-toolbar {
  position: sticky;
  top: 10px; // Adjust if header is sticky
  z-index: 100;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 12px 24px;
  margin-bottom: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: var(--shadow-neu-convex);
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

@keyframes slideDown {
  from { transform: translateY(-20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.batch-btn {
  padding: 6px 16px;
  border-radius: var(--radius-md);
  font-size: 14px;
  cursor: pointer;
  border: none;
  background: var(--bg-secondary);
  color: var(--text-primary);
  transition: all 0.2s;
  
  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  &--danger {
    background: var(--accent-danger);
    color: white;
    &:hover:not(:disabled) { opacity: 0.9; }
  }
  
  &--cancel {
    background: transparent;
    &:hover { color: var(--text-primary); text-decoration: underline; }
  }
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  
  input {
    width: 18px;
    height: 18px;
    cursor: pointer;
  }
  
  .checkbox-label {
    font-size: 14px;
    font-weight: 500;
  }
}

// Filter Bar
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  &__left {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  
  svg {
    position: absolute;
    left: 10px;
    color: var(--text-tertiary);
    pointer-events: none;
  }
  
  input {
    width: 240px;
    padding: 8px 12px 8px 32px;
    border: 1px solid var(--border-light);
    border-radius: var(--radius-md);
    font-size: 14px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    transition: all 0.2s;
    
    &:focus {
      outline: none;
      border-color: var(--accent-primary);
      background: var(--bg-card);
      box-shadow: 0 0 0 2px var(--accent-primary-alpha);
    }
  }
}

.filter-stats {
  font-size: 13px;
  color: var(--text-tertiary);
}

// Grid
.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

.image-card {
  position: relative;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-flat);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover:not(.image-card--selected) {
    transform: translateY(-4px);
    box-shadow: var(--shadow-raised);
    
    .image-card__actions {
      opacity: 1;
    }
    
    .play-overlay .play-icon {
        transform: scale(1.1);
        background: rgba(0,0,0,0.7);
    }
  }
  
  &--selected {
    box-shadow: 0 0 0 2px var(--accent-primary);
    background: var(--bg-secondary);
  }
  
  &__checkbox {
    position: absolute;
    top: 10px;
    left: 10px;
    z-index: 10;
    
    input {
      width: 20px;
      height: 20px;
      cursor: pointer;
      accent-color: var(--accent-primary);
    }
  }

  &__thumb {
    width: 100%;
    aspect-ratio: 16/9;
    background: var(--bg-secondary);
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    overflow: hidden;
    
    .video-thumb-img {
      width: 100%;
      height: 100%;
      object-fit: cover;
    }
    
    .file-icon-placeholder {
      color: var(--text-tertiary);
    }
  }
  
  &__info {
    padding: 16px;
  }
  
  &__name {
    font-size: 15px;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 6px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  &__meta {
    font-size: 13px;
    color: var(--text-tertiary);
    display: flex;
    justify-content: space-between;
  }
  
  &__actions {
    position: absolute;
    top: 8px;
    right: 8px;
    display: flex;
    gap: 6px;
    opacity: 0;
    transition: opacity 0.2s;
    
    .icon-btn {
       width: 30px;
       height: 30px;
       border-radius: 6px;
       background: rgba(255,255,255,0.95);
       border: 1px solid rgba(0,0,0,0.05);
       display: flex;
       align-items: center;
       justify-content: center;
       color: var(--text-secondary);
       cursor: pointer;
       
       &:hover {
         background: white;
         color: var(--text-primary);
       }
       
       &--danger:hover {
         color: var(--accent-danger);
       }
    }
  }
}

.play-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(0,0,0,0.1);
  transition: all 0.2s;
  
  .play-icon {
     width: 48px;
     height: 48px;
     border-radius: 50%;
     background: rgba(0,0,0,0.5);
     color: white;
     display: flex;
     align-items: center;
     justify-content: center;
     transition: all 0.2s;
     backdrop-filter: blur(4px);
  }
}

// Empty State
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 80px 0;
  color: var(--text-tertiary);
  
  svg {
    margin-bottom: 16px;
    opacity: 0.5;
  }
  
  p {
    font-size: 16px;
    margin: 0 0 24px;
  }
}

// Responsive
@media (max-width: 768px) {
  .page {
    padding: 16px;
  }
  
  .page__title {
    font-size: 24px;
  }
  
  .image-grid {
    grid-template-columns: repeat(auto-fill, minmax(100%, 1fr));
    gap: 16px;
  }
  
  .batch-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 16px;
    
    &__left, &__right {
      width: 100%;
      justify-content: space-between;
    }
  }
}
</style>
