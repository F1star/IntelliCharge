__all__ = ['blueprint']
from flask import Blueprint, request, jsonify
import pymysql
from ...dataStructure.User import *
from ...dataStructure.WaitingQueue import Queue
from ...dataStructure.ChargerPile import ChargingPile
from ...dataStructure.Scheduler import Scheduler
from flask_cors import CORS

blueprint = Blueprint('server', __name__)

# 创建全局队列实例
waiting_queue = Queue()

# 创建充电桩实例
charging_piles = {
    'A': ChargingPile('A', 'F'),  # 快充桩A
    'B': ChargingPile('B', 'F'),  # 快充桩B
    'C': ChargingPile('C', 'F'),  # 快充桩C
    'D': ChargingPile('D', 'T'),  # 慢充桩D
    'E': ChargingPile('E', 'T'),  # 慢充桩E
    'F': ChargingPile('F', 'T'),  # 慢充桩F
}

# 注册充电桩信息到队列
for pile in charging_piles.values():
    waiting_queue.register_charging_pile(pile.get_queue_info())

# 创建并启动调度器
scheduler = Scheduler(waiting_queue, charging_piles)
scheduler.start()

@blueprint.route('/', methods=['POST', 'GET'])
async def index():
    return "welcome to use server system"

@blueprint.route('/queue/status', methods=['GET'])
async def get_queue_status():
    """获取队列状态"""
    try:
        status = waiting_queue.get_queue_status()
        return jsonify({
            "status": True,
            "msg": "获取成功",
            "data": status
        })
    except Exception as e:
        print("Error getting queue status:", e)
        return jsonify({
            "status": False,
            "msg": "获取队列状态失败",
            "data": None
        })

@blueprint.route('/queue/join', methods=['POST'])
async def join_queue():
    """加入等候队列"""
    print("receive req for join queue", request.get_json())
    data = request.get_json()
    
    try:
        # 检查队列是否已满
        if waiting_queue.is_full():
            return jsonify({
                "status": False,
                "msg": "等候区已满",
                "data": None
            })

        # 准备车辆信息
        vehicle_info = {
            'username': data['username'],
            'car_id': data['carId'],
            'charging_amount': data['chargingAmount']
        }

        # 添加到队列
        queue_number = waiting_queue.add_vehicle(
            data['chargeType'],
            vehicle_info
        )

        return jsonify({
            "status": True,
            "msg": "加入队列成功",
            "data": {
                "queue_number": queue_number
            }
        })

    except Exception as e:
        print("Error joining queue:", e)
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/queue/leave', methods=['POST'])
async def leave_queue():
    """离开等候队列"""
    print("receive req for leave queue", request.get_json())
    data = request.get_json()
    queue_number = data.get('queue_number')

    try:
        vehicle = waiting_queue.remove_vehicle(queue_number)
        if vehicle:
            return jsonify({
                "status": True,
                "msg": "离开队列成功",
                "data": vehicle
            })
        else:
            return jsonify({
                "status": False,
                "msg": "未找到该排队号码",
                "data": None
            })
    except Exception as e:
        print("Error leaving queue:", e)
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/pile/status', methods=['GET'])
async def get_pile_status():
    """获取所有充电桩状态"""
    try:
        status = {
            pile_id: pile.get_status()
            for pile_id, pile in charging_piles.items()
        }
        return jsonify({
            "status": True,
            "msg": "获取成功",
            "data": status
        })
    except Exception as e:
        print("Error getting pile status:", e)
        return jsonify({
            "status": False,
            "msg": "获取充电桩状态失败",
            "data": None
        })

