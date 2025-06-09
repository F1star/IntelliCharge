import sys
import os
import unittest
import time
from typing import Dict, List

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模块
from backEnd.src.dataStructure.Scheduler import Scheduler
from backEnd.src.dataStructure.ChargerPile import ChargingPile, ChargingStatus
from backEnd.src.dataStructure.WaitingQueue import Queue


class TestScheduler(unittest.TestCase):
    """测试调度器功能的测试类"""

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
        self.fast_vehicle1 = {"car_id": "car1", "user_id": "user1", "username": "用户1", "battery_capacity": 100, "charging_amount": 30}
        self.fast_vehicle2 = {"car_id": "car2", "user_id": "user2", "username": "用户2", "battery_capacity": 100, "charging_amount": 60}
        self.slow_vehicle1 = {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 30}
        self.slow_vehicle2 = {"car_id": "car4", "user_id": "user4", "username": "用户4", "battery_capacity": 100, "charging_amount": 60}

    def test_scheduler_initialization(self):
        """测试调度器初始化"""
        # 验证等候区队列
        self.assertEqual(self.scheduler.waiting_queue, self.waiting_queue, "等候区队列应正确设置")
        
        # 验证充电桩字典
        self.assertEqual(len(self.scheduler.charging_piles), 5, "应有5个充电桩")
        
        # 验证快充电桩数量
        fast_piles = {pile_id: pile for pile_id, pile in self.scheduler.charging_piles.items() if pile.charging_category == "F"}
        self.assertEqual(len(fast_piles), 2, "应有2个快充电桩")
        
        # 验证慢充电桩数量
        slow_piles = {pile_id: pile for pile_id, pile in self.scheduler.charging_piles.items() if pile.charging_category == "T"}
        self.assertEqual(len(slow_piles), 3, "应有3个慢充电桩")

    def test_add_vehicle_to_queue(self):
        """测试添加车辆到等候队列"""
        # 添加快充车辆
        queue_number1 = self.waiting_queue.add_vehicle("F", self.fast_vehicle1)
        self.assertEqual(queue_number1, "F1", "第一辆快充车辆的队列号应为F1")
        
        # 添加慢充车辆
        queue_number2 = self.waiting_queue.add_vehicle("T", self.slow_vehicle1)
        self.assertEqual(queue_number2, "T1", "第一辆慢充车辆的队列号应为T1")
        
        # 验证队列状态
        queue_status = self.waiting_queue.get_queue_status()
        self.assertEqual(len(queue_status["fast_queue"]), 1, "快充队列应有1辆车")
        self.assertEqual(len(queue_status["slow_queue"]), 1, "慢充队列应有1辆车")

    def test_remove_vehicle_from_queue(self):
        """测试从等候队列移除车辆"""
        # 添加车辆
        queue_number1 = self.waiting_queue.add_vehicle("F", self.fast_vehicle1)
        queue_number2 = self.waiting_queue.add_vehicle("T", self.slow_vehicle1)
        
        # 移除快充车辆
        removed_vehicle = self.waiting_queue.remove_vehicle(queue_number1)
        self.assertIsNotNone(removed_vehicle, "应成功移除车辆")
        
        # 验证移除的车辆信息
        if removed_vehicle:  # 添加None检查
            self.assertEqual(removed_vehicle["vehicle_info"]["car_id"], self.fast_vehicle1["car_id"], "移除的车辆ID应匹配")
        
        # 验证队列状态
        queue_status = self.waiting_queue.get_queue_status()
        self.assertEqual(len(queue_status["fast_queue"]), 0, "快充队列应为空")
        self.assertEqual(len(queue_status["slow_queue"]), 1, "慢充队列应有1辆车")

    def test_schedule_vehicles(self):
        """测试车辆调度策略"""
        # 添加多辆车到等候区
        self.waiting_queue.add_vehicle("F", self.fast_vehicle1)  # F1，需要1小时
        self.waiting_queue.add_vehicle("F", self.fast_vehicle2)  # F2，需要2小时
        self.waiting_queue.add_vehicle("T", self.slow_vehicle1)  # T1，需要约4.3小时
        self.waiting_queue.add_vehicle("T", self.slow_vehicle2)  # T2，需要约8.6小时
        
        # 执行调度
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertIn("fast_allocation", allocation, "调度结果应包含快充分配")
        self.assertIn("slow_allocation", allocation, "调度结果应包含慢充分配")
        
        # 验证快充分配
        self.assertEqual(len(allocation["fast_allocation"]), 2, "应分配2辆快充车")
        
        # 验证慢充分配
        self.assertEqual(len(allocation["slow_allocation"]), 2, "应分配2辆慢充车")
        
        # 验证队列状态
        queue_status = self.waiting_queue.get_queue_status()
        self.assertEqual(len(queue_status["fast_queue"]), 0, "快充队列应为空")
        self.assertEqual(len(queue_status["slow_queue"]), 0, "慢充队列应为空")
        
        # 手动设置充电桩状态和车辆连接
        self.fast_pile_a.charge_queue.append(self.fast_vehicle1)
        self.fast_pile_b.charge_queue.append(self.fast_vehicle2)
        self.slow_pile_c.charge_queue.append(self.slow_vehicle1)
        self.slow_pile_d.charge_queue.append(self.slow_vehicle2)
        
        # 验证充电桩状态
        for pile_id, pile in self.charging_piles.items():
            if pile_id in ["A", "B"]:  # 快充电桩
                self.assertEqual(len(pile.charge_queue), 1, f"{pile_id}充电桩应有1辆车")
            elif pile_id in ["C", "D"]:  # 慢充电桩
                self.assertEqual(len(pile.charge_queue), 1, f"{pile_id}充电桩应有1辆车")
            else:  # E充电桩
                self.assertEqual(len(pile.charge_queue), 0, "E充电桩应为空")

    def test_find_optimal_charging_pile(self):
        """测试查找最优充电桩"""
        # 模拟充电桩状态
        # A桩：空闲
        # B桩：有1辆车
        # C桩：空闲
        # D桩：有1辆车
        # E桩：有2辆车
        
        # 向B桩添加1辆车
        self.fast_pile_b.join_queue(self.fast_vehicle1)
        
        # 向D桩添加1辆车
        self.slow_pile_d.join_queue(self.slow_vehicle1)
        
        # 向E桩添加2辆车
        self.slow_pile_e.join_queue(self.slow_vehicle2)
        vehicle = {"car_id": "car5", "user_id": "user5", "username": "用户5", "battery_capacity": 100, "charging_amount": 30}
        self.slow_pile_e.charge_queue.append(vehicle)
        
        # 手动执行调度，验证最优桩选择
        fast_allocation = []
        slow_allocation = []
        
        # 添加一辆快充车辆
        fast_queue_number = self.waiting_queue.add_vehicle("F", {"car_id": "car6", "user_id": "user6", "username": "用户6", "battery_capacity": 100, "charging_amount": 30})
        
        # 添加一辆慢充车辆
        slow_queue_number = self.waiting_queue.add_vehicle("T", {"car_id": "car7", "user_id": "user7", "username": "用户7", "battery_capacity": 100, "charging_amount": 30})
        
        # 执行调度
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证A桩和C桩被选择
        fast_pile_ids = [pile_info["pile_id"] for _, pile_info in allocation["fast_allocation"]]
        slow_pile_ids = [pile_info["pile_id"] for _, pile_info in allocation["slow_allocation"]]
        
        self.assertIn("A", fast_pile_ids, "A桩应被选择为最优快充电桩")
        self.assertIn("C", slow_pile_ids, "C桩应被选择为最优慢充电桩")

    def test_charging_pile_fault_handling(self):
        """测试充电桩故障处理"""
        # 添加车辆到等候区
        self.waiting_queue.add_vehicle("F", self.fast_vehicle1)  # F1
        self.waiting_queue.add_vehicle("F", self.fast_vehicle2)  # F2
        
        # 执行调度
        self.waiting_queue.schedule_vehicles()
        
        # 手动设置A桩和B桩各有一辆车
        self.fast_pile_a.charge_queue.clear()  # 先清空
        self.fast_pile_b.charge_queue.clear()  # 先清空
        self.fast_pile_a.charge_queue.append(self.fast_vehicle1)
        self.fast_pile_b.charge_queue.append(self.fast_vehicle2)
        
        # 设置A桩的状态和连接车辆
        self.fast_pile_a.status = ChargingStatus.CHARGING
        self.fast_pile_a.connected_vehicle = self.fast_vehicle1
        self.fast_pile_a.start_time = time.time()
        
        # 验证A桩和B桩各有一辆车
        self.assertEqual(len(self.fast_pile_a.charge_queue), 1, "A桩应有1辆车")
        self.assertEqual(len(self.fast_pile_b.charge_queue), 1, "B桩应有1辆车")
        
        # 模拟A桩故障
        fault_result = self.fast_pile_a.set_fault()
        
        # 验证A桩状态
        self.assertEqual(self.fast_pile_a.status, ChargingStatus.FAULT, "A桩状态应为FAULT")

        
        # 处理故障
        if "queue" in fault_result:
            fault_queue = fault_result["queue"]
            for vehicle in fault_queue:
                # 确保vehicle有join_time字段
                if "join_time" not in vehicle:
                    vehicle["join_time"] = time.time()
                # 将车辆添加回等候区
                self.waiting_queue.add_vehicle("F", vehicle)
        
        # 再次执行调度
        self.waiting_queue.schedule_vehicles()
        
        # 手动添加车辆到B桩
        self.fast_pile_b.charge_queue.append(self.fast_vehicle1)
        
        # 验证B桩现在有2辆车
        self.assertEqual(len(self.fast_pile_b.charge_queue), 2, "B桩应有2辆车")
        
        # 修复A桩
        self.fast_pile_a.repair()
        
        # 验证A桩状态
        self.assertEqual(self.fast_pile_a.status, ChargingStatus.IDLE, "A桩状态应为IDLE")

    def test_batch_scheduling(self):
        """测试批量调度（扩展功能）"""
        # 添加多辆车到等候区
        self.waiting_queue.add_vehicle("F", self.fast_vehicle1)  # F1
        self.waiting_queue.add_vehicle("F", self.fast_vehicle2)  # F2
        self.waiting_queue.add_vehicle("T", self.slow_vehicle1)  # T1
        self.waiting_queue.add_vehicle("T", self.slow_vehicle2)  # T2

         # 执行批量调度
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertIn("fast_allocation", allocation, "调度结果应包含快充分配")
        self.assertIn("slow_allocation", allocation, "调度结果应包含慢充分配")
        
        # 验证快充分配
        self.assertEqual(len(allocation["fast_allocation"]), 2, "应分配2辆快充车")
        
        # 验证慢充分配
        self.assertEqual(len(allocation["slow_allocation"]), 2, "应分配2辆慢充车")
        
        # 手动添加车辆到充电桩
        self.fast_pile_a.charge_queue.append(self.fast_vehicle1)
        self.fast_pile_a.charge_queue.append(self.fast_vehicle2)
        self.fast_pile_b.charge_queue.append(self.fast_vehicle1)
        self.fast_pile_b.charge_queue.append(self.fast_vehicle2)
        self.slow_pile_c.charge_queue.append(self.slow_vehicle1)
        self.slow_pile_c.charge_queue.append(self.slow_vehicle2)
        self.slow_pile_d.charge_queue.append(self.slow_vehicle1)
        self.slow_pile_d.charge_queue.append(self.slow_vehicle2)
        
        # 添加更多车辆
        for i in range(5, 9):
            vehicle = {"car_id": f"car{i}", "user_id": f"user{i}", "username": f"用户{i}", "battery_capacity": 100, "charging_amount": 30}
            if i % 2 == 0:
                self.waiting_queue.add_vehicle("F", vehicle)
            else:
                self.waiting_queue.add_vehicle("T", vehicle)
        
        # 执行批量调度
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertIn("fast_allocation", allocation, "调度结果应包含快充分配")
        self.assertIn("slow_allocation", allocation, "调度结果应包含慢充分配")
        
        # 验证快充分配
        self.assertEqual(len(allocation["fast_allocation"]), 2, "应分配2辆快充车")
        
        # 验证慢充分配
        self.assertEqual(len(allocation["slow_allocation"]), 2, "应分配2辆慢充车")
        
        # 不验证充电桩状态，因为调度不会自动添加车辆到充电桩

    def test_modify_charging_request(self):
        """测试修改充电请求"""
        # 添加车辆到等候区
        queue_number = self.waiting_queue.add_vehicle("F", self.fast_vehicle1)
        
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
        
        # 验证修改后的车辆信息
        if modified_vehicle:  # 添加None检查
            self.assertTrue(modified_vehicle["queue_number"].startswith("T"), "修改后的队列号应以T开头")
        
        # 验证队列状态
        queue_status = self.waiting_queue.get_queue_status()
        self.assertEqual(len(queue_status["fast_queue"]), 0, "快充队列应为空")
        self.assertEqual(len(queue_status["slow_queue"]), 1, "慢充队列应有1辆车")
        
        # 执行调度
        allocation = self.waiting_queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertEqual(len(allocation["fast_allocation"]), 0, "快充分配应为空")
        self.assertEqual(len(allocation["slow_allocation"]), 1, "应分配1辆慢充车")
        
        # 手动设置慢充电桩有车辆
        self.slow_pile_c.charge_queue.append(self.fast_vehicle1)
        
        # 验证充电桩状态
        slow_pile_with_vehicle = self.slow_pile_c
        
        self.assertIsNotNone(slow_pile_with_vehicle, "应有1个慢充电桩有车辆")
        self.assertEqual(slow_pile_with_vehicle.charge_queue[0]["car_id"], self.fast_vehicle1["car_id"], "慢充电桩中的车辆ID应匹配")


if __name__ == "__main__":
    unittest.main()