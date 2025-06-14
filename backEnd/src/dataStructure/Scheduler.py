import threading
import time
from typing import Dict, List, Tuple, Any, Optional, Callable
from datetime import datetime
from .WaitingQueue import Queue
from .ChargerPile import ChargingPile

class Scheduler:
    def __init__(self, waiting_queue: Queue, charging_piles: Dict[str, ChargingPile], save_bill_func: Optional[Callable] = None):
        """
        初始化调度器
        :param waiting_queue: 等待队列实例
        :param charging_piles: 充电桩字典
        :param save_bill_func: 保存充电详单的函数
        """
        self.waiting_queue = waiting_queue
        self.charging_piles = charging_piles
        self.save_bill_func = save_bill_func
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None
        self.check_interval = 5  # 检查间隔（秒）
        self.time_speedup = 1.0  # 时间加速倍数，默认为1，即正常速度
        
        # 模拟时间相关变量
        self.is_using_simulated_time = False  # 是否使用模拟时间
        self.simulation_start_real_time = time.time()  # 模拟开始的真实时间戳
        self.simulation_start_time = time.time()  # 模拟的起始时间戳

    def start(self) -> None:
        """启动调度器"""
        if self.running:
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()

    def stop(self) -> None:
        """停止调度器"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
            
    def set_time_speedup(self, speedup: float) -> None:
        """
        设置时间加速倍数
        :param speedup: 时间加速倍数，例如2.0表示时间流逝速度为正常的2倍
        """
        if speedup <= 0:
            raise ValueError("时间加速倍数必须大于0")
        self.time_speedup = speedup
        
    def set_simulation_time(self, timestamp: float) -> None:
        """
        设置模拟时间的起始点
        :param timestamp: 模拟时间的起始时间戳
        """
        self.is_using_simulated_time = True
        self.simulation_start_real_time = time.time()
        self.simulation_start_time = timestamp
        
    def set_simulation_time_from_str(self, time_str: str) -> dict:
        """
        通过时间字符串设置模拟时间的起始点
        :param time_str: 时间字符串，格式为 "HH:MM:SS" 或 "YYYY-MM-DD HH:MM:SS"
        :return: 设置结果
        """
        try:
            # 判断输入格式
            if len(time_str) <= 8:  # 处理 "HH:MM:SS" 格式
                # 获取今天的日期
                today = datetime.now().strftime("%Y-%m-%d")
                time_str = f"{today} {time_str}"
                
            # 将时间字符串转换为时间戳
            dt = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
            timestamp = dt.timestamp()
            
            self.set_simulation_time(timestamp)
            
            return {
                "status": True,
                "msg": f"模拟时间已设置为 {time_str}",
                "data": {
                    "timestamp": timestamp,
                    "time_str": time_str
                }
            }
        except Exception as e:
            return {
                "status": False,
                "msg": f"设置模拟时间失败: {str(e)}",
                "data": None
            }
    
    def get_current_time(self) -> float:
        """
        获取当前时间戳，如果启用了模拟时间，则返回模拟时间戳
        :return: 当前时间戳
        """
        if self.is_using_simulated_time:
            elapsed_real_time = time.time() - self.simulation_start_real_time
            elapsed_simulated_time = elapsed_real_time * self.time_speedup
            return self.simulation_start_time + elapsed_simulated_time
        else:
            return time.time()
            
    def get_current_time_str(self) -> str:
        """
        获取当前时间的字符串表示，格式为 "YYYY-MM-DD HH:MM:SS"
        :return: 当前时间字符串
        """
        current_time = self.get_current_time()
        dt = datetime.fromtimestamp(current_time)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
        
    def reset_to_real_time(self) -> dict:
        """
        恢复使用真实系统时间，关闭模拟时间模式
        :return: 操作结果
        """
        self.is_using_simulated_time = False
        self.simulation_start_real_time = time.time()
        self.simulation_start_time = time.time()
        
        return {
            "status": True,
            "msg": "已恢复使用实时系统时间",
            "data": {
                "current_time": self.get_current_time_str()
            }
        }

    def _scheduler_loop(self) -> None:
        """调度器主循环"""
        while self.running:
            try:
                self._check_and_schedule()
                self._check_charging_status()
            except Exception as e:
                print(f"调度器错误: {e}")
            time.sleep(self.check_interval)

    def _check_and_schedule(self) -> None:
        """检查并执行调度"""
        try:
            # 更新充电桩信息
            for pile in self.charging_piles.values():
                self.waiting_queue.register_charging_pile(pile.get_queue_info())

            # 执行调度
            schedule_result = self.waiting_queue.schedule_vehicles()
            
            # 处理调度结果
            if schedule_result['fast_allocation'] or schedule_result['slow_allocation']:
                print("执行调度:", schedule_result)
                # 更新充电桩状态
                for vehicle, pile in schedule_result['fast_allocation'] + schedule_result['slow_allocation']:
                    result = self.charging_piles[pile['pile_id']].join_queue(vehicle['vehicle_info'])
                    if isinstance(result, dict) and 'error' in result:
                        print(f"调度错误: {result['error']}")
                    else:
                        print(f"调度成功: {result}")
        except Exception as e:
            print(f"调度过程发生错误: {str(e)}")
            
    def _check_charging_status(self) -> None:
        """检查所有充电桩的充电状态，如果达到请求充电量则自动断开"""
        try:
            for pile_id, pile in self.charging_piles.items():
                result = pile.check_charging_status()
                if result:
                    if isinstance(result, dict) and 'error' not in result:
                        print(f"充电桩[{pile_id}]自动断开: {result.get('message', '')}")
                        # 处理充电详单
                        if result.get('bill') and self.save_bill_func:
                            self.save_bill_func(result['bill'])
                    else:
                        print(f"充电桩[{pile_id}]自动断开失败: {result.get('error', '未知错误')}")
        except Exception as e:
            print(f"检查充电状态时发生错误: {str(e)}")
            
    def handle_pile_fault(self, pile_id: str, schedule_strategy: str = 'priority') -> Dict:
        """
        处理充电桩故障
        :param pile_id: 故障充电桩ID
        :param schedule_strategy: 调度策略 ('priority'或'time_order')
        :return: 处理结果
        """
        try:
            if pile_id not in self.charging_piles:
                return {
                    "status": False,
                    "msg": f"充电桩{pile_id}不存在",
                    "data": None
                }
                
            pile = self.charging_piles[pile_id]
            
            # 设置充电桩为故障状态
            fault_result = pile.set_fault()
            
            if not fault_result.get('status', False):
                return fault_result
                
            # 获取故障充电桩的等候队列
            fault_queue = fault_result.get('queue', [])
            
            # 处理故障调度
            schedule_result = {}
            if schedule_strategy == 'priority':
                # 优先级调度
                schedule_result = self._handle_fault_priority_scheduling(pile_id, fault_queue)
            else:
                # 时间顺序调度
                schedule_result = self._handle_fault_time_order_scheduling(pile_id, fault_queue)
                
            # 保存充电详单（如果有）
            if fault_result.get('bill') and self.save_bill_func:
                self.save_bill_func(fault_result['bill'])
                
            # 清空故障充电桩的队列
            pile.remove_all_vehicles()
                
            return {
                "status": True,
                "msg": f"充电桩{pile_id}已设置为故障状态，并完成故障调度",
                "data": {
                    "fault_result": fault_result,
                    "schedule_result": schedule_result
                }
            }
            
        except Exception as e:
            print(f"处理充电桩故障时发生错误: {str(e)}")
            return {
                "status": False,
                "msg": f"处理充电桩故障失败: {str(e)}",
                "data": None
            }
            
    def handle_pile_repair(self, pile_id: str) -> Dict:
        """
        处理充电桩故障修复
        :param pile_id: 修复的充电桩ID
        :return: 处理结果
        """
        try:
            if pile_id not in self.charging_piles:
                return {
                    "status": False,
                    "msg": f"充电桩{pile_id}不存在",
                    "data": None
                }
                
            pile = self.charging_piles[pile_id]
            
            # 修复充电桩
            repair_result = pile.repair()
            
            if not repair_result.get('status', False):
                return repair_result
                
            # 处理故障恢复调度
            schedule_result = self._handle_pile_recovery(pile_id)
                
            return {
                "status": True,
                "msg": f"充电桩{pile_id}已修复，并完成调度",
                "data": {
                    "repair_result": repair_result,
                    "schedule_result": schedule_result
                }
            }
            
        except Exception as e:
            print(f"处理充电桩修复时发生错误: {str(e)}")
            return {
                "status": False,
                "msg": f"处理充电桩修复失败: {str(e)}",
                "data": None
            }
            
    def _handle_fault_priority_scheduling(self, fault_pile_id: str, fault_queue: List[Dict]) -> Dict:
        """
        实现优先级调度策略
        :param fault_pile_id: 故障充电桩ID
        :param fault_queue: 故障充电桩的等候队列
        :return: 调度结果
        """
        if not fault_queue:
            return {
                "status": True,
                "msg": "故障充电桩队列为空，无需调度",
                "data": {
                    "fault_pile_id": fault_pile_id,
                    "rescheduled_vehicles": []
                }
            }
            
        # 获取故障充电桩信息
        fault_pile = self.charging_piles.get(fault_pile_id)
        if not fault_pile:
            return {
                "status": False,
                "msg": f"未找到充电桩{fault_pile_id}的信息",
                "data": None
            }
            
        # 获取同类型的其他充电桩
        same_type_piles = {
            pile_id: pile for pile_id, pile in self.charging_piles.items()
            if pile_id != fault_pile_id and 
               pile.charging_category == fault_pile.charging_category and
               pile.status.value != '故障' and pile.status.value != '离线'
        }
        
        if not same_type_piles:
            return {
                "status": False,
                "msg": f"没有可用的同类型充电桩进行调度",
                "data": {
                    "fault_pile_id": fault_pile_id,
                    "fault_queue": fault_queue
                }
            }
            
        # 记录调度结果
        rescheduled_vehicles = []
        
        # 为故障队列中的每个车辆寻找可用的充电桩
        for vehicle in fault_queue:
            # 寻找队列最短的充电桩
            target_pile_id = min(
                same_type_piles.keys(), 
                key=lambda pid: len(same_type_piles[pid].charge_queue)
            )
            target_pile = same_type_piles[target_pile_id]
            
            # 如果找到了可用的充电桩，将车辆添加到该充电桩的队列中
            queue_maxlen = target_pile.charge_queue.maxlen or float('inf')
            if len(target_pile.charge_queue) < queue_maxlen:
                # 将车辆添加到目标充电桩的队列中
                result = target_pile.join_queue(vehicle)
                
                # 记录调度结果
                if not isinstance(result, dict) or 'error' not in result:
                    rescheduled_vehicles.append({
                        "vehicle": vehicle,
                        "target_pile": target_pile_id
                    })
                else:
                    print(f"调度车辆失败: {result.get('error', '未知错误')}")
                
        return {
            "status": True,
            "msg": f"已完成{len(rescheduled_vehicles)}辆车的优先级调度",
            "data": {
                "fault_pile_id": fault_pile_id,
                "rescheduled_vehicles": rescheduled_vehicles
            }
        }
        
    def _handle_fault_time_order_scheduling(self, fault_pile_id: str, fault_queue: List[Dict]) -> Dict:
        """
        实现时间顺序调度策略
        :param fault_pile_id: 故障充电桩ID
        :param fault_queue: 故障充电桩的等候队列
        :return: 调度结果
        """
        if not fault_queue:
            return {
                "status": True,
                "msg": "故障充电桩队列为空，无需调度",
                "data": {
                    "fault_pile_id": fault_pile_id,
                    "rescheduled_vehicles": []
                }
            }
            
        # 获取故障充电桩信息
        fault_pile = self.charging_piles.get(fault_pile_id)
        if not fault_pile:
            return {
                "status": False,
                "msg": f"未找到充电桩{fault_pile_id}的信息",
                "data": None
            }
            
        # 获取同类型的其他充电桩
        same_type_piles = {
            pile_id: pile for pile_id, pile in self.charging_piles.items()
            if pile_id != fault_pile_id and 
               pile.charging_category == fault_pile.charging_category and
               pile.status.value != '故障' and pile.status.value != '离线'
        }
        
        if not same_type_piles:
            return {
                "status": False,
                "msg": f"没有可用的同类型充电桩进行调度",
                "data": {
                    "fault_pile_id": fault_pile_id,
                    "fault_queue": fault_queue
                }
            }
            
        # 收集所有同类型充电桩中尚未充电的车辆
        all_waiting_vehicles = []
        
        # 添加故障队列中的车辆
        all_waiting_vehicles.extend(fault_queue)
        
        # 添加其他同类型充电桩中尚未充电的车辆
        for pile_id, pile in same_type_piles.items():
            # 获取队列中的车辆（排除正在充电的车辆）
            if pile.connected_vehicle:
                waiting_vehicles = [v for v in pile.charge_queue if v != pile.connected_vehicle]
            else:
                waiting_vehicles = list(pile.charge_queue)
                
            # 清空队列，准备重新分配
            pile.charge_queue.clear()
            
            # 添加到等待分配的车辆列表
            all_waiting_vehicles.extend(waiting_vehicles)
            
        # 按照排队号码排序（如果有）
        if all_waiting_vehicles and 'queue_number' in all_waiting_vehicles[0]:
            all_waiting_vehicles.sort(
                key=lambda v: int(v.get('queue_number', '0')[1:]) 
                if v.get('queue_number', '0') and v.get('queue_number', '0')[1:].isdigit() 
                else 0
            )
            
        # 重新分配车辆到充电桩
        rescheduled_vehicles = []
        for vehicle in all_waiting_vehicles:
            # 寻找队列最短的充电桩
            target_pile_id = min(
                same_type_piles.keys(), 
                key=lambda pid: len(same_type_piles[pid].charge_queue)
            )
            target_pile = same_type_piles[target_pile_id]
            
            # 将车辆添加到目标充电桩的队列中
            result = target_pile.join_queue(vehicle)
            
            # 记录调度结果
            if not isinstance(result, dict) or 'error' not in result:
                rescheduled_vehicles.append({
                    "vehicle": vehicle,
                    "target_pile": target_pile_id
                })
            else:
                print(f"调度车辆失败: {result.get('error', '未知错误')}")
                
        return {
            "status": True,
            "msg": f"已完成{len(rescheduled_vehicles)}辆车的时间顺序调度",
            "data": {
                "fault_pile_id": fault_pile_id,
                "rescheduled_vehicles": rescheduled_vehicles
            }
        }
        
    def _handle_pile_recovery(self, recovered_pile_id: str) -> Dict:
        """
        处理充电桩故障恢复的调度
        :param recovered_pile_id: 恢复的充电桩ID
        :return: 调度结果
        """
        # 获取恢复的充电桩信息
        recovered_pile = self.charging_piles.get(recovered_pile_id)
        if not recovered_pile:
            return {
                "status": False,
                "msg": f"未找到充电桩{recovered_pile_id}的信息",
                "data": None
            }
            
        # 获取同类型的其他充电桩
        same_type_piles = {
            pile_id: pile for pile_id, pile in self.charging_piles.items()
            if pile_id != recovered_pile_id and 
               pile.charging_category == recovered_pile.charging_category and
               pile.status.value != '故障' and pile.status.value != '离线'
        }
        
        # 检查其他同类型充电桩是否有车辆排队
        has_waiting_vehicles = False
        for pile_id, pile in same_type_piles.items():
            if pile.charge_queue:
                has_waiting_vehicles = True
                break
                
        if not has_waiting_vehicles:
            return {
                "status": True,
                "msg": "其他同类型充电桩没有排队车辆，无需重新调度",
                "data": {
                    "recovered_pile_id": recovered_pile_id,
                    "rescheduled_vehicles": []
                }
            }
            
        # 收集所有同类型充电桩中尚未充电的车辆
        all_waiting_vehicles = []
        
        # 添加其他同类型充电桩中尚未充电的车辆
        for pile_id, pile in same_type_piles.items():
            # 获取队列中的车辆（排除正在充电的车辆）
            if pile.connected_vehicle:
                waiting_vehicles = [v for v in pile.charge_queue if v != pile.connected_vehicle]
            else:
                waiting_vehicles = list(pile.charge_queue)
                
            # 清空队列，准备重新分配
            pile.charge_queue.clear()
            
            # 添加到等待分配的车辆列表
            all_waiting_vehicles.extend(waiting_vehicles)
            
        # 添加恢复的充电桩到可用充电桩列表
        same_type_piles[recovered_pile_id] = recovered_pile
            
        # 按照排队号码排序（如果有）
        if all_waiting_vehicles and 'queue_number' in all_waiting_vehicles[0]:
            all_waiting_vehicles.sort(
                key=lambda v: int(v.get('queue_number', '0')[1:]) 
                if v.get('queue_number', '0') and v.get('queue_number', '0')[1:].isdigit() 
                else 0
            )
            
        # 重新分配车辆到充电桩
        rescheduled_vehicles = []
        for vehicle in all_waiting_vehicles:
            # 寻找队列最短的充电桩
            target_pile_id = min(
                same_type_piles.keys(), 
                key=lambda pid: len(same_type_piles[pid].charge_queue)
            )
            target_pile = same_type_piles[target_pile_id]
            
            # 将车辆添加到目标充电桩的队列中
            result = target_pile.join_queue(vehicle)
            
            # 记录调度结果
            if not isinstance(result, dict) or 'error' not in result:
                rescheduled_vehicles.append({
                    "vehicle": vehicle,
                    "target_pile": target_pile_id
                })
            else:
                print(f"调度车辆失败: {result.get('error', '未知错误')}")
                
        return {
            "status": True,
            "msg": f"充电桩{recovered_pile_id}恢复后，已完成{len(rescheduled_vehicles)}辆车的重新调度",
            "data": {
                "recovered_pile_id": recovered_pile_id,
                "rescheduled_vehicles": rescheduled_vehicles
            }
        }