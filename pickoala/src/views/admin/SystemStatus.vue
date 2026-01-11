<template>
  <div class="system-status">
    <div class="page-header">
      <h2 class="page-title">{{ $t('admin.systemStatus.title') || 'System Diagnosis' }}</h2>
      <button class="btn btn-primary" @click="runDiagnosis" :disabled="loading">
        <span v-if="loading" class="spinner"></span>
        {{ loading ? ($t('common.processing') || 'Running...') : ($t('admin.systemStatus.start') || 'Start Diagnosis') }}
      </button>
    </div>

    <!-- Health Checks -->
    <div class="section" v-if="results">
      <h3 class="section-title">{{ $t('admin.systemStatus.healthChecks') || 'Health Checks' }}</h3>
      <div class="health-grid">
        <div 
          v-for="check in results.health_checks" 
          :key="check.name"
          class="health-card" 
          :class="check.status"
        >
          <div class="health-icon">
            <svg v-if="check.status === 'pass'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
          </div>
          <div class="health-info">
            <div class="health-name">
              {{ check.name_key ? $t(check.name_key, check.name_params || {}) : check.name }}
            </div>
            <div class="health-message">
              {{ check.message_key ? $t(check.message_key, check.message_params || {}) : check.message }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Configuration Audit Logs -->
    <div class="section" v-if="results && results.config_audit && results.config_audit.length > 0">
      <h3 class="section-title">{{ $t('admin.systemStatus.configAudit') || 'Configuration Diagnosis' }}</h3>
      <div class="audit-list">
        <div 
          v-for="(log, idx) in results.config_audit" 
          :key="idx" 
          class="audit-item"
          :class="log.level || 'info'"
        >
          <span class="audit-icon">
            <svg v-if="log.level === 'warning'" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
            <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
          </span>
          {{ log.message_key ? $t(log.message_key, log.message_params || {}) : log.message }}
        </div>
      </div>
    </div>

    <!-- Effective Limits Matrix -->
    <div class="section" v-if="results && results.limit_matrix">
      <h3 class="section-title">{{ $t('admin.systemStatus.limitMatrix') || 'Effective Configuration Matrix' }}</h3>
      <p class="section-desc">{{ $t('admin.systemStatus.limitMatrixDesc') || 'This table shows the ACTUAL limits enforced by the backend.' }}</p>
      
      <div class="matrix-container">
        <table class="matrix-table">
          <thead>
            <tr>
              <th>{{ $t('admin.systemStatus.type') }}</th>
              <th>{{ $t('admin.systemStatus.metric') }}</th>
              <th>{{ $t('admin.guest') }}</th>
              <th>{{ $t('admin.member') }}</th>
              <th>VIP</th>
            </tr>
          </thead>
          <tbody>
            <template v-for="(metrics, type) in results.limit_matrix" :key="type">
              <tr>
                <td rowspan="2" class="type-cell">
                  <span class="type-badge" :class="type">{{ type.toUpperCase() }}</span>
                </td>
                <td class="metric-name">{{ $t('admin.systemStatus.maxSize') }}</td>
                <td :class="{ 'zero-val': metrics.size.guest === 0 }">{{ formatSize(metrics.size.guest) }}</td>
                <td :class="{ 'zero-val': metrics.size.user === 0 }">{{ formatSize(metrics.size.user) }}</td>
                <td :class="{ 'zero-val': metrics.size.vip === 0 }">{{ formatSize(metrics.size.vip) }}</td>
              </tr>
              <tr class="row-separator">
                <td class="metric-name">{{ $t('admin.systemStatus.rateLimitHour') }}</td>
                <td :class="{ 'zero-val': metrics.rate_hour.guest === 0 }">{{ metrics.rate_hour.guest }}</td>
                <td :class="{ 'zero-val': metrics.rate_hour.user === 0 }">{{ metrics.rate_hour.user }}</td>
                <td :class="{ 'zero-val': metrics.rate_hour.vip === 0 }">{{ metrics.rate_hour.vip }}</td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="!results && !loading" class="empty-state">
      {{ $t('admin.systemStatus.clickStart') || 'Click "Start Diagnosis" to run checks.' }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import api from '@/api'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const results = ref(null)

const runDiagnosis = async () => {
  loading.value = true
  try {
    const res = await api.post('/admin/diagnosis/check')
    results.value = res.data
    ElMessage.success('Diagnosis completed')
  } catch (e) {
    ElMessage.error('Diagnosis failed: ' + (e.response?.data?.detail || e.message))
  } finally {
    loading.value = false
  }
}

const formatSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style lang="scss" scoped>
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn {
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
  
  &-primary {
    background: var(--accent-primary);
    color: white;
    &:hover { background: var(--accent-hover); }
    &:disabled { opacity: 0.7; cursor: not-allowed; }
  }
}

.section {
  background: var(--bg-card);
  border: 1px solid var(--border-light);
  border-radius: var(--radius-lg);
  padding: 24px;
  margin-bottom: 24px;
}

.section-title {
  font-size: 18px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--text-primary);
}

.section-desc {
  color: var(--text-tertiary);
  margin-bottom: 16px;
  font-size: 14px;
}

/* Health Grid */
.health-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 16px;
}

.health-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-light);
  background: var(--bg-secondary);
  
  &.pass {
    border-color: #10b981;
    background: rgba(16, 185, 129, 0.05);
    .health-icon { color: #10b981; }
  }
  
  &.fail {
    border-color: #ef4444;
    background: rgba(239, 68, 68, 0.05);
    .health-icon { color: #ef4444; }
  }
}

.health-name {
  font-weight: 600;
  color: var(--text-primary);
}

.health-message {
  font-size: 13px;
  color: var(--text-secondary);
}

/* Audit List */
.audit-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.audit-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border-radius: var(--radius-md);
  font-size: 14px;
  
  &.warning {
    background: rgba(245, 158, 11, 0.1);
    color: #d97706;
  }
  
  &.info {
    background: var(--bg-secondary);
    color: var(--text-secondary);
  }
}

/* Matrix Table */
.matrix-container {
  overflow-x: auto;
}

.matrix-table {
  width: 100%;
  border-collapse: collapse;
  
  th {
    text-align: left;
    padding: 12px 16px;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    font-size: 13px;
    font-weight: 600;
  }
  
  td {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border-light);
    color: var(--text-primary);
    font-size: 14px;
  }
  
  .type-cell {
    border-right: 1px solid var(--border-light);
    width: 100px;
    vertical-align: middle;
    text-align: center;
  }
  
  .metric-name {
    color: var(--text-secondary);
    font-size: 13px;
  }
  
  .zero-val {
    color: var(--text-tertiary);
    font-style: italic;
  }
  
  .row-separator td {
    border-bottom: 2px solid var(--border-light); /* Stronger separator between types */
  }
}

.type-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 11px;
  font-weight: 700;
  
  &.image { background: #3b82f6; color: white; }
  &.video { background: #8b5cf6; color: white; }
  &.file { background: #10b981; color: white; }
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: var(--text-tertiary);
}
</style>
