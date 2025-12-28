<template>
  <div class="orders-manage">
    <div class="header">
      <h2>{{ $t('admin.orders.title') }}</h2>
      <div class="actions">
        <el-input
          v-model="searchQuery"
          :placeholder="$t('admin.orders.searchPlaceholder')"
          prefix-icon="Search"
          clearable
          @clear="handleSearch"
          @keyup.enter="handleSearch"
          class="search-input"
        />
        <el-select v-model="statusFilter" @change="handleSearch" class="status-select">
          <el-option label="All" value="all" />
          <el-option label="Paid" value="paid" />
          <el-option label="Pending" value="pending" />
          <el-option label="Failed" value="failed" />
        </el-select>
        <el-button type="primary" @click="handleSearch">
          {{ $t('common.search') }}
        </el-button>
      </div>
    </div>

    <el-card class="table-card">
      <el-table
        v-loading="loading"
        :data="orders"
        style="width: 100%"
        border
      >
        <el-table-column prop="id" label="ID" width="80" align="center" />
        
        <el-table-column :label="$t('admin.orders.user')" min-width="150">
          <template #default="{ row }">
            <div class="user-info">
              <span>{{ row.user.username }}</span>
              <small class="text-gray">{{ row.user.email }}</small>
            </div>
          </template>
        </el-table-column>

        <el-table-column prop="amount" :label="$t('admin.orders.amount')" width="120" align="right">
          <template #default="{ row }">
            {{ row.amount }} {{ row.currency.toUpperCase() }}
          </template>
        </el-table-column>

        <el-table-column prop="plan_type" :label="$t('admin.orders.plan')" width="100">
           <template #default="{ row }">
            <el-tag size="small" effect="plain">{{ row.plan_type }}</el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="provider" :label="$t('admin.orders.provider')" width="100">
          <template #default="{ row }">
            <el-tag type="info" size="small">{{ row.provider }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column prop="status" :label="$t('admin.orders.status')" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">{{ row.status }}</el-tag>
          </template>
        </el-table-column>

        <el-table-column :label="$t('admin.orders.transactionId')" min-width="200" show-overflow-tooltip>
          <template #default="{ row }">
            {{ row.out_trade_no || row.stripe_session_id || '-' }}
          </template>
        </el-table-column>

        <el-table-column prop="created_at" :label="$t('admin.orders.time')" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 50, 100]"
          :total="total"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="handleSizeChange"
          @current-change="handleCurrentChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import api from '@/api'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

const loading = ref(false)
const orders = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const searchQuery = ref('')
const statusFilter = ref('all')

const fetchOrders = async () => {
  loading.value = true
  try {
    const params = {
      page: currentPage.value,
      size: pageSize.value,
      status: statusFilter.value,
      search: searchQuery.value
    }
    const res = await api.get('/admin/orders', { params })
    orders.value = res.data.items
    total.value = res.data.total
  } catch (error) {
    console.error('Failed to fetch orders:', error)
    const errorMsg = error.response?.data?.detail || error.message
    const status = error.response?.status
    ElMessage.error(t('admin.orders.loadFailed') + `: [${status}] ${errorMsg}`)
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchOrders()
}

const handleSizeChange = (val) => {
  pageSize.value = val
  fetchOrders()
}

const handleCurrentChange = (val) => {
  currentPage.value = val
  fetchOrders()
}

const getStatusType = (status) => {
  switch (status.toLowerCase()) {
    case 'paid': return 'success'
    case 'pending': return 'warning'
    case 'failed': return 'danger'
    default: return 'info'
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString()
}

onMounted(() => {
  fetchOrders()
})
</script>

<style scoped>
.orders-manage {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 15px;
}

.search-input {
  width: 250px;
}

.status-select {
  width: 120px;
}

.user-info {
  display: flex;
  flex-direction: column;
}

.text-gray {
  color: #909399;
  font-size: 12px;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>
