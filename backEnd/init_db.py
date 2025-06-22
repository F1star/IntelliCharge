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
-- phpMyAdmin SQL Dump
-- version 4.8.5
-- https://www.phpmyadmin.net/
--
-- 主机： localhost
-- 生成日期： 2025-06-11 10:44:13
-- 服务器版本： 5.7.26
-- PHP 版本： 7.3.4

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET AUTOCOMMIT = 0;
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- 数据库： `pile`
--

-- --------------------------------------------------------

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
-- 转存表中的数据 `cars`
--

INSERT INTO `cars` (`id`, `user_id`, `plate_number`, `brand`, `model`, `battery_capacity`) VALUES
(1, 1, '京AD12345', '宝马', 'X5', 70),
(2, 3, '京AD11111', '奔驰', '新能源', 80),
(3, 4, '鲁MD88888', '小米', 'yu7', 96),
(4, 5, '粤AD88888', '尊界', 'S800', 63),
(5, 6, '贵AF88888', '问界', 'M7', 150),
(6, 7, '晋AD88888', '特斯拉', 'ModelY', 78),
(7, 8, '京AD88888', '迈巴赫', 'S580e', 28),
(8, 9, '京AD77777', '奔驰', 'EQS', 108),
(9, 10, '京FD88888', '保时捷', 'Taycan', 93),
(10, 11, '川AD88888', '岚图', '梦想家', 108),
(11, 12, '湘AD88888', '宝马', 'i4', 84),
(12, 13, '鄂AD88888', '蔚来', 'ES8', 80),
(13, 14, '新AD88888', '红旗', 'E-HS9', 99),
(14, 15, '青AD88888', '小鹏', 'P7', 80),
(15, 16, '吉AMW7767', '小鹏', 'P7', 80),
(16, 17, '京CR77V03', '奔驰', 'X5', 200),
(17, 18, '藏E0Q02E5', '特斯拉', 'ModelY', 200),
(18, 19, '吉B6AT145', '特斯拉', 'ModelY', 200),
(19, 20, '黑MU87283', '特斯拉', 'ModelY', 200),
(20, 21, '京OA005B2', '特斯拉', 'ModelY', 200),
(21, 22, '蒙LW1K845', '特斯拉', 'ModelY', 200),
(22, 23, '新B440503', '特斯拉', 'ModelY', 200),
(23, 24, '蒙B34QL31', '特斯拉', 'ModelY', 200),
(24, 25, '浙BPM1613', '特斯拉', 'ModelY', 200),
(25, 26, '浙BPM1612', '特斯拉', 'ModelY', 200),
(26, 26, '浙BPM1633', '特斯拉', 'ModelY', 200);

-- --------------------------------------------------------

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
-- 转存表中的数据 `charging_bills`
--

INSERT INTO `charging_bills` (`bill_id`, `create_time`, `pile_id`, `vehicle_id`, `username`, `charging_amount`, `charging_duration`, `start_time`, `end_time`, `charging_cost`, `service_cost`, `total_cost`) VALUES
('90b24390-8593-4fb5-8059-d07e2573b095', '2025-06-15 07:20:17', 'E', '6', '5', '7.00', '60.00', '2025-06-15 06:20:14', '2025-06-15 07:20:14', '3.50', '5.60', '9.10'),
('b1dbe2f8-86e0-4d41-8887-fd389b7e35e9', '2025-06-15 07:10:17', 'A', '4', '3', '30.00', '60.00', '2025-06-15 06:10:14', '2025-06-15 07:10:14', '13.50', '24.00', '37.50');

-- --------------------------------------------------------

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
-- 转存表中的数据 `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `isadmin`) VALUES
(1, '1234', '123456', 0),
(2, 'root', 'root123', 1),
(3, '1', '111111', 0),
(4, '2', '222222', 0),
(5, '3', '333333', 0),
(6, '4', '444444', 0),
(7, '5', '555555', 0),
(8, '6', '666666', 0),
(9, '7', '777777', 0),
(10, '8', '888888', 0),
(11, '9', '999999', 0),
(12, '10', '101010101010', 0),
(13, '11', '111111111111', 0),
(14, '12', '121212121212', 0),
(15, '13', '131313131313', 0),
(16, '14', '141414141414', 0),
(17, '15', '151515151515', 0),
(18, '16', '161616161616', 0),
(19, '17', '171717171717', 0),
(20, '18', '181818181818', 0),
(21, '19', '191919191919', 0),
(22, '20', '202020202020', 0),
(23, '21', '212121212121', 0),
(24, '22', '222222222222', 0),
(25, '23', '232323232323', 0),
(26, '111111', '111111', 0);

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
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户唯一标识', AUTO_INCREMENT=27;

--
-- 限制导出的表
--

--
-- 限制表 `cars`
--
ALTER TABLE `cars`
  ADD CONSTRAINT `cars_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;

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