import pymysql
import sys
import os

# 添加当前目录到系统路径，确保可以导入config模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入数据库配置
from config.db_config import DB_CONFIG

def check_and_create_database():
    """检查数据库pile是否存在，不存在则创建"""
    # 连接到MySQL服务器（不指定数据库）
    try:
        # 使用配置文件中的连接信息，但不指定数据库名
        conn = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            charset=DB_CONFIG['charset']
        )
        print("成功连接到MySQL服务器")
    except Exception as e:
        print(f"连接MySQL服务器失败: {str(e)}")
        sys.exit(1)

    cursor = conn.cursor()
    
    try:
        # 检查数据库是否存在
        cursor.execute("SHOW DATABASES LIKE 'pile'")
        result = cursor.fetchone()
        
        if result:
            print("数据库'pile'已存在")
            return
        
        print("数据库'pile'不存在，开始创建...")
        
        # 创建数据库
        cursor.execute("CREATE DATABASE pile CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        print("数据库'pile'创建成功")
        
        # 切换到新创建的数据库
        cursor.execute("USE pile")
        
        # 创建表结构
        sql_script = """
SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";

--
-- 表的结构 `cars`
--

CREATE TABLE `cars` (
  `id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL COMMENT '关联用户标识',
  `plate_number` varchar(200) DEFAULT NULL COMMENT '车牌号',
  `brand` varchar(200) DEFAULT NULL COMMENT '车辆品牌',
  `model` varchar(200) DEFAULT NULL COMMENT '车辆型号',
  `battery_capacity` double DEFAULT NULL COMMENT '车辆电池容量'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 表的结构 `charging_bills`
--

CREATE TABLE `charging_bills` (
  `bill_id` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `create_time` datetime NOT NULL,
  `pile_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `vehicle_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL,
  `username` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `charging_amount` decimal(10,2) NOT NULL,
  `charging_duration` decimal(10,2) NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `charging_cost` decimal(10,2) NOT NULL,
  `service_cost` decimal(10,2) NOT NULL,
  `total_cost` decimal(10,2) NOT NULL
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci;

--
-- 表的结构 `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL COMMENT '用户唯一标识',
  `username` varchar(200) DEFAULT NULL COMMENT '用户名',
  `password` varchar(200) DEFAULT NULL COMMENT '密码',
  `isadmin` tinyint(1) NOT NULL DEFAULT '0'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- 转储表的索引
--

--
-- 表的索引 `cars`
--
ALTER TABLE `cars`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- 表的索引 `charging_bills`
--
ALTER TABLE `charging_bills`
  ADD PRIMARY KEY (`bill_id`),
  ADD KEY `idx_pile_id` (`pile_id`),
  ADD KEY `idx_vehicle_id` (`vehicle_id`),
  ADD KEY `idx_username` (`username`),
  ADD KEY `idx_create_time` (`create_time`);

--
-- 表的索引 `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `username` (`username`);

--
-- 在导出的表使用AUTO_INCREMENT
--

--
-- 使用表AUTO_INCREMENT `cars`
--
ALTER TABLE `cars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户唯一标识', AUTO_INCREMENT=4;

--
-- 限制导出的表
--

--
-- 限制表 `cars`
--
ALTER TABLE `cars`
  ADD CONSTRAINT `cars_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

--
-- 添加管理员
--
INSERT INTO `users` (`id`, `username`, `password`, `isadmin`) VALUES
(2, 'root', 'root123', 1)

        """
        
        # 执行SQL脚本中的每个语句
        for statement in sql_script.split(';'):
            if statement.strip():
                cursor.execute(statement)
        
        conn.commit()
        print("数据库表结构创建成功")
        
    except Exception as e:
        conn.rollback()
        print(f"创建数据库或表结构失败: {str(e)}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    check_and_create_database() 