<template>
  <div class="sidebar">
    <div class="logo">
      <img src="@/assets/logo.png" alt="Logo" class="logo-img">
      <span class="logo-text">教师智能助手</span>
    </div>
    
    <el-menu
      :default-active="activeMenu"
      class="sidebar-menu"
      background-color="#304156"
      text-color="#bfcbd9"
      active-text-color="#409EFF"
      unique-opened
      router
    >
      <el-menu-item index="/dashboard">
        <el-icon><Odometer /></el-icon>
        <span>仪表盘</span>
      </el-menu-item>
      
      <el-sub-menu index="1">
        <template #title>
          <el-icon><Document /></el-icon>
          <span>资料中心</span>
        </template>
        <el-menu-item index="/materials">资料管理</el-menu-item>
      </el-sub-menu>
      
      <template v-if="userRole === 'teacher'">
        <el-sub-menu index="2">
          <template #title>
            <el-icon><User /></el-icon>
            <span>课堂考勤</span>
          </template>
          <el-menu-item index="/attendance">考勤管理</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="3">
          <template #title>
            <el-icon><TrendCharts /></el-icon>
            <span>成绩管理</span>
          </template>
          <el-menu-item index="/grades">成绩录入与查询</el-menu-item>
          <el-menu-item index="/courses">课程管理</el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="4">
          <template #title>
            <el-icon><Connection /></el-icon>
            <span>课堂互动</span>
          </template>
          <el-menu-item index="/classroom">人脸识别与座位表</el-menu-item>
        </el-sub-menu>
      </template>
      
      <template v-else>
        <el-menu-item index="/attendance">
          <el-icon><User /></el-icon>
          <span>我的考勤</span>
        </el-menu-item>
        
        <el-menu-item index="/grades">
          <el-icon><TrendCharts /></el-icon>
          <span>我的成绩</span>
        </el-menu-item>
      </template>
      
      <el-sub-menu index="5">
        <template #title>
          <el-icon><MagicStick /></el-icon>
          <span>智能模块</span>
        </template>
        <el-menu-item index="/ai/prediction">成绩预测</el-menu-item>
        <el-menu-item index="/ai/qa">智能问答</el-menu-item>
      </el-sub-menu>
    </el-menu>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/store/auth'

const route = useRoute()
const authStore = useAuthStore()

const activeMenu = computed(() => {
  const { meta, path } = route
  // if set path, the sidebar will highlight the path you set
  if (meta.activeMenu) {
    return meta.activeMenu
  }
  return path
})

const userRole = computed(() => {
  return authStore.user?.role || ''
})
</script>

<style scoped>
.sidebar {
  height: 100%;
  background-color: #304156;
  box-shadow: 2px 0 6px rgba(0, 21, 41, 0.35);
}

.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #2b3a4d;
  color: #fff;
  font-size: 18px;
  font-weight: bold;
}

.logo img {
  width: 32px;
  height: 32px;
  margin-right: 10px;
}

.sidebar-menu {
  border: none;
  height: calc(100% - 60px);
  overflow-y: auto;
}

.sidebar-menu::-webkit-scrollbar {
  width: 6px;
}

.sidebar-menu::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}
</style>