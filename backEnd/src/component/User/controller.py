__all__ = ['blueprint']
from flask import Blueprint, request, jsonify
import pymysql
from ...dataStructure.User import *
from flask_cors import CORS

blueprint = Blueprint('user', __name__)

@blueprint.route('/', methods=['POST', 'GET'])
async def index():
    return "welcome to use user system"

@blueprint.route('/login', methods=["POST"])
async def login():
    print("receive req for login", request.get_json())
    user = User.from_json(request.get_json())
    print("user", user)

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8', database='pile')
    cursor = conn.cursor()

    try:
        sql = "SELECT id, username, password, isadmin FROM users WHERE username = %s"
        cursor.execute(sql, (user.username,))
        data = cursor.fetchone()

        if data is None or data[2] != user.password:
            print("login failed")
            res = LoginResponse({
                "status": False,
                "msg": "login failed",
                "token": "",
                "role": "user"
            })
        else:
            print("login success")
            is_admin = data[3] if len(data) > 3 else 0
            res = LoginResponse({
                "status": True,
                "msg": "login success",
                "token": "",
                "role": "admin" if is_admin == 1 else "user"
            })
    except Exception as e:
        print("Error during login:", e)
        res = LoginResponse({
            "status": False,
            "msg": "internal server error",
            "token": "",
            "role": "user"
        })
    finally:
        cursor.close()
        conn.close()

    return jsonify(res)

@blueprint.route('/register', methods=["POST"])
async def register():
    print("receive req for register", request.get_json())
    user = User.from_json(request.get_json())
    print("user", user)

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8', database='pile')
    cursor = conn.cursor()

    try:
        sql = "SELECT * FROM users WHERE username = %s"
        cursor.execute(sql, (user.username,))
        count = cursor.rowcount

        if count == 0:
            sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(sql, (user.username, user.password))
            conn.commit()
            print("register successfully")
            res = LoginResponse({
                "status": True,
                "msg": "register successfully",
                "token": "",
                "role": "user"
            })
        else:
            print("register failed, username already exists")
            res = LoginResponse({
                "status": False,
                "msg": "register failed, username already exists",
                "token": "",
                "role": "user"
            })
    except Exception as e:
        print("Error during registration:", e)
        res = LoginResponse({
            "status": False,
            "msg": "internal server error",
            "token": "",
            "role": "user"
        })
    finally:
        cursor.close()
        conn.close()

    return jsonify(res)

@blueprint.route('/changePassword', methods=["POST"])
async def change_password():
    print("receive req for change password", request.get_json())
    data = request.get_json()
    username = data.get('username')  # 需要从token中获取
    old_password = data.get('oldPassword')
    new_password = data.get('newPassword')

    if not all([username, old_password, new_password]):
        return jsonify(LoginResponse({
            "status": False,
            "msg": "参数不完整",
            "token": "",
            "role": "user"
        }))

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8', database='pile')
    cursor = conn.cursor()

    try:
        # 验证旧密码
        sql = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(sql, (username, old_password))
        data = cursor.fetchone()

        if data is None:
            print("旧密码验证失败")
            return jsonify(LoginResponse({
                "status": False,
                "msg": "旧密码错误",
                "token": "",
                "role": "user"
            }))

        # 更新密码
        sql = "UPDATE users SET password = %s WHERE username = %s"
        cursor.execute(sql, (new_password, username))
        conn.commit()
        print("密码修改成功")
        return jsonify(LoginResponse({
            "status": True,
            "msg": "密码修改成功",
            "token": "",
            "role": "user"
        }))

    except Exception as e:
        print("Error during password change:", e)
        return jsonify(LoginResponse({
            "status": False,
            "msg": "内部服务器错误",
            "token": "",
            "role": "user"
        }))
    finally:
        cursor.close()
        conn.close()

@blueprint.route('/cars', methods=["GET"])
async def get_user_cars():
    print("receive req for get user cars")
    username = request.args.get('username')  # 从查询参数获取用户名

    if not username:
        return jsonify(LoginResponse({
            "status": False,
            "msg": "参数不完整",
            "token": "",
            "role": "user"
        }))

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8', database='pile')
    cursor = conn.cursor()

    try:
        # 获取用户ID和权限
        sql = "SELECT id, isadmin FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user_data = cursor.fetchone()
        
        if user_data is None:
            return jsonify(LoginResponse({
                "status": False,
                "msg": "用户不存在",
                "token": "",
                "role": "user"
            }))

        user_id = user_data[0]
        is_admin = user_data[1]

        # 获取用户的车辆列表
        sql = """
            SELECT id, user_id, plate_number, brand, model, battery_capacity 
            FROM cars 
            WHERE user_id = %s
        """
        cursor.execute(sql, (user_id,))
        cars_data = cursor.fetchall()

        # 转换为Car对象列表
        cars = []
        for car_data in cars_data:
            car = Car(
                id=str(car_data[0]),
                user_id=str(car_data[1]),
                plate_number=car_data[2],
                brand=car_data[3],
                model=car_data[4],
                battery_capacity=car_data[5]
            )
            cars.append(car)

        return jsonify({
            "status": True,
            "msg": "获取成功",
            "data": [Car.to_json(car) for car in cars],
            "role": "admin" if is_admin == 1 else "user"
        })

    except Exception as e:
        print("Error during getting user cars:", e)
        return jsonify(LoginResponse({
            "status": False,
            "msg": "内部服务器错误",
            "token": "",
            "role": "user"
        }))
    finally:
        cursor.close()
        conn.close()

@blueprint.route('/cars', methods=["POST"])
async def add_car():
    print("receive req for add car", request.get_json())
    data = request.get_json()
    username = data.get('username')
    car_data = data.get('car')

    if not all([username, car_data]):
        return jsonify(LoginResponse({
            "status": False,
            "msg": "参数不完整",
            "token": "",
            "role": "user"
        }))

    conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', password='root', charset='utf8', database='pile')
    cursor = conn.cursor()

    try:
        # 获取用户ID和权限
        sql = "SELECT id, isadmin FROM users WHERE username = %s"
        cursor.execute(sql, (username,))
        user_data = cursor.fetchone()
        
        if user_data is None:
            return jsonify(LoginResponse({
                "status": False,
                "msg": "用户不存在",
                "token": "",
                "role": "user"
            }))

        user_id = user_data[0]
        is_admin = user_data[1]

        # 检查车牌号是否已存在
        sql = "SELECT id FROM cars WHERE plate_number = %s"
        cursor.execute(sql, (car_data['plate_number'],))
        if cursor.fetchone():
            return jsonify(LoginResponse({
                "status": False,
                "msg": "该车牌号已存在",
                "token": "",
                "role": "admin" if is_admin == 1 else "user"
            }))

        # 添加新车辆
        sql = """
            INSERT INTO cars (user_id, plate_number, brand, model, battery_capacity)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(sql, (
            user_id,
            car_data['plate_number'],
            car_data['brand'],
            car_data['model'],
            car_data['battery_capacity']
        ))
        conn.commit()

        return jsonify(LoginResponse({
            "status": True,
            "msg": "添加成功",
            "token": "",
            "role": "admin" if is_admin == 1 else "user"
        }))

    except Exception as e:
        print("Error during adding car:", e)
        return jsonify(LoginResponse({
            "status": False,
            "msg": "内部服务器错误",
            "token": "",
            "role": "user"
        }))
    finally:
        cursor.close()
        conn.close()
