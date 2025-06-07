from ChargerPile import ChargingPile

class Queue:
    def __init__(self):
        self.fast_queue = []  # 快充队列
        self.slow_queue = []  # 慢充队列
        self.fast_counter = 1  # 快充序号计数器
        self.slow_counter = 1  # 慢充序号计数器
        self.max_capacity = 6  # 最大容量

    def is_full(self):
        """检查等候区是否已满"""
        return len(self.fast_queue) + len(self.slow_queue) >= self.max_capacity

    def add_vehicle(self, charge_type, vehicle_info):
        """
        添加车辆到等待队列
        :param charge_type: 'F' 表示快充，'T' 表示慢充
        :param vehicle_info: 车辆信息字典，包含充电量、充电功率等
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

    def remove_vehicle(self, queue_number):
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

    def get_queue_status(self):
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
        