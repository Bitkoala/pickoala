<template>
  <div class="auth-page">
    <div class="auth-card">
      <div class="auth-card__header">
        <h1 class="auth-card__title">{{ $t('auth.welcomeBack') }}</h1>
        <p class="auth-card__subtitle">{{ $t('auth.loginToContinue') }}</p>
      </div>
      
      <form class="auth-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label">{{ $t('auth.usernameOrEmail') }}</label>
          <div class="form-input-wrapper">
            <span class="form-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </span>
            <input
              v-model="form.username"
              type="text"
              class="form-input"
              :placeholder="$t('auth.usernameOrEmail')"
              required
            />
          </div>
        </div>
        
        <div class="form-group">
          <label class="form-label">{{ $t('auth.password') }}</label>
          <div class="form-input-wrapper">
            <span class="form-input-icon">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </span>
            <input
              v-model="form.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              :placeholder="$t('auth.password')"
              required
            />
            <button
              type="button"
              class="form-input-toggle"
              @click="showPassword = !showPassword"
            >
              <svg v-if="!showPassword" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Error Message -->
        <div v-if="errorMessage" class="form-error-box">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="8" x2="12" y2="12"/>
            <line x1="12" y1="16" x2="12.01" y2="16"/>
          </svg>
          {{ errorMessage }}
        </div>
        
        <div class="form-group">
          <button type="submit" class="btn btn--primary btn--lg btn--full" :disabled="loading">
            <span v-if="loading" class="btn-loader"></span>
            <span v-else>{{ $t('auth.login') }}</span>
          </button>
        </div>

        <!-- Casdoor Login Divider (only in 'both' mode) -->
        <!-- Divider (only in 'both' mode) -->
        <div v-if="siteStore.isGoogleEnabled() || siteStore.isLinuxdoEnabled() || siteStore.isGithubEnabled()" class="auth-divider-text">
          <span>{{ $t('auth.orContinueWith') }}</span>
        </div>
      </form>

      <!-- OAuth Login Buttons -->
      <div class="oauth-login">
        <button 
          v-if="siteStore.isGoogleEnabled()"
          type="button" 
          class="btn btn--secondary btn--lg btn--full oauth-btn google-btn" 
          :disabled="loading"
          @click="handleOAuthLogin('google')"
        >
          <svg class="oauth-icon" width="20" height="20" viewBox="0 0 24 24">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-1 .67-2.28 1.07-3.71 1.07-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.11c-.22-.66-.35-1.36-.35-2.11s.13-1.45.35-2.11V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l3.66-2.83z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.83c.87-2.6 3.3-4.51 6.16-4.51z" fill="#EA4335"/>
          </svg>
          <span>{{ $t('auth.loginWithGoogle') }}</span>
        </button>
        <button 
          v-if="siteStore.isLinuxdoEnabled()"
          type="button" 
          class="btn btn--secondary btn--lg btn--full oauth-btn linuxdo-btn" 
          :disabled="loading"
          @click="handleOAuthLogin('linuxdo')"
        >
<img src="https://ssl.shanku.lol/pickoala/linux.png" class="oauth-icon" width="20" height="20" alt="Linux.do" />
          <span>{{ $t('auth.loginWithLinuxdo') }}</span>
        </button>
        <button 
          v-if="siteStore.isGithubEnabled()"
          type="button" 
          class="btn btn--secondary btn--lg btn--full oauth-btn github-btn" 
          :disabled="loading"
          @click="handleOAuthLogin('github')"
        >
          <svg class="oauth-icon" width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/>
          </svg>
          <span>{{ $t('auth.loginWithGithub') }}</span>
        </button>
      </div>
      
      <div class="auth-card__footer">
        <router-link to="/forgot-password" class="auth-link">{{ $t('auth.forgotPassword') }}</router-link>
        <span class="auth-divider">·</span>
        <a href="/register" @click.prevent="handleRegister($event) || $router.push('/register')" class="auth-link">{{ $t('auth.register') }}</a>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useSiteStore } from '@/stores/site'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t, te } = useI18n()
const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const siteStore = useSiteStore()

const loading = ref(false)
const showPassword = ref(false)

const handleOAuthLogin = async (provider) => {
  try {
    loading.value = true
    const redirectUri = window.location.origin + '/callback?provider=' + provider
    const res = await api.get(`/auth/oauth/url/${provider}`, { params: { redirect_url: redirectUri } })
    if (res.data.url) {
      window.location.href = res.data.url
    }
  } catch (error) {
    const detail = error.response?.data?.detail || ''
    if (detail && te(detail)) {
      ElMessage.error(t(detail))
    } else {
      ElMessage.error(detail || t('error.operationFailed'))
    }
  } finally {
    loading.value = false
  }
}


const form = reactive({
  username: '',
  password: '',
})

const errorMessage = ref('')

const handleSubmit = async () => {
  errorMessage.value = ''
  
  if (!form.username.trim()) {
    errorMessage.value = t('error.fieldRequired')
    return
  }
  
  if (!form.password) {
    errorMessage.value = t('error.fieldRequired')
    return
  }
  
  loading.value = true
  try {
    await userStore.login(form.username.trim(), form.password)
    ElMessage.success(t('auth.loginSuccess'))
    
    const redirect = route.query.redirect || '/'
    router.push(redirect)
  } catch (error) {
    const detail = error.response?.data?.detail || ''
    if (detail && te(detail)) {
      errorMessage.value = t(detail)
    } else if (detail.includes('password') || detail.includes('username')) {
      errorMessage.value = t('error.invalidCredentials')
    } else if (detail.includes('verified')) {
      errorMessage.value = t('error.emailNotVerified')
    } else if (detail.includes('disabled')) {
      errorMessage.value = t('error.accountDisabled')
    } else if (detail.includes('locked')) {
      errorMessage.value = t('error.accountLocked')
    } else {
      errorMessage.value = detail || t('auth.loginFailed')
    }
  } finally {
    loading.value = false
  }
}
</script>

<style lang="scss" scoped>
.auth-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: calc(100vh - 280px);
  padding: 40px 0;
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  padding: 40px;
  box-shadow: var(--shadow-neu-flat);
  
  &__header {
    text-align: center;
    margin-bottom: 32px;
  }
  
  &__title {
    font-size: var(--text-2xl);
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 8px;
  }
  
  &__subtitle {
    font-size: var(--text-sm);
    color: var(--text-tertiary);
  }
  
  &__footer {
    text-align: center;
    margin-top: 24px;
    padding-top: 24px;
    border-top: 1px solid var(--border-light);
  }
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.form-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.form-input-icon {
  position: absolute;
  left: 14px;
  color: var(--text-tertiary);
  pointer-events: none;
  display: flex;
}

.form-input {
  width: 100%;
  padding: 14px 14px 14px 44px;
  font-family: var(--font-sans);
  font-size: var(--text-sm);
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-neu-pressed);
  transition: all var(--transition-fast);
  
  &::placeholder {
    color: var(--text-tertiary);
  }
  
  &:hover {
    background: var(--bg-tertiary);
  }
  
  &:focus {
    outline: none;
    background: var(--bg-card);
    border-color: var(--border-medium);
    box-shadow: var(--shadow-neu-flat);
  }
}

.form-input-toggle {
  position: absolute;
  right: 14px;
  background: none;
  border: none;
  color: var(--text-tertiary);
  cursor: pointer;
  display: flex;
  padding: 4px;
  
  &:hover {
    color: var(--text-secondary);
  }
}

.auth-link {
  font-size: var(--text-sm);
  color: var(--text-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
  
  &:hover {
    color: var(--text-primary);
  }
}

.auth-divider {
  margin: 0 12px;
  color: var(--border-medium);
}

.form-error-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  background: var(--accent-danger-bg);
  color: var(--accent-danger);
  border-radius: var(--radius-md);
  font-size: var(--text-sm);
  
  svg {
    flex-shrink: 0;
  }
}

.btn {
  &--full {
    width: 100%;
  }
  
  &--lg {
    padding: 16px 32px;
    font-size: var(--text-base);
  }
}

.btn-loader {
  width: 18px;
  height: 18px;
  border: 2px solid transparent;
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.oauth-login {
  display: flex;
  flex-direction: column;
  gap: 12px;
  
  &.is-only {
    margin-top: 20px;
  }
}

.oauth-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 12px 24px;
}

.oauth-icon {
  flex-shrink: 0;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
