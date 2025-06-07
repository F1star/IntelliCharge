<template>
  <div class="personal-sidebar">
    <a-card class="personal-card">
      <div class="user-info">
        <h2>{{ username }}</h2>
      </div>
      
      <div class="action-buttons">
        <a-button 
          type="primary"
          @click="showChangePasswordModal"
        >
          修改密码
        </a-button>
      </div>

      <div class="car-list">
        <div class="car-list-header">
          <h3>我的爱车</h3>
          <a-button type="primary" @click="showAddCarModal">
            <template #icon><plus-outlined /></template>
            添加爱车
          </a-button>
        </div>
        <a-spin :spinning="loading">
          <a-empty v-if="cars.length === 0" description="暂无车辆" />
          <a-list v-else :data-source="cars" :grid="{ gutter: 16, column: 1 }">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-card hoverable>
                  <template #title>{{ item.brand }} {{ item.model }}</template>
                  <template #extra>
                    <a-tag color="blue">{{ item.plate_number }}</a-tag>
                  </template>
                  <p>电池容量: {{ item.battery_capacity }}kWh</p>
                </a-card>
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </div>
    </a-card>

    <!-- 修改密码对话框 -->
    <a-modal
      v-model:visible="changePasswordVisible"
      title="修改密码"
      @ok="handleChangePassword"
      :confirmLoading="loading"
    >
      <a-form :model="passwordForm" :rules="rules" ref="passwordFormRef">
        <a-form-item name="oldPassword" label="旧密码">
          <a-input-password v-model:value="passwordForm.oldPassword" placeholder="请输入旧密码" />
        </a-form-item>
        <a-form-item name="newPassword" label="新密码">
          <a-input-password v-model:value="passwordForm.newPassword" placeholder="请输入新密码" />
        </a-form-item>
        <a-form-item name="confirmPassword" label="确认新密码">
          <a-input-password v-model:value="passwordForm.confirmPassword" placeholder="请再次输入新密码" />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 添加爱车对话框 -->
    <a-modal
      v-model:visible="addCarVisible"
      title="添加爱车"
      @ok="handleAddCar"
      :confirmLoading="loading"
    >
      <a-form :model="carForm" :rules="carRules" ref="carFormRef">
        <a-form-item name="plate_number" label="车牌号">
          <a-input v-model:value="carForm.plate_number" placeholder="请输入车牌号" />
        </a-form-item>
        <a-form-item name="brand" label="品牌">
          <a-input v-model:value="carForm.brand" placeholder="请输入品牌" />
        </a-form-item>
        <a-form-item name="model" label="型号">
          <a-input v-model:value="carForm.model" placeholder="请输入型号" />
        </a-form-item>
        <a-form-item name="battery_capacity" label="电池容量">
          <a-input-number 
            v-model:value="carForm.battery_capacity" 
            placeholder="请输入电池容量"
            :min="0"
            :max="200"
            addon-after="kWh"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { PlusOutlined } from '@ant-design/icons-vue'
import { useLoginServer } from './LoginSystem/server'
import { mainStore } from '../store'

const userStore = mainStore()
const username = ref(userStore.username)
const isAdmin = ref(false)
const changePasswordVisible = ref(false)
const loading = ref(false)
const passwordFormRef = ref(null)
const cars = ref([])
const addCarVisible = ref(false)
const carFormRef = ref(null)
const carForm = reactive({
  plate_number: '',
  brand: '',
  model: '',
  battery_capacity: null
})

const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

const rules = {
  oldPassword: [{ required: true, message: '请输入旧密码' }],
  newPassword: [
    { required: true, message: '请输入新密码' },
    { min: 6, message: '密码长度不能小于6位' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码' },
    {
      validator: async (rule, value) => {
        if (value !== passwordForm.newPassword) {
          throw new Error('两次输入的密码不一致')
        }
      }
    }
  ]
}

const carRules = {
  plate_number: [
    { required: true, message: '请输入车牌号' },
    { pattern: /^[京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽贵粤青藏川宁琼使领][A-Z][A-Z0-9]{4,5}[A-Z0-9挂学警港澳]$/, message: '请输入正确的车牌号格式' }
  ],
  brand: [{ required: true, message: '请输入品牌' }],
  model: [{ required: true, message: '请输入型号' }],
  battery_capacity: [
    { required: true, message: '请输入电池容量' },
    { type: 'number', min: 0, max: 200, message: '电池容量必须在0-200kWh之间' }
  ]
}

const fetchUserCars = async () => {
  try {
    loading.value = true
    const loginServer = useLoginServer()
    const res = await loginServer.getUserCars()
    if (res.status) {
      cars.value = res.data
    } else {
      message.error(res.msg || '获取车辆列表失败')
    }
  } catch (error) {
    message.error('获取车辆列表失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchUserCars()
})

const showChangePasswordModal = () => {
  changePasswordVisible.value = true
  passwordForm.oldPassword = ''
  passwordForm.newPassword = ''
  passwordForm.confirmPassword = ''
}

const handleChangePassword = async () => {
  try {
    await passwordFormRef.value.validate()
    loading.value = true
    
    const loginServer = useLoginServer()
    const res = await loginServer.changePassword(
      passwordForm.oldPassword,
      passwordForm.newPassword
    )
    
    if (res.status) {
      message.success('密码修改成功')
      changePasswordVisible.value = false
    } else {
      message.error(res.msg || '密码修改失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}

const showAddCarModal = () => {
  addCarVisible.value = true
  carForm.plate_number = ''
  carForm.brand = ''
  carForm.model = ''
  carForm.battery_capacity = null
}

const handleAddCar = async () => {
  try {
    await carFormRef.value.validate()
    loading.value = true
    
    const loginServer = useLoginServer()
    const res = await loginServer.addCar(carForm)
    
    if (res.status) {
      message.success('添加成功')
      addCarVisible.value = false
      fetchUserCars() // 刷新车辆列表
    } else {
      message.error(res.msg || '添加失败')
    }
  } catch (error) {
    if (error.message) {
      message.error(error.message)
    }
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.personal-sidebar {
  padding: 40px;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.personal-card {
  width: 90%;
  max-width: 500px;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.user-info {
  margin-bottom: 40px;
  text-align: center;
}

.user-info h2 {
  font-size: 28px;
  color: #333;
  margin: 0;
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 20px;
  width: 100%;
  margin-bottom: 30px;
}

.action-buttons .ant-btn {
  height: 45px;
  font-size: 16px;
}

.car-list {
  margin-top: 20px;
}

.car-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.car-list-header h3 {
  margin: 0;
  color: #333;
}

:deep(.ant-list-item) {
  padding: 8px 0;
}

:deep(.ant-card) {
  width: 100%;
}
</style>
