import { defineStore } from 'pinia'
import { ref, watch, computed } from 'vue'
import { useSiteStore } from './site'

export const useThemeStore = defineStore('theme', () => {
  const themeMode = ref('light')

  // Initialize from localStorage -> backend settings (TODO) -> system preference
  const initTheme = () => {
    const savedTheme = localStorage.getItem('theme')
    if (savedTheme && ['light', 'dark', 'aurora'].includes(savedTheme)) {
      themeMode.value = savedTheme
    } else {
      // Check backend default setting
      const siteStore = useSiteStore()
      const defaultMode = siteStore.settings.appearance?.theme_mode

      if (defaultMode && ['light', 'dark', 'aurora'].includes(defaultMode)) {
        themeMode.value = defaultMode
      } else {
        // Fallback to system preference
        const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
        themeMode.value = prefersDark ? 'dark' : 'light'
      }
    }
    applyTheme()
  }

  const applyTheme = () => {
    document.documentElement.setAttribute('data-theme', themeMode.value)

    // Helper class for global styles that depend on "dark-ness"
    if (themeMode.value === 'dark' || themeMode.value === 'aurora') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  }

  const toggleTheme = () => {
    // Cycle: light -> dark -> aurora -> light
    if (themeMode.value === 'light') setTheme('dark')
    else if (themeMode.value === 'dark') setTheme('aurora')
    else setTheme('light')
  }

  const setTheme = (mode) => {
    if (!['light', 'dark', 'aurora'].includes(mode)) return
    themeMode.value = mode
    localStorage.setItem('theme', mode)
    applyTheme()
  }

  // Computed for backward compatibility
  const isDark = computed({
    get: () => themeMode.value === 'dark' || themeMode.value === 'aurora',
    set: (val) => setTheme(val ? 'dark' : 'light')
  })

  // Watch for changes
  watch(themeMode, applyTheme)

  return {
    themeMode,
    isDark,
    initTheme,
    toggleTheme,
    setTheme,
  }
})
