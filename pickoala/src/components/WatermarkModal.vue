<template>
  <el-dialog
    v-model="visible"
    :title="$t('watermark.title') || '添加水印'"
    width="90%"
    top="5vh"
    :close-on-click-modal="false"
    :before-close="handleClose"
    custom-class="watermark-dialog"
  >
    <div class="editor-container" v-loading="loading">
      <div class="editor-main">
        <div class="preview-wrapper" ref="previewWrapper">
          <img :src="imageUrl" class="preview-image" ref="imageRef" :style="{ opacity: loading ? 0.5 : 1 }" />
          
          <!-- Watermark Overlay Preview -->
          <div 
            v-if="config.type === 'text' && config.text"
            class="watermark-overlay text-overlay"
            :style="textStyle"
          >
            {{ config.text }}
          </div>
          
          <!-- Image Watermark Preview -->
          <div 
            v-if="config.type === 'image' && (config.image_path || userStore.user?.watermark_image_path)"
            class="watermark-overlay image-overlay"
            :style="imageStyle"
          >
             <img :src="watermarkImageUrl" alt="Watermark" v-if="watermarkImageUrl" />
             <span v-else>Watermark Image</span>
          </div>
        </div>
      </div>
      
      <div class="editor-sidebar">
        <!-- Type Selection -->
        <div class="control-group">
           <div class="control-label">{{ $t('watermark.type') || '类型' }}</div>
            <el-radio-group v-model="config.type" size="small">
             <el-radio-button label="text">{{ $t('watermark.typeText') || '文字' }}</el-radio-button>
             <el-radio-button label="image">{{ $t('watermark.typeImage') || '图片' }}</el-radio-button>
           </el-radio-group>
         </div>

        <!-- Text Settings -->
        <div v-if="config.type === 'text'" class="text-settings">
          <div class="control-group">
            <div class="control-label">{{ $t('watermark.text') || '内容' }}</div>
            <el-input v-model="config.text" :placeholder="$t('watermark.textPlaceholder') || '请输入水印文字'" size="small" maxlength="50" />
          </div>
          
          <div class="control-group">
            <div class="control-label">{{ $t('watermark.color') || '颜色' }}</div>
            <el-color-picker v-model="config.color" show-alpha size="small" />
          </div>
          
          <div class="control-group">
            <div class="control-label">{{ $t('watermark.fontSize') || '大小' }} (px)</div>
            <el-slider v-model="config.size" :min="12" :max="100" size="small" />
          </div>
        </div>
        
        <div v-if="config.type === 'image'" class="image-settings">
          <div class="control-group">
            <div class="control-label">{{ $t('watermark.imageContent') || '图片内容' }}</div>
            <div class="watermark-upload" @click="triggerWatermarkUpload">
               <img v-if="watermarkImageUrl" :src="watermarkImageUrl" class="watermark-preview-img" />
               <div v-else class="upload-placeholder">
                 <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/></svg>
                 <span>{{ $t('watermark.uploadHint') || '点击上传水印图片' }}</span>
               </div>
               <input type="file" ref="watermarkInput" class="hidden" accept="image/png,image/webp" @change="handleWatermarkUpload" />
            </div>
          </div>
        </div>

        <!-- Common Settings -->
        <div class="control-group">
          <div class="control-label">{{ $t('watermark.opacity') || '不透明度' }} (%)</div>
          <el-slider v-model="config.opacity" :min="0" :max="100" size="small" />
        </div>

        <div class="control-group">
          <div class="control-label">{{ $t('watermark.position') || '位置' }}</div>
          <div class="position-grid">
            <div 
              v-for="pos in positions" 
              :key="pos" 
              class="position-cell"
              :class="{ active: config.position === pos }"
              @click="config.position = pos"
            >
              <div class="dot"></div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="saving">{{ $t('common.cancel') }}</el-button>
        <el-button 
          type="primary" 
          @click="apply" 
          :loading="saving" 
          :disabled="loading"
        >
          {{ $t('common.apply') || '应用并保存' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import { useSiteStore } from '@/stores/site'
import api from '@/api'

const props = defineProps({
  modelValue: Boolean,
  image: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const userStore = useUserStore()
const siteStore = useSiteStore()
const visible = ref(false)
const loading = ref(false)
const saving = ref(false)
const imageUrl = ref('')
const watermarkInput = ref(null)

const positions = ['top-left', 'top-right', 'center', 'bottom-left', 'bottom-right']

// Initial config from user defaults or sensible defaults
const config = reactive({
  type: 'text',
  text: '',
  image_path: null,
  opacity: 50,
  position: 'bottom-right',
  color: '#FFFFFF',
  size: 20
})

const watermarkImageUrl = computed(() => {
    // Prefer locally uploaded/configured path
    if (config.image_path) {
        return `${window.location.origin}/uploads/${config.image_path}`
    }
    // Fallback to user default (legacy support)
    if (userStore.user?.watermark_image_path) {
        return `${window.location.origin}/uploads/${userStore.user.watermark_image_path}`
    }
    return null
})

const triggerWatermarkUpload = () => watermarkInput.value?.click()

const handleWatermarkUpload = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await api.post('/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    config.image_path = response.data.file_path
    ElMessage.success('水印图片上传成功')
  } catch (error) {
    ElMessage.error('水印图片上传失败')
  }
}

watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    imageUrl.value = props.image.url
    // Load defaults from user store
    const u = userStore.user
    if (u) {
       config.type = u.watermark_type || 'text'
       config.text = u.watermark_text || siteStore.siteName()
       config.image_path = u.watermark_image_path
       config.opacity = u.watermark_opacity || 50
       config.position = u.watermark_position || 'bottom-right'
       // Default size logic is slightly complex in backend (width/20), here we just pick a reasonable default
       config.size = 24 
    }
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

const handleClose = () => {
    if (saving.value) return
    visible.value = false
}

const apply = async () => {
    saving.value = true
    try {
        const payload = { ...config }
        // Clean up text if type is image, etc.
        if (payload.type === 'image') payload.text = null
        
        const res = await api.post(`/images/${props.image.id}/watermark`, payload)
        ElMessage.success('水印应用成功')
        emit('saved', res.data)
        visible.value = false
    } catch (e) {
        console.error(e)
        ElMessage.error(e.response?.data?.detail || '应用失败')
    } finally {
        saving.value = false
    }
}

// Compute styles for preview
const textStyle = computed(() => {
    const s = {
        opacity: config.opacity / 100,
        color: config.color,
        fontSize: `${config.size}px`,
        position: 'absolute',
        fontWeight: 'bold',
        textShadow: '0 1px 3px rgba(0,0,0,0.5)',
        pointerEvents: 'none'
    }
    
    // Position logic (simplified for CSS preview)
    const margin = '20px'
    
    switch (config.position) {
        case 'top-left':
            s.top = margin; s.left = margin; break
        case 'top-right':
            s.top = margin; s.right = margin; break
        case 'bottom-left':
            s.bottom = margin; s.left = margin; break
        case 'bottom-right':
            s.bottom = margin; s.right = margin; break
        case 'center':
            s.top = '50%'; s.left = '50%'; s.transform = 'translate(-50%, -50%)'; break
    }
    
    return s
})

const imageStyle = computed(() => {
    const s = {
        opacity: config.opacity / 100,
        position: 'absolute',
        pointerEvents: 'none',
        // Max width to simulate 20% width logic roughly? 
        // Backend logic is: width * 0.2. In CSS percentage is relative to parent container.
        width: '20%' 
    }
    
    const margin = '20px'
    switch (config.position) {
        case 'top-left':
            s.top = margin; s.left = margin; break
        case 'top-right':
            s.top = margin; s.right = margin; break
        case 'bottom-left':
            s.bottom = margin; s.left = margin; break
        case 'bottom-right':
            s.bottom = margin; s.right = margin; break
        case 'center':
            s.top = '50%'; s.left = '50%'; s.transform = 'translate(-50%, -50%)'; break
    }
    return s
})

</script>

<style lang="scss">
.watermark-dialog {
  .el-dialog__body {
    padding: 0;
  }
}
</style>

<style lang="scss" scoped>
.editor-container {
  display: flex;
  height: 65vh;
  min-height: 400px;
  background: var(--bg-primary);
  
  @media (max-width: 768px) {
    flex-direction: column;
    height: 80vh;
  }
}

.editor-main {
  flex: 1;
  background: #111;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  position: relative;
  padding: 20px;
}

.preview-wrapper {
  position: relative;
  max-width: 100%;
  max-height: 100%;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
}

.preview-image {
  display: block;
  max-width: 100%;
  max-height: 60vh;
  object-fit: contain;
}

.editor-sidebar {
  width: 280px;
  padding: 24px;
  background: var(--bg-card);
  border-left: 1px solid var(--border-light);
  overflow-y: auto;
  
  @media (max-width: 768px) {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--border-light);
  }
}

.control-group {
  margin-bottom: 24px;
}

.control-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.position-grid {
  display: grid;
  grid-template-areas: 
    "tl . tr"
    ".  c  ."
    "bl . br";
  gap: 8px;
  width: 120px;
  height: 80px;
  background: var(--bg-secondary);
  padding: 8px;
  border-radius: 8px;
  
  .position-cell {
    border-radius: 4px;
    cursor: pointer;
    background: rgba(255,255,255,0.1);
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.2s;
    
    &:hover { background: rgba(255,255,255,0.2); }
    &.active { 
        background: var(--accent-primary); 
        .dot { background: white; }
    }
    
    .dot {
        width: 6px; 
        height: 6px; 
        border-radius: 50%; 
        background: var(--text-tertiary);
    }
    
    &:nth-child(1) { grid-area: tl; }
    &:nth-child(2) { grid-area: tr; }
    &:nth-child(3) { grid-area: c; }
    &:nth-child(4) { grid-area: bl; }
    &:nth-child(5) { grid-area: br; }
  }
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 20px;
}

.warning-text {
    font-size: 12px;
    color: var(--accent-warning);
    margin-bottom: 16px;
}

.text-overlay {
    white-space: nowrap;
    z-index: 10;
}
.image-overlay {
    z-index: 10;
    img { width: 100%; height: auto; }
}

.watermark-upload {
  width: 100%;
  height: 100px;
  border: 2px dashed var(--border-light);
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  overflow: hidden;
  background: var(--bg-secondary);
  position: relative;
  
  &:hover {
    border-color: var(--accent-primary);
    background: var(--bg-tertiary);
  }
  
  .upload-placeholder {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
    color: var(--text-tertiary);
    font-size: 12px;
    
    svg { opacity: 0.6; }
  }
  
  .watermark-preview-img {
    max-width: 90%;
    max-height: 90%;
    object-fit: contain;
  }
}

.hidden { display: none; }
</style>
