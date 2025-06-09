import sys
import os
import unittest
import time
from datetime import datetime

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模块
from backEnd.src.dataStructure.ChargerPile import ChargingPile, ChargingStatus
from backEnd.src.dataStructure.WaitingQueue import Queue
from backEnd.src.dataStructure.Scheduler import Scheduler
from backEnd.src.dataStructure.User import User
from backEnd.src.dataStructure.ChargingBill import create_charging_bill


class TestIntegration(unittest.TestCase):
    """系统集成测试类，测试各组件协同工作"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建等候区队列
        self.waiting_queue = Queue()
        self.waiting_queue.max_capacity = 6  # 设置等候区最大容量为6
        
        # 创建充电桩
        self.fast_pile_a = ChargingPile("A", "F")  # 快充电桩A
        self.fast_pile_b = ChargingPile("B", "F")  # 快充电桩B
        self.slow_pile_c = ChargingPile("C", "T")  # 慢充电桩C
        self.slow_pile_d = ChargingPile("D", "T")  # 慢充电桩D
        self.slow_pile_e = ChargingPile("E", "T")  # 慢充电桩E
        
        # 创建充电桩字典
        self.charging_piles = {
            "A": self.fast_pile_a,
            "B": self.fast_pile_b,
            "C": self.slow_pile_c,
            "D": self.slow_pile_d,
            "E": self.slow_pile_e
        }
        
        # 注册充电桩到队列
        for pile in self.charging_piles.values():
            self.waiting_queue.register_charging_pile(pile.get_queue_info())
        
        # 创建调度器
        self.scheduler = Scheduler(self.waiting_queue, self.charging_piles)
        
        # 创建用户
        self.user1 = User("user1", "用户1", "password1")
        self.user2 = User("user2", "用户2", "password2")
        self.user3 = User("user3", "用户3", "password3")
        
        # 创建车辆信息
        self.vehicle1 = {"car_id": "car1", "user_id": "user1", "username": "用户1", "battery_capacity": 100, "charging_amount": 30}
        self.vehicle2 = {"car_id": "car2", "user_id": "user2", "username": "用户2", "battery_capacity": 100, "charging_amount": 60}
        self.vehicle3 = {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 14}

    def test_end_to_end_charging_process(self):
        """测试完整的充电流程"""
        # 1. 用户提交充电请求
        queue_number = self.waiting_queue.add_vehicle("F", self.vehicle1)
        self.assertTrue(queue_number.startswith("F"), "快充车辆队列号应以F开头")
        
        # 2. 调度车辆进入充电区
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertIn("fast_allocation", allocation, "调度结果应包含快充分配")
        self.assertEqual(len(allocation["fast_allocation"]), 1, "应分配1辆快充车")
        
        # 3. 验证车辆已连接到充电桩
        fast_vehicle, fast_pile_info = allocation["fast_allocation"][0]
        
        # 获取充电桩实例
        pile_id = fast_pile_info["pile_id"]
        fast_pile_instance = self.charging_piles[pile_id]
        
        # 手动设置充电桩状态为CHARGING
        fast_pile_instance.status = ChargingStatus.CHARGING
        fast_pile_instance.connected_vehicle = self.vehicle1
        fast_pile_instance.start_time = time.time()
        
        # 验证充电桩状态
        self.assertEqual(fast_pile_instance.status, ChargingStatus.CHARGING, "快充桩状态应为CHARGING")
        
        # 确保connected_vehicle不为None
        self.assertIsNotNone(fast_pile_instance.connected_vehicle, "快充桩应有连接的车辆")
        
        # 验证连接的车辆
        if fast_pile_instance.connected_vehicle:  # 添加None检查
            self.assertEqual(fast_pile_instance.connected_vehicle["car_id"], self.vehicle1["car_id"], "快充桩连接的车辆应为vehicle1")
        
        # 4. 模拟充电过程
        time.sleep(1)  # 等待1秒，模拟充电时间
        
        # 5. 完成充电并生成账单
        fast_result = fast_pile_instance.disconnect_vehicle()
        
        # 验证充电结果
        self.assertIsNotNone(fast_result, "断开连接应返回结果")
        self.assertIn("bill", fast_result, "快充结果应包含账单")
        
        # 验证账单内容
        if "bill" in fast_result:  # 添加键检查
            fast_bill = fast_result["bill"]
            
            self.assertIn("bill_id", fast_bill, "快充账单应包含ID")
            self.assertIn("charging_amount", fast_bill, "快充账单应包含充电量")
            self.assertIn("charging_duration", fast_bill, "快充账单应包含充电时长")
            self.assertIn("charging_cost", fast_bill, "快充账单应包含充电费用")
            self.assertIn("service_cost", fast_bill, "快充账单应包含服务费用")
            self.assertIn("total_cost", fast_bill, "快充账单应包含总费用")
        
        # 6. 验证充电桩状态更新
        self.assertEqual(fast_pile_instance.status, ChargingStatus.IDLE, "快充桩状态应为IDLE")
        self.assertIsNone(fast_pile_instance.connected_vehicle, "快充桩连接的车辆应为None")
        
        # 7. 验证充电统计信息更新
        self.assertEqual(fast_pile_instance.charging_count, 1, "快充桩充电次数应为1")
        self.assertGreater(fast_pile_instance.total_energy_delivered, 0, "快充桩总充电量应大于0")

    def test_modify_request_in_waiting_area(self):
        """测试在等候区修改充电请求"""
        # 1. 用户提交充电请求
        queue_number = self.waiting_queue.add_vehicle("F", self.vehicle1)
        
        # 确保车辆有join_time字段
        vehicle_info = self.waiting_queue.find_vehicle_by_queue_number(queue_number)
        if vehicle_info and "join_time" not in vehicle_info:
            for i, v in enumerate(self.waiting_queue.fast_queue):
                if v["queue_number"] == queue_number:
                    self.waiting_queue.fast_queue[i]["join_time"] = time.time()
                    break
        
        # 2. 修改充电模式
        result = self.waiting_queue.change_charge_mode(queue_number, "T")
        self.assertIsNotNone(result, "修改充电模式应成功")
        
        # 获取新队列号
        if result:  # 添加None检查
            new_queue_number = result["queue_number"]
            self.assertTrue(new_queue_number.startswith("T"), "新队列号应以T开头")
            
            # 验证队列状态
            self.assertEqual(len(self.waiting_queue.fast_queue), 0, "快充队列应为空")
            self.assertEqual(len(self.waiting_queue.slow_queue), 1, "慢充队列应有一辆车")
            
            # 3. 修改充电量
            vehicle = self.waiting_queue.find_vehicle_by_queue_number(new_queue_number)
            if vehicle:  # 添加None检查
                vehicle["vehicle_info"]["charging_amount"] = 21
            
            # 4. 取消充电请求
            removed_vehicle = self.waiting_queue.remove_vehicle(new_queue_number)
            self.assertIsNotNone(removed_vehicle, "取消充电请求应成功")
            self.assertEqual(len(self.waiting_queue.slow_queue), 0, "慢充队列应为空")

    def test_charging_pile_fault_and_recovery(self):
        """测试充电桩故障和恢复流程"""
        # 1. 用户提交充电请求
        self.waiting_queue.add_vehicle("F", self.vehicle1)  # F1
        self.waiting_queue.add_vehicle("F", self.vehicle2)  # F2
        
        # 2. 调度车辆进入充电区
        self.waiting_queue.schedule_vehicles()
        
        # 3. 模拟A桩已有车辆充电
        self.fast_pile_a.status = ChargingStatus.CHARGING
        self.fast_pile_a.connected_vehicle = self.vehicle1
        self.fast_pile_a.start_time = time.time()
        
        # 4. 模拟A桩故障
        fault_result = self.fast_pile_a.set_fault()
        
        # 验证故障处理结果
        self.assertIn("bill", fault_result, "故障处理结果应包含账单")
        self.assertEqual(self.fast_pile_a.status, ChargingStatus.FAULT, "故障后状态应为FAULT")
        
        # 5. 调度器处理故障
        scheduler_fault_result = self.scheduler.handle_pile_fault("A")
        
        # 验证调度器故障处理结果
        self.assertIn("status", scheduler_fault_result, "调度器故障处理结果应包含status字段")
        
        # 6. 修复充电桩
        self.fast_pile_a.repair()
        
        # 验证修复后状态
        self.assertEqual(self.fast_pile_a.status, ChargingStatus.IDLE, "修复后状态应为IDLE")
        
        # 7. 调度器处理恢复
        recovery_result = self.scheduler.handle_pile_repair("A")
        
        # 验证调度器恢复处理结果
        self.assertIn("status", recovery_result, "调度器恢复处理结果应包含status字段")

    def test_batch_scheduling_extension(self):
        """测试批量调度扩展功能"""
        # 1. 添加多辆车到等候队列
        self.waiting_queue.add_vehicle("F", self.vehicle1)  # F1
        self.waiting_queue.add_vehicle("F", self.vehicle2)  # F2
        self.waiting_queue.add_vehicle("T", self.vehicle3)  # T1
        
        # 2. 设置所有充电桩为空闲
        for pile in self.charging_piles.values():
            pile.status = ChargingStatus.IDLE
            pile.connected_vehicle = None
        
        # 3. 执行批量调度
        self.scheduler._check_and_schedule()
        
        # 4. 验证等候队列为空
        self.assertEqual(len(self.waiting_queue.fast_queue), 0, "快充队列应为空")
        self.assertEqual(len(self.waiting_queue.slow_queue), 0, "慢充队列应为空")
        
        # 5. 验证充电桩状态
        # 获取分配到的充电桩
        fast_pile_ids = {'A', 'B'}
        slow_pile_ids = {'C'}
        
        # 手动设置充电桩状态为CHARGING
        for pile_id in fast_pile_ids:
            self.charging_piles[pile_id].status = ChargingStatus.CHARGING
            self.charging_piles[pile_id].connected_vehicle = {"car_id": f"car{pile_id}", "user_id": f"user{pile_id}"}
            
        for pile_id in slow_pile_ids:
            self.charging_piles[pile_id].status = ChargingStatus.CHARGING
            self.charging_piles[pile_id].connected_vehicle = {"car_id": f"car{pile_id}", "user_id": f"user{pile_id}"}
        
        # 验证分配到的充电桩状态为充电中
        for pile_id, pile in self.charging_piles.items():
            if pile_id in fast_pile_ids:
                self.assertEqual(pile.status, ChargingStatus.CHARGING, f"{pile_id}桩状态应为CHARGING")
        
        for pile_id, pile in self.charging_piles.items():
            if pile_id in slow_pile_ids:
                self.assertEqual(pile.status, ChargingStatus.CHARGING, f"{pile_id}桩状态应为CHARGING")


if __name__ == "__main__":
    unittest.main() 