<template>
  <transition name="modal-fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="close">
      <div class="modal-content announcement-modal">
        <div class="modal-header">
          <h3>{{ siteName }} {{ $t('admin.announcement') }}</h3>
          <button class="modal-close" @click="close">&times;</button>
        </div>
        <div class="modal-body">
           <div class="announcement-content" v-html="content"></div>
        </div>
        <div class="modal-footer">
          <button class="btn btn--secondary btn--text" @click="dismissSession">{{ $t('common.dontShowAgainSession') }}</button>
          <button class="btn btn--primary" @click="close">{{ $t('common.confirm') }}</button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useSiteStore } from '@/stores/site'

const siteStore = useSiteStore()
const isOpen = ref(false)

const content = computed(() => siteStore.popupContent())
const enabled = computed(() => siteStore.isPopupEnabled())
const siteName = computed(() => siteStore.siteName())

const STORAGE_KEY = 'pickoala_announcement_read_hash'
const SESSION_STORAGE_KEY = 'pickoala_announcement_session_dismissed'

// Simple hash function to detect content changes
const simpleHash = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return hash;
}

const checkAndShow = () => {
    if (!enabled.value || !content.value) return;

    // Check session dismissal
    if (sessionStorage.getItem(SESSION_STORAGE_KEY)) return;

    const currentHash = simpleHash(content.value).toString();
    const lastReadHash = localStorage.getItem(STORAGE_KEY);

    if (lastReadHash !== currentHash) {
        isOpen.value = true;
    }
}

const close = () => {
    isOpen.value = false;
    if (content.value) {
        const currentHash = simpleHash(content.value).toString();
        localStorage.setItem(STORAGE_KEY, currentHash);
    }
}

const dismissSession = () => {
    sessionStorage.setItem(SESSION_STORAGE_KEY, 'true');
    isOpen.value = false;
}

// Watch for store loading to complete
watch(() => siteStore.loaded, (newVal) => {
    if (newVal) {
        checkAndShow();
    }
})

// Manual trigger
watch(() => siteStore.showAnnouncementManual, (newVal) => {
    if (newVal > 0) {
        isOpen.value = true;
    }
})

onMounted(() => {
    if (siteStore.loaded) {
        checkAndShow();
    }
})
</script>

<style lang="scss" scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--bg-card);
  border-radius: 16px;
  width: 90%;
  max-width: 600px;
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.2);
  border: 1px solid var(--border-light);
  overflow: hidden;
}

.modal-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-light);
  display: flex;
  align-items: center;
  justify-content: space-between;
  
  h3 {
    margin: 0;
    font-size: 18px;
    font-weight: 600;
      color: var(--text-primary);
  }
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  color: var(--text-secondary);
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
  
  &:hover {
    color: var(--text-primary);
  }
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  line-height: 1.6;
  color: var(--text-primary);
  
  .announcement-content {
    ::v-deep(img) {
      max-width: 100%;
      height: auto;
      border-radius: 8px;
      margin: 12px 0;
    }
    
    ::v-deep(p) {
        margin-bottom: 1em;
    }
    ::v-deep(a) {
        color: var(--accent-primary);
        text-decoration: none;
        &:hover {
           text-decoration: underline;
        }
    }
  }
}

.modal-footer {
  padding: 16px 24px;
  border-top: 1px solid var(--border-light);
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  background: var(--bg-secondary);

  .btn--text {
    opacity: 0.7;
    font-size: 13px;
    &:hover {
      opacity: 1;
      text-decoration: underline;
    }
  }
}

// Animations
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
  
  .modal-content {
    transition: transform 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  }
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
  
  .modal-content {
    transform: scale(0.9) translateY(20px);
  }
}
</style>
