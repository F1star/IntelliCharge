import { defineStore } from 'pinia';

export const mainStore = defineStore('main', {
  state: () => ({
    username: '',
  }),
  getters: {},
  actions: {
    setUser(username) {
      this.username = username;
    },
    isLogin() {
      if (this.username === '') return false;
      else return true;
    }
  }
});
