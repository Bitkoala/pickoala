<template>
  <div class="upgrade-page">
    <div class="upgrade-container">
      <div class="header-section">
        <h1>{{ $t('vip.upgradeTitle') }}</h1>
        <p class="subtitle">{{ $t('vip.upgradeSubtitle') }}</p>
      </div>
      
      <!-- VIP Benefits Summary -->
      <div class="benefits-summary">
        <div class="crown-icon">
          <svg width="48" height="48" viewBox="0 0 24 24" fill="#F59E0B">
            <path d="M5 16L3 5l5.5 5L12 4l3.5 6L21 5l-2 11H5zm14 3c0 .6-.4 1-1 1H6c-.6 0-1-.4-1-1v-1h14v1z"/>
          </svg>
        </div>
        <div class="benefit-items">
          <div class="benefit-item">
            <span class="check-icon">✓</span><span>{{ $t('vip.benefit1') }}</span>
          </div>
          <div class="benefit-item">
            <span class="check-icon">✓</span><span>{{ $t('vip.benefit2') }}</span>
          </div>
          <div class="benefit-item">
            <span class="check-icon">✓</span><span>{{ $t('vip.benefit3') }}</span>
          </div>
        </div>
      </div>

      <!-- Pricing Cards Grid -->
      <div class="pricing-grid" v-if="availablePlans.length > 0">
        <div 
          v-for="plan in availablePlans" 
          :key="plan.key"
          class="pricing-card"
          :class="{ 'recommended': plan.key === 'year' || plan.key === 'forever' }"
        >
          <div class="card-badge" v-if="plan.key === 'year'">{{ $t('vip.recommended') }}</div>
          <div class="card-badge best-value" v-if="plan.key === 'forever'">{{ $t('vip.bestValue') }}</div>
          
          <div class="card-header">
            <h3>{{ getPlanName(plan.key) }}</h3>
          </div>
          
          <div class="card-price">
            <span class="currency">¥</span>
            <span class="amount">{{ plan.price }}</span>
          </div>
          
          <div class="card-features">
            <!-- Dynamic features based on plan type could go here -->

             <p v-if="plan.key === 'year'">{{ $t('vip.save20') }}</p>
             <p v-if="plan.key === 'forever'">{{ $t('vip.oneTime') }}</p>
          </div>

          <button class="subscribe-btn" @click="openPaymentModal(plan)">
            {{ $t('vip.subscribeNow') }}
          </button>
        </div>
      </div>
      
      <!-- Secure Payment Note -->
      <div class="secure-footer">
        <p class="secure-note">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
            <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
          </svg>
          {{ $t('vip.securePayment') }}
        </p>
      </div>

      <!-- Payment Method Selection Modal -->
      <div v-if="showPaymentModal" class="modal-overlay" @click.self="closePaymentModal">
        <div class="modal-content payment-modal">
          <div class="modal-header">
            <h3>{{ $t('vip.subscribeNow') }} - {{ getPlanName(selectedPlanObj?.key) }}</h3>
            <button class="close-icon" @click="closePaymentModal">&times;</button>
          </div>
          
          <div class="modal-body">
            <p class="payment-amount">{{ $t('nav.totalAmount', { amount: `¥ ${selectedPlanObj?.price}` }) }}</p>
            
            <div class="payment-methods-grid">
               <label class="method-card" :class="{ active: paymentMethod === 'stripe' }" v-if="siteStore.isStripeEnabled()">
                 <input type="radio" value="stripe" v-model="paymentMethod">
                 <img src="@/assets/images/stripe.png" alt="Stripe" class="method-logo stripe-logo" />
                 <span class="method-label">{{ $t('nav.paymentMethod.stripe') }}</span>
               </label>
               <label class="method-card" :class="{ active: paymentMethod === 'alipay' }" v-if="siteStore.isAlipayEnabled()">
                 <input type="radio" value="alipay" v-model="paymentMethod">
                 <img src="@/assets/images/alipay.png" alt="Alipay" class="method-logo alipay-logo" />
                 <span class="method-label">{{ $t('nav.paymentMethod.alipay') }}</span>
               </label>
            </div>
            
            <button class="confirm-pay-btn" @click="confirmPayment" :disabled="loading || !paymentMethod">
              <span v-if="loading">{{ $t('common.processing') }}</span>
              <span v-else>{{ $t('common.confirm') }}</span>
            </button>
          </div>
        </div>
      </div>
      
      <!-- Alipay QR Modal (Nested or Separate? Separate is cleaner) -->
      <div v-if="showAlipayQrModal" class="modal-overlay" @click.self="closeAlipayQrModal">
        <div class="modal-content qr-modal">
          <h3>{{ $t('nav.scanToPay') }}</h3>
          <div class="qr-container">
            <img :src="alipayQrCode" alt="Alipay QR Code" />
          </div>
          <p class="amount-text">¥ {{ selectedPlanObj?.price }}</p>
          <p class="hint-text">{{ $t('nav.useAlipayApp') }}</p>
          <button class="close-btn" @click="closeAlipayQrModal">{{ $t('common.close') }}</button>
        </div>
      </div>

      <!-- Activation Code Redemption -->
      <div class="activation-section">
        <h3>{{ $t('vip.activationTitle') }}</h3>
        <p>{{ $t('vip.activationDesc') }}</p>
        <div class="activation-input-group">
            <input 
                type="text" 
                v-model="activationCode" 
                :placeholder="$t('vip.activationPlaceholder')"
                @keyup.enter="redeemCode"
            >
            <button @click="redeemCode" :disabled="!activationCode || redeeming">
                {{ redeeming ? $t('common.processing') : $t('vip.redeem') }}
            </button>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onUnmounted, computed, watch, onMounted, watchEffect } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import QRCode from 'qrcode'
import api from '@/api'
import { useUserStore } from '@/stores/user'
import { useSiteStore } from '@/stores/site'

const { t } = useI18n()
const router = useRouter()
const userStore = useUserStore()
const siteStore = useSiteStore()

const loading = ref(false)
const paymentMethod = ref('') 
const showPaymentModal = ref(false)
const showAlipayQrModal = ref(false)
const alipayQrCode = ref('')
const selectedPlanObj = ref(null)
const availablePlans = ref([])
const activationCode = ref('')
const redeeming = ref(false)
let pollTimer = null

const redeemCode = async () => {
    if (!activationCode.value) return
    redeeming.value = true
    try {
        const res = await api.post('/activation/redeem', { code: activationCode.value })
        ElMessage.success(t('vip.redeemSuccess'))
        // Refresh user data
        await userStore.loadUser()
        activationCode.value = ''
        router.push('/vip/success')
    } catch (error) {
        ElMessage.error(error.response?.data?.detail || t('vip.redeemFailed'))
    } finally {
        redeeming.value = false
    }
}

// Load Plans
onMounted(async () => {
    if (siteStore.settings.vip_plans) {
        processPlans(siteStore.settings.vip_plans)
    } else {
        await siteStore.fetchSettings()
        processPlans(siteStore.settings.vip_plans)
    }
})

const processPlans = (plansData) => {
    if (!plansData) return
    const plans = []
    const typeMap = { 'month': 0, 'quarter': 1, 'year': 2, 'forever': 3 }
    
    Object.keys(plansData).forEach(key => {
        if (plansData[key].enabled) {
            plans.push({
                key: key,
                ...plansData[key],
                order: typeMap[key] || 99
            })
        }
    })
    plans.sort((a,b) => a.order - b.order)
    availablePlans.value = plans
}

watch(() => siteStore.settings.vip_plans, (newVal) => {
    processPlans(newVal)
}, { deep: true })

const getPlanName = (key) => {
    if (!key) return ''
    const map = {
        'month': t('vip.month'),
        'quarter': t('vip.quarter'),
        'year': t('vip.year'),
        'forever': t('vip.forever')
    }
    return map[key] || key
}

// Auto-select payment method
watchEffect(() => {
  if (siteStore.loaded && !paymentMethod.value) {
    if (siteStore.isStripeEnabled()) paymentMethod.value = 'stripe'
    else if (siteStore.isAlipayEnabled()) paymentMethod.value = 'alipay'
  }
})

const openPaymentModal = (plan) => {
    if (!userStore.isLoggedIn) {
        router.push({ name: 'Login', query: { redirect: '/vip/upgrade' } })
        return
    }
    selectedPlanObj.value = plan
    showPaymentModal.value = true
}

const closePaymentModal = () => {
    showPaymentModal.value = false
}

const confirmPayment = async () => {
    if (!selectedPlanObj.value) return
    
    if (paymentMethod.value === 'stripe') {
        loading.value = true
        try {
            const response = await api.post('/payments/checkout', {
                plan: selectedPlanObj.value.key
            })
            if (response.data.url) {
                window.location.href = response.data.url
            } else {
                ElMessage.error('Failed to get checkout URL')
            }
        } catch (error) {
            ElMessage.error(error.response?.data?.detail || 'Upgrade failed')
        } finally {
            loading.value = false
        }
    } else if (paymentMethod.value === 'alipay') {
        loading.value = true
        try {
            const response = await api.post('/payments/alipay/pay', {
                plan: selectedPlanObj.value.key
            })
            const { qr_code, out_trade_no } = response.data
            
            alipayQrCode.value = await QRCode.toDataURL(qr_code)
            showPaymentModal.value = false // Close selection modal
            showAlipayQrModal.value = true // Open QR modal
            
            startPolling(out_trade_no)
        } catch (error) {
           ElMessage.error(error.response?.data?.detail || 'Alipay failed')
        } finally {
           loading.value = false
        }
    }
}

const startPolling = (outTradeNo) => {
  if (pollTimer) clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const res = await api.get(`/payments/alipay/check/${outTradeNo}`)
      if (res.data.status === 'paid') {
        clearInterval(pollTimer)
        showAlipayQrModal.value = false
        ElMessage.success('Payment Successful!')
        router.push('/vip/success')
      }
    } catch (e) { console.error(e) }
  }, 2000)
}

const closeAlipayQrModal = () => {
  showAlipayQrModal.value = false
  if (pollTimer) clearInterval(pollTimer)
}

onUnmounted(() => {
  if (pollTimer) clearInterval(pollTimer)
})
</script>

<style scoped lang="scss">
.upgrade-page {
  min-height: calc(100vh - 64px);
  /* background: var(--bg-primary); Removed to allow MainLayout background to show through */
  display: flex;
  justify-content: center;
  padding: 60px 20px;
}

.upgrade-container {
  max-width: 1400px;
  width: 100%;
  text-align: center;
}

.header-section {
  margin-bottom: 40px;
  
  h1 {
    font-size: 32px;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 12px;
  }
  
  .subtitle {
    color: var(--text-secondary);
    font-size: 18px;
  }
}

.benefits-summary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 32px;
  margin-bottom: 60px;
  flex-wrap: wrap;
  
  .crown-icon {
    filter: drop-shadow(0 0 15px rgba(245, 158, 11, 0.5));
  }
  
  .benefit-items {
    display: flex;
    gap: 24px;
    
    @media (max-width: 768px) {
      flex-direction: column;
      gap: 12px;
    }
  }
  
  .benefit-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16px;
    color: var(--text-primary);
    
    .check-icon {
      color: #10B981;
      background: rgba(16, 185, 129, 0.1);
      width: 20px;
      height: 20px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
    }
  }
}

// Pricing Grid
.pricing-grid {
  display: flex;
  justify-content: center;
  gap: 24px;
  flex-wrap: wrap;
  margin-bottom: 40px;
}

.pricing-card {
  flex: 1;
  min-width: 240px;
  max-width: 300px;
  background: var(--bg-card);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 20px;
  padding: 32px;
  border: 1px solid var(--border-light);
  display: flex;
  flex-direction: column;
  position: relative;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  
  &:hover {
    transform: translateY(-8px);
    box-shadow: var(--shadow-xl);
    border-color: var(--accent-primary);
  }
  
  &.recommended {
    border-color: var(--accent-primary);
    background: rgba(var(--accent-primary-rgb), 0.03); // check rgb usage later
  }
  
  .card-badge {
    position: absolute;
    top: -12px;
    left: 50%;
    transform: translateX(-50%);
    background: #F59E0B;
    color: white;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    box-shadow: 0 4px 10px rgba(245, 158, 11, 0.3);
    
    &.best-value {
      background: var(--accent-secondary);
      box-shadow: 0 4px 10px rgba(189, 0, 255, 0.3);
    }
  }
  
  .card-header h3 {
    margin: 0 0 16px;
    font-size: 18px;
    color: var(--text-secondary);
    font-weight: 600;
  }
  
  .card-price {
    margin-bottom: 24px;
    color: var(--text-primary);
    
    .currency { font-size: 24px; vertical-align: top; }
    .amount { font-size: 48px; font-weight: 700; line-height: 1; }
  }
  
  .card-features {
    flex: 1;
    margin-bottom: 32px;
    color: var(--text-secondary);
    font-size: 14px;
    
    p { margin: 8px 0; }
  }
  
  .subscribe-btn {
    width: 100%;
    padding: 14px;
    border-radius: 12px;
    background: var(--bg-secondary);
    color: var(--text-primary);
    border: 1px solid var(--border-light);
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    
    &:hover {
      background: var(--accent-primary);
      color: var(--text-inverse);
      border-color: transparent;
    }
  }
}

.secure-footer {
  margin-top: 40px;
}
.secure-note {
  font-size: 13px;
  color: var(--text-tertiary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

// Modal
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-card);
  padding: 32px;
  border-radius: 20px;
  width: 90%;
  max-width: 440px;
  box-shadow: var(--shadow-2xl);
  border: 1px solid var(--border-light);
  
  &.qr-modal {
    text-align: center;
    max-width: 360px;
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  
  h3 { margin: 0; font-size: 20px; color: var(--text-primary); }
  .close-icon {
    background: none;
    border: none;
    font-size: 24px;
    color: var(--text-tertiary);
    cursor: pointer;
    &:hover { color: var(--text-primary); }
  }
}

.payment-amount {
  font-size: 24px;
  font-weight: 700;
  color: var(--text-primary);
  text-align: center;
  margin-bottom: 32px;
}

.payment-methods-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
  margin-bottom: 32px;
}

.method-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border: 1px solid var(--border-light);
  border-radius: 12px;
  cursor: pointer;
  background: var(--bg-secondary);
  transition: all 0.2s;
  
  input { display: none; }
  
  .method-logo { height: 32px; object-fit: contain; }
  .method-label { font-size: 13px; font-weight: 500; color: var(--text-secondary); }
  
  &:hover { background: var(--bg-tertiary); }
  
  &.active {
    border-color: var(--accent-primary);
    background: rgba(var(--accent-primary-rgb), 0.05); // check rgb usage
    box-shadow: 0 0 0 2px rgba(var(--accent-primary-rgb), 0.1);
  }
}

.confirm-pay-btn {
  width: 100%;
  padding: 16px;
  border-radius: 12px;
  background: linear-gradient(135deg, #F59E0B, #D97706);
  color: white;
  border: none;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  
  &:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);
  }
  
  &:disabled { opacity: 0.6; cursor: not-allowed; }
}

.qr-container img { width: 100%; }
.close-btn { 
  margin-top: 20px; 
  background: var(--bg-secondary); 
  border: none; 
  padding: 8px 20px; 
  border-radius: 8px; 
  cursor: pointer;
  color: var(--text-primary);
}

.activation-section {
    margin-top: 60px;
    padding-top: 40px;
    border-top: 1px solid var(--border-light);
    max-width: 600px;
    margin-left: auto;
    margin-right: auto;
    
    h3 {
        color: var(--text-primary);
        font-size: 20px;
        margin-bottom: 8px;
    }
    
    p {
        color: var(--text-secondary);
        font-size: 14px;
        margin-bottom: 20px;
    }
}

.activation-input-group {
    display: flex;
    gap: 12px;
    
    input {
        flex: 1;
        padding: 12px 16px;
        border: 1px solid var(--border-light);
        border-radius: 12px;
        background: var(--bg-card);
        color: var(--text-primary);
        font-size: 16px;
        outline: none;
        
        &:focus {
            border-color: var(--accent-primary);
        }
    }
    
    button {
        padding: 0 24px;
        background: var(--bg-secondary);
        color: var(--text-primary);
        border: 1px solid var(--border-light);
        border-radius: 12px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s;
        
        &:hover:not(:disabled) {
            background: var(--accent-primary);
            color: white;
            border-color: transparent;
        }
        
        &:disabled {
            opacity: 0.6;
            cursor: not-allowed;
        }
    }
}
</style>
