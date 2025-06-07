import { defineStore } from "pinia";
import { SERVER_CONFIG } from "../../config";
import { User } from "./User";
import axios from "axios";
import { mainStore } from "../../store";

/**
 * @typedef {Object} LoginResponse
 * @property {boolean} status - 登录状态
 * @property {string} token - 登录令牌
 * @property {string} msg - 提示信息
 */

export const useLoginServer = defineStore("loginServer", () => {
    const userStore = mainStore();

    const server = axios.create({
        baseURL: `${SERVER_CONFIG.SERVER}:${SERVER_CONFIG.PORT}/user/`,
        timeout: 10000,
        headers: {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
        },
    });

    /**
     * 登录函数
     * @param {User} user - 用户对象
     * @returns {Promise<LoginResponse>}
     */
    const login = async (user) => {
        const res = await server.post("login", User.toJson(user));
        return /** @type {LoginResponse} */ (res.data);
    };

    /**
     * 注册函数
     * @param {User} user - 用户对象
     * @returns {Promise<LoginResponse>}
     */
    const register = async (user) => {
        const res = await server.post("register", User.toJson(user));
        return /** @type {LoginResponse} */ (res.data);
    };

    /**
     * 修改密码函数
     * @param {string} oldPassword - 旧密码
     * @param {string} newPassword - 新密码
     * @returns {Promise<LoginResponse>}
     */
    const changePassword = async (oldPassword, newPassword) => {
        const res = await server.post("changePassword", {
            username: userStore.username,
            oldPassword,
            newPassword
        });
        return /** @type {LoginResponse} */ (res.data);
    };

    /**
     * 获取用户车辆列表
     * @returns {Promise<{status: boolean, msg: string, data: Array}>}
     */
    const getUserCars = async () => {
        const res = await server.get("cars", {
            params: {
                username: userStore.username
            }
        });
        return res.data;
    };

     /**
     * 添加新车辆
     * @param {Object} carData - 车辆信息
     * @returns {Promise<LoginResponse>}
     */
     const addCar = async (carData) => {
        const res = await server.post("cars", {
            username: userStore.username,
            car: carData
        });
        return res.data;
    };

    return {
        login,
        register,
        changePassword,
        getUserCars,
        addCar
    };
});
