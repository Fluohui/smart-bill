import { createApp } from 'vue'
import App from './App.vue'
import Antd from 'ant-design-vue'
import 'ant-design-vue/dist/reset.css'
import router from './router'
import BasicLayout from '@/layouts/BasicLayout.vue'

createApp(BasicLayout).use(router).use(Antd).mount('#app')