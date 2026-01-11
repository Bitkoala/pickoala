<template>
  <div class="admin-page">
    <h2 class="admin-page__title">{{ $t('admin.videos') }}</h2>
    
    <div class="filter-bar">
      <div class="search-box">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        </svg>
        <input v-model="search" type="text" :placeholder="$t('admin.searchFilename')" @keyup.enter="loadVideos" />
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
            <th style="width: 80px">{{ $t('admin.preview') }}</th>
            <th>{{ $t('admin.filename') }}</th>
            <th>{{ $t('admin.user') }}</th>
            <th>{{ $t('common.size') }}</th>
            <th>{{ $t('admin.downloadCount') }}</th>
            <th>{{ $t('admin.uploadTime') }}</th>
            <th>{{ $t('common.actions') }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="video in videos" :key="video.id">
            <td>
              <div class="video-preview" @click="showPreview(video)">
                 <!-- Fallback icon or poster if thumbnail available -->
                 <img v-if="video.thumbnail_path" :src="'/uploads/' + video.thumbnail_path" class="preview-img" style="object-fit: cover;" />
                 <div v-else class="video-icon-placeholder">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="23 7 16 12 23 17 23 7"/><rect x="1" y="5" width="15" height="14" rx="2" ry="2"/></svg>
                 </div>
              </div>
            </td>
            <td class="cell-primary">
              <div class="image-name">{{ video.original_filename }}</div>
              <div class="file-meta-sm">{{ video.filename }}</div>
            </td>
            <td>
              <a 
                v-if="video.user_id" 
                href="javascript:;" 
                class="user-link" 
                @click="filterByUser(video.user_id, video.username)"
                :title="$t('admin.filterByUser')"
              >
                {{ video.username }}
              </a>
              <span v-else class="text-muted">{{ $t('admin.guest') }}</span>
            </td>
            <td class="cell-muted">{{ formatSize(video.file_size) }}</td>
            <td class="cell-muted">{{ video.download_count }}</td>
            <td class="cell-muted">{{ formatDate(video.created_at) }}</td>
            <td>
              <div class="action-btns">
                <button class="action-btn" @click="copyDirectLink(video)" :title="$t('common.copyLink') || 'Copy Link'">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/>
                    <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>
                  </svg>
                </button>
                <button class="action-btn action-btn--danger" @click="deleteVideo(video)" :title="$t('common.delete')">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="3,6 5,6 21,6"/>
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                  </svg>
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="videos.length === 0">
            <td colspan="7" class="empty-cell">{{ $t('common.noData') }}</td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="total > pageSize" class="table-pagination">
        <span class="table-pagination__info">{{ $t('admin.totalItems', { count: total }) }}</span>
        <div class="table-pagination__btns">
          <button :disabled="page <= 1" @click="page--; loadVideos()">{{ $t('common.prev') }}</button>
          <span>{{ page }} / {{ Math.ceil(total / pageSize) }}</span>
          <button :disabled="page >= Math.ceil(total / pageSize)" @click="page++; loadVideos()">{{ $t('common.next') }}</button>
        </div>
      </div>
    </div>
    
    <!-- Video Preview Dialog -->
    <div v-if="previewVisible" class="dialog-overlay" @click.self="closePreview">
      <div class="dialog dialog--lg">
        <div class="dialog__header">
          <h3>{{ previewVideo?.original_filename }}</h3>
          <button class="dialog__close" @click="closePreview">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
          </button>
        </div>
        <div class="dialog__body" v-if="previewVideo">
           <video 
             controls 
             autoplay 
             class="preview-video"
             :src="getVideoUrl(previewVideo)"
           >
             Your browser does not support the video tag.
           </video>
           <div class="preview-info">
             <span>{{ formatSize(previewVideo.file_size) }}</span>
             <span>{{ formatDate(previewVideo.created_at) }}</span>
           </div>
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

const videos = ref([])
const loading = ref(false)
const page = ref(1)
const pageSize = 20
const total = ref(0)
const search = ref('')
const userIdFilter = ref(null)
const userFilterName = ref('')

const previewVisible = ref(false)
const previewVideo = ref(null)

const loadVideos = async () => {
  loading.value = true
  try {
    const params = { page: page.value, page_size: pageSize, file_type: 'video' }
    if (search.value) params.search = search.value
    if (userIdFilter.value) params.user_id = userIdFilter.value
    
    const response = await api.get('/admin/files', { params })
    videos.value = response.data.items || []
    total.value = response.data.total || 0
  } catch (error) {
    console.error('Error loading videos:', error)
    ElMessage.error(t('error.loadFailed'))
  } finally {
    loading.value = false
  }
}

const filterByUser = (userId, username) => {
  userIdFilter.value = userId
  userFilterName.value = username
  page.value = 1
  loadVideos()
}

const clearUserFilter = () => {
  userIdFilter.value = null
  userFilterName.value = ''
  page.value = 1
  loadVideos()
}

const deleteVideo = async (video) => {
  try {
    await ElMessageBox.confirm(
        t('files.deleteConfirm'), 
        t('admin.deleteConfirm'), 
        { type: 'warning' }
    )
    await api.delete(`/admin/files/${video.id}`)
    ElMessage.success(t('common.success'))
    loadVideos()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

const showPreview = (video) => {
  previewVideo.value = video
  previewVisible.value = true
}

const closePreview = () => {
  previewVisible.value = false
  previewVideo.value = null
}

const copyDirectLink = async (video) => {
    const url = `${window.location.origin}/uploads/${video.file_path}`
    try {
        await navigator.clipboard.writeText(url)
        ElMessage.success(t('common.copied') || 'Copied')
    } catch (err) {
        console.error(err)
        ElMessage.error(t('error.copyFailed') || 'Copy failed')
    }
}

const getVideoUrl = (video) => {
    // If storage_url explicitly exists, use it
    // Otherwise construct local path
    // NOTE: For local, we need to access via /api/uploads/ OR check if backend serves via /uploads
    // File model url property logic: return self.storage_url or f"/uploads/{self.file_path}"
    // But frontend might need full path or relative to API base if strict.
    // Assuming /uploads/... is served by backend static mount.
    // Let's assume standard serving logic.
    return `/uploads/${video.file_path}`
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
  loadVideos()
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

.video-preview {
  width: 50px; height: 50px; border-radius: var(--radius-sm); overflow: hidden; cursor: pointer;
  background: #000; display: flex; align-items: center; justify-content: center;
  .preview-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.15s; }
  .video-icon-placeholder { color: #555; }
  &:hover .preview-img { transform: scale(1.1); }
  &:hover .video-icon-placeholder { color: #fff; }
}

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

// Dialog
.dialog-overlay {
  position: fixed; inset: 0; background: rgba(0, 0, 0, 0.8); display: flex; align-items: center; justify-content: center; z-index: 1000;
}
.dialog {
  width: 100%; max-width: 800px; background: var(--bg-card); border-radius: var(--radius-xl); box-shadow: var(--shadow-lg);
  &--lg { max-width: 800px; }
  
  &__header {
    display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 1px solid var(--border-light);
    h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0; }
  }
  &__close { background: none; border: none; color: var(--text-tertiary); cursor: pointer; padding: 4px; &:hover { color: var(--text-primary); } }
  &__body { padding: 24px; text-align: center; }
}
.preview-video {
    width: 100%; max-height: 500px; border-radius: var(--radius-md); background: #000;
}
.preview-info {
  display: flex; justify-content: center; gap: 20px; font-size: 13px; color: var(--text-tertiary); margin-top: 16px;
}
</style>
