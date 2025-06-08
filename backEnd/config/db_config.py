"""
数据库配置文件
包含所有与数据库连接相关的参数
"""

# 数据库连接配置
DB_CONFIG = {
    'host': '127.0.0.1',
    'port': 3306,
    'user': 'root',
    'password': 'root',
    'charset': 'utf8',
    'database': 'pile'
}

def get_db_config():
    """
    获取数据库配置
    """
    return DB_CONFIG 