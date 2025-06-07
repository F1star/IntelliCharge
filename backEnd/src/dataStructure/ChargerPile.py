import time
from enum import Enum
from typing import Dict, TypedDict, Any, Union, List
from datetime import datetime, time as dt_time
from collections import deque


class ChargingStatus(Enum):
    """充电桩状态枚举"""
    IDLE = "空闲"        # 空闲状态
    CHARGING = "充电中"  # 充电中状态
    FAULT = "故障"       # 故障状态
    OFFLINE = "离线"     # 离线状态

# 定义充电账单的数据结构
class ChargingBill(TypedDict):
    vehicle_id: str
    charging_duration: float
    energy_consumed: float
    cost: float

# 定义错误响应的数据结构
class ErrorResponse(TypedDict):
    error: str

class ChargingPile:
    def __init__(self, pile_id: str, charging_category: str):
        """
        初始化充电桩
        :param pile_id: 充电桩唯一标识
        :param charging_category: 充电桩类型（F:快充, T:慢充）
        """
        self.pile_id = pile_id
        
        if charging_category == 'F':
            self.power = 30  # 单位：度/每小时
        elif charging_category == 'T':
            self.power = 7
        else:
            self.power = 0

        self.status = ChargingStatus.IDLE
        self.connected_vehicle = None
        self.start_time = None
        self.total_energy_delivered = 0.0  # 累计充电量(度)
        self.total_earnings = 0.0  # 累计收益(元)
        self.charge_queue = deque(maxlen=2)  # 最多容纳2个车位的队列

        self.rate_periods = [
            # 谷时(0.4元/度): 23:00~次日7:00
            (dt_time(23, 0), dt_time(7, 0), 0.4),
            
            # 平时(0.7元/度): 7:00~10:00, 15:00~18:00, 21:00~23:00
            (dt_time(7, 0), dt_time(10, 0), 0.7),
            (dt_time(15, 0), dt_time(18, 0), 0.7),
            (dt_time(21, 0), dt_time(23, 0), 0.7),
            
            # 峰时(1.0元/度): 10:00~15:00, 18:00~21:00
            (dt_time(10, 0), dt_time(15, 0), 1.0),
            (dt_time(18, 0), dt_time(21, 0), 1.0),
        ]

    def join_queue(self, vehicle_id: str) -> Union[str, ErrorResponse]:
        """
        车辆加入充电队列
        :param vehicle_id: 车辆唯一标识
        :return: 操作结果信息
        """
        if self.status == ChargingStatus.FAULT:
            return {"error": f"操作失败: 充电桩{self.pile_id}处于故障状态"}
        
        if vehicle_id in self.charge_queue:
            return {"error": f"操作失败: 车辆[{vehicle_id}]已在队列中"}
        
        if len(self.charge_queue) >= 2:
            return {"error": f"操作失败: 充电桩{self.pile_id}队列已满"}
        
        self.charge_queue.append(vehicle_id)
        
        # 如果充电桩空闲且队列不为空，开始充电
        if self.status == ChargingStatus.IDLE and len(self.charge_queue) > 0:
            return self.connect_vehicle(self.charge_queue[0])
        
        return f"车辆[{vehicle_id}]已加入充电桩[{self.pile_id}]的等待队列"

    def leave_queue(self, vehicle_id: str) -> Union[str, ErrorResponse]:
        """
        车辆离开充电队列
        :param vehicle_id: 车辆唯一标识
        :return: 操作结果信息
        """
        if vehicle_id not in self.charge_queue:
            return {"error": f"操作失败: 车辆[{vehicle_id}]不在队列中"}
        
        self.charge_queue.remove(vehicle_id)
        return f"车辆[{vehicle_id}]已离开充电桩[{self.pile_id}]的等待队列"

    def connect_vehicle(self, vehicle_id: str) -> Union[str, ErrorResponse]:
        """
        车辆连接充电桩
        :param vehicle_id: 车辆唯一标识
        :return: 操作结果信息
        """
        if self.status != ChargingStatus.IDLE:
            return {"error": f"操作失败: 充电桩{self.pile_id}当前状态[{self.status.value}]不可用"}
        
        if vehicle_id not in self.charge_queue:
            return {"error": f"操作失败: 车辆[{vehicle_id}]不在队列中"}
        
        if self.charge_queue[0] != vehicle_id:
            return {"error": f"操作失败: 车辆[{vehicle_id}]不是队列中的第一辆车"}
        
        self.connected_vehicle = vehicle_id
        self.status = ChargingStatus.CHARGING
        self.start_time = time.time()
        return f"车辆[{vehicle_id}]已成功连接充电桩[{self.pile_id}]"
    
    def disconnect_vehicle(self) -> Union[ChargingBill, ErrorResponse]:
        """断开车辆连接并计算费用（考虑分时电价）"""
        if self.status != ChargingStatus.CHARGING:
            return {"error": f"操作失败: 充电桩{self.pile_id}未处于充电状态"}
        
        if self.start_time is None:
            return {"error": f"系统错误: 充电桩{self.pile_id}未记录充电开始时间"}
        
        end_time = time.time()
        start_time = self.start_time
        charging_duration = end_time - start_time
        
        # 计算总电量和总费用（考虑分时电价）
        energy_consumed, cost = self._calculate_charging_cost(start_time, end_time)
        
        # 更新统计数据
        self.total_energy_delivered += energy_consumed
        self.total_earnings += cost
        
        # 重置状态
        vehicle_id = self.connected_vehicle or "未知车辆"
        self.connected_vehicle = None
        self.status = ChargingStatus.IDLE
        self.start_time = None
        
        # 从队列中移除已充电的车辆
        if vehicle_id in self.charge_queue:
            self.charge_queue.remove(vehicle_id)
        
        # 如果队列中还有车辆，自动开始下一辆车的充电
        if len(self.charge_queue) > 0:
            self.connect_vehicle(self.charge_queue[0])
        
        # 返回明确类型的充电账单
        return {
            "vehicle_id": vehicle_id,
            "charging_duration": round(charging_duration, 2),
            "energy_consumed": round(energy_consumed, 2),
            "cost": round(cost, 2)
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态信息"""
        return {
            "queue_length": len(self.charge_queue),
            "queue_vehicles": list(self.charge_queue),
            "current_vehicle": self.connected_vehicle
        }

    def _get_current_rate(self, timestamp: float) -> float:
        """
        根据时间戳获取当前电价
        :param timestamp: 时间戳
        :return: 当前电价(元/度)
        """
        dt = datetime.fromtimestamp(timestamp)
        current_time = dt.time()
        
        # 处理跨天的谷时时段(23:00~24:00)
        if current_time >= dt_time(23, 0):
            return 0.4
        
        # 处理跨天的谷时时段(00:00~07:00)
        if current_time < dt_time(7, 0):
            return 0.4
        
        # 检查其他时段
        for start, end, rate in self.rate_periods:
            if start <= current_time < end:
                return rate
        
        # 默认返回谷时电价
        return 0.4

    
    def _calculate_charging_cost(self, start: float, end: float) -> tuple:
        """
        计算充电费用（考虑分时电价）
        :param start: 开始时间戳
        :param end: 结束时间戳
        :return: (总电量, 总费用)
        """
        total_energy = 0.0
        total_cost = 0.0
        current = start
        
        # 将充电时间分成小段计算（每段最多1分钟）
        while current < end:
            # 确定当前时间段的结束点（最多1分钟）
            segment_end = min(current + 60, end)  # 60秒=1分钟
            
            # 计算时间段长度（小时）
            segment_duration = (segment_end - current) / 3600.0
            
            # 获取当前电价
            current_rate = self._get_current_rate(current)
            
            # 计算当前时间段的电量（度）和费用（元）
            segment_energy = self.power * segment_duration
            segment_cost = segment_energy * current_rate
            
            total_energy += segment_energy
            total_cost += segment_cost
            
            # 移动到下一个时间段
            current = segment_end
        
        return total_energy, total_cost
    
    def set_fault(self):
        """设置充电桩为故障状态"""
        if self.status == ChargingStatus.CHARGING:
            self.disconnect_vehicle()
        self.status = ChargingStatus.FAULT
        return f"充电桩[{self.pile_id}]已设置为故障状态"
    
    def repair(self):
        """修复充电桩"""
        if self.status == ChargingStatus.FAULT:
            self.status = ChargingStatus.IDLE
            return f"充电桩[{self.pile_id}]已修复"
        return f"操作失败: 充电桩[{self.pile_id}]当前不在故障状态"
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态信息"""
        return {
            "pile_id": self.pile_id,
            "power": self.power,
            "status": self.status.value,
            "connected_vehicle": self.connected_vehicle,
            "total_energy": round(self.total_energy_delivered, 2),
            "total_earnings": round(self.total_earnings, 2)
        }
    
    def update_charging_rate(self, new_rate: float):
        """更新充电费率"""
        self.charging_rate = new_rate
        return f"充电桩[{self.pile_id}]费率已更新为{new_rate}元/度"
    
    def get_current_rate(self) -> float:
        """获取当前电价"""
        if self.status != ChargingStatus.CHARGING or self.start_time is None:
            return self._get_current_rate(time.time())
        return self._get_current_rate(time.time())
    
if __name__ == "__main__":
    # 创建充电桩实例（7.5kW功率）
    pile = ChargingPile("A", "T")

    print(pile.join_queue("V-001"))  # 第一辆车加入
    print(pile.join_queue("V-002"))  # 第二辆车加入
    print(pile.join_queue("V-003"))  # 队列已满，会返回错误信息

    # 查看队列状态
    status = pile.get_queue_status()
    print(status)  # 显示队列长度、车辆列表和当前充电车辆

    # 车辆离开队列
    print(pile.leave_queue("V-002"))  # 第二辆车离开队列

    # 查看队列状态
    status = pile.get_queue_status()
    print(status)

    # 模拟充电过程（这里用sleep代替实际充电）
    time.sleep(10)  # 充电10秒

    # 停止充电并获取账单
    bill = pile.disconnect_vehicle()

    print(f"充电账单: 时长={bill['charging_duration']}秒, "
        f"电量={bill['energy_consumed']}度, "
        f"费用={bill['cost']}元")

    # 查询当前电价（根据当前时间）
    current_rate = pile.get_current_rate()
    print(f"当前电价: {current_rate}元/度")

    # 查询充电桩状态
    status = pile.get_status()
    print(f"充电桩状态: {status}")