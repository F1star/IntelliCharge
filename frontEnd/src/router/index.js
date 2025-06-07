import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import { mainStore } from '../store';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/edit',
      name: 'edit',
      component: () => import('../views/Edit.vue')
    }
  ]
})

router.beforeEach((to, from, next) => {
  const store = mainStore();
  // 检查用户是否已登录
  if (!store.isLogin() && to.path != '/login' && to.path != '/register' && to.path != '/') {
    // 重定向到登录页面
    next('/login');
  } else {
    // 继续路由导航
    next();
  }
});

export default router
