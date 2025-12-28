<template>
  <div v-if="visible" class="modal-overlay" @click.self="handleClose">
    <div class="modal-content">
      <button class="close-btn" @click="handleClose">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner"></div>
      </div>
      
      <div class="video-container">
        <video 
          ref="videoRef"
          controls 
          autoplay
          playsinline
          :src="videoSrc"
          class="video-player"
          @error="handleError"
          @loadeddata="loading = false"
        >
          Your browser does not support the video tag.
        </video>
      </div>
      
      <div class="video-info" v-if="video">
        <h3>{{ video.original_filename }}</h3>
        <p class="video-meta">{{ formatSize(video.file_size) }} · {{ formatDate(video.created_at) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { formatDateTime } from '@/utils/timezone'

const props = defineProps({
  visible: Boolean,
  video: Object
})

const emit = defineEmits(['update:visible', 'close'])
const videoRef = ref(null)
const loading = ref(true)

const videoSrc = computed(() => {
  if (!props.video) return ''
  // Use unique code for streaming if backend supports range requests on this endpoint
  // Or direct download URL
  // Ideally, use a specific stream endpoint or the download endpoint
  return `/api/files/d/${props.video.unique_code}`
})

const handleClose = () => {
  emit('update:visible', false)
  emit('close')
}

const handleError = (e) => {
  console.error("Video error", e)
  loading.value = false
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

watch(() => props.visible, (newVal) => {
  if (newVal) {
    loading.value = true
  } else {
    // Stop video when closed
    if (videoRef.value) {
      videoRef.value.pause()
    }
  }
})

// Keyboard support (Escape to close)
const handleKeydown = (e) => {
  if (e.key === 'Escape' && props.visible) {
    handleClose()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style scoped lang="scss">
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  backdrop-filter: blur(5px);
  animation: fadeIn 0.3s ease;
}

.modal-content {
  position: relative;
  width: 100%;
  max-width: 1000px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: zoomIn 0.3s ease;
}

.close-btn {
  position: absolute;
  top: -40px;
  right: 0;
  background: none;
  border: none;
  color: white;
  opacity: 0.7;
  cursor: pointer;
  padding: 8px;
  z-index: 10;
  
  &:hover {
    opacity: 1;
    transform: scale(1.1);
  }
}

.video-container {
  width: 100%;
  background: black;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0,0,0,0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.video-player {
  max-width: 100%;
  max-height: 80vh;
  width: auto;
  height: auto;
  outline: none;
}

.video-info {
  margin-top: 16px;
  color: white;
  text-align: center;
  
  h3 {
    margin: 0 0 4px;
    font-size: 18px;
    font-weight: 500;
  }
  
  .video-meta {
    margin: 0;
    font-size: 13px;
    opacity: 0.6;
  }
}

.loading-state {
  position: absolute;
  inset: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 5;
  pointer-events: none;
  
  .spinner {
    width: 40px;
    height: 40px;
    border: 3px solid rgba(255,255,255,0.3);
    border-top-color: white;
    border-radius: 50%;
    animation: spin 1s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes zoomIn {
  from { transform: scale(0.95); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}
</style>
