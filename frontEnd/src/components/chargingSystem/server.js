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

    return {
        getQueueStatus,
        joinQueue,
        leaveQueue
    };
});