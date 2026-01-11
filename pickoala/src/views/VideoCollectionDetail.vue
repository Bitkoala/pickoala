<template>
  <div class="page">
    <div class="page__header">
      <div class="header-left">
        <button class="back-btn" @click="$router.push('/video-collections')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15,18 9,12 15,6"/>
          </svg>
          {{ $t('common.back') || '返回' }}
        </button>
        <div class="header-info">
          <h1 class="page__title">{{ collection?.name }}</h1>
          <span class="header-desc" v-if="collection?.description">{{ collection.description }}</span>
        </div>
      </div>
      <div class="header-actions">
           <!-- Add files trigger if needed, usually we move files INTO collection from Videos page, but maybe upload direct? -->
           <!-- For now, we assume management via Videos page move action -->
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading__spinner"></div>
    </div>
    
    <div v-else-if="files.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <rect x="2" y="2" width="20" height="20" rx="2.18" ry="2.18"></rect>
        <line x1="7" y1="2" x2="7" y2="22"></line>
        <line x1="17" y1="2" x2="17" y2="22"></line>
        <line x1="2" y1="12" x2="22" y2="12"></line>
      </svg>
      <p>{{ $t('fileCollections.noFiles') || '此视频集暂无视频' }}</p>
      <button class="btn btn--secondary" @click="$router.push('/videos')">{{ $t('common.addFromLibrary') || '从库中添加' }}</button>
    </div>
    
    <div v-else class="image-grid">
      <div 
        v-for="file in files" 
        :key="file.id" 
        class="image-card"
        @click="playVideo(file)"
      >
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
        
        <div class="image-card__actions" @click.stop>
          <button class="icon-btn" @click="removeFromCollection(file)" :title="$t('fileCollections.removeFromCollection') || '移出视频集'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
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
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '@/api'
import { formatDateTime } from '@/utils/timezone'
import VideoPlayerModal from '@/components/VideoPlayerModal.vue'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()
const collection = ref(null)
const files = ref([])
const loading = ref(false)
const playerVisible = ref(false)
const currentVideo = ref(null)

const loadCollection = async () => {
  loading.value = true
  try {
    const id = route.params.id
    // Get info
    const infoRes = await api.get(`/file-collections/${id}`)
    collection.value = infoRes.data
    
    // Get files
    const filesRes = await api.get(`/file-collections/${id}/files`)
    files.value = filesRes.data.items || []
  } catch (error) {
    console.error(error)
    ElMessage.error(t('error.loadFailed') || '加载失败')
    router.push('/video-collections')
  } finally {
    loading.value = false
  }
}

const getThumbnailUrl = (file) => {
  if (file.thumbnail_url) {
    return file.thumbnail_url
  }
  return ''
}

const playVideo = (file) => {
  currentVideo.value = file
  playerVisible.value = true
}

const removeFromCollection = async (file) => {
  try {
    await ElMessageBox.confirm(
      t('fileCollections.removeConfirm') || '确定要从视频集中移除此视频吗？',
      t('common.confirm') || '确认',
      { type: 'warning' }
    )
    
    // API logic to remove from collection?
    // Usually update file to set collection_id=null
    // Or if we have collection endpoint to remove file
    // The collection delete endpoint supports deleting files, but not removing specific one via collection endpoint usually.
    // We should update the file directly.
    await api.put(`/files/${file.id}`, { collection_id: null })
    
    ElMessage.success(t('common.success') || '移除成功')
    files.value = files.value.filter(f => f.id !== file.id)
    
  } catch (error) {
    if (error !== 'cancel') {
        console.error(error)
        ElMessage.error(t('error.operationFailed') || '操作失败')
    }
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
  loadCollection()
})
</script>

<style lang="scss" scoped>
.page {
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 32px 48px;
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
      flex-direction: column;
      align-items: flex-start;
      gap: 16px;
    }
    
    .header-info {
        display: flex;
        align-items: baseline;
        gap: 12px;
    }
  }
  
  &__title {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
  }
  
  .header-desc {
      color: var(--text-tertiary);
      font-size: 14px;
  }
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  margin-bottom: 8px;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
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

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  
  svg { margin-bottom: 16px; opacity: 0.5; }
  p { margin: 0 0 20px; font-size: 15px; }
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
  
  &--secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    
    &:hover { background: var(--bg-tertiary); }
  }
}

// Reuse Image Grid styles from Videos.vue
// Ideally this should be a component but for now we duplicate or scope
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
  
  &:hover {
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
</style>
