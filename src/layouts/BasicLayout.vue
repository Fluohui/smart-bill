<template>
  <a-layout style="min-height:100vh">
    <!-- 顶部栏 -->
    <a-layout-header style="background:#fff;padding:0 16px">
      <span style="font-size:18px;font-weight:bold">智能账单</span>
    </a-layout-header>

    <a-layout>
      <!-- 左侧菜单 -->
      <a-layout-sider v-model:collapsed="collapsed" collapsible>
        <a-menu theme="dark" mode="inline" :selected-keys="[$route.name]">
          <a-menu-item key="Dashboard" @click="$router.push('/')">
            <HomeOutlined />
            <span>仪表盘</span>
          </a-menu-item>
          <a-menu-item key="List" @click="$router.push('/list')">
            <UnorderedListOutlined />
            <span>账单列表</span>
          </a-menu-item>
          <a-menu-item key="Settings" @click="$router.push('/settings')">
            <SettingOutlined />
            <span>设置</span>
          </a-menu-item>
        </a-menu>
      </a-layout-sider>

      <!-- 内容区 -->
      <a-layout-content style="margin:16px">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { ref } from 'vue'
import {
  HomeOutlined,
  UnorderedListOutlined,
  SettingOutlined
} from '@ant-design/icons-vue'

const collapsed = ref(false)
</script>