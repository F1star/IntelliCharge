import { defineStore } from "pinia";
import { User } from "./User";
import { useLoginServer } from "./server";

export const useUserStore = defineStore("user", () => {
    const server = useLoginServer();

    /**
     * 登录函数
     * @param {User} user - 用户对象
     * @returns {Promise<LoginResponse>}
     */
    async function login(user) {
        const res = await server.login(user);
        return res;
    }

    /**
     * 注册函数
     * @param {User} user - 用户对象
     * @returns {Promise<LoginResponse>}
     */
    async function register(user) {
        const res = await server.register(user);
        return res;
    }

    return {
        login,
        register
    };
});
