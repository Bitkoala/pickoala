<template>
  <el-dialog
    v-model="visible"
    :title="$t('editor.title')"
    width="90%"
    top="5vh"
    :close-on-click-modal="false"
    :before-close="handleClose"
    custom-class="image-editor-dialog"
  >
    <div class="editor-container" v-loading="loading">
      <div class="editor-main">
        <div class="cropper-wrapper">
          <img ref="imageRef" :src="imageUrl" class="cropper-target" />
        </div>
      </div>
      
      <div class="editor-sidebar">
        <div class="control-group">
          <div class="control-label">{{ $t('editor.crop') }}</div>
          <div class="aspect-ratio-buttons">
            <el-button-group>
              <el-button size="small" @click="setAspectRatio(NaN)">{{ $t('editor.aspectRatio.free') }}</el-button>
              <el-button size="small" @click="setAspectRatio(1)">1:1</el-button>
              <el-button size="small" @click="setAspectRatio(4/3)">4:3</el-button>
              <el-button size="small" @click="setAspectRatio(16/9)">16:9</el-button>
            </el-button-group>
          </div>
        </div>

        <div class="control-group">
          <div class="control-label">{{ $t('editor.rotate') }}</div>
          <el-button-group>
            <el-button size="small" @click="rotate(-90)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 4v6h6M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
              </svg>
            </el-button>
            <el-button size="small" @click="rotate(90)">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M23 4v6h-6M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/>
              </svg>
            </el-button>
          </el-button-group>
        </div>

        <div class="control-group">
          <div class="control-label">{{ $t('editor.flip') }}</div>
          <el-button-group>
            <el-button size="small" @click="flip('h')">{{ $t('editor.flipHorizontal') }}</el-button>
            <el-button size="small" @click="flip('v')">{{ $t('editor.flipVertical') }}</el-button>
          </el-button-group>
        </div>

        <div class="control-group">
          <div class="control-label">{{ $t('editor.zoom') }}</div>
          <el-button-group>
            <el-button size="small" @click="zoom(0.1)">{{ $t('editor.zoomIn') }}</el-button>
            <el-button size="small" @click="zoom(-0.1)">{{ $t('editor.zoomOut') }}</el-button>
            <el-button size="small" @click="reset">{{ $t('editor.reset') }}</el-button>
          </el-button-group>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="saving">{{ $t('common.cancel') }}</el-button>
        <el-button 
          type="primary" 
          plain 
          @click="save('new')" 
          :loading="saving" 
          :disabled="loading"
        >
          {{ $t('editor.saveAsNew') }}
        </el-button>
        <el-button 
          type="primary" 
          @click="confirmOverwrite" 
          :loading="saving" 
          :disabled="loading"
        >
          {{ $t('editor.overwrite') }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import Cropper from 'cropperjs'
import 'cropperjs/dist/cropper.css'
import { ElMessageBox, ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const props = defineProps({
  modelValue: Boolean,
  image: {
    type: Object,
    required: true
  }
})

const emit = defineEmits(['update:modelValue', 'saved'])

const { t } = useI18n()
const visible = ref(false)
const imageRef = ref(null)
const cropper = ref(null)
const loading = ref(false)
const saving = ref(false)
const imageUrl = ref('')

// Watch for visibility changes to initialize/destroy cropper
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    imageUrl.value = props.image.url
    nextTick(() => {
      initCropper()
    })
  } else {
    destroyCropper()
  }
})

// Sync visible back to parent
watch(visible, (val) => {
  emit('update:modelValue', val)
})

const initCropper = () => {
  if (!imageRef.value) return
  
  loading.value = true
  cropper.value = new Cropper(imageRef.value, {
    viewMode: 1,
    dragMode: 'move',
    autoCropArea: 0.8,
    restore: false,
    guides: true,
    center: true,
    highlight: false,
    cropBoxMovable: true,
    cropBoxResizable: true,
    toggleDragModeOnDblclick: false,
    ready() {
      loading.value = false
    }
  })
}

const destroyCropper = () => {
  if (cropper.value) {
    cropper.value.destroy()
    cropper.value = null
  }
}

const handleClose = () => {
  if (saving.value) return
  visible.value = false
}

const setAspectRatio = (ratio) => {
  cropper.value?.setAspectRatio(ratio)
}

const rotate = (degree) => {
  cropper.value?.rotate(degree)
}

const flip = (dir) => {
  const data = cropper.value?.getData()
  if (!data) return
  if (dir === 'h') {
    cropper.value?.scaleX(data.scaleX * -1)
  } else {
    cropper.value?.scaleY(data.scaleY * -1)
  }
}

const zoom = (val) => {
  cropper.value?.zoom(val)
}

const reset = () => {
  cropper.value?.reset()
}

const confirmOverwrite = () => {
  ElMessageBox.confirm(
    t('editor.confirmOverwriteMsg'),
    t('editor.confirmOverwriteTitle'),
    {
      confirmButtonText: t('editor.overwrite'),
      cancelButtonText: t('common.cancel'),
      type: 'warning',
    }
  ).then(() => {
    save('overwrite')
  }).catch(() => {})
}

const save = async (mode) => {
  if (!cropper.value) return
  
  saving.value = true
  try {
    const canvas = cropper.value.getCroppedCanvas({
       maxWidth: 4096,
       maxHeight: 4096,
    })
    
    canvas.toBlob(async (blob) => {
      if (!blob) {
        ElMessage.error('Canvas export failed')
        saving.value = false
        return
      }
      
      const formData = new FormData()
      formData.append('file', blob, props.image.original_filename)
      if (props.image.album_id) {
        formData.append('album_id', props.image.album_id)
      }
      
      try {
        let res
        if (mode === 'new') {
          res = await api.post('/upload', formData)
          ElMessage.success(t('editor.saveAsNewSuccess'))
        } else {
          res = await api.put(`/images/${props.image.id}/content`, formData)
          ElMessage.success(t('editor.saveSuccess'))
        }
        
        emit('saved', res.data)
        visible.value = false
      } catch (e) {
        ElMessage.error(e.response?.data?.detail || 'Save failed')
      } finally {
        saving.value = false
      }
    }, 'image/webp', 0.9)
    
  } catch (e) {
    console.error(e)
    ElMessage.error('Error during image processing')
    saving.value = false
  }
}
</script>

<style lang="scss">
.image-editor-dialog {
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
}

.cropper-wrapper {
  max-width: 100%;
  max-height: 100%;
}

.cropper-target {
  display: block;
  max-width: 100%;
}

.editor-sidebar {
  width: 240px;
  padding: 20px;
  background: var(--bg-card);
  border-left: 1px solid var(--border-light);
  overflow-y: auto;
  
  @media (max-width: 768px) {
    width: 100%;
    border-left: none;
    border-top: 1px solid var(--border-light);
    display: flex;
    gap: 20px;
    padding: 12px;
  }
}

.control-group {
  margin-bottom: 24px;
  
  @media (max-width: 768px) {
    margin-bottom: 0;
    flex-shrink: 0;
  }
}

.control-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.aspect-ratio-buttons {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 12px 20px;
}
</style>
