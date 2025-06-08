from typing import List, Dict, Any, Tuple, Optional, Union
import itertools

class Queue:
    def __init__(self):
        self.fast_queue = []  # 快充队列
        self.slow_queue = []  # 慢充队列
        self.fast_counter = 1  # 快充序号计数器
        self.slow_counter = 1  # 慢充序号计数器
        self.max_capacity = 6  # 最大容量
        self.charging_piles = {}  # 充电桩信息字典

    def register_charging_pile(self, pile_info: Dict[str, Any]):
        """
        注册充电桩信息
        :param pile_info: 充电桩信息
        """
        self.charging_piles[pile_info['pile_id']] = pile_info

    def calculate_total_charging_time(self, vehicles: List[Dict], piles: List[Dict]) -> float:
        """
        计算指定车辆在指定充电桩上的总充电时间
        :param vehicles: 车辆列表
        :param piles: 充电桩列表
        :return: 总充电时间（小时）
        """
        total_time = 0
        for vehicle, pile in zip(vehicles, piles):
            charging_time = vehicle['vehicle_info']['charging_amount'] / pile['power']
            total_time += charging_time
        return total_time

    def find_optimal_allocation(self, vehicles: List[Dict], available_piles: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """
        找到最优的车辆分配方案
        :param vehicles: 待分配车辆列表
        :param available_piles: 可用充电桩列表
        :return: 最优分配方案，列表中的每个元素是(车辆, 充电桩)的元组
        """
        if not vehicles or not available_piles:
            return []

        # 生成所有可能的分配方案
        pile_permutations = list(itertools.permutations(available_piles, len(vehicles)))
        min_total_time = float('inf')
        optimal_allocation = []

        for pile_perm in pile_permutations:
            total_time = self.calculate_total_charging_time(vehicles, list(pile_perm))
            if total_time < min_total_time:
                min_total_time = total_time
                optimal_allocation = list(zip(vehicles, pile_perm))

        return optimal_allocation

    def schedule_vehicles(self) -> Dict[str, List[Tuple[Dict, Dict]]]:
        """
        执行车辆调度
        :return: 调度结果，包含快充和慢充的分配方案
        """
        # 获取可用的快充和慢充充电桩
        fast_piles = [pile for pile in self.charging_piles.values() 
                     if pile['charging_category'] == 'F' and pile['available_slots'] > 0]
        slow_piles = [pile for pile in self.charging_piles.values() 
                     if pile['charging_category'] == 'T' and pile['available_slots'] > 0]

        # 获取待调度的车辆（按照先来后到原则）
        fast_vehicles = self.fast_queue[:len(fast_piles)]
        slow_vehicles = self.slow_queue[:len(slow_piles)]

        # 执行调度
        fast_allocation = self._allocate_vehicles(fast_vehicles, fast_piles)
        slow_allocation = self._allocate_vehicles(slow_vehicles, slow_piles)

        # 从队列中移除已调度的车辆
        for vehicle, _ in fast_allocation:
            self.fast_queue.remove(vehicle)
        for vehicle, _ in slow_allocation:
            self.slow_queue.remove(vehicle)

        return {
            'fast_allocation': fast_allocation,
            'slow_allocation': slow_allocation
        }

    def _allocate_vehicles(self, vehicles: List[Dict], piles: List[Dict]) -> List[Tuple[Dict, Dict]]:
        """
        根据最短总时间原则分配车辆到充电桩
        :param vehicles: 待分配车辆列表
        :param piles: 可用充电桩列表
        :return: 分配方案，列表中的每个元素是(车辆, 充电桩)的元组
        """
        if not vehicles or not piles:
            return []

        # 计算每个车辆在每个充电桩上的充电时间
        charging_times = {}
        for vehicle in vehicles:
            charging_times[vehicle['queue_number']] = {}
            for pile in piles:
                # 计算当前充电桩的总充电时间（包括队列中其他车辆的充电时间）
                total_time = 0
                # 加上队列中其他车辆的充电时间
                for queued_vehicle in pile.get('queue_vehicles', []):
                    total_time += queued_vehicle['charging_amount'] / pile['power']
                # 加上当前车辆的充电时间
                total_time += vehicle['vehicle_info']['charging_amount'] / pile['power']
                charging_times[vehicle['queue_number']][pile['pile_id']] = total_time

        # 使用匈牙利算法找到最优分配方案
        allocation = self._hungarian_algorithm(charging_times, piles)
        
        # 转换为(车辆, 充电桩)元组列表
        result = []
        for vehicle in vehicles:
            if vehicle['queue_number'] in allocation:
                pile_id = allocation[vehicle['queue_number']]
                pile = next(p for p in piles if p['pile_id'] == pile_id)
                result.append((vehicle, pile))
        
        return result

    def _hungarian_algorithm(self, costs: Dict[str, Dict[str, float]], piles: List[Dict]) -> Dict[str, str]:
        """
        使用匈牙利算法求解最优分配方案
        :param costs: 成本矩阵，格式为 {车辆ID: {充电桩ID: 充电时间}}
        :param piles: 充电桩列表
        :return: 最优分配方案，格式为 {车辆ID: 充电桩ID}
        """
        # 简化的匈牙利算法实现
        allocation = {}
        used_piles = set()
        
        # 对每个车辆，选择充电时间最短的可用充电桩
        for vehicle_id, pile_costs in costs.items():
            # 按充电时间排序
            sorted_piles = sorted(pile_costs.items(), key=lambda x: x[1])
            # 找到第一个未使用的充电桩
            for pile_id, _ in sorted_piles:
                if pile_id not in used_piles:
                    allocation[vehicle_id] = pile_id
                    used_piles.add(pile_id)
                    break
        
        return allocation

    def is_full(self):
        """检查等候区是否已满"""
        return len(self.fast_queue) + len(self.slow_queue) >= self.max_capacity

    def is_vehicle_in_queue(self, car_id: str) -> bool:
        """
        检查车辆是否在等待队列中
        :param car_id: 车辆ID
        :return: 是否在队列中
        """
        # 检查快充队列
        for vehicle in self.fast_queue:
            if vehicle['vehicle_info']['car_id'] == car_id:
                return True
        
        # 检查慢充队列
        for vehicle in self.slow_queue:
            if vehicle['vehicle_info']['car_id'] == car_id:
                return True
        
        return False

    def is_vehicle_charging(self, car_id: str) -> bool:
        """
        检查车辆是否正在充电
        :param car_id: 车辆ID
        :return: 是否正在充电
        """
        for pile in self.charging_piles.values():
            if pile['connected_vehicle'] and pile['connected_vehicle']['car_id'] == car_id:
                return True
            # 检查充电队列中的车辆
            queue_vehicles = pile.get('queue_vehicles', [])
            if isinstance(queue_vehicles, list):
                for vehicle in queue_vehicles:
                    if vehicle['car_id'] == car_id:
                        return True
        return False

    def add_vehicle(self, charge_type: str, vehicle_info: Dict) -> str:
        """
        添加车辆到等待队列
        :param charge_type: 'F' 表示快充，'T' 表示慢充
        :param vehicle_info: 车辆信息字典
        :return: 分配的排队号码
        """
        if self.is_full():
            raise Exception("等候区已满")

        # 检查车辆是否已在队列中
        if self.is_vehicle_in_queue(vehicle_info['car_id']):
            raise Exception("该车辆已在等候队列中")

        # 检查车辆是否正在充电
        if self.is_vehicle_charging(vehicle_info['car_id']):
            raise Exception("该车辆正在充电或已在充电队列中")

        if charge_type == 'F':
            queue_number = f"F{self.fast_counter}"
            self.fast_queue.append({
                'queue_number': queue_number,
                'vehicle_info': vehicle_info
            })
            self.fast_counter += 1
            return queue_number
        elif charge_type == 'T':
            queue_number = f"T{self.slow_counter}"
            self.slow_queue.append({
                'queue_number': queue_number,
                'vehicle_info': vehicle_info
            })
            self.slow_counter += 1
            return queue_number
        else:
            raise ValueError("无效的充电类型")

    def remove_vehicle(self, queue_number: str) -> Optional[Dict[str, Any]]:
        """
        从队列中移除车辆
        :param queue_number: 排队号码
        :return: 被移除的车辆信息
        """
        if queue_number.startswith('F'):
            for i, vehicle in enumerate(self.fast_queue):
                if vehicle['queue_number'] == queue_number:
                    return self.fast_queue.pop(i)
        elif queue_number.startswith('T'):
            for i, vehicle in enumerate(self.slow_queue):
                if vehicle['queue_number'] == queue_number:
                    return self.slow_queue.pop(i)
        return None

    def get_queue_status(self) -> Dict:
        """
        获取当前队列状态
        :return: 包含快充和慢充队列信息的字典
        """
        return {
            'fast_queue': self.fast_queue,
            'slow_queue': self.slow_queue,
            'total_vehicles': len(self.fast_queue) + len(self.slow_queue)
        }
        
    def find_vehicle_by_queue_number(self, queue_number: str) -> Optional[Dict[str, Any]]:
        """
        通过队列号查找车辆
        :param queue_number: 队列号
        :return: 找到的车辆信息，如果未找到则返回None
        """
        # 检查快充队列
        if queue_number.startswith('F'):
            for vehicle in self.fast_queue:
                if vehicle['queue_number'] == queue_number:
                    return vehicle
        # 检查慢充队列
        elif queue_number.startswith('T'):
            for vehicle in self.slow_queue:
                if vehicle['queue_number'] == queue_number:
                    return vehicle
        return None
        
    def change_charge_mode(self, queue_number: str, new_mode: str) -> Optional[Dict[str, Any]]:
        """
        修改充电模式（快充/慢充）
        :param queue_number: 排队号码
        :param new_mode: 新的充电模式 ('F': 快充, 'T': 慢充)
        :return: 更新后的车辆信息，如果未找到则返回None
        """
        # 检查新模式是否有效
        if new_mode not in ['F', 'T']:
            return None
            
        # 查找车辆
        vehicle = self.find_vehicle_by_queue_number(queue_number)
        if not vehicle:
            return None
            
        # 从原队列中移除
        if queue_number.startswith('F'):
            self.fast_queue.remove(vehicle)
        else:
            self.slow_queue.remove(vehicle)
            
        # 生成新的排队号码
        if new_mode == 'F':
            new_queue_number = f"F{self.fast_counter:03d}"
            self.fast_counter += 1
            self.fast_queue.append({
                'queue_number': new_queue_number,
                'vehicle_info': vehicle['vehicle_info'],
                'join_time': vehicle['join_time']
            })
        else:
            new_queue_number = f"T{self.slow_counter:03d}"
            self.slow_counter += 1
            self.slow_queue.append({
                'queue_number': new_queue_number,
                'vehicle_info': vehicle['vehicle_info'],
                'join_time': vehicle['join_time']
            })
            
        # 返回更新后的车辆信息
        return self.find_vehicle_by_queue_number(new_queue_number)
        
    def handle_fault_priority_scheduling(self, fault_pile_id: str, fault_queue: List[Dict]) -> Dict:
        """
        处理充电桩故障的优先级调度
        优先级调度：暂停等候区叫号服务，当其它同类型充电桩队列有空位时，优先为故障充电桩等候队列提供调度
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
        same_type_piles = [
            pile for pile_id, pile in self.charging_piles.items()
            if pile_id != fault_pile_id and 
               pile['charging_category'] == fault_pile['charging_category'] and
               pile['status'] != 'FAULT' and pile['status'] != '故障' and
               pile['status'] != 'OFFLINE' and pile['status'] != '离线'
        ]
        
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
            target_pile = min(same_type_piles, key=lambda p: len(p.get('queue_vehicles', [])))
            
            # 如果找到了可用的充电桩，将车辆添加到该充电桩的队列中
            if target_pile and len(target_pile.get('queue_vehicles', [])) < target_pile.get('queue_maxlen', 2):
                # 记录调度结果
                rescheduled_vehicles.append({
                    "vehicle": vehicle,
                    "target_pile": target_pile['pile_id']
                })
                
                # 将车辆添加到目标充电桩的队列中
                if 'queue_vehicles' not in target_pile:
                    target_pile['queue_vehicles'] = []
                target_pile['queue_vehicles'].append(vehicle)
                
        return {
            "status": True,
            "msg": f"已完成{len(rescheduled_vehicles)}辆车的优先级调度",
            "data": {
                "fault_pile_id": fault_pile_id,
                "rescheduled_vehicles": rescheduled_vehicles
            }
        }
        
    def handle_fault_time_order_scheduling(self, fault_pile_id: str, fault_queue: List[Dict]) -> Dict:
        """
        处理充电桩故障的时间顺序调度
        时间顺序调度：将其它同类型充电桩中尚未充电的车辆与故障队列中车辆合为一组，按照排队号码先后顺序重新调度
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
        same_type_piles = [
            pile for pile_id, pile in self.charging_piles.items()
            if pile_id != fault_pile_id and 
               pile['charging_category'] == fault_pile['charging_category'] and
               pile['status'] != 'FAULT' and pile['status'] != '故障' and
               pile['status'] != 'OFFLINE' and pile['status'] != '离线'
        ]
        
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
        for pile in same_type_piles:
            queue_vehicles = pile.get('queue_vehicles', [])
            if isinstance(queue_vehicles, list):
                # 过滤掉正在充电的车辆
                waiting_vehicles = [v for v in queue_vehicles if pile.get('connected_vehicle') is None or v['car_id'] != pile.get('connected_vehicle', {}).get('car_id')]
                all_waiting_vehicles.extend(waiting_vehicles)
                
        # 按照排队号码排序（假设排队号码格式为"X123"，其中X是类型，123是序号）
        all_waiting_vehicles.sort(key=lambda v: int(v.get('queue_number', '0')[1:]) if v.get('queue_number', '0')[1:].isdigit() else 0)
        
        # 清空所有同类型充电桩的队列
        for pile in same_type_piles:
            pile['queue_vehicles'] = []
            
        # 重新分配车辆到充电桩
        rescheduled_vehicles = []
        for vehicle in all_waiting_vehicles:
            # 寻找队列最短的充电桩
            target_pile = min(same_type_piles, key=lambda p: len(p.get('queue_vehicles', [])))
            
            if target_pile:
                # 记录调度结果
                rescheduled_vehicles.append({
                    "vehicle": vehicle,
                    "target_pile": target_pile['pile_id']
                })
                
                # 将车辆添加到目标充电桩的队列中
                if 'queue_vehicles' not in target_pile:
                    target_pile['queue_vehicles'] = []
                target_pile['queue_vehicles'].append(vehicle)
                
        return {
            "status": True,
            "msg": f"已完成{len(rescheduled_vehicles)}辆车的时间顺序调度",
            "data": {
                "fault_pile_id": fault_pile_id,
                "rescheduled_vehicles": rescheduled_vehicles
            }
        }
        
    def handle_pile_recovery(self, recovered_pile_id: str) -> Dict:
        """
        处理充电桩故障恢复的调度
        当充电桩故障恢复，若其它同类型充电桩中尚有车辆排队，则将其它同类型充电桩中尚未充电的车辆合为一组，按照排队号码先后顺序重新调度
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
        same_type_piles = [
            pile for pile_id, pile in self.charging_piles.items()
            if pile_id != recovered_pile_id and 
               pile['charging_category'] == recovered_pile['charging_category'] and
               pile['status'] != 'FAULT' and pile['status'] != '故障' and
               pile['status'] != 'OFFLINE' and pile['status'] != '离线'
        ]
        
        # 检查其他同类型充电桩是否有车辆排队
        has_waiting_vehicles = False
        for pile in same_type_piles:
            queue_vehicles = pile.get('queue_vehicles', [])
            if isinstance(queue_vehicles, list) and queue_vehicles:
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
        for pile in same_type_piles:
            queue_vehicles = pile.get('queue_vehicles', [])
            if isinstance(queue_vehicles, list):
                # 过滤掉正在充电的车辆
                waiting_vehicles = [v for v in queue_vehicles if pile.get('connected_vehicle') is None or v['car_id'] != pile.get('connected_vehicle', {}).get('car_id')]
                all_waiting_vehicles.extend(waiting_vehicles)
                
        # 添加恢复的充电桩到可用充电桩列表
        same_type_piles.append(recovered_pile)
        
        # 按照排队号码排序
        all_waiting_vehicles.sort(key=lambda v: int(v.get('queue_number', '0')[1:]) if v.get('queue_number', '0')[1:].isdigit() else 0)
        
        # 清空所有同类型充电桩的队列
        for pile in same_type_piles:
            pile['queue_vehicles'] = []
            
        # 重新分配车辆到充电桩
        rescheduled_vehicles = []
        for vehicle in all_waiting_vehicles:
            # 寻找队列最短的充电桩
            target_pile = min(same_type_piles, key=lambda p: len(p.get('queue_vehicles', [])))
            
            if target_pile:
                # 记录调度结果
                rescheduled_vehicles.append({
                    "vehicle": vehicle,
                    "target_pile": target_pile['pile_id']
                })
                
                # 将车辆添加到目标充电桩的队列中
                if 'queue_vehicles' not in target_pile:
                    target_pile['queue_vehicles'] = []
                target_pile['queue_vehicles'].append(vehicle)
                
        return {
            "status": True,
            "msg": f"充电桩{recovered_pile_id}恢复后，已完成{len(rescheduled_vehicles)}辆车的重新调度",
            "data": {
                "recovered_pile_id": recovered_pile_id,
                "rescheduled_vehicles": rescheduled_vehicles
            }
        }
        