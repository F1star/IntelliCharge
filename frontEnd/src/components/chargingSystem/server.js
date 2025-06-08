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

    return {
        getQueueStatus,
        getPileStatus,
        joinQueue,
        leaveQueue,
        modifyCharging,
        stopCharging,
        changeChargeMode,
        cancelCharging
    };
});