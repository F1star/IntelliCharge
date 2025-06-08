__all__ = ['blueprint']
from flask import Blueprint, request, jsonify
import pymysql
from ...dataStructure.User import *
from ...dataStructure.WaitingQueue import Queue
from ...dataStructure.ChargerPile import ChargingPile, ChargingStatus
from ...dataStructure.Scheduler import Scheduler
from flask_cors import CORS
import time
import sys
import os
from decimal import Decimal

# 添加项目根目录到系统路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from config.db_config import DB_CONFIG

blueprint = Blueprint('server', __name__)

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        charset=DB_CONFIG['charset'],
        database=DB_CONFIG['database']
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

@blueprint.route('/bills', methods=['GET'])
async def get_charging_bills():
    """获取充电详单列表"""
    username = request.args.get('username')  # 可选参数，按用户名筛选
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()  # 使用普通游标
        
        if username:
            # 按用户名筛选
            sql = """
                SELECT * FROM charging_bills 
                WHERE username = %s
                ORDER BY create_time DESC
            """
            cursor.execute(sql, (username,))
        else:
            # 获取所有详单
            sql = """
                SELECT * FROM charging_bills 
                ORDER BY create_time DESC
            """
            cursor.execute(sql)
            
        columns = [col[0] for col in cursor.description]
        bills = []
        
        for row in cursor.fetchall():
            bill = {}
            for i, value in enumerate(row):
                # 处理Decimal类型
                if isinstance(value, Decimal):
                    bill[columns[i]] = float(value)
                else:
                    bill[columns[i]] = value
            bills.append(bill)
        
        return jsonify({
            "status": True,
            "msg": "获取充电详单成功",
            "data": bills
        })
        
    except Exception as e:
        print("Error getting charging bills:", str(e))
        return jsonify({
            "status": False,
            "msg": f"获取充电详单失败: {str(e)}",
            "data": None
        })
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# 管理员API接口
@blueprint.route('/admin/pile/toggle', methods=['POST'])
async def toggle_charging_pile():
    """启动/关闭充电桩"""
    data = request.get_json()
    pile_id = data.get('pile_id')
    action = data.get('action')  # 'start' 或 'stop'
    
    try:
        if pile_id not in charging_piles:
            return jsonify({
                "status": False,
                "msg": "充电桩不存在",
                "data": None
            })
            
        pile = charging_piles[pile_id]
        
        if action == 'start':
            # 启动充电桩
            if pile.status == ChargingStatus.OFFLINE:
                pile.status = ChargingStatus.IDLE
                return jsonify({
                    "status": True,
                    "msg": f"充电桩{pile_id}已启动",
                    "data": pile.get_status()
                })
            else:
                return jsonify({
                    "status": False,
                    "msg": f"充电桩{pile_id}已处于启动状态",
                    "data": pile.get_status()
                })
        elif action == 'stop':
            # 关闭充电桩
            if pile.status != ChargingStatus.OFFLINE:
                # 如果有车辆正在充电，先断开连接并生成详单
                if pile.status == ChargingStatus.CHARGING and pile.connected_vehicle:
                    result = pile.disconnect_vehicle()
                    # 检查结果是否包含错误信息
                    if isinstance(result, dict) and 'error' in result:
                        return jsonify({
                            "status": False,
                            "msg": result['error'],
                            "data": None
                        })
                    # 保存充电详单
                    if isinstance(result, dict) and 'bill' in result:
                        save_charging_bill(result['bill'])
                
                pile.status = ChargingStatus.OFFLINE
                return jsonify({
                    "status": True,
                    "msg": f"充电桩{pile_id}已关闭",
                    "data": pile.get_status()
                })
            else:
                return jsonify({
                    "status": False,
                    "msg": f"充电桩{pile_id}已处于关闭状态",
                    "data": pile.get_status()
                })
        else:
            return jsonify({
                "status": False,
                "msg": "无效的操作，必须是'start'或'stop'",
                "data": None
            })
            
    except Exception as e:
        print("Error toggling charging pile:", str(e))
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/admin/pile/status', methods=['GET'])
async def get_admin_pile_status():
    """获取所有充电桩详细状态（管理员视图）"""
    try:
        status = {}
        for pile_id, pile in charging_piles.items():
            # 获取基本状态
            pile_status = pile.get_status()
            
            # 添加管理员需要的详细信息
            pile_status.update({
                'charging_count': pile.charging_count,
                'total_charging_duration': round(pile.total_charging_duration / 60, 2),  # 转换为小时
                'total_energy_delivered': round(pile.total_energy_delivered, 2),
                'total_earnings': round(pile.total_earnings, 2),
                'is_working': pile.status != ChargingStatus.OFFLINE and pile.status != ChargingStatus.FAULT
            })
            
            status[pile_id] = pile_status
            
        return jsonify({
            "status": True,
            "msg": "获取充电桩状态成功",
            "data": status
        })
    except Exception as e:
        print("Error getting admin pile status:", str(e))
        return jsonify({
            "status": False,
            "msg": "获取充电桩状态失败",
            "data": None
        })

@blueprint.route('/admin/queue/waiting', methods=['GET'])
async def get_waiting_vehicles():
    """获取等候服务的车辆信息"""
    try:
        # 获取所有等候队列中的车辆
        queue_status = waiting_queue.get_queue_status()
        
        # 处理等候车辆信息
        waiting_vehicles = []
        
        # 处理快充队列
        for vehicle in queue_status['fast_queue']:
            # 计算排队时长（分钟）
            queue_time = (time.time() - vehicle['join_time']) / 60
            
            waiting_vehicles.append({
                'queue_number': vehicle['queue_number'],
                'user_id': vehicle['vehicle_info']['username'],
                'car_id': vehicle['vehicle_info']['car_id'],
                'charge_mode': '快充',
                'battery_capacity': 0,  # 需要从数据库获取
                'charging_amount': vehicle['vehicle_info']['charging_amount'],
                'queue_time': round(queue_time, 2)  # 排队时长（分钟）
            })
            
        # 处理慢充队列
        for vehicle in queue_status['slow_queue']:
            # 计算排队时长（分钟）
            queue_time = (time.time() - vehicle['join_time']) / 60
            
            waiting_vehicles.append({
                'queue_number': vehicle['queue_number'],
                'user_id': vehicle['vehicle_info']['username'],
                'car_id': vehicle['vehicle_info']['car_id'],
                'charge_mode': '慢充',
                'battery_capacity': 0,  # 需要从数据库获取
                'charging_amount': vehicle['vehicle_info']['charging_amount'],
                'queue_time': round(queue_time, 2)  # 排队时长（分钟）
            })
            
        # 获取车辆电池容量信息
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for vehicle in waiting_vehicles:
            try:
                sql = """
                    SELECT battery_capacity FROM cars 
                    WHERE id = %s
                """
                cursor.execute(sql, (vehicle['car_id'],))
                result = cursor.fetchone()
                if result:
                    vehicle['battery_capacity'] = float(result[0])
            except Exception as e:
                print(f"Error getting battery capacity for car {vehicle['car_id']}: {str(e)}")
                
        cursor.close()
        conn.close()
            
        return jsonify({
            "status": True,
            "msg": "获取等候车辆信息成功",
            "data": waiting_vehicles
        })
    except Exception as e:
        print("Error getting waiting vehicles:", str(e))
        return jsonify({
            "status": False,
            "msg": str(e),
            "data": None
        })

@blueprint.route('/admin/reports', methods=['GET'])
async def get_charging_reports():
    """获取充电报表数据"""
    report_type = request.args.get('type', 'day')  # 报表类型：day, week, month
    start_date = request.args.get('start_date')  # 开始日期
    
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 根据报表类型构建SQL查询
        if report_type == 'day':
            # 按日统计
            date_format = "%Y-%m-%d"
        elif report_type == 'week':
            # 按周统计
            date_format = "%Y-%u"  # 年-周数
        elif report_type == 'month':
            # 按月统计
            date_format = "%Y-%m"
        else:
            return jsonify({
                "status": False,
                "msg": "无效的报表类型，必须是'day'、'week'或'month'",
                "data": None
            })
            
        # 构建SQL查询 - 使用子查询避免GROUP BY问题
        sql = """
            SELECT 
                time_period,
                pile_id,
                COUNT(*) as charging_count,
                SUM(charging_duration) as total_duration,
                SUM(charging_amount) as total_amount,
                SUM(charging_cost) as total_charging_cost,
                SUM(service_cost) as total_service_cost,
                SUM(total_cost) as total_cost
            FROM (
                SELECT 
                    DATE_FORMAT(start_time, %s) as time_period,
                    pile_id,
                    charging_duration,
                    charging_amount,
                    charging_cost,
                    service_cost,
                    total_cost
                FROM charging_bills
        """
        
        params = [date_format]
        
        # 添加日期筛选条件
        if start_date:
            sql += " WHERE start_time >= %s"
            params.append(start_date)
            
        sql += """
            ) AS temp
            GROUP BY time_period, pile_id
            ORDER BY time_period DESC, pile_id
        """
        
        cursor.execute(sql, params)
        columns = [col[0] for col in cursor.description]
        reports = []
        
        for row in cursor.fetchall():
            report = {}
            for i, value in enumerate(row):
                # 处理Decimal类型
                if isinstance(value, Decimal):
                    report[columns[i]] = float(value)
                else:
                    report[columns[i]] = value
            reports.append(report)
            
        return jsonify({
            "status": True,
            "msg": "获取充电报表成功",
            "data": reports
        })
        
    except Exception as e:
        print("Error getting charging reports:", str(e))
        return jsonify({
            "status": False,
            "msg": f"获取充电报表失败: {str(e)}",
            "data": None
        })
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@blueprint.route('/admin/pile/fault', methods=['POST'])
async def set_pile_fault():
    """设置充电桩故障"""
    data = request.get_json()
    pile_id = data.get('pile_id')
    schedule_strategy = data.get('schedule_strategy', 'priority')  # 'priority' 或 'time_order'
    
    try:
        # 使用调度器处理充电桩故障
        result = scheduler.handle_pile_fault(pile_id, schedule_strategy)
        return jsonify(result)
        
    except Exception as e:
        print("Error setting pile fault:", str(e))
        return jsonify({
            "status": False,
            "msg": f"设置充电桩故障失败: {str(e)}",
            "data": None
        })

@blueprint.route('/admin/pile/repair', methods=['POST'])
async def repair_pile():
    """修复充电桩故障"""
    data = request.get_json()
    pile_id = data.get('pile_id')
    
    try:
        # 使用调度器处理充电桩修复
        result = scheduler.handle_pile_repair(pile_id)
        return jsonify(result)
        
    except Exception as e:
        print("Error repairing pile:", str(e))
        return jsonify({
            "status": False,
            "msg": f"修复充电桩故障失败: {str(e)}",
            "data": None
        })

