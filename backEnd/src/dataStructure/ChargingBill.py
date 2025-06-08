from datetime import datetime
from typing import TypedDict, Optional
import uuid

class ChargingBill(TypedDict):
    """充电详单数据结构"""
    bill_id: str              # 详单编号
    create_time: str          # 详单生成时间
    pile_id: str             # 充电桩编号
    vehicle_id: str          # 车辆ID
    username: str            # 用户名
    charging_amount: float   # 充电电量
    charging_duration: float # 充电时长（分钟）
    start_time: str         # 启动时间
    end_time: str           # 停止时间
    charging_cost: float    # 充电费用
    service_cost: float     # 服务费用
    total_cost: float       # 总费用

def create_charging_bill(
    pile_id: str,
    vehicle_info: dict,
    charging_amount: float,
    charging_duration: float,
    start_time: float,
    end_time: float,
    charging_cost: float
) -> ChargingBill:
    """
    创建充电详单
    :param pile_id: 充电桩编号
    :param vehicle_info: 车辆信息
    :param charging_amount: 充电电量
    :param charging_duration: 充电时长（分钟）
    :param start_time: 开始时间戳
    :param end_time: 结束时间戳
    :param charging_cost: 充电费用
    :return: 充电详单
    """
    # 计算服务费用（充电费用的10%）
    service_cost = round(charging_cost * 0.1, 2)
    total_cost = round(charging_cost + service_cost, 2)

    return {
        'bill_id': str(uuid.uuid4()),
        'create_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pile_id': pile_id,
        'vehicle_id': vehicle_info['car_id'],
        'username': vehicle_info['username'],
        'charging_amount': round(charging_amount, 2),
        'charging_duration': round(charging_duration, 2),
        'start_time': datetime.fromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S'),
        'end_time': datetime.fromtimestamp(end_time).strftime('%Y-%m-%d %H:%M:%S'),
        'charging_cost': round(charging_cost, 2),
        'service_cost': service_cost,
        'total_cost': total_cost
    } 