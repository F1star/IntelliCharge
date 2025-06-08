<template>
  <div class="bill-list">
    <div class="bill-header">
      <h2>充电详单列表</h2>
      <a-button type="primary" @click="refreshBills">
        <template #icon><reload-outlined /></template>
        刷新
      </a-button>
    </div>

    <a-spin :spinning="loading">
      <a-empty v-if="bills.length === 0" description="暂无充电详单" />
      
      <a-list v-else class="bill-items" :data-source="bills" :pagination="pagination">
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card class="bill-card" :title="`详单编号: ${item.bill_id}`">
              <a-descriptions bordered size="small">
                <a-descriptions-item label="生成时间" :span="2">{{ item.create_time }}</a-descriptions-item>
                <a-descriptions-item label="充电桩编号">{{ item.pile_id }}</a-descriptions-item>
                <a-descriptions-item label="充电电量">{{ item.charging_amount }} 度</a-descriptions-item>
                <a-descriptions-item label="充电时长">{{ item.charging_duration }} 分钟</a-descriptions-item>
                <a-descriptions-item label="启动时间" :span="2">{{ item.start_time }}</a-descriptions-item>
                <a-descriptions-item label="停止时间" :span="2">{{ item.end_time }}</a-descriptions-item>
                <a-descriptions-item label="充电费用">¥ {{ item.charging_cost }}</a-descriptions-item>
                <a-descriptions-item label="服务费用">¥ {{ item.service_cost }}</a-descriptions-item>
                <a-descriptions-item label="总费用">¥ {{ item.total_cost }}</a-descriptions-item>
              </a-descriptions>
            </a-card>
          </a-list-item>
        </template>
      </a-list>
    </a-spin>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useChargingServer } from './server'
import { mainStore } from '../../store'

const userStore = mainStore()
const chargingServer = useChargingServer()
const loading = ref(false)
const bills = ref([])

// 分页配置
const pagination = {
  pageSize: 5,
  showTotal: (total) => `共 ${total} 条记录`
}

// 获取充电详单列表
const fetchBills = async () => {
  try {
    loading.value = true
    const res = await chargingServer.getChargingBills(userStore.username)
    
    if (res.status) {
      bills.value = res.data
    } else {
      message.error(res.msg || '获取充电详单失败')
    }
  } catch (error) {
    message.error('获取充电详单失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

// 刷新充电详单列表
const refreshBills = () => {
  fetchBills()
}

onMounted(() => {
  fetchBills()
})
</script>

<style scoped>
.bill-list {
  padding: 20px;
}

.bill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.bill-items {
  margin-top: 20px;
}

.bill-card {
  width: 100%;
  margin-bottom: 16px;
}
</style> 