<template>
  <div id="app">
    <router-view v-slot="{ Component }">
      <template v-if="$route.meta.requiresAuth === false">
        <component :is="Component" />
      </template>
      <template v-else>
        <el-container class="layout-container">
          <el-aside :width="isCollapse ? '64px' : '200px'" class="sidebar-container">
            <Sidebar />
          </el-aside>
          
          <el-container>
            <el-header class="navbar-container">
              <Navbar @toggle-sidebar="toggleSidebar" />
            </el-header>
            
            <el-main class="main-container">
              <component :is="Component" />
            </el-main>
          </el-container>
        </el-container>
      </template>
    </router-view>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '@/store/auth'
import Sidebar from '@/components/Layout/Sidebar.vue'
import Navbar from '@/components/Layout/Navbar.vue'

const authStore = useAuthStore()

// 侧边栏折叠状态
const isCollapse = ref(false)

// 切换侧边栏折叠状态
const toggleSidebar = () => {
  isCollapse.value = !isCollapse.value
}

// 检查用户是否已认证
const isAuthenticated = computed(() => authStore.isAuthenticated)
</script>

<style>
#app {
  height: 100vh;
  overflow: hidden;
}

.layout-container {
  height: 100%;
}

.sidebar-container {
  transition: width 0.28s;
  background-color: #304156;
}

.navbar-container {
  padding: 0;
  height: 60px;
}

.main-container {
  padding: 20px;
  overflow: auto;
  background-color: #f0f2f5;
  height: calc(100vh - 60px);
}
</style>