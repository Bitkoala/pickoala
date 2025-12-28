import { defineStore } from 'pinia'
import { ref, watch } from 'vue'
import api from '@/api'

export const useSiteStore = defineStore('site', () => {
  const settings = ref({
    site_name: 'PicKoala',
    site_title: '考拉云图 - 简洁优雅的图床服务',
    site_description: '免费稳定的图片托管服务',
    site_slogan: '简洁优雅的图床服务',
    site_footer: '考拉云图 - 让图片分享更简单',
    site_logo: '',
    site_logo_dark: '',
    site_favicon: '',
    timezone: 'Asia/Shanghai',
    max_upload_size_guest: 5242880,
    max_upload_size_user: 10485760,
    allowed_extensions: ['png', 'jpg', 'jpeg', 'gif', 'webp'],
    enable_registration: true,
    enable_guest_upload: true,
    guest_rate_limit_per_minute: 3,
    guest_rate_limit_per_hour: 10,
    guest_rate_limit_per_day: 30,
    user_rate_limit_per_minute: 10,
    user_rate_limit_per_hour: 100,
    user_rate_limit_per_day: 500,
    max_upload_size_vip: 52428800,
    vip_rate_limit_per_minute: 30,
    vip_rate_limit_per_hour: 300,
    vip_rate_limit_per_day: 2000,
    // File Rate Limits
    guest_file_limit_per_minute: 1,
    guest_file_limit_per_hour: 3,
    guest_file_limit_per_day: 10,
    user_file_limit_per_minute: 5,
    user_file_limit_per_hour: 20,
    user_file_limit_per_day: 50,
    vip_file_limit_per_minute: 10,
    vip_file_limit_per_hour: 50,
    vip_file_limit_per_day: 200,
    // Homepage Text
    home_features: '[]',
    home_table_cols: '{}',
    home_table_rows: '{}',
  })

  const loaded = ref(false)
  const loading = ref(false)

  const updatePageMeta = () => {
    if (settings.value.site_title) {
      document.title = settings.value.site_title
    }

    if (settings.value.site_favicon) {
      const link = document.querySelector("link[rel*='icon']") || document.createElement('link')
      link.type = 'image/x-icon'
      link.rel = 'shortcut icon'
      link.href = settings.value.site_favicon
      document.getElementsByTagName('head')[0].appendChild(link)
    }
  }

  const loadSettings = async () => {
    if (loading.value) return
    loading.value = true
    try {
      const res = await api.get('/site/settings')
      // Merge settings from API
      Object.assign(settings.value, res.data)
      loaded.value = true
      updatePageMeta()
    } catch (e) {
      console.error('Failed to load settings:', e)
    } finally {
      loading.value = false
    }
  }

  // Computed helpers
  const siteName = () => settings.value.site_name
  const siteTitle = () => settings.value.site_title
  const siteDescription = () => settings.value.site_description
  const siteSlogan = () => settings.value.site_slogan
  const siteFooter = () => settings.value.site_footer
  const siteLogo = () => settings.value.site_logo
  const siteLogoDark = () => settings.value.site_logo_dark
  const siteFavicon = () => settings.value.site_favicon
  const maxSizeGuest = () => settings.value.max_upload_size_guest
  const maxSizeUser = () => settings.value.max_upload_size_user
  const maxSizeGuestMB = () => Math.round(settings.value.max_upload_size_guest / 1024 / 1024)
  const maxSizeUserMB = () => Math.round(settings.value.max_upload_size_user / 1024 / 1024)
  const maxSizeVipMB = () => Math.round(settings.value.max_upload_size_vip / 1024 / 1024)
  const allowedExtensions = () => settings.value.allowed_extensions
  const isRegistrationEnabled = () => settings.value.enable_registration
  const isGuestUploadEnabled = () => settings.value.enable_guest_upload

  const timezone = () => settings.value.timezone || 'Asia/Shanghai'
  // Image Rate Limits
  const guestRateLimitPerMinute = () => settings.value.guest_rate_limit_per_minute
  const guestRateLimitPerHour = () => settings.value.guest_rate_limit_per_hour
  const guestRateLimitPerDay = () => settings.value.guest_rate_limit_per_day
  const userRateLimitPerMinute = () => settings.value.user_rate_limit_per_minute
  const userRateLimitPerHour = () => settings.value.user_rate_limit_per_hour
  const userRateLimitPerDay = () => settings.value.user_rate_limit_per_day
  const vipRateLimitPerMinute = () => settings.value.vip_rate_limit_per_minute
  const vipRateLimitPerHour = () => settings.value.vip_rate_limit_per_hour
  const vipRateLimitPerDay = () => settings.value.vip_rate_limit_per_day

  // File Rate Limits
  const guestFileLimitPerMinute = () => settings.value.guest_file_limit_per_minute
  const guestFileLimitPerHour = () => settings.value.guest_file_limit_per_hour
  const guestFileLimitPerDay = () => settings.value.guest_file_limit_per_day
  const userFileLimitPerMinute = () => settings.value.user_file_limit_per_minute
  const userFileLimitPerHour = () => settings.value.user_file_limit_per_hour
  const userFileLimitPerDay = () => settings.value.user_file_limit_per_day
  const vipFileLimitPerMinute = () => settings.value.vip_file_limit_per_minute
  const vipFileLimitPerHour = () => settings.value.vip_file_limit_per_hour
  const vipFileLimitPerDay = () => settings.value.vip_file_limit_per_day

  return {
    settings,
    loaded,
    loading,
    loadSettings,
    updatePageMeta,
    siteName,
    siteTitle,
    siteDescription,
    siteSlogan,
    siteFooter,
    siteLogo,
    siteLogoDark,
    siteFavicon,
    maxSizeGuest,
    maxSizeUser,
    maxSizeGuestMB,
    maxSizeUserMB,
    maxSizeVipMB,
    allowedExtensions,
    isRegistrationEnabled,
    isGuestUploadEnabled,
    timezone,
    guestRateLimitPerMinute,
    guestRateLimitPerHour,
    guestRateLimitPerDay,
    userRateLimitPerMinute,
    userRateLimitPerHour,
    userRateLimitPerDay,
    vipRateLimitPerMinute,
    vipRateLimitPerHour,
    vipRateLimitPerDay,
    vipRateLimitPerDay,

    // File Rate Limits
    guestFileLimitPerMinute,
    guestFileLimitPerHour,
    guestFileLimitPerDay,
    userFileLimitPerMinute,
    userFileLimitPerHour,
    userFileLimitPerDay,
    vipFileLimitPerMinute,
    vipFileLimitPerHour,
    vipFileLimitPerDay,
    // Helper for boolean values (handles string 'true'/'false' from DB)
    getBool: (key) => {
      const val = settings.value[key]
      return val === true || val === 'true'
    },

    // Payment Configs
    isStripeEnabled: () => settings.value.payment_stripe_enabled === true || settings.value.payment_stripe_enabled === 'true',
    isAlipayEnabled: () => settings.value.payment_alipay_enabled === true || settings.value.payment_alipay_enabled === 'true',

    // Master switch for VIP features: Visible only if at least one payment method is enabled
    isVipFeatureEnabled: () => {
      const s = settings.value
      return (s.payment_stripe_enabled === true || s.payment_stripe_enabled === 'true') ||
        (s.payment_alipay_enabled === true || s.payment_alipay_enabled === 'true')
    },

    // Announcement
    isPopupEnabled: () => settings.value.announcement_popup_enabled === true || settings.value.announcement_popup_enabled === 'true',
    popupContent: () => settings.value.announcement_popup_content,
    isNavbarEnabled: () => settings.value.announcement_navbar_enabled === true || settings.value.announcement_navbar_enabled === 'true',
    navbarContent: () => settings.value.announcement_navbar_content,

    // Homepage Text Getters (Parsed JSON)
    homeFeatures: () => {
      try { return JSON.parse(settings.value.home_features || '[]') } catch { return [] }
    },
    homeTableCols: () => {
      try { return JSON.parse(settings.value.home_table_cols || '{}') } catch { return {} }
    },
    homeTableRows: () => {
      try { return JSON.parse(settings.value.home_table_rows || '{}') } catch { return {} }
    },
    // Helper to get text based on current locale
    getLocalizedText: (obj, locale) => {
      if (!obj || typeof obj !== 'object') return obj || ''
      // Try exact match -> fallback to 'en' -> fallback to 'zh' -> fallback to first key
      return obj[locale] || obj['zh-CN'] || obj['zh'] || obj['en'] || Object.values(obj)[0] || ''
    }
  }
})
