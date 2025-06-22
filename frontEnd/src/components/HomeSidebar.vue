<template>
  <div class="home-sidebar">
    <a-card class="queue-card">
      <template #title>
        <div class="card-title">
          <span>充电站状态</span>
          <a-button type="primary" class="refresh-button" @click="refreshQueueStatus">
            <template #icon><reload-outlined /></template>
            刷新
          </a-button>
        </div>
      </template>

      <a-spin :spinning="loading">
        <div class="queue-status">
          <!-- 充电桩状态 -->
          <div class="charging-piles">
            <h3>充电桩状态</h3>
            <div class="pile-grid">
              <div v-for="pile in filteredChargingPiles" :key="pile.pile_id" class="pile-item">
                <h4>充电桩 {{ pile.pile_id }}</h4>
                <a-tag :color="getPileStatusColor(pile.status)">
                  {{ pile.status }}
                </a-tag>
                <div class="pile-info">
                  <p>类型: {{ pile.charging_category === 'F' ? '快充' : '慢充' }}</p>
                  <p>功率: {{ pile.power }}kW</p>
                  <p v-if="pile.connected_vehicle">
                    当前车辆: {{ pile.connected_vehicle }}
                  </p>
                  <p v-if="pile.queue_length > 1">
                    等待车辆: {{ pile.queue_length - 1 }}
                  </p>
                  <p v-if="isUserWaitingForPile(pile)">
                    预计等待时间: {{ calculateWaitingTime(pile) }} 分钟
                  </p>
                  <div v-if="pile.status === '充电中'" class="pile-actions">
                    <a-button 
                      type="primary" 
                      size="small" 
                      @click="showModifyChargingModal(pile)"
                      :disabled="!isAdmin"
                    >
                      修改充电
                    </a-button>
                    <a-button 
                      type="primary" danger ghost
                      size="small" 
                      @click="handleCancelCharging(pile.pile_id)"
                      >
                      结束充电
                    </a-button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 原有的队列状态 -->
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

          <!-- 等候队列详情 -->
          <div class="queue-details" v-if="queueStatus.fast_queue.length > 0 || queueStatus.slow_queue.length > 0">
            <h3>等候队列详情</h3>
            
            <!-- 快充队列 -->
            <div v-if="queueStatus.fast_queue.length > 0" class="queue-section">
              <h4>快充队列</h4>
              <a-list size="small" bordered>
                <a-list-item v-for="vehicle in filteredFastQueue" :key="vehicle.queue_number">
                  <div class="queue-vehicle-item">
                    <span>{{ vehicle.vehicle_info.username }} - {{ vehicle.queue_number }}</span>
                    <span>{{ vehicle.vehicle_info.charging_amount }}度</span>
                    <div class="queue-vehicle-actions">
                      <a-button 
                        size="small" 
                        type="primary"
                        @click="showModifyQueueChargingModal(vehicle)"
                      >
                        修改充电量
                      </a-button>
                      <a-button 
                        size="small" 
                        type="primary"
                        @click="showChangeModeModal(vehicle)"
                      >
                        改为慢充
                      </a-button>
                      <a-button 
                        size="small" 
                        type="danger"
                        @click="handleCancelQueue(vehicle.queue_number)"
                      >
                        取消
                      </a-button>
                    </div>
                  </div>
                </a-list-item>
              </a-list>
            </div>
            
            <!-- 慢充队列 -->
            <div v-if="queueStatus.slow_queue.length > 0" class="queue-section">
              <h4>慢充队列</h4>
              <a-list size="small" bordered>
                <a-list-item v-for="vehicle in filteredSlowQueue" :key="vehicle.queue_number">
                  <div class="queue-vehicle-item">
                    <span>{{ vehicle.vehicle_info.username }} - {{ vehicle.queue_number }}</span>
                    <span>{{ vehicle.vehicle_info.charging_amount }}度</span>
                    <div class="queue-vehicle-actions">
                      <a-button 
                        size="small" 
                        type="primary"
                        @click="showModifyQueueChargingModal(vehicle)"
                      >
                        修改充电量
                      </a-button>
                      <a-button 
                        size="small" 
                        type="primary"
                        @click="showChangeModeModal(vehicle)"
                      >
                        改为快充
                      </a-button>
                      <a-button 
                        size="small" 
                        type="danger"
                        @click="handleCancelQueue(vehicle.queue_number)"
                      >
                        取消
                      </a-button>
                    </div>
                  </div>
                </a-list-item>
              </a-list>
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

      </a-form>
    </a-modal>

    <!-- 修改充电对话框 -->
    <a-modal
      v-model:visible="modifyChargingVisible"
      title="修改充电请求"
      @ok="handleModifyCharging"
      :confirmLoading="loading"
    >
      <a-form :model="modifyForm" :rules="modifyRules" ref="modifyFormRef">
        <a-form-item name="chargingAmount" label="充电量">
          <a-input-number
            v-model:value="modifyForm.chargingAmount"
            :min="0"
            :max="selectedCar ? selectedCar.battery_capacity : 100"
            :step="1"
            addon-after="kWh"
          />
        </a-form-item>

        <div class="charging-info" v-if="modifyForm.chargingAmount">
          <p>预计充电时间：{{ calculateModifiedChargingTime }} 分钟</p>
          <p v-if="modifyForm.currentChargingAmount > 0">
            当前已充电量：{{ modifyForm.currentChargingAmount }} 度
          </p>
        </div>
      </a-form>
    </a-modal>
    
    <!-- 修改等候队列充电请求对话框 -->
    <a-modal
      v-model:visible="modifyQueueChargingVisible"
      title="修改等候队列充电请求"
      @ok="handleModifyQueueCharging"
      :confirmLoading="loading"
    >
      <a-form :model="modifyQueueForm" :rules="modifyRules" ref="modifyQueueFormRef">
        <a-form-item name="chargingAmount" label="充电量">
          <a-input-number
            v-model:value="modifyQueueForm.chargingAmount"
            :min="0"
            :max="selectedCar ? selectedCar.battery_capacity : 100"
            :step="1"
            addon-after="kWh"
          />
        </a-form-item>

        <div class="charging-info" v-if="modifyQueueForm.chargingAmount">
          <p>预计充电时间：
            {{ modifyQueueForm.chargeType === 'F' ? 
              Math.ceil((modifyQueueForm.chargingAmount / 30) * 60) : 
              Math.ceil((modifyQueueForm.chargingAmount / 7) * 60) }} 分钟
          </p>
        </div>
      </a-form>
    </a-modal>
    
    <!-- 修改充电模式对话框 -->
    <a-modal
      v-model:visible="changeModeVisible"
      title="修改充电模式"
      @ok="handleChangeMode"
      :confirmLoading="loading"
    >
      <p>确定要将充电模式从{{ changeModeForm.currentMode === 'F' ? '快充' : '慢充' }}
        改为{{ changeModeForm.currentMode === 'F' ? '慢充' : '快充' }}吗？</p>
      <p>修改后将重新生成排队号并排到对应模式队列的最后一位。</p>
    </a-modal>
    
    <!-- 确认取消对话框 -->
    <a-modal
      v-model:visible="confirmCancelVisible"
      title="确认取消"
      @ok="confirmCancel"
      :confirmLoading="loading"
    >
      <p>确定要取消当前的充电请求吗？</p>
      <p v-if="cancelForm.pile_id">取消后将生成充电详单。</p>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined } from '@ant-design/icons-vue'
import { useLoginServer } from './LoginSystem/server'
import { useChargingServer } from './chargingSystem/server'
import { mainStore } from '../store'

const userStore = mainStore()
const loginServer = useLoginServer()
const chargingServer = useChargingServer()
const loading = ref(false)
const joinQueueVisible = ref(false)
const queueFormRef = ref(null)
const userCars = ref([])
const queueStatus = reactive({
  fast_queue: [],
  slow_queue: [],
  total_vehicles: 0
})

const isAdmin = computed(() => userStore.role === 'admin')

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
  return queueStatus.total_vehicles >= 10
})

const selectedCar = computed(() => {
  return userCars.value.find(car => car.id === queueForm.carId)
})

const chargingPiles = ref([])

const filteredChargingPiles = computed(() => {
  if (isAdmin.value) {
    return chargingPiles.value
  }
  
  console.log('chargingPiles:', chargingPiles.value)
  console.log('userCars:', userCars.value)
  
  const filtered = chargingPiles.value.filter(pile => {
    // 检查车辆是否正在充电
    const isCharging = pile.connected_vehicle && 
      userCars.value.some(car => {
        console.log('Comparing:', car.id, pile.connected_vehicle.car_id)
        return car.id === pile.connected_vehicle.car_id
      })
    
    // 检查车辆是否在队列中
    const isInQueue = Array.from(pile.charge_queue).some(vehicle => 
      userCars.value.some(car => {
        console.log('Queue comparing:', car.id, vehicle.car_id)
        return car.id === vehicle.car_id
      })
    )
    
    console.log('Pile:', pile.pile_id, 'isCharging:', isCharging, 'isInQueue:', isInQueue)
    return isCharging || isInQueue
  })
  
  console.log('Filtered piles:', filtered)
  return filtered
})

const getPileStatusColor = (status) => {
  switch (status) {
    case '空闲':
      return 'green'
    case '充电中':
      return 'blue'
    case '故障':
      return 'red'
    case '离线':
      return 'gray'
    default:
      return 'default'
  }
}

const fetchUserCars = async () => {
  try {
    const res = await loginServer.getUserCars()
    if (res.status) {
      userCars.value = res.data
    }
  } catch (error) {
    message.error('获取车辆列表失败')
  }
}

const refreshChargingPiles = async () => {
  try {
    const res = await chargingServer.getPileStatus()
    console.log(res)
    if (res.status) {
      chargingPiles.value = Object.values(res.data)
    } else {
      message.error(res.msg || '获取充电桩状态失败')
    }
  } catch (error) {
    message.error('获取充电桩状态失败')
  }
}

const refreshQueueStatus = async () => {
  try {
    loading.value = true
    await Promise.all([
      chargingServer.getQueueStatus().then(res => {
        if (res.status) {
          Object.assign(queueStatus, res.data)
        } else {
          message.error(res.msg || '获取队列状态失败')
        }
      }),
      refreshChargingPiles()
    ])
  } catch (error) {
    message.error('获取状态失败')
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
    
    const res = await chargingServer.joinQueue({
      carId: queueForm.carId,
      chargeType: queueForm.chargeType,
      chargingAmount: queueForm.chargingAmount
    })
    
    if (res.status) {
      message.success('成功加入等候队列')
      joinQueueVisible.value = false
      refreshQueueStatus()
    } else {
      message.error({
        content: res.msg || '加入队列失败',
        duration: 3,
        style: {
          marginTop: '20vh',
        },
      })
    }
  } catch (error) {
    if (error.message) {
      message.error({
        content: error.message,
        duration: 3,
        style: {
          marginTop: '20vh',
        },
      })
    }
  } finally {
    loading.value = false
  }
}

const modifyChargingVisible = ref(false)
const modifyFormRef = ref(null)
const modifyForm = reactive({
  pile_id: '',
  chargingAmount: 0,
  currentChargingAmount: 0
})

const modifyRules = {
  chargingAmount: [
    { required: true, message: '请输入充电量' },
    { type: 'number', min: 0, message: '充电量必须大于0' }
  ]
}

const calculateModifiedChargingTime = computed(() => {
  if (!modifyForm.chargingAmount) return 0
  const pile = chargingPiles.value.find(p => p.pile_id === modifyForm.pile_id)
  if (!pile) return 0
  
  const chargingRate = pile.charging_category === 'F' ? 60 : 30 // 快充60度/小时，慢充30度/小时
  return Math.ceil((modifyForm.chargingAmount / chargingRate) * 60)
})

const showModifyChargingModal = (pile) => {
  modifyForm.pile_id = pile.pile_id
  modifyForm.chargingAmount = pile.connected_vehicle?.charging_amount || 0
  modifyForm.currentChargingAmount = pile.current_charging_amount || 0
  modifyChargingVisible.value = true
}

const handleModifyCharging = async () => {
  try {
    await modifyFormRef.value.validate()
    loading.value = true
    
    const res = await chargingServer.modifyCharging({
      pile_id: modifyForm.pile_id,
      charging_amount: modifyForm.chargingAmount
    })
    
    if (res.status) {
      message.success('修改充电请求成功')
      modifyChargingVisible.value = false
      refreshQueueStatus()
    } else {
      message.error(res.msg || '修改充电请求失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

const handleStopCharging = async (pileId) => {
  try {
    loading.value = true
    const res = await chargingServer.stopCharging(pileId)
    
    if (res.status) {
      message.success('提前结束充电成功')
      refreshQueueStatus()
    } else {
      message.error(res.msg || '提前结束充电失败')
    }
  } catch (error) {
    message.error('提前结束充电失败')
  } finally {
    loading.value = false
  }
}

const isUserVehicle = (vehicleId) => {
  return userCars.value.some(car => car.id === vehicleId)
}

// 等候队列相关
const filteredFastQueue = computed(() => {
  if (isAdmin.value) {
    return queueStatus.fast_queue
  }
  return queueStatus.fast_queue.filter(vehicle => 
    vehicle.vehicle_info.username === userStore.username
  )
})

const filteredSlowQueue = computed(() => {
  if (isAdmin.value) {
    return queueStatus.slow_queue
  }
  return queueStatus.slow_queue.filter(vehicle => 
    vehicle.vehicle_info.username === userStore.username
  )
})

const modifyQueueChargingVisible = ref(false)
const modifyQueueFormRef = ref(null)
const modifyQueueForm = reactive({
  queue_number: '',
  chargingAmount: 0,
  chargeType: 'F'
})

const showModifyQueueChargingModal = (vehicle) => {
  modifyQueueForm.queue_number = vehicle.queue_number
  modifyQueueForm.chargingAmount = vehicle.vehicle_info.charging_amount
  modifyQueueForm.chargeType = vehicle.queue_number.startsWith('F') ? 'F' : 'T'
  modifyQueueChargingVisible.value = true
}

const handleModifyQueueCharging = async () => {
  try {
    await modifyQueueFormRef.value.validate()
    loading.value = true
    
    const res = await chargingServer.modifyCharging({
      queue_number: modifyQueueForm.queue_number,
      charging_amount: modifyQueueForm.chargingAmount
    })
    
    if (res.status) {
      message.success('修改充电请求成功')
      modifyQueueChargingVisible.value = false
      refreshQueueStatus()
    } else {
      message.error(res.msg || '修改充电请求失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

// 修改充电模式相关
const changeModeVisible = ref(false)
const changeModeForm = reactive({
  queue_number: '',
  currentMode: 'F',
  new_mode: 'T'
})

const showChangeModeModal = (vehicle) => {
  changeModeForm.queue_number = vehicle.queue_number
  changeModeForm.currentMode = vehicle.queue_number.startsWith('F') ? 'F' : 'T'
  changeModeForm.new_mode = changeModeForm.currentMode === 'F' ? 'T' : 'F'
  changeModeVisible.value = true
}

const handleChangeMode = async () => {
  try {
    loading.value = true
    
    const res = await chargingServer.changeChargeMode(
      changeModeForm.queue_number,
      changeModeForm.new_mode
    )
    
    if (res.status) {
      message.success(res.msg)
      changeModeVisible.value = false
      refreshQueueStatus()
    } else {
      message.error(res.msg || '修改充电模式失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

// 取消充电相关
const confirmCancelVisible = ref(false)
const cancelForm = reactive({
  queue_number: '',
  pile_id: ''
})

const handleCancelQueue = (queue_number) => {
  cancelForm.queue_number = queue_number
  cancelForm.pile_id = ''
  confirmCancelVisible.value = true
}

const handleCancelCharging = (pile_id) => {
  cancelForm.queue_number = ''
  cancelForm.pile_id = pile_id
  confirmCancelVisible.value = true
}

const confirmCancel = async () => {
  try {
    loading.value = true
    
    const data = {}
    if (cancelForm.queue_number) {
      data.queue_number = cancelForm.queue_number
    } else if (cancelForm.pile_id) {
      data.pile_id = cancelForm.pile_id
    }
    
    const res = await chargingServer.cancelCharging(data)
    
    if (res.status) {
      message.success(res.msg)
      confirmCancelVisible.value = false
      refreshQueueStatus()
    } else {
      message.error(res.msg || '取消充电失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

const isUserWaitingForPile = (pile) => {
  if (!pile.connected_vehicle) return false
  const currentVehicle = pile.connected_vehicle
  const userQueuePosition = queueStatus[pile.charging_category === 'F' ? 'fast_queue' : 'slow_queue']
    .findIndex(vehicle => vehicle.vehicle_info.username === userStore.username)
  
  return userQueuePosition !== -1
}

const calculateWaitingTime = (pile) => {
  if (!pile.connected_vehicle) return 0
  
  const chargingRate = pile.charging_category === 'F' ? 60 : 30 // 快充60度/小时，慢充30度/小时
  const remainingAmount = pile.connected_vehicle.charging_amount - (pile.current_charging_amount || 0)
  const remainingTime = Math.ceil((remainingAmount / chargingRate) * 60)
  
  return remainingTime
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

.charging-piles {
  margin-bottom: 24px;
}

.pile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin-top: 16px;
}

.pile-item {
  padding: 16px;
  border: 1px solid #e8e8e8;
  border-radius: 4px;
  background-color: #fafafa;
}

.pile-item h4 {
  margin-bottom: 8px;
  color: #333;
}

.pile-info {
  margin-top: 8px;
}

.pile-info p {
  margin: 4px 0;
  color: #666;
  font-size: 14px;
}

.pile-actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.pile-actions .ant-btn {
  flex: 1;
}

.queue-details {
  margin-bottom: 20px;
}

.queue-section {
  margin-bottom: 16px;
}

.queue-vehicle-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.queue-vehicle-item span {
  flex: 1;
}

.queue-vehicle-actions {
  display: flex;
  gap: 4px;
}

.refresh-button {
  margin-bottom: 16px;
}
</style>
