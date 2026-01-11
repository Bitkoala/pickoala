<template>
  <div class="cs-widget" v-if="shouldShow">
    <!-- Custom Mode: Floating Button & Popover -->
    <template v-if="isCustomMode">
      <!-- Floating Button -->
      <button 
        class="cs-fab" 
        :class="{ 'is-open': isOpen }"
        @click="togglePopover"
        :title="customTitle"
      >
        <span class="cs-fab__icon">
          <!-- Close Icon when Open -->
          <svg v-if="isOpen" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
          <!-- Headset Icon when Closed -->
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
        </span>
      </button>

      <!-- Popover Window -->
      <transition name="popover-fade">
        <div v-if="isOpen" class="cs-popover">
          <div class="cs-popover__header">
            <h3>{{ customTitle }}</h3>
          </div>
          <div class="cs-popover__body">
            <!-- QR Code -->
            <div v-if="customQr" class="cs-qr-container">
              <img :src="customQr" alt="Contact QR Code" class="cs-qr-code" />
            </div>
            
            <!-- Description Text -->
            <p v-if="customDesc" class="cs-desc">{{ customDesc }}</p>
            
            <!-- Action Button -->
            <a 
              v-if="customLink" 
              :href="customLink" 
              target="_blank" 
              rel="noopener noreferrer"
              class="cs-action-btn"
            >
              {{ customLinkText }}
            </a>
          </div>
        </div>
      </transition>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useSiteStore } from '@/stores/site'

const siteStore = useSiteStore()
const isOpen = ref(false)

// Settings Shortcuts
const mode = computed(() => siteStore.settings.cs_mode)
const crispId = computed(() => siteStore.settings.cs_crisp_id)
const customTitle = computed(() => siteStore.settings.cs_custom_title)
const customQr = computed(() => siteStore.settings.cs_custom_qr)
const customDesc = computed(() => siteStore.settings.cs_custom_desc)
const customLink = computed(() => siteStore.settings.cs_custom_link)
const customLinkText = computed(() => siteStore.settings.cs_custom_link_text)

const shouldShow = computed(() => mode.value !== 'off')
const isCustomMode = computed(() => mode.value === 'custom')

// Toggle Popover
const togglePopover = () => {
  isOpen.value = !isOpen.value
}

// Crisp Integration Logic
const loadedCrispId = ref(null)

const loadCrisp = (id) => {
  if (!id || window.$crisp || loadedCrispId.value === id) return
  
  window.$crisp = []
  window.CRISP_WEBSITE_ID = id
  
  const d = document
  const s = d.createElement("script")
  s.src = "https://client.crisp.chat/l.js"
  s.async = 1
  d.getElementsByTagName("head")[0].appendChild(s)
  
  loadedCrispId.value = id
}

// Handle Mode Changes
watch(mode, (newMode) => {
  if (newMode === 'crisp' && crispId.value) {
    loadCrisp(crispId.value)
  }
  // If switching away from Crisp, we can't easily unload the script, strictly speaking.
  // But typically user won't toggle modes back and forth rapidly in production.
  // For Custom mode, the template v-if handles showing the widget.
}, { immediate: true })

watch(crispId, (newId) => {
  if (mode.value === 'crisp' && newId) {
    loadCrisp(newId)
  }
})

</script>

<style lang="scss" scoped>
.cs-widget {
  position: fixed;
  bottom: 24px;
  right: 24px;
  z-index: 9999;
  font-family: inherit;
}

// Floating Action Button
.cs-fab {
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--accent-primary);
  color: white;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  position: relative;
  z-index: 10001;
  
  &:hover {
    transform: scale(1.05);
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
  }
  
  &:active {
    transform: scale(0.95);
  }
  
  &.is-open {
    transform: rotate(90deg);
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-medium);
  }
  
  &__icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }
}

// Popover Container
.cs-popover {
  position: absolute;
  bottom: 72px;
  right: 0;
  width: 320px;
  background: var(--bg-card);
  border-radius: 16px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
  border: 1px solid var(--border-light);
  overflow: hidden;
  z-index: 10000;
  transform-origin: bottom right;
  
  &__header {
    background: var(--accent-primary);
    padding: 16px 20px;
    
    h3 {
      margin: 0;
      color: white;
      font-size: 16px;
      font-weight: 600;
    }
  }
  
  &__body {
    padding: 24px;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
  }
}

// Content Elements
.cs-qr-container {
  width: 180px;
  height: 180px;
  background: white;
  padding: 8px;
  border-radius: 8px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  
  .cs-qr-code {
    width: 100%;
    height: 100%;
    object-fit: contain;
  }
}

.cs-desc {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0 0 20px;
  line-height: 1.5;
}

.cs-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 10px 24px;
  background: var(--bg-secondary);
  color: var(--text-primary);
  font-size: 14px;
  font-weight: 500;
  text-decoration: none;
  border-radius: 8px;
  border: 1px solid var(--border-medium);
  transition: all 0.2s;
  width: 100%;
  
  &:hover {
    background: var(--bg-tertiary);
    border-color: var(--border-dark);
    color: var(--accent-primary);
  }
}

// Animations
.popover-fade-enter-active,
.popover-fade-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}

.popover-fade-enter-from,
.popover-fade-leave-to {
  opacity: 0;
  transform: scale(0.9) translateY(20px);
}
</style>
