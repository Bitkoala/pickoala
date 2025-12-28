<template>
  <div class="theme-switch">
    <button 
      class="theme-switch__item" 
      :class="{ 'is-active': themeStore.themeMode === 'aurora' }"
      @click="themeStore.setTheme('aurora')"
      :title="$t('theme.aurora')"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/>
      </svg>
    </button>
    <button 
      class="theme-switch__item" 
      :class="{ 'is-active': themeStore.themeMode === 'light' }"
      @click="themeStore.setTheme('light')"
      :title="$t('theme.light')"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="5"/>
        <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"/>
      </svg>
    </button>
    <button 
      class="theme-switch__item" 
      :class="{ 'is-active': themeStore.themeMode === 'dark' }"
      @click="themeStore.setTheme('dark')"
      :title="$t('theme.dark')"
    >
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
      </svg>
    </button>
  </div>
</template>

<script setup>
import { useThemeStore } from '@/stores/theme'

const themeStore = useThemeStore()
</script>

<style lang="scss" scoped>
.theme-switch {
  display: flex;
  align-items: center;
  background: var(--bg-tertiary);
  padding: 3px;
  border-radius: 20px;
  border: 1px solid var(--border-light);
  
  &__item {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 32px;
    height: 28px;
    border: none;
    background: transparent;
    color: var(--text-tertiary);
    cursor: pointer;
    border-radius: 16px;
    transition: all 0.2s ease;
    padding: 0;
    
    &:hover {
      color: var(--text-secondary);
    }
    
    &.is-active {
      background: var(--bg-card);
      color: var(--accent-primary);
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
      
      // Override for Aurora active state
      .theme-switch__item:first-child & {
        
      }
    }
  }
}
</style>
