from typing import List, Dict, Any, Tuple
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

        # 获取待调度的车辆
        fast_vehicles = self.fast_queue[:sum(pile['available_slots'] for pile in fast_piles)]
        slow_vehicles = self.slow_queue[:sum(pile['available_slots'] for pile in slow_piles)]

        # 执行调度
        fast_allocation = self.find_optimal_allocation(fast_vehicles, fast_piles)
        slow_allocation = self.find_optimal_allocation(slow_vehicles, slow_piles)

        # 从队列中移除已调度的车辆
        for vehicle, _ in fast_allocation:
            self.fast_queue.remove(vehicle)
        for vehicle, _ in slow_allocation:
            self.slow_queue.remove(vehicle)

        return {
            'fast_allocation': fast_allocation,
            'slow_allocation': slow_allocation
        }

    def is_full(self):
        """检查等候区是否已满"""
        return len(self.fast_queue) + len(self.slow_queue) >= self.max_capacity

    def add_vehicle(self, charge_type: str, vehicle_info: Dict) -> str:
        """
        添加车辆到等待队列
        :param charge_type: 'F' 表示快充，'T' 表示慢充
        :param vehicle_info: 车辆信息字典
        :return: 分配的排队号码
        """
        if self.is_full():
            raise Exception("等候区已满")

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

    def remove_vehicle(self, queue_number: str) -> Dict | None:
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

    def calculate_waiting_time(self, charge_type, vehicle_info):
        """
        计算指定车辆的预计等待时间
        :param charge_type: 'F' 或 'T'
        :param vehicle_info: 车辆信息
        :return: 预计等待时间（分钟）
        """
        waiting_time = 0
        if charge_type == 'F':
            for vehicle in self.fast_queue:
                waiting_time += vehicle['vehicle_info']['charging_time']
        else:
            for vehicle in self.slow_queue:
                waiting_time += vehicle['vehicle_info']['charging_time']
        
        # 加上自己的充电时间
        charging_time = vehicle_info['charging_amount'] / vehicle_info['charging_power']
        return waiting_time + charging_time
        