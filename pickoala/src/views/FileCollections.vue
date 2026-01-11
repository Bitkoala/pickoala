<template>
  <div class="page">
    <div class="page__header">
      <div class="header-left">
        <button class="back-btn" @click="$router.push('/files')">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="15,18 9,12 15,6"/>
          </svg>
          {{ $t('common.back') || '返回' }}
        </button>
        <h1 class="page__title">{{ $t('fileCollections.title') || '文件集' }}</h1>
      </div>
      <button class="btn btn--primary" @click="showCreateDialog">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        {{ $t('fileCollections.create') || '新建文件集' }}
      </button>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="loading__spinner"></div>
    </div>
    
    <div v-else-if="collections.length === 0" class="empty-state">
      <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
        <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
      </svg>
      <p>{{ $t('fileCollections.noCollections') || '暂无文件集' }}</p>
      <button class="btn btn--primary" @click="showCreateDialog">{{ $t('fileCollections.createFirst') || '创建第一个文件集' }}</button>
    </div>
    
    <div v-else class="collection-grid">
      <div
        v-for="collection in collections"
        :key="collection.id"
        class="collection-card"
        @click="$router.push(`/file-collections/${collection.id}`)"
      >
        <div class="collection-card__icon">
          <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
          </svg>
        </div>
        <div class="collection-card__info">
          <h3 class="collection-card__name">{{ collection.name }}</h3>
          <p v-if="collection.description" class="collection-card__desc">{{ collection.description }}</p>
          <span class="collection-card__count">{{ $t('fileCollections.fileCount', { count: collection.file_count || 0 }) || `${collection.file_count || 0} 个文件` }}</span>
        </div>
        <div class="collection-card__actions" @click.stop>
          <button class="icon-btn" @click="showEditDialog(collection)" :title="$t('common.edit') || '编辑'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
              <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
          </button>
          <button class="icon-btn icon-btn--danger" @click="deleteCollection(collection)" :title="$t('common.delete') || '删除'">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3,6 5,6 21,6"/><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Dialog -->
    <div v-if="dialogVisible" class="dialog-overlay" @click.self="dialogVisible = false">
      <div class="dialog">
        <div class="dialog__header">
          <h3>{{ editingCollection ? ($t('fileCollections.edit') || '编辑文件集') : ($t('fileCollections.create') || '新建文件集') }}</h3>
          <button class="dialog__close" @click="dialogVisible = false">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        <div class="dialog__body">
          <div class="form-group">
            <label class="form-label">{{ $t('fileCollections.name') || '名称' }} <span class="required">*</span></label>
            <input v-model="form.name" type="text" class="form-input" :placeholder="$t('fileCollections.namePlaceholder') || '请输入名称'" />
          </div>
          <div class="form-group">
            <label class="form-label">{{ $t('common.description') || '描述' }}</label>
            <textarea v-model="form.description" class="form-input form-textarea" :placeholder="$t('fileCollections.descPlaceholder') || '可选描述'" rows="3"></textarea>
          </div>
          <!-- Temporarily disabled as per user request
          <div class="form-group form-group--inline">
            <label class="form-label" :title="$t('fileCollections.publicHint')">{{ $t('fileCollections.isPublic') || '公开文件集' }}</label>
            <label class="switch">
              <input type="checkbox" v-model="form.is_public" />
              <span class="switch__slider"></span>
            </label>
          </div>
          -->
        </div>
        <div class="dialog__footer">
          <button class="btn btn--secondary" @click="dialogVisible = false">{{ $t('common.cancel') || '取消' }}</button>
          <button class="btn btn--primary" @click="submitForm" :disabled="!form.name || submitting">
            {{ submitting ? ($t('common.loading') || '处理中...') : (editingCollection ? ($t('common.save') || '保存') : ($t('common.create') || '创建')) }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useI18n } from 'vue-i18n'
import api from '@/api'

const { t } = useI18n()
const collections = ref([])
const loading = ref(false)
const dialogVisible = ref(false)
const editingCollection = ref(null)
const submitting = ref(false)

const form = reactive({
  name: '',
  description: '',
  is_public: false,
})

const loadCollections = async () => {
  loading.value = true
  try {
    const response = await api.get('/file-collections')
    collections.value = response.data.items || []
  } catch (error) {
    console.error(error)
    ElMessage.error(t('error.loadFailed') || '加载失败')
  } finally {
    loading.value = false
  }
}

const showCreateDialog = () => {
  editingCollection.value = null
  form.name = ''
  form.description = ''
  form.is_public = false
  dialogVisible.value = true
}

const showEditDialog = (collection) => {
  editingCollection.value = collection
  form.name = collection.name
  form.description = collection.description || ''
  form.is_public = collection.is_public
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!form.name) return
  
  submitting.value = true
  try {
    if (editingCollection.value) {
      await api.put(`/file-collections/${editingCollection.value.id}`, form)
      ElMessage.success(t('common.updateSuccess') || '更新成功')
    } else {
      await api.post('/file-collections', form)
      ElMessage.success(t('common.createSuccess') || '创建成功')
    }
    dialogVisible.value = false
    loadCollections()
  } catch (error) {
    console.error(error)
    ElMessage.error(error.response?.data?.detail || (t('error.operationFailed') || '操作失败'))
  } finally {
    submitting.value = false
  }
}

const deleteCollection = async (collection) => {
  try {
    await ElMessageBox.confirm(
      t('fileCollections.deleteConfirm') || '确定要删除这个文件集吗？文件不会被删除。',
      t('common.confirm') || '确认',
      { type: 'warning' }
    )
    await api.delete(`/file-collections/${collection.id}`)
    ElMessage.success(t('common.deleteSuccess') || '删除成功')
    loadCollections()
  } catch (error) {
    if (error !== 'cancel') console.error(error)
  }
}

onMounted(() => {
  loadCollections()
})
</script>

<style lang="scss" scoped>
.page {
  width: 100%;
  max-width: 1200px;
  margin: 0 auto;
  padding: 24px 20px;
  box-sizing: border-box;
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    gap: 24px;
    padding-bottom: 24px;
    border-bottom: 1px solid var(--border-light);

    .header-left {
      display: flex;
      align-items: center;
      gap: 16px;
    }
  }
  
  &__title {
    font-size: 28px;
    font-weight: 700;
    color: var(--text-primary);
    margin: 0;
    letter-spacing: -0.5px;
  }
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  font-size: 14px;
  color: var(--text-secondary);
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
}

.loading {
  display: flex;
  justify-content: center;
  padding: 60px;
  
  &__spinner {
    width: 32px;
    height: 32px;
    border: 3px solid var(--border-light);
    border-top-color: var(--text-primary);
    border-radius: 50%;
    animation: spin 0.8s linear infinite;
  }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-tertiary);
  
  svg { margin-bottom: 16px; }
  p { margin: 0 0 20px; font-size: 15px; }
}

.collection-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.collection-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: var(--bg-card);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-neu-flat);
  cursor: pointer;
  transition: all 0.2s;
  
  &:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-neu-convex);
  }
  
  &__icon {
    width: 56px;
    height: 56px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: var(--bg-secondary);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    flex-shrink: 0;
  }
  
  &__info {
    flex: 1;
    min-width: 0;
  }
  
  &__name {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
    margin: 0 0 4px;
  }
  
  &__desc {
    font-size: 13px;
    color: var(--text-tertiary);
    margin: 0 0 4px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }
  
  &__count {
    font-size: 12px;
    color: var(--text-tertiary);
  }
  
  &__actions {
    display: flex;
    gap: 4px;
  }
}

.icon-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--bg-secondary);
  border: none;
  border-radius: var(--radius-sm);
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.15s;
  
  &:hover {
    background: var(--bg-tertiary);
    color: var(--text-primary);
  }
  
  &--danger:hover {
    background: var(--accent-danger-bg);
    color: var(--accent-danger);
  }
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 500;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: all 0.15s;
  
  &--primary {
    background: var(--accent-primary);
    color: var(--text-inverse);
    
    &:hover { opacity: 0.9; }
    &:disabled { opacity: 0.5; cursor: not-allowed; }
  }
  
  &--secondary {
    background: var(--bg-secondary);
    color: var(--text-primary);
    
    &:hover { background: var(--bg-tertiary); }
  }
}

// Dialog
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  width: 100%;
  max-width: 420px;
  background: var(--bg-card);
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-lg);
  
  &__header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border-light);
    
    h3 {
      font-size: 16px;
      font-weight: 600;
      color: var(--text-primary);
      margin: 0;
    }
  }
  
  &__close {
    background: none;
    border: none;
    color: var(--text-tertiary);
    cursor: pointer;
    padding: 4px;
    
    &:hover { color: var(--text-primary); }
  }
  
  &__body {
    padding: 24px;
  }
  
  &__footer {
    display: flex;
    justify-content: flex-end;
    gap: 12px;
    padding: 16px 24px;
    border-top: 1px solid var(--border-light);
  }
}

.form-group {
  margin-bottom: 20px;
  
  &:last-child { margin-bottom: 0; }
  
  &--inline {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
}

.form-label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  margin-bottom: 8px;
  
  .required { color: var(--accent-danger); }
}

.form-input {
  width: 100%;
  padding: 10px 14px;
  font-size: 14px;
  color: var(--text-primary);
  background: var(--bg-secondary);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  transition: all 0.15s;
  
  &::placeholder { color: var(--text-tertiary); }
  &:focus {
    outline: none;
    border-color: var(--border-medium);
    background: var(--bg-card);
  }
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
}

.switch {
  position: relative;
  display: inline-block;
  width: 44px;
  height: 24px;
  
  input {
    opacity: 0;
    width: 0;
    height: 0;
    
    &:checked + .switch__slider {
      background: var(--accent-primary);
      
      &::before {
        transform: translateX(20px);
      }
    }
  }
  
  &__slider {
    position: absolute;
    inset: 0;
    background: var(--bg-tertiary);
    border-radius: 12px;
    cursor: pointer;
    transition: 0.2s;
    
    &::before {
      content: '';
      position: absolute;
      left: 2px;
      top: 2px;
      width: 20px;
      height: 20px;
      background: white;
      border-radius: 50%;
      transition: 0.2s;
      box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
  }
}
</style>
