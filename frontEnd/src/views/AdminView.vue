<template>
  <div class="admin-view">
    <a-layout>
      <a-layout-header class="header">
        <h1>充电桩管理系统 - 管理员控制台</h1>
      </a-layout-header>
      <a-layout>
        <a-layout-sider width="200" style="background: #fff">
          <a-menu
            v-model:selectedKeys="selectedKeys"
            mode="inline"
            :style="{ height: '100%', borderRight: 0 }"
          >
            <a-menu-item key="pile-status">
              <dashboard-outlined />
              <span>充电桩状态</span>
            </a-menu-item>
            <a-menu-item key="waiting-vehicles">
              <car-outlined />
              <span>等候车辆信息</span>
            </a-menu-item>
                      <a-menu-item key="reports">
            <bar-chart-outlined />
            <span>充电报表</span>
          </a-menu-item>
          <a-menu-item key="time-control">
            <dashboard-outlined />
            <span>时间控制面板</span>
          </a-menu-item>
        </a-menu>
        </a-layout-sider>
        <a-layout-content class="content">
          <!-- 充电桩状态 -->
          <div v-if="selectedKeys.includes('pile-status')" class="content-section">
            <h2>充电桩状态管理</h2>
            <a-button type="primary" @click="refreshPileStatus" class="refresh-button">
              <template #icon><reload-outlined /></template>
              刷新
            </a-button>
            <a-spin :spinning="loading.pileStatus">
              <a-table :dataSource="pileStatusList" :columns="pileStatusColumns" rowKey="pile_id">
                <template #bodyCell="{ column, record }">
                  <template v-if="column.key === 'status'">
                    <a-tag :color="getPileStatusColor(record.status)">
                      {{ record.status }}
                    </a-tag>
                  </template>
                  <template v-if="column.key === 'is_working'">
                    <a-tag :color="record.is_working ? 'green' : 'red'">
                      {{ record.is_working ? '正常工作' : '未工作' }}
                    </a-tag>
                  </template>
                  <template v-if="column.key === 'action'">
                    <a-space>
                      <a-button 
                        v-if="record.status === '离线'" 
                        type="primary" 
                        size="small"
                        @click="togglePile(record.pile_id, 'start')"
                      >
                        启动
                      </a-button>
                      <a-button 
                        v-else-if="record.status === '故障'"
                        type="primary" 
                        size="small"
                        @click="repairPile(record.pile_id)"
                      >
                        排除故障
                      </a-button>
                      <template v-else>
                        <a-button 
                          type="danger" 
                          size="small"
                          @click="togglePile(record.pile_id, 'stop')"
                        >
                          关闭
                        </a-button>
                        <a-button 
                          type="danger" 
                          size="small"
                          @click="showSetFaultModal(record.pile_id)"
                        >
                          设置故障
                        </a-button>
                      </template>
                    </a-space>
                  </template>
                </template>
              </a-table>
            </a-spin>
          </div>

          <!-- 等候车辆信息 -->
          <div v-if="selectedKeys.includes('waiting-vehicles')" class="content-section">
            <h2>等候服务车辆信息</h2>
            <a-button type="primary" @click="refreshWaitingVehicles" class="refresh-button">
              <template #icon><reload-outlined /></template>
              刷新
            </a-button>
            <a-spin :spinning="loading.waitingVehicles">
              <a-empty v-if="waitingVehicles.length === 0" description="暂无等候车辆" />
              <a-table 
                v-else 
                :dataSource="waitingVehicles" 
                :columns="waitingVehiclesColumns" 
                rowKey="queue_number"
              />
            </a-spin>
          </div>

          <!-- 充电报表 -->
          <div v-if="selectedKeys.includes('reports')" class="content-section">
            <h2>充电报表</h2>
            <div class="report-filters">
              <a-radio-group v-model:value="reportType" button-style="solid">
                <a-radio-button value="day">按日</a-radio-button>
                <a-radio-button value="week">按周</a-radio-button>
                <a-radio-button value="month">按月</a-radio-button>
              </a-radio-group>
              <a-date-picker 
                v-model:value="startDate" 
                :format="reportType === 'day' ? 'YYYY-MM-DD' : (reportType === 'week' ? 'YYYY-wo周' : 'YYYY-MM')"
                :picker="reportType === 'day' ? 'date' : (reportType === 'week' ? 'week' : 'month')"
                placeholder="选择开始日期"
                style="margin-left: 16px;"
              />
              <a-button 
                type="primary" 
                @click="generateReport" 
                style="margin-left: 16px;"
              >
                生成报表
              </a-button>
            </div>
            <a-spin :spinning="loading.reports">
              <a-empty v-if="reports.length === 0" description="暂无报表数据" />
              <a-table 
                v-else 
                :dataSource="reports" 
                :columns="reportsColumns" 
                rowKey="id"
              />
            </a-spin>
          </div>

          <!-- 故障设置模态框 -->
          <a-modal
            v-model:visible="faultModalVisible"
            title="设置充电桩故障"
            @ok="handleSetFault"
            :confirmLoading="loading.fault"
          >
            <p>您确定要将充电桩 {{ selectedPileId }} 设置为故障状态吗？</p>
            <p>如果充电桩正在为车辆充电，将会停止充电并生成详单。</p>
            <p>请选择故障调度策略：</p>
            <a-radio-group v-model:value="faultScheduleStrategy">
              <a-radio value="priority">
                <span>优先级调度</span>
                <div class="strategy-description">
                  暂停等候区叫号服务，当其它同类型充电桩队列有空位时，优先为故障充电桩等候队列提供调度
                </div>
              </a-radio>
              <a-radio value="time_order">
                <span>时间顺序调度</span>
                <div class="strategy-description">
                  暂停等候区叫号服务，将其它同类型充电桩中尚未充电的车辆与故障队列中车辆合为一组，按照排队号码先后顺序重新调度
                </div>
              </a-radio>
            </a-radio-group>
          </a-modal>

          <!-- 时间控制面板 -->
          <div v-if="selectedKeys.includes('time-control')" class="content-section">
            <h2>时间控制面板</h2>
            <div class="time-control-panel">
              <a-alert 
                type="warning" 
                message="时间控制功能" 
                description="可自定义起始时间并加速时间流逝，便于快速测试系统。请注意，加速系数过高可能会导致系统响应变慢。"
                show-icon
                style="margin-bottom: 20px;"
              />
              
              <div class="current-time-display">
                <h3>当前系统时间:</h3>
                <div class="system-time">{{ currentSystemTime }}</div>
                <div>
                  <a-tag v-if="isUsingSimulatedTime" color="orange">模拟时间模式</a-tag>
                  <a-tag v-else color="green">实时模式</a-tag>
                  <a-button 
                    v-if="isUsingSimulatedTime"
                    type="primary" 
                    danger
                    @click="resetTimeToReal"
                    style="margin-left: 10px;"
                  >
                    恢复实时时间
                  </a-button>
                </div>
              </div>
              
              <a-divider />
              
              <div class="time-control-section">
                <h3>设置时间加速</h3>
                <div class="time-control-form">
                  <a-form-item label="时间加速倍数">
                    <a-input-number 
                      v-model:value="timeSpeedup" 
                      :min="1" 
                      :max="500"
                      style="width: 150px;"
                    />
                  </a-form-item>
                  <a-form-item>
                    <a-button type="primary" @click="setTimeSpeed">
                      应用时间加速
                    </a-button>
                  </a-form-item>
                </div>
                
                <div class="preset-speeds">
                  <a-button-group>
                    <a-button @click="applyPresetSpeed(1)">正常速度(1x)</a-button>
                    <a-button @click="applyPresetSpeed(10)">10倍速</a-button>
                    <a-button @click="applyPresetSpeed(60)">60倍速</a-button>
                    <a-button @click="applyPresetSpeed(300)">300倍速</a-button>
                  </a-button-group>
                </div>
              </div>
              
              <a-divider />
              
              <div class="time-control-section">
                <h3>设置起始时间</h3>
                <div class="time-control-form">
                  <a-form-item label="自定义时间">
                    <a-input 
                      v-model:value="customTime" 
                      placeholder="格式: HH:MM:SS 或 YYYY-MM-DD HH:MM:SS" 
                      style="width: 300px;"
                    />
                  </a-form-item>
                  <a-form-item>
                    <a-button type="primary" @click="setSystemTime">
                      设置系统时间
                    </a-button>
                  </a-form-item>
                </div>
                
                <div class="preset-times">
                  <h4>快速设置测试时间点:</h4>
                  <a-button-group>
                    <a-button @click="customTime = '6:00:00'">06:00:00</a-button>
                    <a-button @click="customTime = '6:30:00'">06:30:00</a-button>
                    <a-button @click="customTime = '7:00:00'">07:00:00</a-button>
                    <a-button @click="customTime = '7:30:00'">07:30:00</a-button>
                  </a-button-group>
                  <br /><br />
                  <a-button-group>
                    <a-button @click="customTime = '8:00:00'">08:00:00</a-button>
                    <a-button @click="customTime = '8:30:00'">08:30:00</a-button>
                    <a-button @click="customTime = '9:00:00'">09:00:00</a-button>
                    <a-button @click="customTime = '9:30:00'">09:30:00</a-button>
                  </a-button-group>
                  <br /><br />
                  <a-button-group>
                    <a-button @click="customTime = '10:00:00'">10:00:00</a-button>
                    <a-button @click="customTime = '10:30:00'">10:30:00</a-button>
                    <a-button @click="customTime = '11:00:00'">11:00:00</a-button>
                  </a-button-group>
                </div>
              </div>
            </div>
          </div>
        </a-layout-content>
      </a-layout>
    </a-layout>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  ReloadOutlined, 
  DashboardOutlined, 
  CarOutlined, 
  BarChartOutlined 
} from '@ant-design/icons-vue'
import { useChargingServer } from '../components/chargingSystem/server'
import { mainStore } from '../store'
import dayjs from 'dayjs'

const userStore = mainStore()
const chargingServer = useChargingServer()
const selectedKeys = ref(['pile-status'])

// 加载状态
const loading = reactive({
  pileStatus: false,
  waitingVehicles: false,
  reports: false,
  fault: false
})

// 充电桩状态
const pileStatusList = ref([])
const pileStatusColumns = [
  { title: '充电桩编号', dataIndex: 'pile_id', key: 'pile_id' },
  { title: '充电桩类型', dataIndex: 'charging_category', key: 'charging_category', 
    customRender: ({ text }) => text === 'F' ? '快充' : '慢充' },
  { title: '当前状态', dataIndex: 'status', key: 'status' },
  { title: '工作状态', dataIndex: 'is_working', key: 'is_working' },
  { title: '累计充电次数', dataIndex: 'charging_count', key: 'charging_count' },
  { title: '累计充电时长(小时)', dataIndex: 'total_charging_duration', key: 'total_charging_duration' },
  { title: '累计充电电量(度)', dataIndex: 'total_energy_delivered', key: 'total_energy_delivered' },
  { title: '累计收益(元)', dataIndex: 'total_earnings', key: 'total_earnings' },
  { title: '操作', key: 'action' }
]

// 等候车辆信息
const waitingVehicles = ref([])
const waitingVehiclesColumns = [
  { title: '排队号', dataIndex: 'queue_number', key: 'queue_number' },
  { title: '用户ID', dataIndex: 'user_id', key: 'user_id' },
  { title: '充电模式', dataIndex: 'charge_mode', key: 'charge_mode' },
  { title: '电池总容量(度)', dataIndex: 'battery_capacity', key: 'battery_capacity' },
  { title: '请求充电量(度)', dataIndex: 'charging_amount', key: 'charging_amount' },
  { title: '排队时长(分钟)', dataIndex: 'queue_time', key: 'queue_time' }
]

// 充电报表
const reportType = ref('day')
const startDate = ref(null)
const reports = ref([])
const reportsColumns = [
  { title: '时间', dataIndex: 'time_period', key: 'time_period' },
  { title: '充电桩编号', dataIndex: 'pile_id', key: 'pile_id' },
  { title: '累计充电次数', dataIndex: 'charging_count', key: 'charging_count' },
  { title: '累计充电时长(分钟)', dataIndex: 'total_duration', key: 'total_duration' },
  { title: '累计充电量(度)', dataIndex: 'total_amount', key: 'total_amount' },
  { title: '累计充电费用(元)', dataIndex: 'total_charging_cost', key: 'total_charging_cost' },
  { title: '累计服务费用(元)', dataIndex: 'total_service_cost', key: 'total_service_cost' },
  { title: '累计总费用(元)', dataIndex: 'total_cost', key: 'total_cost' }
]

// 故障设置模态框
const faultModalVisible = ref(false)
const selectedPileId = ref(null)
const faultScheduleStrategy = ref('priority')

// 时间加速控制
const timeSpeedup = ref(1)
const systemTime = ref('')
const customTime = ref('')
const currentSystemTime = ref('')
const systemTimeUpdateInterval = ref(null)
const isUsingSimulatedTime = ref(false)

// 获取充电桩状态
const refreshPileStatus = async () => {
  try {
    loading.pileStatus = true
    const res = await chargingServer.getAdminPileStatus()
    
    if (res.status) {
      // 转换对象为数组
      pileStatusList.value = Object.values(res.data)
    } else {
      message.error(res.msg || '获取充电桩状态失败')
    }
  } catch (error) {
    message.error('获取充电桩状态失败')
    console.error(error)
  } finally {
    loading.pileStatus = false
  }
}

// 获取等候车辆信息
const refreshWaitingVehicles = async () => {
  try {
    loading.waitingVehicles = true
    const res = await chargingServer.getWaitingVehicles()
    
    if (res.status) {
      waitingVehicles.value = res.data
    } else {
      message.error(res.msg || '获取等候车辆信息失败')
    }
  } catch (error) {
    message.error('获取等候车辆信息失败')
    console.error(error)
  } finally {
    loading.waitingVehicles = false
  }
}

// 生成充电报表
const generateReport = async () => {
  try {
    loading.reports = true
    
    // 格式化开始日期
    let formattedDate = null
    if (startDate.value) {
      formattedDate = dayjs(startDate.value).format('YYYY-MM-DD')
    }
    
    const res = await chargingServer.getChargingReports(reportType.value, formattedDate)
    
    if (res.status) {
      reports.value = res.data.map((item, index) => ({
        ...item,
        id: `${item.time_period}-${item.pile_id}-${index}` // 生成唯一key
      }))
    } else {
      message.error(res.msg || '获取充电报表失败')
    }
  } catch (error) {
    message.error('获取充电报表失败')
    console.error(error)
  } finally {
    loading.reports = false
  }
}

// 启动/关闭充电桩
const togglePile = async (pileId, action) => {
  try {
    const res = await chargingServer.toggleChargingPile(pileId, action)
    
    if (res.status) {
      message.success(res.msg)
      refreshPileStatus() // 刷新充电桩状态
    } else {
      message.error(res.msg || `${action === 'start' ? '启动' : '关闭'}充电桩失败`)
    }
  } catch (error) {
    message.error(`${action === 'start' ? '启动' : '关闭'}充电桩失败`)
    console.error(error)
  }
}

// 获取充电桩状态颜色
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

// 显示故障设置模态框
const showSetFaultModal = (pileId) => {
  selectedPileId.value = pileId
  faultModalVisible.value = true
}

// 处理故障设置
const handleSetFault = async () => {
  try {
    loading.fault = true
    const res = await chargingServer.setPileFault(selectedPileId.value, faultScheduleStrategy.value)
    
    if (res.status) {
      message.success(res.msg)
      refreshPileStatus() // 刷新充电桩状态
      refreshWaitingVehicles() // 刷新等候车辆信息
    } else {
      message.error(res.msg || '设置充电桩故障失败')
      console.error('设置故障失败:', res)
    }
  } catch (error) {
    message.error('设置充电桩故障失败')
    console.error('设置故障异常:', error)
  } finally {
    loading.fault = false
    faultModalVisible.value = false
  }
}

// 修复充电桩故障
const repairPile = async (pileId) => {
  try {
    const res = await chargingServer.repairPile(pileId)
    
    if (res.status) {
      message.success(res.msg)
      refreshPileStatus() // 刷新充电桩状态
    } else {
      message.error(res.msg || '修复充电桩故障失败')
    }
  } catch (error) {
    message.error('修复充电桩故障失败')
    console.error(error)
  }
}

// 设置时间加速
const setTimeSpeed = async () => {
  try {
    const res = await chargingServer.setTimeSpeedup(timeSpeedup.value)
    if (res.status) {
      message.success(res.msg)
    } else {
      message.error(res.msg || '设置时间加速失败')
    }
  } catch (error) {
    message.error('设置时间加速失败')
    console.error(error)
  }
}

// 应用预设速度
const applyPresetSpeed = (speed) => {
  timeSpeedup.value = speed
  setTimeSpeed()
}

// 设置系统时间
const setSystemTime = async () => {
  if (!customTime.value) {
    message.error('请输入有效的时间')
    return
  }
  
  try {
    const res = await chargingServer.setSimulationTime(customTime.value)
    if (res.status) {
      message.success(res.msg)
      updateSystemTime() // 立即更新系统时间
      isUsingSimulatedTime.value = true
    } else {
      message.error(res.msg || '设置系统时间失败')
    }
  } catch (error) {
    message.error('设置系统时间失败')
    console.error(error)
  }
}

// 恢复实时系统时间
const resetTimeToReal = async () => {
  try {
    const res = await chargingServer.resetToRealTime()
    if (res.status) {
      message.success(res.msg)
      updateSystemTime() // 立即更新系统时间
      isUsingSimulatedTime.value = false
      timeSpeedup.value = 1 // 同时将时间加速倍数设为1
    } else {
      message.error(res.msg || '恢复实时系统时间失败')
    }
  } catch (error) {
    message.error('恢复实时系统时间失败')
    console.error(error)
  }
}

// 获取并更新系统时间
const updateSystemTime = async () => {
  try {
    const res = await chargingServer.getSystemTime()
    if (res.status) {
      currentSystemTime.value = res.data.time_str
      isUsingSimulatedTime.value = res.data.is_using_simulated_time
    }
  } catch (error) {
    console.error('获取系统时间失败:', error)
  }
}

onMounted(() => {
  // 检查用户是否为管理员
  if (userStore.role !== 'admin') {
    message.error('您没有访问此页面的权限')
    // 可以添加重定向到其他页面的逻辑
  }
  
  // 加载初始数据
  refreshPileStatus()
  refreshWaitingVehicles()
  
  // 获取系统时间并设置定时更新
  updateSystemTime()
  systemTimeUpdateInterval.value = setInterval(updateSystemTime, 1000) // 每秒更新一次
})

// 组件销毁时清除定时器
import { onBeforeUnmount } from 'vue'

onBeforeUnmount(() => {
  if (systemTimeUpdateInterval.value) {
    clearInterval(systemTimeUpdateInterval.value)
  }
})
</script>

<style scoped>
.admin-view {
  min-height: 100vh;
}

.header {
  background: #fff;
  padding: 0 20px;
  display: flex;
  align-items: center;
}

.header h1 {
  margin: 0;
  color: #1890ff;
}

.content {
  padding: 24px;
  background: #fff;
  min-height: calc(100vh - 64px);
}

.content-section {
  margin-bottom: 24px;
}

.refresh-button {
  margin-bottom: 16px;
}

.report-filters {
  margin-bottom: 24px;
  display: flex;
  align-items: center;
}

.strategy-description {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-left: 24px;
  margin-top: 4px;
  margin-bottom: 8px;
}

.time-control-panel {
  background-color: #f8f8f8;
  padding: 20px;
  border-radius: 8px;
}

.time-control-form {
  display: flex;
  align-items: center;
  margin-bottom: 20px;
}

.time-control-form .ant-form-item {
  margin-right: 16px;
  margin-bottom: 0;
}

.preset-speeds {
  margin-top: 20px;
}

.current-time-display {
  text-align: center;
  margin-bottom: 20px;
}

.system-time {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}

.time-control-section {
  margin-bottom: 20px;
}

.preset-times {
  margin-top: 20px;
}
</style> 