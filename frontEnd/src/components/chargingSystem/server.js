import { defineStore } from "pinia";
import { SERVER_CONFIG } from "../../config";

import axios from "axios";
import { mainStore } from "../../store";

export const useChargingServer = defineStore("chargingServer", () => {
    const userStore = mainStore();

    // 创建服务端API实例
    const serverApi = axios.create({
        baseURL: `${SERVER_CONFIG.SERVER}:${SERVER_CONFIG.PORT}/server/`,
        timeout: 10000,
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    });

    /**
     * 获取队列状态
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const getQueueStatus = async () => {
        const res = await serverApi.get("queue/status");
        return res.data;
    };

    /**
     * 获取充电桩状态
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const getPileStatus = async () => {
        const res = await serverApi.get("pile/status");
        return res.data;
    };

    /**
     * 加入等候队列
     * @param {Object} queueData - 队列信息
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const joinQueue = async (queueData) => {
        const res = await serverApi.post("queue/join", {
            username: userStore.username,
            ...queueData
        });
        return res.data;
    };

    /**
     * 离开等候队列
     * @param {string} queueNumber - 排队号码
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const leaveQueue = async (queueNumber) => {
        const res = await serverApi.post("queue/leave", {
            queue_number: queueNumber
        });
        return res.data;
    };

    /**
     * 修改充电请求
     * @param {Object} data - 修改信息，可以包含pile_id或queue_number
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const modifyCharging = async (data) => {
        const res = await serverApi.post("pile/modify_charging", data);
        return res.data;
    };

    /**
     * 修改充电模式（快充/慢充）
     * @param {string} queue_number - 排队号码
     * @param {string} new_mode - 新的充电模式 ('F': 快充, 'T': 慢充)
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const changeChargeMode = async (queue_number, new_mode) => {
        const res = await serverApi.post("queue/change_mode", {
            queue_number,
            new_mode
        });
        return res.data;
    };

    /**
     * 取消充电请求
     * @param {Object} data - 取消信息，包含queue_number(等候区)或pile_id(充电区)
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const cancelCharging = async (data) => {
        const res = await serverApi.post("queue/cancel", data);
        return res.data;
    };

    /**
     * 提前结束充电
     * @param {string} pileId - 充电桩ID
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const stopCharging = async (pileId) => {
        const res = await serverApi.post("pile/disconnect", {
            pile_id: pileId
        });
        return res.data;
    };

    /**
     * 获取充电详单列表
     * @param {string} username - 可选，按用户名筛选
     * @returns {Promise<{status: boolean, msg: string, data: Array}>}
     */
    const getChargingBills = async (username) => {
        const params = username ? { username } : {};
        const res = await serverApi.get("bills", { params });
        return res.data;
    };

    /**
     * 启动/关闭充电桩（管理员）
     * @param {string} pileId - 充电桩ID
     * @param {string} action - 操作类型：'start' 或 'stop'
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const toggleChargingPile = async (pileId, action) => {
        const res = await serverApi.post("admin/pile/toggle", {
            pile_id: pileId,
            action
        });
        return res.data;
    };

    /**
     * 获取充电桩详细状态（管理员）
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const getAdminPileStatus = async () => {
        const res = await serverApi.get("admin/pile/status");
        return res.data;
    };

    /**
     * 获取等候服务的车辆信息（管理员）
     * @returns {Promise<{status: boolean, msg: string, data: Array}>}
     */
    const getWaitingVehicles = async () => {
        const res = await serverApi.get("admin/queue/waiting");
        return res.data;
    };

    /**
     * 获取充电报表数据（管理员）
     * @param {string} type - 报表类型：'day', 'week', 'month'
     * @param {string} startDate - 可选，开始日期
     * @returns {Promise<{status: boolean, msg: string, data: Array}>}
     */
    const getChargingReports = async (type = 'day', startDate = null) => {
        const params = { type };
        if (startDate) {
            params.start_date = startDate;
        }
        const res = await serverApi.get("admin/reports", { params });
        return res.data;
    };

    /**
     * 设置充电桩故障（管理员）
     * @param {string} pileId - 充电桩ID
     * @param {string} scheduleStrategy - 调度策略：'priority'（优先级调度）或'time_order'（时间顺序调度）
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const setPileFault = async (pileId, scheduleStrategy = 'priority') => {
        try {
            const res = await serverApi.post("admin/pile/fault", {
                pile_id: pileId,
                schedule_strategy: scheduleStrategy
            });
            return res.data;
        } catch (error) {
            console.error("设置充电桩故障API错误:", error);
            return {
                status: false,
                msg: error.response?.data?.msg || "设置充电桩故障请求失败",
                data: null
            };
        }
    };

    /**
     * 修复充电桩故障（管理员）
     * @param {string} pileId - 充电桩ID
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const repairPile = async (pileId) => {
        const res = await serverApi.post("admin/pile/repair", {
            pile_id: pileId
        });
        return res.data;
    };

    /**
     * 设置时间加速倍数（管理员）
     * @param {number} speedup - 时间加速倍数，例如 10 表示时间流逝速度为正常的10倍
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const setTimeSpeedup = async (speedup) => {
        const res = await serverApi.post("admin/time_speedup", {
            speedup
        });
        return res.data;
    };
    
    /**
     * 设置模拟时间（管理员）
     * @param {string} timeStr - 时间字符串，格式为 "HH:MM:SS" 或 "YYYY-MM-DD HH:MM:SS"
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const setSimulationTime = async (timeStr) => {
        const res = await serverApi.post("admin/set_time", {
            time_str: timeStr
        });
        return res.data;
    };
    
    /**
     * 获取当前系统时间（管理员）
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const getSystemTime = async () => {
        const res = await serverApi.get("admin/get_time");
        return res.data;
    };
    
    /**
     * 恢复使用实时系统时间（管理员）
     * @returns {Promise<{status: boolean, msg: string, data: Object}>}
     */
    const resetToRealTime = async () => {
        const res = await serverApi.post("admin/reset_time");
        return res.data;
    };

    return {
        getQueueStatus,
        getPileStatus,
        joinQueue,
        leaveQueue,
        modifyCharging,
        stopCharging,
        changeChargeMode,
        cancelCharging,
        getChargingBills,
        // 管理员API
        toggleChargingPile,
        getAdminPileStatus,
        getWaitingVehicles,
        getChargingReports,
        setPileFault,
        repairPile,
        setTimeSpeedup,
        setSimulationTime,
        getSystemTime,
        resetToRealTime
    };
});