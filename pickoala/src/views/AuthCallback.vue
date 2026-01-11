<template>
  <div class="auth-callback">
    <div class="callback-container">
      <div v-if="error" class="error-state">
        <el-icon class="error-icon"><CircleCloseFilled /></el-icon>
        <h2>{{ $t('auth.loginFailed') }}</h2>
        <p>{{ error }}</p>
        <el-button type="primary" @click="$router.push('/login')">
          {{ $t('auth.backToLogin') }}
        </el-button>
      </div>
      <div v-else class="loading-state">
        <el-icon class="loading-icon is-loading"><Loading /></el-icon>
        <h2>{{ $t('auth.authenticating') }}</h2>
        <p>{{ $t('auth.pleaseWait') }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'
import { Loading, CircleCloseFilled } from '@element-plus/icons-vue'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()
const { t, te } = useI18n()

const error = ref(null)

onMounted(async () => {
  const code = route.query.code
  const state = route.query.state
  const provider = route.query.provider || 'google' // Default or error if missing

  if (!code) {
    error.value = t('error.invalidCallback')
    return
  }

  try {
    const redirectUrl = window.location.origin + '/callback?provider=' + provider
    await userStore.loginWithOAuth(provider, code, state, redirectUrl)
    ElMessage.success(t('auth.loginSuccess'))
    
    // Redirect to home or saved redirect path
    const redirectPath = localStorage.getItem('redirectPath') || '/'
    localStorage.removeItem('redirectPath')
    router.push(redirectPath)
  } catch (err) {
    console.error('OAuth login error:', err)
    const detail = err.response?.data?.detail || ''
    if (detail && te(detail)) {
        error.value = t(detail)
    } else {
        error.value = detail || t('error.operationFailed')
    }
  }
})
</script>

<style scoped>
.auth-callback {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 60vh;
}

.callback-container {
  text-align: center;
  padding: 40px;
  background: var(--bg-card);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  max-width: 400px;
  width: 100%;
}

.loading-icon, .error-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.loading-icon {
  color: var(--color-primary);
}

.error-icon {
  color: var(--color-danger);
}

h2 {
  margin-bottom: 12px;
  color: var(--text-primary);
}

p {
  color: var(--text-secondary);
  margin-bottom: 24px;
}
</style>
落。
