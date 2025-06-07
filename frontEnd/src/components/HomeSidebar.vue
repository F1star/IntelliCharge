<template>
  <div class="home-sidebar">
    <a-card class="queue-card">
      <template #title>
        <div class="card-title">
          <span>充电站状态</span>
          <a-button type="primary" @click="refreshQueueStatus">
            <template #icon><reload-outlined /></template>
            刷新
          </a-button>
        </div>
      </template>

      <a-spin :spinning="loading">
        <div class="queue-status">
          <div class="queue-info">
            <div class="queue-item">
              <h4>快充队列</h4>
              <a-tag color="blue">{{ queueStatus.fast_queue.length }} 辆车</a-tag>
            </div>
            <div class="queue-item">
              <h4>慢充队列</h4>
              <a-tag color="green">{{ queueStatus.slow_queue.length }} 辆车</a-tag>
            </div>
            <div class="queue-item">
              <h4>总等待车辆</h4>
              <a-tag color="orange">{{ queueStatus.total_vehicles }} 辆车</a-tag>
            </div>
          </div>

          <a-button 
            type="primary" 
            block 
            @click="showJoinQueueModal"
            :disabled="isQueueFull"
          >
            加入等候队列
          </a-button>
        </div>
      </a-spin>
    </a-card>

    <!-- 加入队列对话框 -->
    <a-modal
      v-model:visible="joinQueueVisible"
      title="加入等候队列"
      @ok="handleJoinQueue"
      :confirmLoading="loading"
    >
      <a-form :model="queueForm" :rules="queueRules" ref="queueFormRef">
        <a-form-item name="carId" label="选择车辆">
          <a-select
            v-model:value="queueForm.carId"
            placeholder="请选择车辆"
            @change="handleCarSelect"
          >
            <a-select-option v-for="car in userCars" :key="car.id" :value="car.id">
              {{ car.brand }} {{ car.model }} ({{ car.plate_number }})
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item name="chargeType" label="充电类型">
          <a-radio-group v-model:value="queueForm.chargeType">
            <a-radio value="F">快充</a-radio>
            <a-radio value="T">慢充</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item name="chargingAmount" label="充电量">
          <a-input-number
            v-model:value="queueForm.chargingAmount"
            :min="0"
            :max="selectedCar ? selectedCar.battery_capacity : 100"
            :step="1"
            addon-after="kWh"
          />
        </a-form-item>

        <div class="charging-info" v-if="queueForm.chargingAmount">
          <p>预计充电时间：{{ calculateChargingTime }} 分钟</p>
          <p>预计等待时间：{{ calculateWaitingTime }} 分钟</p>
        </div>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useLoginServer } from './LoginSystem/server'
import { mainStore } from '../store'

const userStore = mainStore()
const loading = ref(false)
const joinQueueVisible = ref(false)
const queueFormRef = ref(null)
const userCars = ref([])
const queueStatus = reactive({
  fast_queue: [],
  slow_queue: [],
  total_vehicles: 0
})

const queueForm = reactive({
  carId: undefined,
  chargeType: 'F',
  chargingAmount: 0
})

const queueRules = {
  carId: [{ required: true, message: '请选择车辆' }],
  chargeType: [{ required: true, message: '请选择充电类型' }],
  chargingAmount: [
    { required: true, message: '请输入充电量' },
    { type: 'number', min: 0, message: '充电量必须大于0' }
  ]
}

const isQueueFull = computed(() => {
  return queueStatus.total_vehicles >= 6
})

const selectedCar = computed(() => {
  return userCars.value.find(car => car.id === queueForm.carId)
})

const calculateChargingTime = computed(() => {
  if (!queueForm.chargingAmount || !selectedCar.value) return 0
  const power = queueForm.chargeType === 'F' ? 60 : 30 // 快充60kW，慢充30kW
  return Math.ceil(queueForm.chargingAmount / power * 60)
})

const calculateWaitingTime = computed(() => {
  if (!queueForm.chargingAmount || !selectedCar.value) return 0
  const power = queueForm.chargeType === 'F' ? 60 : 30
  const chargingTime = queueForm.chargingAmount / power * 60
  
  let waitingTime = 0
  if (queueForm.chargeType === 'F') {
    waitingTime = queueStatus.fast_queue.reduce((total, vehicle) => {
      return total + vehicle.vehicle_info.charging_time
    }, 0)
  } else {
    waitingTime = queueStatus.slow_queue.reduce((total, vehicle) => {
      return total + vehicle.vehicle_info.charging_time
    }, 0)
  }
  
  return Math.ceil(waitingTime + chargingTime)
})

const fetchUserCars = async () => {
  try {
    const loginServer = useLoginServer()
    const res = await loginServer.getUserCars()
    if (res.status) {
      userCars.value = res.data
    }
  } catch (error) {
    message.error('获取车辆列表失败')
  }
}

const refreshQueueStatus = async () => {
  try {
    loading.value = true
    const loginServer = useLoginServer()
    const res = await loginServer.getQueueStatus()
    if (res.status) {
      Object.assign(queueStatus, res.data)
    } else {
      message.error(res.msg || '获取队列状态失败')
    }
  } catch (error) {
    message.error('获取队列状态失败')
  } finally {
    loading.value = false
  }
}

const showJoinQueueModal = () => {
  if (userCars.value.length === 0) {
    message.warning('请先添加车辆')
    return
  }
  joinQueueVisible.value = true
  queueForm.carId = undefined
  queueForm.chargeType = 'F'
  queueForm.chargingAmount = 0
}

const handleCarSelect = (value) => {
  const car = userCars.value.find(car => car.id === value)
  if (car) {
    queueForm.chargingAmount = Math.min(20, car.battery_capacity) // 默认充电量
  }
}

const handleJoinQueue = async () => {
  try {
    await queueFormRef.value.validate()
    loading.value = true
    
    const loginServer = useLoginServer()
    const res = await loginServer.joinQueue({
      carId: queueForm.carId,
      chargeType: queueForm.chargeType,
      chargingAmount: queueForm.chargingAmount,
      chargingPower: queueForm.chargeType === 'F' ? 60 : 30,
      chargingTime: calculateChargingTime.value
    })
    
    if (res.status) {
      message.success('成功加入等候队列')
      joinQueueVisible.value = false
      refreshQueueStatus()
    } else {
      message.error(res.msg || '加入队列失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUserCars()
  refreshQueueStatus()
})
</script>

<style scoped>
.home-sidebar {
  padding: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.queue-card {
  width: 90%;
  max-width: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.card-title {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-status {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.queue-info {
  display: flex;
  justify-content: space-between;
  margin-bottom: 20px;
}

.queue-item {
  text-align: center;
}

.queue-item h4 {
  margin-bottom: 8px;
  color: #333;
}

.charging-info {
  margin-top: 16px;
  padding: 12px;
  background-color: #f5f5f5;
  border-radius: 4px;
}

.charging-info p {
  margin: 4px 0;
  color: #666;
}
</style>
