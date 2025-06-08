<script>
import { ref } from 'vue';
import { useUserStore } from '../components/LoginSystem/userStore';
import { onMounted } from 'vue';
import { message } from 'ant-design-vue';
import { useRouter } from 'vue-router';
import { mainStore } from '../store/index';

export default {
  name: 'LoginView',
  setup() {
    const user = useUserStore();
    const username = ref('');
    const password = ref('');
    const router = useRouter();
    const userStore = mainStore();

    const login = async () => {
      try {
        const res = await user.login({
          username: username.value,
          password: password.value
        });
        console.log("login res", res);
        if (res.status === true) {
          message.success('登录成功！');
          userStore.setUser(username.value, res.role);
          
          // 根据角色重定向到不同页面
          if (res.role === 'admin') {
            router.push({ name: 'admin' });
          } else {
            router.push({ name: 'edit' });
          }
        } else {
          message.error('登录失败，请检查用户名和密码。');
        }
      } catch (error) {
        message.error('登录失败，请检查用户名和密码。');
      }
    };

    return {
      username,
      password,
      login
    };
  }
};
</script>

<template>
  <main style="display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f2f5;">
    <a-card class="box-card" style="width: 400px;">
      <h2 style="text-align: center; margin-bottom: 20px;">登录</h2>
      <a-form>
        <a-form-item>
          <a-input v-model:value="username" placeholder="用户名"></a-input>
        </a-form-item>
        <a-form-item>
          <a-input-password v-model:value="password" type="password" placeholder="密码"></a-input-password>
        </a-form-item>
        <a-form-item>
          <a-button type="primary" @click="login" style="width: 100%;">登录</a-button>
        </a-form-item>
      </a-form>
    </a-card>
  </main>
</template>
