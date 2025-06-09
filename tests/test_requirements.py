import sys
import os
import unittest
import time
from datetime import datetime, timedelta
import json

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模块
from backEnd.src.dataStructure.ChargerPile import ChargingPile, ChargingStatus
from backEnd.src.dataStructure.WaitingQueue import Queue
from backEnd.src.dataStructure.Scheduler import Scheduler
from backEnd.src.dataStructure.User import User
from backEnd.src.dataStructure.ChargingBill import create_charging_bill


class TestChargingStationRequirements(unittest.TestCase):
    """测试充电站系统需求的测试类"""

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
        
        # 创建测试车辆
        self.vehicle1 = {"car_id": "car1", "user_id": "user1", "username": "用户1", "battery_capacity": 100, "charging_amount": 30}
        self.vehicle2 = {"car_id": "car2", "user_id": "user2", "username": "用户2", "battery_capacity": 100, "charging_amount": 60}
        self.vehicle3 = {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 90}

    def test_charging_pile_count(self):
        """测试充电桩数量要求：2个快充桩和3个慢充桩"""
        # 统计快充和慢充电桩数量
        fast_count = 0
        slow_count = 0
        for pile in self.charging_piles.values():
            if pile.charging_category == "F":
                fast_count += 1
            elif pile.charging_category == "T":
                slow_count += 1
        
        # 验证数量
        self.assertEqual(fast_count, 2, "快充电桩数量应为2")
        self.assertEqual(slow_count, 3, "慢充电桩数量应为3")

    def test_charging_power(self):
        """测试充电桩功率：快充30度/小时，慢充7度/小时"""
        # 验证快充电桩功率
        self.assertEqual(self.fast_pile_a.power, 30, "快充电桩功率应为30度/小时")
        self.assertEqual(self.fast_pile_b.power, 30, "快充电桩功率应为30度/小时")
        
        # 验证慢充电桩功率
        self.assertEqual(self.slow_pile_c.power, 7, "慢充电桩功率应为7度/小时")
        self.assertEqual(self.slow_pile_d.power, 7, "慢充电桩功率应为7度/小时")
        self.assertEqual(self.slow_pile_e.power, 7, "慢充电桩功率应为7度/小时")

    def test_charging_pile_queue_length(self):
        """测试充电桩队列长度为2"""
        # 验证快充电桩队列长度
        self.assertEqual(self.fast_pile_a.charge_queue.maxlen, 2, "快充电桩队列长度应为2")
        self.assertEqual(self.fast_pile_b.charge_queue.maxlen, 2, "快充电桩队列长度应为2")
        
        # 验证慢充电桩队列长度
        self.assertEqual(self.slow_pile_c.charge_queue.maxlen, 2, "慢充电桩队列长度应为2")
        self.assertEqual(self.slow_pile_d.charge_queue.maxlen, 2, "慢充电桩队列长度应为2")
        self.assertEqual(self.slow_pile_e.charge_queue.maxlen, 2, "慢充电桩队列长度应为2")

    def test_waiting_area_capacity(self):
        """测试等候区最大车位容量为6"""
        # 验证等候区最大容量
        self.assertEqual(self.waiting_queue.max_capacity, 6, "等候区最大容量应为6")
        
        # 添加6辆车到等候区
        for i in range(6):
            vehicle = {"car_id": f"car{i+1}", "user_id": f"user{i+1}", "username": f"用户{i+1}", "battery_capacity": 100, "charging_amount": 30}
            if i % 2 == 0:
                self.waiting_queue.add_vehicle("F", vehicle)
            else:
                self.waiting_queue.add_vehicle("T", vehicle)
        
        # 验证等候区已满
        self.assertTrue(self.waiting_queue.is_full(), "添加6辆车后等候区应已满")
        
        # 尝试添加第7辆车，应该失败
        with self.assertRaises(Exception) as context:
            vehicle = {"car_id": "car7", "user_id": "user7", "username": "用户7", "battery_capacity": 100, "charging_amount": 30}
            self.waiting_queue.add_vehicle("F", vehicle)
        
        self.assertIn("等候区已满", str(context.exception), "应抛出等候区已满异常")

    def test_queue_number_generation(self):
        """测试排队号码生成规则"""
        # 添加快充车辆
        queue_number1 = self.waiting_queue.add_vehicle("F", self.vehicle1)
        self.assertEqual(queue_number1, "F1", "第一辆快充车辆的队列号应为F1")
        
        # 添加慢充车辆
        queue_number2 = self.waiting_queue.add_vehicle("T", self.vehicle2)
        self.assertEqual(queue_number2, "T1", "第一辆慢充车辆的队列号应为T1")
        
        # 再添加一辆快充车辆
        queue_number3 = self.waiting_queue.add_vehicle("F", self.vehicle3)
        self.assertEqual(queue_number3, "F2", "第二辆快充车辆的队列号应为F2")

    def test_charging_billing(self):
        """测试充电计费规则"""
        # 测试峰时费率（10:00-15:00，18:00-21:00，单价1.0元/度）
        peak_rate = 1.0
        
        # 测试平时费率（7:00-10:00，15:00-18:00，21:00-23:00，单价0.7元/度）
        normal_rate = 0.7
        
        # 测试谷时费率（23:00-次日7:00，单价0.4元/度）
        valley_rate = 0.4
        
        # 测试服务费（0.8元/度）
        service_rate = 0.8
        
        # 模拟充电
        self.fast_pile_a.join_queue(self.vehicle1)  # 30度电
        
        # 等待一段时间
        time.sleep(1)
        
        # 断开连接，生成账单
        result = self.fast_pile_a.disconnect_vehicle()
        
        # 验证账单
        self.assertIn("bill", result, "断开连接应返回账单")
        bill = result["bill"]
        
        # 验证账单内容
        self.assertIn("charging_cost", bill, "账单应包含充电费用")
        self.assertIn("service_cost", bill, "账单应包含服务费用")
        self.assertIn("total_cost", bill, "账单应包含总费用")
        
        # 验证服务费计算
        charging_amount = bill["charging_amount"]
        service_cost = bill["service_cost"]
        self.assertAlmostEqual(service_cost, charging_amount * service_rate, delta=0.1, msg="服务费应为充电量*0.8元/度")

    def test_charging_detail_record(self):
        """测试充电详单生成"""
        # 模拟充电
        self.fast_pile_a.join_queue(self.vehicle1)  # 30度电
        
        # 等待一段时间
        time.sleep(1)
        
        # 断开连接，生成账单
        result = self.fast_pile_a.disconnect_vehicle()
        
        # 验证账单
        self.assertIn("bill", result, "断开连接应返回账单")
        bill = result["bill"]
        
        # 验证账单详情
        self.assertIn("bill_id", bill, "账单应包含账单ID")
        self.assertIn("username", bill, "账单应包含用户名")
        self.assertIn("pile_id", bill, "账单应包含充电桩ID")
        self.assertIn("charging_amount", bill, "账单应包含充电量")
        self.assertIn("charging_duration", bill, "账单应包含充电时长")
        self.assertIn("start_time", bill, "账单应包含开始时间")
        self.assertIn("end_time", bill, "账单应包含结束时间")
        self.assertIn("charging_cost", bill, "账单应包含充电费用")
        self.assertIn("service_cost", bill, "账单应包含服务费用")
        self.assertIn("total_cost", bill, "账单应包含总费用")

    def test_charging_pile_fault_handling(self):
        """测试充电桩故障处理"""
        # 向A桩添加车辆并开始充电
        self.fast_pile_a.join_queue(self.vehicle1)
        
        # 模拟A桩故障
        fault_result = self.fast_pile_a.set_fault()
        
        # 验证故障处理结果
        self.assertIn("status", fault_result, "故障处理结果应包含status字段")
        self.assertTrue(fault_result["status"], "故障处理应成功")
        
        # 验证A桩状态
        self.assertEqual(self.fast_pile_a.status, ChargingStatus.FAULT, "A桩状态应为FAULT")
        
        # 尝试向故障桩添加车辆，应该失败
        result = self.fast_pile_a.join_queue(self.vehicle2)
        self.assertIn("error", result, "向故障桩添加车辆应失败")
        
        # 修复A桩
        repair_result = self.fast_pile_a.repair()
        
        # 验证修复结果
        self.assertIn("status", repair_result, "修复结果应包含status字段")
        self.assertTrue(repair_result["status"], "修复应成功")
        
        # 验证A桩状态
        self.assertEqual(self.fast_pile_a.status, ChargingStatus.IDLE, "修复后A桩状态应为IDLE")

    def test_scheduling_strategy(self):
        """测试调度策略"""
        # 添加多辆车到等候区
        self.waiting_queue.add_vehicle("F", self.vehicle1)  # F1，需要1小时
        self.waiting_queue.add_vehicle("F", self.vehicle2)  # F2，需要2小时
        self.waiting_queue.add_vehicle("T", {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 30})  # T1，需要约4.3小时
        
        # 执行调度
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertIn("fast_allocation", allocation, "调度结果应包含快充分配")
        self.assertIn("slow_allocation", allocation, "调度结果应包含慢充分配")
        
        # 验证快充分配
        self.assertEqual(len(allocation["fast_allocation"]), 2, "应分配2辆快充车")
        
        # 验证慢充分配
        self.assertEqual(len(allocation["slow_allocation"]), 1, "应分配1辆慢充车")

    def test_modify_charging_request(self):
        """测试修改充电请求"""
        # 添加车辆到等候区
        queue_number = self.waiting_queue.add_vehicle("F", self.vehicle1)
        
        # 确保车辆有join_time字段
        vehicle = self.waiting_queue.find_vehicle_by_queue_number(queue_number)
        if vehicle and "join_time" not in vehicle:
            for i, v in enumerate(self.waiting_queue.fast_queue):
                if v["queue_number"] == queue_number:
                    self.waiting_queue.fast_queue[i]["join_time"] = time.time()
                    break
        
        # 修改充电模式
        modified_vehicle = self.waiting_queue.change_charge_mode(queue_number, "T")
        self.assertIsNotNone(modified_vehicle, "应成功修改充电模式")
        self.assertTrue(modified_vehicle["queue_number"].startswith("T"), "修改后的队列号应以T开头")
        
        # 验证队列状态
        queue_status = self.waiting_queue.get_queue_status()
        self.assertEqual(len(queue_status["fast_queue"]), 0, "快充队列应为空")
        self.assertEqual(len(queue_status["slow_queue"]), 1, "慢充队列应有1辆车")


if __name__ == "__main__":
    unittest.main() 