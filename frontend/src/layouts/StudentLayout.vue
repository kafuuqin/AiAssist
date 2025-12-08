<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '../stores/auth'
import { useCourseStore } from '../stores/course'
import {
  House,
  Document,
  Calendar,
  TrendCharts,
  ChatDotRound,
  MagicStick,
  User,
  SwitchButton
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const courseStore = useCourseStore()
const sidebarCollapsed = ref(false)
const activeMenu = ref('')

const menuItems = computed(() => [
  {
    index: '/student/dashboard',
    title: '学习总览',
    icon: House,
    roles: ['student']
  },
  {
    index: '/student/materials',
    title: '课程资料',
    icon: Document,
    roles: ['student']
  },
  {
    index: '/student/attendance',
    title: '课堂签到',
    icon: Calendar,
    roles: ['student']
  },
  {
    index: '/student/grades',
    title: '我的成绩',
    icon: TrendCharts,
    roles: ['student']
  },
  {
    index: '/student/interaction',
    title: '课堂互动',
    icon: ChatDotRound,
    roles: ['student']
  },
  {
    index: '/student/assistant',
    title: '学习助手',
    icon: MagicStick,
    roles: ['student']
  }
])

const currentCourse = computed(() => {
  return courseStore.activeCourse || { name: '选择课程', code: '' }
})

const handleMenuClick = (index) => {
  router.push(index)
}

const handleCourseChange = async (courseId) => {
  try {
    await courseStore.setActiveCourse(courseId)
    ElMessage.success(`已切换到 ${courseStore.activeCourse?.name}`)
  } catch (err) {
    ElMessage.error('切换课程失败')
  }
}

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}

onMounted(async () => {
  activeMenu.value = route.path
  // 加载学生课程数据 - 添加更安全的错误处理
  try {
    if (courseStore.courses.length === 0) {
      await courseStore.loadStudentCourses()
    }
  } catch (err) {
    console.error('加载课程数据失败:', err)
    // 静默处理错误，不影响页面渲染
  }
})
</script>

<template>
  <div class="layout">
    <!-- 侧边栏 -->
    <div class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span v-if="!sidebarCollapsed" class="logo-text">学生端</span>
        </div>
      </div>

      <!-- 课程选择 -->
      <div class="course-selector" v-if="!sidebarCollapsed">
        <el-select
          v-model="courseStore.activeCourseId"
          placeholder="选择课程"
          @change="handleCourseChange"
          style="width: 100%"
        >
          <el-option
            v-for="course in courseStore.courses"
            :key="course.id"
            :label="course.name"
            :value="course.id"
          >
            <span>{{ course.name }}</span>
            <span style="float: right; color: #8492a6; font-size: 13px">
              {{ course.code }}
            </span>
          </el-option>
        </el-select>
      </div>

      <!-- 菜单 -->
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        :collapse="sidebarCollapsed"
        @select="handleMenuClick"
      >
        <el-menu-item
          v-for="item in menuItems"
          :key="item.index"
          :index="item.index"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <template #title>{{ item.title }}</template>
        </el-menu-item>
      </el-menu>

      <!-- 用户信息 -->
      <div class="user-info">
        <el-dropdown trigger="click">
          <div class="user-dropdown">
            <el-avatar :size="32" :src="auth.user?.avatar">
              {{ auth.user?.name?.charAt(0) }}
            </el-avatar>
            <div v-if="!sidebarCollapsed" class="user-details">
              <div class="user-name">{{ auth.user?.name }}</div>
              <div class="user-role">学生</div>
            </div>
          </div>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item @click="handleLogout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 主内容区域 -->
    <div class="main-content">
      <div class="content-header">
        <div class="header-left">
          <el-button
            :icon="sidebarCollapsed ? 'Expand' : 'Fold'"
            @click="sidebarCollapsed = !sidebarCollapsed"
            text
          />
          <div class="breadcrumb">
            <span class="current-course">{{ currentCourse.name }}</span>
            <span class="course-code">{{ currentCourse.code }}</span>
          </div>
        </div>
        <div class="header-right">
          <span class="welcome">欢迎，{{ auth.user?.name }}</span>
        </div>
      </div>

      <div class="content-body">
        <router-view />
      </div>
    </div>
  </div>
</template>

<style scoped>
.layout {
  display: flex;
  height: 100vh;
  background: #f8fafc;
}

.sidebar {
  width: 240px;
  background: #0f172a;
  color: white;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 64px;
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #1e293b;
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo img {
  width: 32px;
  height: 32px;
}

.logo-text {
  font-size: 18px;
  font-weight: 700;
  color: white;
}

.course-selector {
  padding: 16px;
  border-bottom: 1px solid #1e293b;
}

.sidebar-menu {
  flex: 1;
  border: none;
  background: transparent;
}

.sidebar-menu :deep(.el-menu-item) {
  color: #cbd5e1;
  height: 48px;
  line-height: 48px;
}

.sidebar-menu :deep(.el-menu-item:hover) {
  background: #1e293b;
  color: white;
}

.sidebar-menu :deep(.el-menu-item.is-active) {
  background: #6366f1;
  color: white;
}

.user-info {
  padding: 16px;
  border-top: 1px solid #1e293b;
}

.user-dropdown {
  display: flex;
  align-items: center;
  gap: 12px;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: background 0.2s;
}

.user-dropdown:hover {
  background: #1e293b;
}

.user-details {
  flex: 1;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: white;
}

.user-role {
  font-size: 12px;
  color: #94a3b8;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}

.content-header {
  height: 64px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 24px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
}

.current-course {
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.course-code {
  font-size: 14px;
  color: #64748b;
}

.welcome {
  font-size: 14px;
  color: #64748b;
}

.content-body {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    z-index: 1000;
    height: 100vh;
  }

  .sidebar.collapsed {
    width: 0;
    overflow: hidden;
  }

  .main-content {
    margin-left: 0;
  }
}
</style>