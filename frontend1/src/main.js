import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import { useAuthStore } from '@/store/auth'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import api from '@/services/api'
import * as XLSX from 'xlsx'

// 将XLSX添加到全局属性中
const app = createApp(App)
app.config.globalProperties.$xlsx = XLSX

// 注册Element Plus图标组件
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 使用插件
const pinia = createPinia()
app.use(pinia)
app.use(router)
app.use(ElementPlus)

// 初始化认证状态
const authStore = useAuthStore(pinia)
// 从localStorage获取token并设置到store中
const token = localStorage.getItem('token')
if (token) {
  authStore.token = token
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`
  console.log('应用初始化时设置认证头部')
}

// 挂载应用
app.mount('#app')