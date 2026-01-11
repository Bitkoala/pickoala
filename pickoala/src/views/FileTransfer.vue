<template>
  <div class="transfer-page">
    <div class="transfer-card">
      <div v-if="loading" class="loading__spinner"></div>
      
      <template v-else-if="error">
        <div class="error-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
        </div>
        <h2 class="error-title">{{ error }}</h2>
        <button class="btn btn--secondary" @click="$router.push('/')">
          {{ $t('common.backHome') || '返回首页' }}
        </button>
      </template>
      
      <template v-else-if="file">
        <!-- Video Player -->
        <div v-if="isVideo" class="video-preview">
          <video 
            controls 
            playsinline 
            :src="downloadUrl" 
            :poster="file.thumbnail_path ? ('/uploads/' + file.thumbnail_path) : ''"
            class="video-player"
          >
            Your browser does not support the video tag.
          </video>
        </div>

        <div class="file-icon" v-else>
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
            <polyline points="14 2 14 8 20 8"></polyline>
            <line x1="12" y1="18" x2="12" y2="12"></line>
            <polyline points="9 15 12 18 15 15"></polyline>
          </svg>
        </div>
        
        <h1 class="file-name">{{ file.original_filename }}</h1>
        <div class="file-meta">
          <span>{{ formatSize(file.file_size) }}</span>
          <span class="dot">·</span>
          <span>{{ formatDate(file.created_at) }}</span>
        </div>
        
        <div v-if="file.expire_at" class="file-warning">
          此文件将于 {{ formatDate(file.expire_at) }} 过期
        </div>

        <div class="action-area">
          <div v-if="file.has_password" class="password-input-wrapper">
            <input 
              v-model="password" 
              type="password" 
              class="password-input" 
              :placeholder="$t('common.passwordRequired') || '请输入提取密码'"
            >
          </div>
          
          <button class="btn btn--primary btn--large" @click="downloadFile">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            {{ $t('common.download') || '下载文件' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import api from '@/api'
import { formatDateTime } from '@/utils/timezone'

const route = useRoute()
const { t } = useI18n()
const loading = ref(true)
const error = ref(null)
const file = ref(null)
const apiBase = import.meta.env.VITE_API_URL || '/api'
const password = ref('')

const isVideo = computed(() => {
  return file.value?.mime_type?.startsWith('video/')
})

const downloadUrl = computed(() => {
  let url = `${apiBase}/files/d/${route.params.code}`
  if (password.value) {
    url += `?password=${encodeURIComponent(password.value)}`
  }
  return url
})

const loadFileInfo = async () => {
  try {
    const res = await api.get(`/files/s/${route.params.code}`)
    file.value = res.data
  } catch (err) {
    if (err.response?.status === 404) {
      error.value = t('error.fileNotFound') || '文件不存在'
    } else if (err.response?.status === 410) {
      error.value = t('error.linkExpired') || '链接已过期'
    } else {
      error.value = t('error.loadFailed') || '加载失败'
    }
  } finally {
    loading.value = false
  }
}

const downloadFile = () => {
  if (file.value.has_password && !password.value) {
    ElMessage.warning(t('common.passwordRequired') || '请输入提取密码')
    return
  }
  window.open(downloadUrl.value, '_blank')
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
  loadFileInfo()
})
</script>

<style lang="scss" scoped>
.transfer-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}

.transfer-card {
  width: 100%;
  max-width: 600px;
  background: var(--bg-card);
  border-radius: 24px;
  box-shadow: var(--shadow-lg);
  padding: 48px 32px;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.video-preview {
  width: 100%;
  margin-bottom: 24px;
  border-radius: 12px;
  overflow: hidden;
  background: black;
  
  .video-player {
    width: 100%;
    max-height: 400px;
    display: block;
  }
}

.file-icon {
  width: 96px;
  height: 96px;
  background: var(--bg-secondary);
  border-radius: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--accent-primary);
  margin-bottom: 24px;
}


.file-name {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 12px;
  word-break: break-all;
}

.file-meta {
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 32px;
  
  .dot {
    margin: 0 8px;
  }
}

.file-warning {
  color: var(--warning);
  font-size: 13px;
  background: rgba(245, 158, 11, 0.1);
  padding: 8px 16px;
  border-radius: 100px;
  margin-bottom: 32px;
}

.action-area {
  width: 100%;
}

.btn--large {
  width: 100%;
  height: 48px;
  font-size: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.error-icon {
  color: var(--danger);
  margin-bottom: 16px;
}

.error-title {
  font-size: 18px;
  margin-bottom: 24px;
}

.password-input-wrapper {
  margin-bottom: 20px;
  width: 100%;
}

.password-input {
  width: 100%;
  padding: 12px 16px;
  border: 2px solid var(--border-light);
  border-radius: 12px;
  font-size: 16px;
  text-align: center;
  transition: all 0.2s;
  
  &:focus {
    outline: none;
    border-color: var(--accent-primary);
    background: var(--bg-secondary);
  }
}
</style>
