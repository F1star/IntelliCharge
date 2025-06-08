__all__ = ['blueprint']
from flask import Blueprint, request, jsonify
import pymysql
from ...dataStructure.User import *
from ...dataStructure.WaitingQueue import Queue
from ...dataStructure.ChargerPile import ChargingPile, ChargingStatus
from ...dataStructure.Scheduler import Scheduler
from flask_cors import CORS
import time

blueprint = Blueprint('server', __name__)

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        password='root',
        charset='utf8',
        database='pile'
    )

def save_charging_bill(bill: dict):
    """保存充电详单到数据库"""
    conn = None
    cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        sql = """
            INSERT INTO charging_bills (
                bill_id, create_time, pile_id, vehicle_id, username,
                charging_amount, charging_duration, start_time, end_time,
                charging_cost, service_cost, total_cost
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
        """
        cursor.execute(sql, (
            bill['bill_id'],
            bill['create_time'],
            bill['pile_id'],
            bill['vehicle_id'],
            bill['username'],
            bill['charging_amount'],
            bill['charging_duration'],
            bill['start_time'],
            bill['end_time'],
            bill['charging_cost'],
            bill['service_cost'],
            bill['total_cost']
        ))
        conn.commit()
    except Exception as e:
        print(f"保存充电详单失败: {str(e)}")
        if conn:
            conn.rollback()
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

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

# 创建并启动调度器，传入保存账单的函数
scheduler = Scheduler(waiting_queue, charging_piles, save_charging_bill)
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
        print("Error joining queue:", str(e))
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
        status = {}
        for pile_id, pile in charging_piles.items():
            pile_status = pile.get_status()
            
            # 使用安全方法获取当前充电量
            current_charging_amount = pile.get_current_charging_amount()
            pile_status['current_charging_amount'] = round(current_charging_amount, 2)
            
            status[pile_id] = pile_status
            
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

@blueprint.route('/pile/disconnect', methods=['POST'])
async def disconnect_vehicle():
    """断开车辆连接并生成充电详单"""
    data = request.get_json()
    pile_id = data.get('pile_id')
    
    try:
        if pile_id not in charging_piles:
            return jsonify({
                "status": False,
                "msg": "充电桩不存在",
                "data": None
            })
        
        result = charging_piles[pile_id].disconnect_vehicle()
        if isinstance(result, dict) and 'error' in result:
            return jsonify({
                "status": False,
                "msg": result['error'],
                "data": None
            })
        
        # 保存充电详单到数据库
        if result.get('bill'):
            save_charging_bill(result['bill'])
        
        return jsonify({
            "status": True,
            "msg": result['message'],
            "data": result.get('bill')
        })
        
    except Exception as e:
        print("Error disconnecting vehicle:", str(e))
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/pile/modify_charging', methods=['POST'])
async def modify_charging():
    """修改充电请求"""
    data = request.get_json()
    pile_id = data.get('pile_id')
    charging_amount = data.get('charging_amount')
    queue_number = data.get('queue_number')  # 可选，如果是修改等候队列中的车辆
    
    try:
        # 检查充电量是否有效
        if charging_amount is None or charging_amount <= 0:
            return jsonify({
                "status": False,
                "msg": "充电量必须大于0",
                "data": None
            })
        
        # 如果提供了queue_number，表示修改等候队列中的车辆
        if queue_number:
            # 在等候队列中查找并修改
            vehicle = waiting_queue.find_vehicle_by_queue_number(queue_number)
            if not vehicle:
                return jsonify({
                    "status": False,
                    "msg": "未找到该排队号码对应的车辆",
                    "data": None
                })
            
            # 修改充电请求量
            old_amount = vehicle['vehicle_info'].get('charging_amount', 0)
            vehicle['vehicle_info']['charging_amount'] = charging_amount
            
            return jsonify({
                "status": True,
                "msg": f"等候队列中的充电请求已从{old_amount}度修改为{charging_amount}度",
                "data": {
                    "queue_number": queue_number,
                    "charging_amount": charging_amount
                }
            })
        
        # 否则是修改正在充电的车辆
        if pile_id not in charging_piles:
            return jsonify({
                "status": False,
                "msg": "充电桩不存在",
                "data": None
            })
        
        pile = charging_piles[pile_id]
        
        # 检查充电桩是否有连接的车辆
        if pile.status != ChargingStatus.CHARGING or not pile.connected_vehicle:
            return jsonify({
                "status": False,
                "msg": "该充电桩当前没有连接车辆",
                "data": None
            })
        
        # 获取当前充电量
        current_charging_amount = pile.get_current_charging_amount()
        
        # 如果新的充电量小于已充电量，则拒绝修改
        if charging_amount < current_charging_amount:
            return jsonify({
                "status": False,
                "msg": f"新的充电量({charging_amount}度)不能小于已充电量({current_charging_amount:.2f}度)",
                "data": None
            })
        
        # 获取旧的充电量
        old_amount = pile.connected_vehicle.get('charging_amount', 0)
        
        # 更新充电请求
        pile.connected_vehicle['charging_amount'] = charging_amount
        
        return jsonify({
            "status": True,
            "msg": f"充电请求已从{old_amount}度修改为{charging_amount}度",
            "data": {
                "pile_id": pile_id,
                "charging_amount": charging_amount,
                "current_charging_amount": round(current_charging_amount, 2)
            }
        })
        
    except Exception as e:
        print("Error modifying charging request:", str(e))
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/queue/change_mode', methods=['POST'])
async def change_charge_mode():
    """修改充电模式（快充/慢充）"""
    data = request.get_json()
    queue_number = data.get('queue_number')
    new_mode = data.get('new_mode')  # 'F'或'T'
    
    try:
        if not queue_number or not new_mode:
            return jsonify({
                "status": False,
                "msg": "缺少必要参数",
                "data": None
            })
            
        if new_mode not in ['F', 'T']:
            return jsonify({
                "status": False,
                "msg": "无效的充电模式，必须是'F'(快充)或'T'(慢充)",
                "data": None
            })
        
        # 修改充电模式
        vehicle = waiting_queue.change_charge_mode(queue_number, new_mode)
        if not vehicle:
            return jsonify({
                "status": False,
                "msg": "未找到该排队号码对应的车辆",
                "data": None
            })
        
        return jsonify({
            "status": True,
            "msg": f"充电模式已修改为{'快充' if new_mode == 'F' else '慢充'}，新的排队号为{vehicle['queue_number']}",
            "data": {
                "queue_number": vehicle['queue_number'],
                "charge_mode": new_mode
            }
        })
        
    except Exception as e:
        print("Error changing charge mode:", str(e))
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/queue/cancel', methods=['POST'])
async def cancel_charging():
    """取消充电请求"""
    data = request.get_json()
    queue_number = data.get('queue_number')  # 等候区取消
    pile_id = data.get('pile_id')  # 充电区取消
    
    try:
        # 等候区取消
        if queue_number:
            vehicle = waiting_queue.remove_vehicle(queue_number)
            if not vehicle:
                return jsonify({
                    "status": False,
                    "msg": "未找到该排队号码对应的车辆",
                    "data": None
                })
                
            return jsonify({
                "status": True,
                "msg": "已成功取消排队",
                "data": {
                    "queue_number": queue_number
                }
            })
        
        # 充电区取消
        if pile_id:
            if pile_id not in charging_piles:
                return jsonify({
                    "status": False,
                    "msg": "充电桩不存在",
                    "data": None
                })
                
            pile = charging_piles[pile_id]
            if pile.status != ChargingStatus.CHARGING or not pile.connected_vehicle:
                return jsonify({
                    "status": False,
                    "msg": "该充电桩当前没有连接车辆",
                    "data": None
                })
                
            # 断开车辆并生成详单
            result = pile.disconnect_vehicle()
            if isinstance(result, dict) and 'error' in result:
                return jsonify({
                    "status": False,
                    "msg": result['error'],
                    "data": None
                })
            
            # 保存充电详单到数据库
            if result.get('bill'):
                save_charging_bill(result['bill'])
            
            return jsonify({
                "status": True,
                "msg": "已成功取消充电并生成详单",
                "data": result.get('bill')
            })
        
        return jsonify({
            "status": False,
            "msg": "缺少必要参数",
            "data": None
        })
        
    except Exception as e:
        print("Error canceling charging:", str(e))
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

