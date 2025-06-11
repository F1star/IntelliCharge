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
-- 表的结构 `admin_reports`
--

CREATE TABLE `admin_reports` (
  `id` int(11) NOT NULL,
  `report_id` varchar(36) COLLATE utf8_unicode_ci NOT NULL,
  `time_period` varchar(20) COLLATE utf8_unicode_ci NOT NULL COMMENT '报表时间段',
  `period_type` enum('day','week','month') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'day' COMMENT '时间段类型',
  `pile_id` varchar(50) COLLATE utf8_unicode_ci NOT NULL COMMENT '充电桩编号',
  `charging_count` int(11) NOT NULL DEFAULT '0' COMMENT '累计充电次数',
  `total_duration` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '累计充电时长(分钟)',
  `total_amount` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '累计充电量(度)',
  `total_charging_cost` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '累计充电费用',
  `total_service_cost` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '累计服务费用',
  `total_cost` decimal(10,2) NOT NULL DEFAULT '0.00' COMMENT '累计总费用',
  `create_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '报表生成时间',
  `update_time` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '报表更新时间'
) ENGINE=MyISAM DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci COMMENT='管理员报表数据';

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
(5, 6, '贵AF88888', '问界', 'M7', 40),
(6, 7, '晋AD88888', '特斯拉', 'ModelY', 78),
(7, 8, '京AD88888', '迈巴赫', 'S580e', 28),
(8, 9, '京AD77777', '奔驰', 'EQS', 108),
(9, 10, '京FD88888', '保时捷', 'Taycan', 93),
(10, 11, '川AD88888', '岚图', '梦想家', 108),
(11, 12, '湘AD88888', '宝马', 'i4', 84),
(12, 13, '鄂AD88888', '蔚来', 'ES8', 80),
(13, 14, '新AD88888', '红旗', 'E-HS9', 99),
(14, 15, '青AD88888', '小鹏', 'P7', 80);

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
('780aa72b-8160-498e-b964-40fc7be1fa7d', '2025-06-08 13:22:43', 'A', '2', '1', '0.02', '0.03', '2025-06-08 13:22:41', '2025-06-08 13:22:43', '0.02', '0.00', '0.02'),
('517dc777-0f65-42b0-a29c-ec1e46d368bd', '2025-06-08 13:37:45', 'A', '2', '1', '0.03', '0.07', '2025-06-08 13:37:41', '2025-06-08 13:37:45', '0.03', '0.00', '0.03'),
('d9a09fb1-08e2-4936-abdf-88d88ea1dc4c', '2025-06-08 13:38:26', 'A', '1', '1234', '0.04', '0.08', '2025-06-08 13:38:21', '2025-06-08 13:38:26', '0.04', '0.00', '0.04'),
('26f3bfb5-2062-4fb0-9708-b1dbdc9de620', '2025-06-08 13:54:44', 'A', '2', '1', '0.06', '0.11', '2025-06-08 13:54:37', '2025-06-08 13:54:44', '0.06', '0.01', '0.07'),
('9715ca7e-eead-4d6e-8eee-1c2dace16333', '2025-06-08 14:00:21', 'A', '2', '1', '0.55', '1.11', '2025-06-08 13:59:14', '2025-06-08 14:00:21', '0.55', '0.06', '0.61'),
('88163c70-e11e-40e7-bf7c-c429ae34c064', '2025-06-08 14:13:05', 'A', '2', '1', '0.50', '1.00', '2025-06-08 14:12:05', '2025-06-08 14:13:05', '0.50', '0.05', '0.55'),
('5694b482-edec-49a1-a6ac-07a811096a9f', '2025-06-08 14:26:11', 'A', '2', '1', '1.51', '3.02', '2025-06-08 14:23:09', '2025-06-08 14:26:11', '1.51', '0.15', '1.66'),
('7156cb97-6cc0-4d4c-812e-b100ea92f8e5', '2025-06-08 15:17:15', 'A', '2', '1', '0.11', '0.22', '2025-06-08 15:17:02', '2025-06-08 15:17:15', '0.08', '0.01', '0.09'),
('9b18e68c-7328-4fa1-aa96-c2a238488517', '2025-06-10 23:13:14', 'A', '2', '1', '0.08', '0.17', '2025-06-10 23:13:04', '2025-06-10 23:13:14', '0.03', '0.00', '0.03'),
('1d7ae386-f441-4974-8676-e9bff4b61e6c', '2025-06-10 23:56:08', 'A', '2', '1', '0.11', '0.22', '2025-06-10 23:55:55', '2025-06-10 23:56:08', '0.04', '0.00', '0.04'),
('4a45058f-cb71-441a-a54c-ae26e10589cf', '2025-06-10 23:56:30', 'A', '2', '1', '1.50', '3.00', '2025-06-10 23:56:20', '2025-06-10 23:59:20', '0.60', '0.06', '0.66'),
('24f3138b-075f-4cef-b218-6f9c8622028d', '2025-06-10 23:57:45', 'A', '2', '1', '1.50', '3.00', '2025-06-10 23:57:35', '2025-06-11 00:00:35', '0.60', '0.06', '0.66'),
('6659a192-8383-493a-a6b9-b374db573e66', '2025-06-10 23:59:34', 'A', '2', '1', '0.05', '0.10', '2025-06-10 23:59:24', '2025-06-10 23:59:30', '0.02', '0.00', '0.02'),
('28dc4a69-22d5-45de-b2da-56027a3b1d25', '2025-06-11 01:24:20', 'A', '2', '1', '20.00', '40.00', '2025-06-11 00:44:20', '2025-06-11 01:24:20', '8.00', '0.80', '8.80'),
('b4a9b943-a193-410a-b716-9e3ab623954f', '2025-06-11 01:24:25', 'B', '3', '2', '20.00', '40.00', '2025-06-11 00:44:25', '2025-06-11 01:24:25', '8.00', '0.80', '8.80'),
('9fd36f25-974d-4255-8fef-99bd149ac54c', '2025-06-11 01:24:30', 'C', '4', '3', '20.00', '40.00', '2025-06-11 00:44:30', '2025-06-11 01:24:30', '8.00', '0.80', '8.80'),
('5f6d88d5-f57e-4f56-a97e-f63aa5e4c17b', '2025-06-11 01:38:19', 'A', '2', '1', '1.33', '2.66', '2025-06-11 01:35:39', '2025-06-11 01:38:19', '0.53', '0.05', '0.58');

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
(9, '7', '7777777', 0),
(10, '8', '888888', 0),
(11, '9', '999999', 0),
(12, '10', '101010', 0),
(13, '11', '111111', 0),
(14, '12', '121212', 0),
(15, '13', '131313', 0);

--
-- 转储表的索引
--

--
-- 表的索引 `admin_reports`
--
ALTER TABLE `admin_reports`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `uk_report_pile_period` (`time_period`,`period_type`,`pile_id`),
  ADD KEY `idx_report_id` (`report_id`),
  ADD KEY `idx_pile_id` (`pile_id`),
  ADD KEY `idx_period_type` (`period_type`),
  ADD KEY `idx_time_period` (`time_period`);

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
-- 使用表AUTO_INCREMENT `admin_reports`
--
ALTER TABLE `admin_reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- 使用表AUTO_INCREMENT `cars`
--
ALTER TABLE `cars`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=15;

--
-- 使用表AUTO_INCREMENT `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户唯一标识', AUTO_INCREMENT=16;

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