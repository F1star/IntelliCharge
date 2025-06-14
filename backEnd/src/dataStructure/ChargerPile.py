import time
from enum import Enum
from typing import Dict, TypedDict, Any, Union, List, Optional
from datetime import datetime, time as dt_time
from collections import deque
from .ChargingBill import create_charging_bill


class ChargingStatus(Enum):
    """充电桩状态枚举"""
    IDLE = "空闲"        # 空闲状态
    CHARGING = "充电中"  # 充电中状态
    FAULT = "故障"       # 故障状态
    OFFLINE = "离线"     # 离线状态

# 定义充电账单的数据结构
class ChargingBill(TypedDict, total=False):
    vehicle_id: str
    charging_duration: float
    energy_consumed: float
    cost: float
    error: str

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
        self.charging_category = charging_category
        
        if charging_category == 'F':
            self.power = 30  # 单位：度/每小时
        elif charging_category == 'T':
            self.power = 7
        else:
            self.power = 0

        self.status = ChargingStatus.IDLE
        self.connected_vehicle = None
        self.start_time = None
        self.total_energy_delivered = 0.0
        self.total_earnings = 0.0
        self.charge_queue = deque(maxlen=2)
        self.charging_bills = []  # 存储充电详单
        self.current_charging_amount = 0.0  # 当前充电量
        
        # 管理员统计信息
        self.charging_count = 0  # 充电次数
        self.total_charging_duration = 0.0  # 总充电时长（分钟）

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

    def join_queue(self, vehicle: dict) -> Union[str, ErrorResponse]:
        """
        车辆加入充电队列
        :param vehicle_id: 车辆唯一标识
        :return: 操作结果信息
        """
        vehicle_id = vehicle['car_id']
        if self.status == ChargingStatus.FAULT:
            return {"error": f"操作失败: 充电桩{self.pile_id}处于故障状态"}
        
        if vehicle_id in self.charge_queue:
            return {"error": f"操作失败: 车辆[{vehicle_id}]已在队列中"}
        
        if len(self.charge_queue) >= 2:
            return {"error": f"操作失败: 充电桩{self.pile_id}队列已满"}
        
        self.charge_queue.append(vehicle)
        
        # 如果充电桩空闲且队列不为空，开始充电
        if self.status == ChargingStatus.IDLE and len(self.charge_queue) > 0:
            return self.connect_vehicle(self.charge_queue[0])
        
        print(self.charge_queue)
        
        return f"车辆[{vehicle_id}]已加入充电桩[{self.pile_id}]的等待队列"

    def leave_queue(self, vehicle: dict) -> Union[str, ErrorResponse]:
        """
        车辆离开充电队列
        :param vehicle_id: 车辆唯一标识
        :return: 操作结果信息
        """
        vehicle_id = vehicle['car_id']
        if vehicle not in self.charge_queue:
            return {"error": f"操作失败: 车辆[{vehicle_id}]不在队列中"}
        
        self.charge_queue.remove(vehicle)
        return f"车辆[{vehicle_id}]已离开充电桩[{self.pile_id}]的等待队列"

    def connect_vehicle(self, vehicle: dict) -> Union[str, ErrorResponse]:
        """
        车辆连接充电桩
        :param vehicle_id: 车辆唯一标识
        :return: 操作结果信息
        """
        if self.status != ChargingStatus.IDLE:
            return {"error": f"操作失败: 充电桩{self.pile_id}当前状态[{self.status.value}]不可用"}
        vehicle_id = vehicle['car_id']
        if vehicle not in self.charge_queue:
            return {"error": f"操作失败: 车辆[{vehicle_id}]不在队列中"}
        
        if self.charge_queue[0] != vehicle:
            return {"error": f"操作失败: 车辆[{vehicle_id}]不是队列中的第一辆车"}
        
        self.connected_vehicle = vehicle
        self.status = ChargingStatus.CHARGING
        self.start_time = time.time()
        self.current_charging_amount = 0.0  # 重置当前充电量
        return f"车辆[{vehicle_id}]已成功连接充电桩[{self.pile_id}]"
    
    def disconnect_vehicle(self, is_auto_end: bool = False) -> Union[Dict, ErrorResponse]:
        """断开车辆连接并生成充电详单"""
        if self.status != ChargingStatus.CHARGING:
            return {"error": f"操作失败: 充电桩{self.pile_id}未处于充电状态"}
        
        if self.start_time is None:
            return {"error": f"系统错误: 充电桩{self.pile_id}未记录充电开始时间"}
        
        if not self.connected_vehicle:
            return {"error": f"系统错误: 充电桩{self.pile_id}未连接车辆"}
        
        if is_auto_end:
            end_time = self.start_time + self.connected_vehicle['charging_amount'] / self.power * 3600
        else:
            end_time = time.time()

        start_time = self.start_time
        charging_duration = (end_time - start_time) / 60  # 转换为分钟
        
        # 计算总电量和总费用（考虑分时电价）
        energy_consumed, cost = self._calculate_charging_cost(start_time, end_time)
        
        # 更新统计数据
        self.total_energy_delivered += energy_consumed
        self.total_earnings += cost
        
        # 更新管理员统计信息
        self.charging_count += 1
        self.total_charging_duration += charging_duration
        
        # 生成充电详单
        bill = create_charging_bill(
            pile_id=self.pile_id,
            vehicle_info=self.connected_vehicle,
            charging_amount=energy_consumed,
            charging_duration=charging_duration,
            start_time=start_time,
            end_time=end_time,
            charging_cost=cost
        )
        self.charging_bills.append(bill)
        
        # 保存当前车辆信息用于返回
        vehicle = self.connected_vehicle
        
        # 重置状态
        self.connected_vehicle = None
        self.status = ChargingStatus.IDLE
        self.start_time = None
        self.current_charging_amount = 0.0
        
        # 从队列中移除已充电的车辆
        if vehicle in self.charge_queue:
            self.charge_queue.remove(vehicle)
        
        # 如果队列中还有车辆，自动开始下一辆车的充电
        if len(self.charge_queue) > 0:
            self.connect_vehicle(self.charge_queue[0])
        
        return {
            "status": "success",
            "message": f"车辆[{vehicle['car_id']}]已完成充电",
            "bill": bill
        }
    

    def fault_vehicle(self) -> Union[Dict, ErrorResponse]:
        """故障断开车辆连接并生成充电详单"""
        
        if self.start_time is None:
            return {"error": f"系统错误: 充电桩{self.pile_id}未记录充电开始时间"}
        
        if not self.connected_vehicle:
            return {"error": f"系统错误: 充电桩{self.pile_id}未连接车辆"}
        
        end_time = time.time()
        start_time = self.start_time
        charging_duration = (end_time - start_time) / 60  # 转换为分钟
        
        # 计算总电量和总费用（考虑分时电价）
        energy_consumed, cost = self._calculate_charging_cost(start_time, end_time)
        
        # 更新统计数据
        self.total_energy_delivered += energy_consumed
        self.total_earnings += cost
        
        # 更新管理员统计信息
        self.charging_count += 1
        self.total_charging_duration += charging_duration
        
        # 生成充电详单
        bill = create_charging_bill(
            pile_id=self.pile_id,
            vehicle_info=self.connected_vehicle,
            charging_amount=energy_consumed,
            charging_duration=charging_duration,
            start_time=start_time,
            end_time=end_time,
            charging_cost=cost
        )
        self.charging_bills.append(bill)
        
        # 保存当前车辆信息用于返回
        vehicle = self.connected_vehicle
        
        # 重置状态
        self.connected_vehicle = None
        self.start_time = None
        self.current_charging_amount = 0.0
        
        return {
            "status": "success",
            "message": f"车辆[{vehicle['car_id']}]已完成故障断开充电",
            "bill": bill
        }

    def get_queue_status(self) -> Dict[str, Any]:
        """获取队列状态信息"""
        return {
            "pile_id": self.pile_id,
            "pile_name": f"充电桩{self.pile_id}",
            "waiting_count": len(self.charge_queue),
            "waiting_vehicles": [
                {
                    "id": vehicle["car_id"],
                    "name": vehicle.get("name", "未知车辆"),
                    "plateNumber": vehicle.get("plate_number", "未知车牌"),
                    "userId": vehicle.get("user_id")
                }
                for vehicle in self.charge_queue
            ],
            "current_vehicle": {
                "id": self.connected_vehicle["car_id"],
                "name": self.connected_vehicle.get("name", "未知车辆"),
                "plateNumber": self.connected_vehicle.get("plate_number", "未知车牌"),
                "userId": self.connected_vehicle.get("user_id")
            } if self.connected_vehicle else None
        }

    def is_user_vehicle(self, vehicle: Optional[Dict], user_id: str) -> bool:
        """
        检查车辆是否属于指定用户
        :param vehicle: 车辆信息
        :param user_id: 用户ID
        :return: 是否属于该用户
        """
        if not vehicle:
            return False
        return vehicle.get("user_id") == user_id

    def can_user_operate(self, user_id: str, is_admin: bool = False) -> bool:
        """
        检查用户是否有权限操作此充电桩
        :param user_id: 用户ID
        :param is_admin: 是否是管理员
        :return: 是否有权限
        """
        if is_admin:
            return True
        return self.is_user_vehicle(self.connected_vehicle, user_id)

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
    
    def set_fault(self) -> Dict:
        """设置充电桩为故障状态，并处理正在充电的车辆"""
        # 如果充电桩已经是故障或离线状态，不做处理
        if self.status == ChargingStatus.FAULT:
            return {
                "status": False,
                "msg": f"充电桩{self.pile_id}已处于故障状态",
                "data": None
            }
            
        if self.status == ChargingStatus.OFFLINE:
            return {
                "status": False,
                "msg": f"充电桩{self.pile_id}处于离线状态，无法设置故障",
                "data": None
            }
            
        # 保存原始状态
        original_status = self.status
        
        # 设置为故障状态
        self.status = ChargingStatus.FAULT
        
        # 如果有车辆正在充电，生成充电详单并断开连接
        bill_data = None
        if original_status == ChargingStatus.CHARGING and self.connected_vehicle:
            result = self.fault_vehicle()
            if isinstance(result, dict) and 'bill' in result:
                bill_data = result['bill']
                
        # 获取当前队列中的车辆
        queue_vehicles = list(self.charge_queue)
                
        return {
            "status": True,
            "msg": f"充电桩{self.pile_id}已设置为故障状态",
            "original_status": original_status.value,
            "queue": queue_vehicles,
            "bill": bill_data
        }
        
    def repair(self) -> Dict:
        """修复充电桩故障"""
        # 如果充电桩不是故障状态，不做处理
        if self.status != ChargingStatus.FAULT:
            return {
                "status": False,
                "msg": f"充电桩{self.pile_id}不处于故障状态，当前状态为{self.status.value}",
                "data": None
            }
            
        # 设置为空闲状态
        self.status = ChargingStatus.IDLE
        
        return {
            "status": True,
            "msg": f"充电桩{self.pile_id}已修复",
            "data": {
                "pile_id": self.pile_id,
                "status": self.status.value
            }
        }
        
    def remove_all_vehicles(self) -> List[Dict]:
        """移除所有排队车辆（用于故障调度）"""
        vehicles = list(self.charge_queue)
        self.charge_queue.clear()
        return vehicles

    def get_status(self) -> Dict[str, Any]:
        """获取当前状态信息"""
        return {
            "pile_id": self.pile_id,
            "power": self.power,
            "status": self.status.value,
            "connected_vehicle": self.connected_vehicle,
            "charge_queue": list(self.charge_queue),
            "charging_category": self.charging_category,
            "queue_length": len(self.charge_queue),
            "total_energy": round(self.total_energy_delivered, 2),
            "total_earnings": round(self.total_earnings, 2),
            "charging_bills": self.charging_bills,
            "waiting_count": len(self.charge_queue)
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
    
    def calculate_charging_time(self, charging_amount: float) -> float:
        """
        计算指定充电量所需的充电时间（小时）
        :param charging_amount: 充电量（kWh）
        :return: 充电时间（小时）
        """
        return charging_amount / self.power

    def calculate_total_time(self, vehicle_info: dict) -> float:
        """
        计算指定车辆的总等待时间（包括队列中其他车辆的充电时间）
        :param vehicle_info: 车辆信息
        :return: 总等待时间（小时）
        """
        total_time = 0
        # 计算队列中其他车辆的充电时间
        for vehicle in self.charge_queue:
            if vehicle != vehicle_info:
                total_time += self.calculate_charging_time(vehicle['charging_amount'])
        # 加上自己的充电时间
        total_time += self.calculate_charging_time(vehicle_info['charging_amount'])
        return total_time

    def get_available_slots(self) -> int:
        """
        获取当前可用的充电位数量
        :return: 可用充电位数量
        """
        maxlen = self.charge_queue.maxlen or 0
        return maxlen - len(self.charge_queue)

    def get_queue_info(self) -> dict:
        """
        获取队列信息，用于调度决策
        :return: 队列信息字典
        """
        return {
            'pile_id': self.pile_id,
            'charging_category': self.charging_category,
            'power': self.power,
            'available_slots': self.get_available_slots(),
            'queue_length': len(self.charge_queue),
            'queue_vehicles': list(self.charge_queue),
            'connected_vehicle': self.connected_vehicle,
            'status': self.status.value
        }

    def get_charging_bills(self) -> List[Dict]:
        """获取充电详单列表"""
        return self.charging_bills

    def check_charging_status(self) -> Optional[Union[Dict[str, Any], ErrorResponse]]:
        """
        检查当前充电状态，如果达到请求充电量则自动断开
        :return: 如果达到请求量返回断开结果，否则返回None
        """
        if self.status != ChargingStatus.CHARGING or not self.connected_vehicle or self.start_time is None:
            return None
            
        # 使用调度器的时间函数，自动考虑时间加速和模拟时间
        from ..component.Server.controller import scheduler
            
        current_time = scheduler.get_current_time()  # 获取当前模拟时间
        
        # 计算充电时长
        if isinstance(self.start_time, (int, float)):  # 确保start_time是数值类型
            elapsed_time = (current_time - self.start_time) / 3600.0  # 转换为小时
        else:
            elapsed_time = 0.0
        self.current_charging_amount = self.power * elapsed_time
        
        # 检查是否达到请求充电量
        requested_amount = self.connected_vehicle.get('charging_amount', 0)
        if requested_amount > 0 and self.current_charging_amount >= requested_amount:
            print(f"车辆[{self.connected_vehicle['car_id']}]已达到请求充电量{requested_amount}度，自动断开")
            return self.disconnect_vehicle(is_auto_end=True)
            
        return None

    def modify_charging_request(self, charging_amount: float) -> Union[Dict[str, Any], ErrorResponse]:
        """
        修改当前充电请求
        :param charging_amount: 新的充电量
        :return: 操作结果
        """
        if self.status != ChargingStatus.CHARGING:
            return {"error": f"操作失败: 充电桩{self.pile_id}未处于充电状态"}
        
        if not self.connected_vehicle:
            return {"error": f"操作失败: 充电桩{self.pile_id}未连接车辆"}
        
        # 计算当前已充电量
        current_time = time.time()
        elapsed_time = (current_time - self.start_time) / 3600.0  # 转换为小时
        self.current_charging_amount = self.power * elapsed_time
        
        # 如果新的充电量小于已充电量，则直接断开充电
        if charging_amount <= self.current_charging_amount:
            print(f"新的充电量{charging_amount}度小于已充电量{self.current_charging_amount}度，自动断开")
            return self.disconnect_vehicle()
        
        # 获取旧的充电量（如果存在）
        old_amount_str = ""
        try:
            if self.connected_vehicle.get('charging_amount'):
                old_amount_str = f"从{self.connected_vehicle.get('charging_amount')}度"
        except Exception:
            pass
            
        # 更新充电请求
        self.connected_vehicle['charging_amount'] = charging_amount
        
        return {
            "status": "success",
            "message": f"充电请求已{old_amount_str}修改为{charging_amount}度",
            "data": {
                "pile_id": self.pile_id,
                "vehicle_id": self.connected_vehicle['car_id'],
                "charging_amount": charging_amount,
                "current_charging_amount": round(self.current_charging_amount, 2)
            }
        }

    def get_current_charging_amount(self) -> float:
        """获取当前已充电量"""
        if self.status != ChargingStatus.CHARGING or not self.connected_vehicle or self.start_time is None:
            return 0.0
            
        # 计算当前已充电量，使用调度器的时间函数
        from ..component.Server.controller import scheduler
        current_time = scheduler.get_current_time()  # 获取当前模拟时间
        
        if isinstance(self.start_time, (int, float)):  # 确保start_time是数值类型
            elapsed_time = (current_time - self.start_time) / 3600.0  # 转换为小时
        else:
            elapsed_time = 0.0
        return self.power * elapsed_time

if __name__ == "__main__":
    # 创建充电桩实例（7.5kW功率）
    pile = ChargingPile("A", "T")

    # 测试车辆数据
    test_vehicles = [
        {
            "car_id": "V-001",
            "name": "测试车辆1",
            "plate_number": "京A12345",
            "user_id": "user1"
        },
        {
            "car_id": "V-002",
            "name": "测试车辆2",
            "plate_number": "京B67890",
            "user_id": "user2"
        },
        {
            "car_id": "V-003",
            "name": "测试车辆3",
            "plate_number": "京C13579",
            "user_id": "user3"
        }
    ]

    print(pile.join_queue(test_vehicles[0]))  # 第一辆车加入
    print(pile.join_queue(test_vehicles[1]))  # 第二辆车加入
    print(pile.join_queue(test_vehicles[2]))  # 队列已满，会返回错误信息

    # 查看队列状态
    status = pile.get_queue_status()
    print(status)  # 显示队列长度、车辆列表和当前充电车辆

    # 车辆离开队列
    print(pile.leave_queue(test_vehicles[1]))  # 第二辆车离开队列

    # 查看队列状态
    status = pile.get_queue_status()
    print(status)

    # 模拟充电过程（这里用sleep代替实际充电）
    time.sleep(10)  # 充电10秒

    # 停止充电并获取账单
    bill = pile.disconnect_vehicle()
    if isinstance(bill, dict) and 'error' not in bill:
        print(f"充电账单: 时长={bill.get('charging_duration', 0)}秒, "
              f"电量={bill.get('energy_consumed', 0)}度, "
              f"费用={bill.get('cost', 0)}元")
    else:
        print(f"获取账单失败: {bill.get('error', '未知错误')}")

    # 查询当前电价（根据当前时间）
    current_rate = pile.get_current_rate()
    print(f"当前电价: {current_rate}元/度")

    # 查询充电桩状态
    status = pile.get_status()
    print(f"充电桩状态: {status}")