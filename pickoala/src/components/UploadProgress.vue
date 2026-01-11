<template>
  <div class="upload-progress" :class="{ 'is-collapsed': isCollapsed }">
    <div class="upload-progress__header" @click="toggleCollapse">
      <div class="header-left">
        <div class="status-icon" :class="{ 'is-spinning': uploadingCount > 0 }">
          <svg v-if="uploadingCount > 0" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 12a9 9 0 1 1-6.219-8.56"/>
          </svg>
          <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
        </div>
        <span class="header-title">
          {{ uploadingCount > 0 
            ? $t('upload.uploading', { count: uploadingCount }) 
            : $t('upload.complete', { count: completedCount }) 
          }}
        </span>
      </div>
      <div class="header-actions">
        <button class="header-btn" @click.stop="toggleCollapse">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" :class="{ 'is-rotated': isCollapsed }">
            <polyline points="6 9 12 15 18 9" />
          </svg>
        </button>
        <button class="header-btn" @click.stop="$emit('close')">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>
    </div>

    <div class="upload-progress__body">
      <div v-for="file in files" :key="file.id" class="progress-item">
        <div class="progress-item__icon">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
            <circle cx="8.5" cy="8.5" r="1.5"/>
            <polyline points="21 15 16 10 5 21"/>
          </svg>
        </div>
        <div class="progress-item__info">
          <div class="info-top">
            <span class="file-name" :title="file.name">{{ file.name }}</span>
            <span class="file-status" :class="file.status">
              {{ file.status === 'exception' ? $t('common.error') : file.progress + '%' }}
            </span>
          </div>
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :class="file.status"
              :style="{ width: file.progress + '%' }"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  files: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['close'])

const isCollapsed = ref(false)

const uploadingCount = computed(() => props.files.filter(f => !f.status || f.status === 'uploading').length)
const completedCount = computed(() => props.files.filter(f => f.status === 'success').length)

const toggleCollapse = () => {
  isCollapsed.value = !isCollapsed.value
}
</script>

<style lang="scss" scoped>
.upload-progress {
  position: fixed;
  bottom: 24px;
  right: 24px;
  width: 320px;
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-xl);
  z-index: 1000;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);

  &.is-collapsed {
    transform: translateY(calc(100% - 48px));
  }

  &__header {
    height: 48px;
    padding: 0 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-light);
    cursor: pointer;
    user-select: none;

    .header-left {
      display: flex;
      align-items: center;
      gap: 12px;
    }

    .status-icon {
      display: flex;
      color: var(--text-secondary);
      
      &.is-spinning {
        color: var(--accent-primary);
        animation: spin 1s linear infinite;
      }
    }

    .header-title {
      font-size: 14px;
      font-weight: 600;
      color: var(--text-primary);
    }

    .header-actions {
      display: flex;
      align-items: center;
      gap: 4px;
    }

    .header-btn {
      background: none;
      border: none;
      color: var(--text-tertiary);
      padding: 6px;
      cursor: pointer;
      display: flex;
      border-radius: 4px;
      transition: all 0.2s;

      &:hover {
        background: var(--bg-tertiary);
        color: var(--text-primary);
      }

      svg {
        transition: transform 0.3s;
        
        &.is-rotated {
          transform: rotate(180deg);
        }
      }
    }
  }

  &__body {
    max-height: 300px;
    overflow-y: auto;
    padding: 8px 0;

    &::-webkit-scrollbar {
      width: 4px;
    }
    &::-webkit-scrollbar-thumb {
      background: var(--border-medium);
      border-radius: 2px;
    }
  }
}

.progress-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  
  &:hover {
    background: var(--bg-surface);
  }

  &__icon {
    color: var(--text-tertiary);
    flex-shrink: 0;
  }

  &__info {
    flex: 1;
    min-width: 0;
  }
}

.info-top {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-size: 12px;

  .file-name {
    color: var(--text-primary);
    font-weight: 500;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    max-width: 180px;
  }

  .file-status {
    color: var(--text-tertiary);
    font-variant-numeric: tabular-nums;

    &.success { color: var(--success); }
    &.exception { color: var(--danger); }
  }
}

.progress-bar {
  height: 4px;
  background: var(--bg-secondary);
  border-radius: 2px;
  overflow: hidden;

  .progress-fill {
    height: 100%;
    background: var(--accent-primary);
    border-radius: 2px;
    transition: width 0.2s linear;

    &.success { background: var(--success); }
    &.exception { background: var(--danger); }
  }
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
