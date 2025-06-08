import { defineStore } from 'pinia';

export const mainStore = defineStore('main', {
  state: () => ({
    username: '',
    role: '',
  }),
  getters: {},
  actions: {
    setUser(username, role) {
      this.username = username;
      this.role = role;
    },
    isLogin() {
      if (this.username === '') return false;
      else return true;
    }
  }
});
