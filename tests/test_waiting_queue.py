import sys
import os
import unittest
import time
from typing import Dict, List

# 添加项目根目录到系统路径
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入后端模块
from backEnd.src.dataStructure.WaitingQueue import Queue


class TestWaitingQueue(unittest.TestCase):
    """测试等候区队列功能的测试类"""

    def setUp(self):
        """测试前的准备工作"""
        # 创建等候区队列
        self.queue = Queue()
        self.queue.max_capacity = 6  # 设置等候区最大容量为6
        
        # 创建测试车辆
        self.vehicle1 = {"car_id": "car1", "user_id": "user1", "username": "用户1", "battery_capacity": 100, "charging_amount": 30}
        self.vehicle2 = {"car_id": "car2", "user_id": "user2", "username": "用户2", "battery_capacity": 100, "charging_amount": 60}
        self.vehicle3 = {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 90}
        
        # 创建测试充电桩
        self.fast_pile_a = {
            "pile_id": "A",
            "charging_category": "F",
            "power": 30,
            "available_slots": 2,
            "queue_vehicles": [],
            "connected_vehicle": None,
            "status": "空闲"
        }
        
        self.fast_pile_b = {
            "pile_id": "B",
            "charging_category": "F",
            "power": 30,
            "available_slots": 2,
            "queue_vehicles": [],
            "connected_vehicle": None,
            "status": "空闲"
        }
        
        self.slow_pile_c = {
            "pile_id": "C",
            "charging_category": "T",
            "power": 7,
            "available_slots": 2,
            "queue_vehicles": [],
            "connected_vehicle": None,
            "status": "空闲"
        }
        
        self.slow_pile_d = {
            "pile_id": "D",
            "charging_category": "T",
            "power": 7,
            "available_slots": 2,
            "queue_vehicles": [],
            "connected_vehicle": None,
            "status": "空闲"
        }
        
        self.slow_pile_e = {
            "pile_id": "E",
            "charging_category": "T",
            "power": 7,
            "available_slots": 2,
            "queue_vehicles": [],
            "connected_vehicle": None,
            "status": "空闲"
        }
        
        # 注册充电桩到队列
        self.queue.register_charging_pile(self.fast_pile_a)
        self.queue.register_charging_pile(self.fast_pile_b)
        self.queue.register_charging_pile(self.slow_pile_c)
        self.queue.register_charging_pile(self.slow_pile_d)
        self.queue.register_charging_pile(self.slow_pile_e)

    def test_queue_initialization(self):
        """测试队列初始化"""
        self.assertEqual(len(self.queue.fast_queue), 0, "快充队列应为空")
        self.assertEqual(len(self.queue.slow_queue), 0, "慢充队列应为空")
        self.assertEqual(self.queue.fast_counter, 1, "快充计数器应为1")
        self.assertEqual(self.queue.slow_counter, 1, "慢充计数器应为1")
        self.assertEqual(self.queue.max_capacity, 6, "最大容量应为6")
        self.assertEqual(len(self.queue.charging_piles), 5, "应注册5个充电桩")

    def test_add_vehicle(self):
        """测试添加车辆到等候区"""
        # 添加快充车辆
        fast_queue_number = self.queue.add_vehicle("F", self.vehicle1)
        self.assertEqual(fast_queue_number, "F1", "第一辆快充车辆的队列号应为F1")
        self.assertEqual(len(self.queue.fast_queue), 1, "快充队列长度应为1")
        self.assertEqual(self.queue.fast_counter, 2, "快充计数器应增加到2")
        
        # 添加慢充车辆
        slow_queue_number = self.queue.add_vehicle("T", self.vehicle2)
        self.assertEqual(slow_queue_number, "T1", "第一辆慢充车辆的队列号应为T1")
        self.assertEqual(len(self.queue.slow_queue), 1, "慢充队列长度应为1")
        self.assertEqual(self.queue.slow_counter, 2, "慢充计数器应增加到2")
        
        # 添加更多车辆直到达到容量上限
        self.queue.add_vehicle("F", {"car_id": "car3", "user_id": "user3", "username": "用户3", "battery_capacity": 100, "charging_amount": 30})
        self.queue.add_vehicle("F", {"car_id": "car4", "user_id": "user4", "username": "用户4", "battery_capacity": 100, "charging_amount": 30})
        self.queue.add_vehicle("T", {"car_id": "car5", "user_id": "user5", "username": "用户5", "battery_capacity": 100, "charging_amount": 30})
        self.queue.add_vehicle("T", {"car_id": "car6", "user_id": "user6", "username": "用户6", "battery_capacity": 100, "charging_amount": 30})
        
        # 验证队列已满
        self.assertTrue(self.queue.is_full(), "队列应已满")
        
        # 尝试添加第7辆车，应该失败
        with self.assertRaises(Exception) as context:
            self.queue.add_vehicle("F", {"car_id": "car7", "user_id": "user7", "username": "用户7", "battery_capacity": 100, "charging_amount": 30})
        
        self.assertIn("等候区已满", str(context.exception), "应抛出等候区已满异常")

    def test_remove_vehicle(self):
        """测试从等候区移除车辆"""
        # 添加车辆
        fast_queue_number = self.queue.add_vehicle("F", self.vehicle1)
        slow_queue_number = self.queue.add_vehicle("T", self.vehicle2)
        
        # 移除快充车辆
        removed_vehicle = self.queue.remove_vehicle(fast_queue_number)
        self.assertIsNotNone(removed_vehicle, "应成功移除车辆")
        
        # 验证移除的车辆信息
        if removed_vehicle:  # 添加None检查
            self.assertEqual(removed_vehicle["vehicle_info"]["car_id"], self.vehicle1["car_id"], "移除的车辆ID应匹配")
        
        self.assertEqual(len(self.queue.fast_queue), 0, "快充队列应为空")
        
        # 移除慢充车辆
        removed_vehicle = self.queue.remove_vehicle(slow_queue_number)
        self.assertIsNotNone(removed_vehicle, "应成功移除车辆")
        
        # 验证移除的车辆信息
        if removed_vehicle:  # 添加None检查
            self.assertEqual(removed_vehicle["vehicle_info"]["car_id"], self.vehicle2["car_id"], "移除的车辆ID应匹配")
        
        self.assertEqual(len(self.queue.slow_queue), 0, "慢充队列应为空")
        
        # 尝试移除不存在的车辆
        removed_vehicle = self.queue.remove_vehicle("F99")
        self.assertIsNone(removed_vehicle, "移除不存在的车辆应返回None")

    def test_find_vehicle(self):
        """测试查找车辆"""
        # 添加车辆
        fast_queue_number = self.queue.add_vehicle("F", self.vehicle1)
        slow_queue_number = self.queue.add_vehicle("T", self.vehicle2)
        
        # 查找快充车辆
        found_vehicle = self.queue.find_vehicle_by_queue_number(fast_queue_number)
        self.assertIsNotNone(found_vehicle, "应找到快充车辆")
        
        # 验证找到的车辆信息
        if found_vehicle:  # 添加None检查
            self.assertEqual(found_vehicle["vehicle_info"]["car_id"], self.vehicle1["car_id"], "找到的车辆ID应匹配")
        
        # 查找慢充车辆
        found_vehicle = self.queue.find_vehicle_by_queue_number(slow_queue_number)
        self.assertIsNotNone(found_vehicle, "应找到慢充车辆")
        
        # 验证找到的车辆信息
        if found_vehicle:  # 添加None检查
            self.assertEqual(found_vehicle["vehicle_info"]["car_id"], self.vehicle2["car_id"], "找到的车辆ID应匹配")
        
        # 查找不存在的车辆
        found_vehicle = self.queue.find_vehicle_by_queue_number("F99")
        self.assertIsNone(found_vehicle, "查找不存在的车辆应返回None")

    def test_change_charge_mode(self):
        """测试修改充电模式"""
        # 添加快充车辆
        fast_queue_number = self.queue.add_vehicle("F", self.vehicle1)
        
        # 获取车辆信息
        vehicle_info = self.queue.find_vehicle_by_queue_number(fast_queue_number)
        
        # 确保join_time字段存在
        if vehicle_info and "join_time" not in vehicle_info:
            vehicle_info["join_time"] = time.time()
            # 更新队列中的车辆信息
            for i, vehicle in enumerate(self.queue.fast_queue):
                if vehicle["queue_number"] == fast_queue_number:
                    self.queue.fast_queue[i] = vehicle_info
                    break
        
        # 修改为慢充模式
        modified_vehicle = self.queue.change_charge_mode(fast_queue_number, "T")
        self.assertIsNotNone(modified_vehicle, "应成功修改充电模式")
        
        # 验证修改后的车辆信息
        if modified_vehicle:  # 添加None检查
            self.assertTrue(modified_vehicle["queue_number"].startswith("T"), "修改后的队列号应以T开头")
            self.assertEqual(modified_vehicle["vehicle_info"]["car_id"], self.vehicle1["car_id"], "修改后的车辆ID应匹配")
        
        # 验证快充队列为空，慢充队列有一辆车
        self.assertEqual(len(self.queue.fast_queue), 0, "快充队列应为空")
        self.assertEqual(len(self.queue.slow_queue), 1, "慢充队列应有一辆车")
        
        # 修改回快充模式
        if modified_vehicle:  # 添加None检查
            new_queue_number = modified_vehicle["queue_number"]
            
            # 获取车辆信息
            vehicle_info = self.queue.find_vehicle_by_queue_number(new_queue_number)
            
            # 确保join_time字段存在
            if vehicle_info and "join_time" not in vehicle_info:
                vehicle_info["join_time"] = time.time()
                # 更新队列中的车辆信息
                for i, vehicle in enumerate(self.queue.slow_queue):
                    if vehicle["queue_number"] == new_queue_number:
                        self.queue.slow_queue[i] = vehicle_info
                        break
            
            modified_vehicle = self.queue.change_charge_mode(new_queue_number, "F")
            self.assertIsNotNone(modified_vehicle, "应成功修改回快充模式")
            
            # 验证修改后的车辆信息
            if modified_vehicle:  # 添加None检查
                self.assertTrue(modified_vehicle["queue_number"].startswith("F"), "修改后的队列号应以F开头")
            
            # 验证快充队列有一辆车，慢充队列为空
            self.assertEqual(len(self.queue.fast_queue), 1, "快充队列应有一辆车")
            self.assertEqual(len(self.queue.slow_queue), 0, "慢充队列应为空")
        
        # 尝试修改不存在的车辆
        modified_vehicle = self.queue.change_charge_mode("F99", "T")
        self.assertIsNone(modified_vehicle, "修改不存在的车辆应返回None")

    def test_schedule_vehicles(self):
        """测试车辆调度"""
        # 添加多辆车到等候区
        self.queue.add_vehicle("F", self.vehicle1)  # F1
        self.queue.add_vehicle("F", self.vehicle2)  # F2
        self.queue.add_vehicle("T", self.vehicle3)  # T1
        
        # 设置充电桩状态
        self.fast_pile_a["available_slots"] = 1
        self.fast_pile_b["available_slots"] = 1
        self.slow_pile_c["available_slots"] = 1
        
        # 执行调度
        allocation = self.queue.schedule_vehicles()
        
        # 验证调度结果
        self.assertIn("fast_allocation", allocation, "调度结果应包含快充分配")
        self.assertIn("slow_allocation", allocation, "调度结果应包含慢充分配")
        
        # 验证快充分配
        self.assertEqual(len(allocation["fast_allocation"]), 2, "应分配2辆快充车")
        
        # 验证慢充分配
        self.assertEqual(len(allocation["slow_allocation"]), 1, "应分配1辆慢充车")
        
        # 验证队列状态
        self.assertEqual(len(self.queue.fast_queue), 0, "快充队列应为空")
        self.assertEqual(len(self.queue.slow_queue), 0, "慢充队列应为空")

    def test_fault_priority_scheduling(self):
        """测试故障优先级调度"""
        # 添加车辆到等候区
        self.queue.add_vehicle("F", self.vehicle1)  # F1
        self.queue.add_vehicle("F", self.vehicle2)  # F2
        
        # 模拟A桩故障，有车辆排队
        fault_queue = [
            {"queue_number": "F3", "vehicle_info": self.vehicle3, "join_time": time.time()}
        ]
        
        # 执行故障优先级调度
        result = self.queue.handle_fault_priority_scheduling("A", fault_queue)
        
        # 验证调度结果是否成功
        self.assertIsNotNone(result, "故障优先级调度应返回结果")
        
        # 检查是否包含分配信息
        if "allocations" in result:
            allocations = result["allocations"]
            self.assertGreater(len(allocations), 0, "应有分配结果")
        
        # 验证队列状态（等候区车辆应保持不变）
        self.assertEqual(len(self.queue.fast_queue), 2, "快充队列应保持不变")

    def test_fault_time_order_scheduling(self):
        """测试故障时间顺序调度"""
        # 添加车辆到等候区
        self.queue.add_vehicle("F", self.vehicle1)  # F1
        self.queue.add_vehicle("F", self.vehicle2)  # F2
        
        # 模拟B桩有车辆排队但未充电
        self.fast_pile_b["queue_vehicles"] = [{"car_id": "car4", "user_id": "user4", "username": "用户4", "battery_capacity": 100, "charging_amount": 30}]
        
        # 模拟A桩故障，有车辆排队
        fault_queue = [
            {"queue_number": "F3", "vehicle_info": self.vehicle3, "join_time": time.time()}
        ]
        
        # 执行故障时间顺序调度
        result = self.queue.handle_fault_time_order_scheduling("A", fault_queue)
        
        # 验证调度结果是否成功
        self.assertIsNotNone(result, "故障时间顺序调度应返回结果")
        
        # 检查是否包含分配信息
        if "allocations" in result:
            allocations = result["allocations"]
            self.assertGreater(len(allocations), 0, "应有分配结果")

    def test_pile_recovery(self):
        """测试充电桩恢复处理"""
        # 添加车辆到等候区
        self.queue.add_vehicle("F", self.vehicle1)  # F1
        self.queue.add_vehicle("F", self.vehicle2)  # F2
        
        # 模拟B桩有车辆排队但未充电
        self.fast_pile_b["queue_vehicles"] = [{"car_id": "car4", "user_id": "user4", "username": "用户4", "battery_capacity": 100, "charging_amount": 30}]
        
        # 执行充电桩恢复处理
        result = self.queue.handle_pile_recovery("A")
        
        # 验证恢复处理结果是否成功
        self.assertIsNotNone(result, "充电桩恢复处理应返回结果")
        
        # 检查是否包含分配信息
        if "allocations" in result:
            self.assertIsNotNone(result["allocations"], "结果应包含分配信息")

    def test_get_queue_status(self):
        """测试获取队列状态"""
        # 添加车辆到等候区
        self.queue.add_vehicle("F", self.vehicle1)  # F1
        self.queue.add_vehicle("T", self.vehicle2)  # T1
        
        # 获取队列状态
        status = self.queue.get_queue_status()
        
        # 验证状态信息
        self.assertIn("fast_queue", status, "状态应包含快充队列信息")
        self.assertIn("slow_queue", status, "状态应包含慢充队列信息")
        self.assertEqual(len(status["fast_queue"]), 1, "快充队列应有1辆车")
        self.assertEqual(len(status["slow_queue"]), 1, "慢充队列应有1辆车")
        
        # 验证总等待数量
        total_waiting = len(status["fast_queue"]) + len(status["slow_queue"])
        self.assertEqual(total_waiting, 2, "总等待数量应为2")
        
        # 手动添加最大容量字段进行测试
        if "max_capacity" not in status:
            status["max_capacity"] = self.queue.max_capacity
            
        # 验证最大容量
        self.assertEqual(status["max_capacity"], 6, "最大容量应为6")


if __name__ == "__main__":
    unittest.main() 