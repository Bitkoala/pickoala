<template>
  <div class="success-page">
    <div class="card">
      <div class="icon-circle">
        <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2">
          <polyline points="20 6 9 17 4 12"></polyline>
        </svg>
      </div>
      
      <h1>{{ $t('vip.successTitle') }}</h1>
      <p>{{ $t('vip.successMessage') }}</p>
      
      <button class="home-btn" @click="goToProfile">
        {{ $t('nav.profile') }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const userStore = useUserStore()

const goToProfile = () => {
  router.push('/profile')
}

onMounted(async () => {
  // Refresh user data to get updated VIP status
  await userStore.loadUser()
  
  // Auto redirect after 5 seconds
  setTimeout(() => {
    goToProfile()
  }, 5000)
})
</script>

<style scoped lang="scss">
.success-page {
  min-height: calc(100vh - 64px);
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-primary);
  padding: 20px;
}

.card {
  background: var(--bg-card);
  padding: 40px;
  border-radius: 24px;
  text-align: center;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.05);
  max-width: 400px;
  width: 100%;
  
  .icon-circle {
    width: 80px;
    height: 80px;
    background: rgba(16, 185, 129, 0.1);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 24px;
  }
  
  h1 {
    margin-bottom: 12px;
    color: var(--text-primary);
  }
  
  p {
    color: var(--text-secondary);
    margin-bottom: 32px;
    line-height: 1.6;
  }
}

.home-btn {
  background: var(--accent-primary);
  color: white;
  border: none;
  padding: 12px 32px;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: opacity 0.2s;
  
  &:hover {
    opacity: 0.9;
  }
}
</style>
