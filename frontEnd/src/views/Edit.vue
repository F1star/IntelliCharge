<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider :style="{ overflow: 'auto', height: '100vh', position: 'fixed', left: 0, top: 0, bottom: 0 }">
      <div class="logo" />
      <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
        <a-menu-item key="1" @click="showHomeSidebar">
          <message-outlined />
          <span>主页</span>
        </a-menu-item>
        <a-menu-item key="2" @click="showPersonalSidebar">
          <team-outlined />
          <span>个人</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout :style="{ marginLeft: '200px' }">
      <a-layout-header style="background: #fff; padding: 0" />
      <a-layout-content :style="contentStyle">
        <div v-if="activeSidebar === 'personal'" class="sidebar-content">
          <PersonalSidebar />
        </div>
        <div v-if="activeSidebar === 'home'" class="sidebar-content">
          <HomeSidebar />
        </div>
        <div v-else :style="editorStyle">
          <HomeSidebar/>
        </div>
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { onMounted, ref, computed, h } from 'vue';

import { TranslationOutlined, MessageOutlined, PictureOutlined, TeamOutlined, FileOutlined, AudioOutlined, SaveOutlined } from '@ant-design/icons-vue';
import { createFromIconfontCN } from '@ant-design/icons-vue';
import { message, TypographyText } from 'ant-design-vue';

import PersonalSidebar from '../components/PersonalSidebar.vue';
import HomeSidebar from '../components/HomeSidebar.vue';

// 使用阿里图标库的 URL 创建自定义图标组件
const IconFont = createFromIconfontCN({
  scriptUrl: '//at.alicdn.com/t/c/font_4614419_md6m4y39h1k.js', // 替换为你的图标库 URL
});

const contentStyle = computed(() => ({
  margin: '0 16px',
  display: 'flex',
  transition: 'all 0.3s',
}));

const editorStyle = computed(() => {
  const sidebarWidth = activeSidebar.value ? '300px' : '0';
  const editorMarginRight = activeSidebar.value ? '316px' : '16px';
  return {
    flex: 1,
    marginRight: editorMarginRight,
    transition: 'all 0.3s',
  };
});

const activeSidebar = ref('');
const isModalVisiblePersonal = ref(false);
const showHomeSidebar = () => {
  activeSidebar.value = 'home';
};
const showPersonalSidebar = () => {
  activeSidebar.value = 'personal';
};

</script>

<style>
#app {
  height: 100%;
  margin: 0;
}

.container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

h1 {
  text-align: center;
  margin-bottom: 20px;
}

#components-layout-demo-side .logo {
  height: 32px;
  margin: 16px;
  background: rgba(255, 255, 255, 0.3);
}

.site-layout .site-layout-background {
  background: #fff;
}

[data-theme='dark'] .site-layout .site-layout-background {
  background: #141414;
}

.sidebar-content {
  width: 100%;
  height: 100vh;
  position: relative;
  background: #f5f7fa;
}
</style>
