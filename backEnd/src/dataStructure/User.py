from typing import TypedDict, List

class LoginResponse(TypedDict):
    status: bool  # 登录状态
    token: str  # 令牌
    msg: str  # 消息

class Car:
    def __init__(self, id, user_id, plate_number, brand, model, battery_capacity):
        self.id = id
        self.user_id = user_id
        self.plate_number = plate_number
        self.brand = brand
        self.model = model
        self.battery_capacity = battery_capacity

    @staticmethod
    def to_json(car):
        return {
            'id': car.id,
            'user_id': car.user_id,
            'plate_number': car.plate_number,
            'brand': car.brand,
            'model': car.model,
            'battery_capacity': car.battery_capacity
        }

    @staticmethod
    def from_json(json: dict):
        return Car(
            json.get('id', '0'),
            json.get('user_id', '0'),
            json['plate_number'],
            json['brand'],
            json['model'],
            json['battery_capacity']
        )

class User:
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password
        self.cars: List[Car] = []

    @staticmethod
    def to_json(user):
        return {
            'id': user.id,
            'username': user.username,
            'password': user.password,
            'cars': [Car.to_json(car) for car in user.cars]
        }

    @staticmethod
    def from_json(json: dict):
        user = User("0", json['username'], json['password'])
        if 'cars' in json:
            user.cars = [Car.from_json(car) for car in json['cars']]
        return user

    