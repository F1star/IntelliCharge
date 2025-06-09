import sys
import os
import unittest
import time
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模块
from backEnd.src.dataStructure.ChargerPile import ChargingPile, ChargingStatus


class TestChargingPile(unittest.TestCase):
    """测试充电桩功能的测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建快充和慢充电桩
        self.fast_pile = ChargingPile("A", "F")  # 快充电桩
        self.slow_pile = ChargingPile("C", "T")  # 慢充电桩
        
        # 创建测试车辆
        self.vehicle1 = {"car_id": "car1", "user_id": "user1", "username": "用户1", "battery_capacity": 100, "charging_amount": 30}
        self.vehicle2 = {"car_id": "car2", "user_id": "user2", "username": "用户2", "battery_capacity": 100, "charging_amount": 60}
        self.vehicle3 = {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 90}

    def test_charging_pile_initialization(self):
        """测试充电桩初始化"""
        # 验证快充电桩属性
        self.assertEqual(self.fast_pile.pile_id, "A", "充电桩ID应为A")
        self.assertEqual(self.fast_pile.charging_category, "F", "充电桩类型应为F")
        self.assertEqual(self.fast_pile.power, 30, "快充电桩功率应为30度/小时")
        self.assertEqual(self.fast_pile.status, ChargingStatus.IDLE, "初始状态应为IDLE")
        self.assertIsNone(self.fast_pile.connected_vehicle, "初始连接车辆应为None")
        self.assertEqual(len(self.fast_pile.charge_queue), 0, "初始队列应为空")
        
        # 验证慢充电桩属性
        self.assertEqual(self.slow_pile.pile_id, "C", "充电桩ID应为C")
        self.assertEqual(self.slow_pile.charging_category, "T", "充电桩类型应为T")
        self.assertEqual(self.slow_pile.power, 7, "慢充电桩功率应为7度/小时")
        self.assertEqual(self.slow_pile.status, ChargingStatus.IDLE, "初始状态应为IDLE")
        self.assertIsNone(self.slow_pile.connected_vehicle, "初始连接车辆应为None")
        self.assertEqual(len(self.slow_pile.charge_queue), 0, "初始队列应为空")

    def test_join_queue(self):
        """测试车辆加入充电队列"""
        # 第一辆车加入队列
        result1 = self.fast_pile.join_queue(self.vehicle1)
        self.assertNotIsInstance(result1, dict, "第一辆车应该成功加入队列")
        self.assertEqual(len(self.fast_pile.charge_queue), 1, "队列长度应为1")
        self.assertEqual(self.fast_pile.status, ChargingStatus.CHARGING, "状态应变为CHARGING")
        self.assertEqual(self.fast_pile.connected_vehicle, self.vehicle1, "连接的车辆应为vehicle1")
        
        # 第二辆车加入队列
        result2 = self.fast_pile.join_queue(self.vehicle2)
        self.assertNotIsInstance(result2, dict, "第二辆车应该成功加入队列")
        self.assertEqual(len(self.fast_pile.charge_queue), 2, "队列长度应为2")
        
        # 第三辆车加入队列（应该失败，因为队列已满）
        result3 = self.fast_pile.join_queue(self.vehicle3)
        self.assertIsInstance(result3, dict, "第三辆车加入队列应该失败")
        self.assertIn("error", result3, "失败结果应包含error字段")
        self.assertEqual(len(self.fast_pile.charge_queue), 2, "队列长度应保持为2")

    def test_leave_queue(self):
        """测试车辆离开充电队列"""
        # 车辆加入队列
        self.fast_pile.join_queue(self.vehicle1)
        
        # 添加第二辆车并确保在队列中
        self.fast_pile.charge_queue.append(self.vehicle2)
        
        # 车辆离开队列
        result = self.fast_pile.leave_queue(self.vehicle2)
        self.assertNotIsInstance(result, dict, "车辆离开队列应该成功")
        self.assertEqual(len(self.fast_pile.charge_queue), 1, "队列长度应为1")
        
        # 不存在的车辆离开队列
        result = self.fast_pile.leave_queue({"car_id": "non_existent_car"})
        self.assertIsInstance(result, dict, "不存在的车辆离开队列应该失败")
        self.assertIn("error", result, "失败结果应包含error字段")

    def test_connect_disconnect_vehicle(self):
        """测试车辆连接和断开充电桩"""
        # 车辆加入队列
        self.fast_pile.join_queue(self.vehicle1)
        
        # 验证车辆已连接
        self.assertEqual(self.fast_pile.status, ChargingStatus.CHARGING, "状态应为CHARGING")
        self.assertEqual(self.fast_pile.connected_vehicle, self.vehicle1, "连接的车辆应为vehicle1")
        self.assertIsNotNone(self.fast_pile.start_time, "充电开始时间应不为None")
        
        # 等待一段时间
        time.sleep(1)
        
        # 断开车辆连接
        result = self.fast_pile.disconnect_vehicle()
        self.assertIsInstance(result, dict, "断开连接应返回字典")
        self.assertIn("status", result, "结果应包含status字段")
        self.assertEqual(result["status"], "success", "断开连接应成功")
        self.assertIn("bill", result, "结果应包含bill字段")
        
        # 验证充电桩状态
        self.assertEqual(self.fast_pile.status, ChargingStatus.IDLE, "断开后状态应为IDLE")
        self.assertIsNone(self.fast_pile.connected_vehicle, "断开后连接的车辆应为None")
        self.assertIsNone(self.fast_pile.start_time, "断开后充电开始时间应为None")
        self.assertEqual(len(self.fast_pile.charge_queue), 0, "断开后队列应为空")
        self.assertEqual(self.fast_pile.charging_count, 1, "充电次数应为1")
        self.assertGreater(self.fast_pile.total_energy_delivered, 0, "总充电量应大于0")
        
        # 验证充电详单
        bill = result["bill"]
        self.assertIn("bill_id", bill, "详单应包含bill_id")
        self.assertIn("charging_amount", bill, "详单应包含充电量")
        self.assertIn("charging_duration", bill, "详单应包含充电时长")
        self.assertIn("charging_cost", bill, "详单应包含充电费用")
        self.assertIn("service_cost", bill, "详单应包含服务费用")
        self.assertIn("total_cost", bill, "详单应包含总费用")

    def test_charging_cost_calculation(self):
        """测试充电费用计算"""
        # 模拟不同时段的充电
        # 峰时：10:00-15:00，18:00-21:00，单价1.0元/度
        # 平时：7:00-10:00，15:00-18:00，21:00-23:00，单价0.7元/度
        # 谷时：23:00-次日7:00，单价0.4元/度
        
        # 创建一个私有方法调用测试
        def calculate_cost(start_hour, end_hour, energy):
            # 创建当天的时间戳
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            start_time = today.replace(hour=start_hour).timestamp()
            end_time = today.replace(hour=end_hour).timestamp()
            
            # 调用私有方法计算费用
            energy_consumed, cost = self.fast_pile._calculate_charging_cost(start_time, end_time)
            return energy_consumed, cost
        
        # 测试峰时充电（12:00-14:00）
        energy, cost = calculate_cost(12, 14, 60)
        self.assertAlmostEqual(energy, 60, delta=1, msg="峰时充电量应约为60度")
        self.assertAlmostEqual(cost, 60, delta=1, msg="峰时充电费用应约为60元（60度*1.0元/度）")
        
        # 测试平时充电（8:00-10:00）
        energy, cost = calculate_cost(8, 10, 60)
        self.assertAlmostEqual(energy, 60, delta=1, msg="平时充电量应约为60度")
        self.assertAlmostEqual(cost, 42, delta=1, msg="平时充电费用应约为42元（60度*0.7元/度）")
        
        # 测试谷时充电（1:00-3:00）
        energy, cost = calculate_cost(1, 3, 60)
        self.assertAlmostEqual(energy, 60, delta=1, msg="谷时充电量应约为60度")
        self.assertAlmostEqual(cost, 24, delta=1, msg="谷时充电费用应约为24元（60度*0.4元/度）")
        
        # 测试跨时段充电（6:00-9:00，跨谷时和平时）
        energy, cost = calculate_cost(6, 9, 90)
        self.assertAlmostEqual(energy, 90, delta=1, msg="跨时段充电量应约为90度")
        # 6:00-7:00是谷时，1小时，30度，30*0.4=12元
        # 7:00-9:00是平时，2小时，60度，60*0.7=42元
        # 总费用：12+42=54元
        self.assertAlmostEqual(cost, 54, delta=3, msg="跨时段充电费用应约为54元")

    def test_fault_and_repair(self):
        """测试充电桩故障和修复"""
        # 车辆加入队列并开始充电
        self.fast_pile.join_queue(self.vehicle1)
        self.assertEqual(self.fast_pile.status, ChargingStatus.CHARGING, "状态应为CHARGING")
        
        # 模拟充电桩故障
        result = self.fast_pile.set_fault()
        self.assertIsInstance(result, dict, "故障设置应返回字典")
        self.assertIn("status", result, "结果应包含status字段")
        self.assertTrue(result["status"], "故障设置应成功")
        self.assertIn("bill", result, "故障结果应包含bill字段")
        
        # 验证故障状态
        self.assertEqual(self.fast_pile.status, ChargingStatus.FAULT, "故障后状态应为FAULT")
        self.assertIsNone(self.fast_pile.connected_vehicle, "故障后连接的车辆应为None")
        self.assertIsNone(self.fast_pile.start_time, "故障后充电开始时间应为None")
        
        # 尝试在故障状态下加入队列
        result = self.fast_pile.join_queue(self.vehicle2)
        self.assertIsInstance(result, dict, "故障状态下加入队列应失败")
        self.assertIn("error", result, "失败结果应包含error字段")
        
        # 修复充电桩
        result = self.fast_pile.repair()
        self.assertIsInstance(result, dict, "修复应返回字典")
        self.assertIn("status", result, "结果应包含status字段")
        self.assertTrue(result["status"], "修复应成功")
        
        # 验证修复后状态
        self.assertEqual(self.fast_pile.status, ChargingStatus.IDLE, "修复后状态应为IDLE")
        
        # 修复后再次加入队列
        result = self.fast_pile.join_queue(self.vehicle2)
        self.assertNotIsInstance(result, dict, "修复后加入队列应成功")
        self.assertEqual(self.fast_pile.status, ChargingStatus.CHARGING, "加入队列后状态应为CHARGING")

    def test_queue_management(self):
        """测试队列管理功能"""
        # 添加两辆车到队列
        self.fast_pile.join_queue(self.vehicle1)  # 直接充电
        self.fast_pile.charge_queue.append(self.vehicle2)  # 手动添加到队列
        
        # 验证队列状态
        queue_status = self.fast_pile.get_queue_status()
        self.assertEqual(queue_status["pile_id"], "A", "队列状态应包含正确的充电桩ID")
        self.assertEqual(queue_status["waiting_count"], 2, "等待数量应为2")
        self.assertEqual(len(queue_status["waiting_vehicles"]), 2, "等待车辆列表长度应为2")
        
        # 验证可用槽位
        available_slots = self.fast_pile.get_available_slots()
        self.assertEqual(available_slots, 0, "可用槽位应为0")
        
        # 断开第一辆车
        self.fast_pile.disconnect_vehicle()
        
        # 验证第二辆车自动开始充电
        self.assertEqual(self.fast_pile.status, ChargingStatus.CHARGING, "断开后状态应为CHARGING")
        self.assertEqual(self.fast_pile.connected_vehicle, self.vehicle2, "连接的车辆应为vehicle2")
        
        # 验证队列状态更新
        queue_status = self.fast_pile.get_queue_status()
        self.assertEqual(queue_status["waiting_count"], 1, "等待数量应为1")
        
        # 验证可用槽位更新
        available_slots = self.fast_pile.get_available_slots()
        self.assertEqual(available_slots, 1, "可用槽位应为1")


if __name__ == "__main__":
    unittest.main() 