<script setup>
import { computed, ref } from 'vue'
import { useRoute, useRouter, RouterView } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCourseStore } from '../stores/course'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const courseStore = useCourseStore()
const collapsed = ref(false)

const courseId = computed(() => route.params.courseId || courseStore.activeCourseId || 'demo')

const menus = computed(() => {
  const base = [
    { title: '总览', index: '/', path: '/' },
    { title: '资料中心', index: `/courses/${courseId.value}/materials`, path: `/courses/${courseId.value}/materials` },
    { title: '课堂考勤', index: `/courses/${courseId.value}/attendance`, path: `/courses/${courseId.value}/attendance` },
    { title: '成绩分析', index: `/courses/${courseId.value}/grades`, path: `/courses/${courseId.value}/grades` },
    { title: '课堂互动', index: `/courses/${courseId.value}/interaction`, path: `/courses/${courseId.value}/interaction` },
    { title: '智能中心', index: '/ai', path: '/ai' },
  ]
  // 拥有者才显示课程成员
  const course = courseStore.currentCourse
  const isOwner = course && auth.user && course.owner_id === auth.user.id
  if (isOwner) {
    base.splice(3, 0, { title: '课程成员', index: `/courses/${courseId.value}/members`, path: `/courses/${courseId.value}/members` })
  }
  return base
})

const activeMenu = computed(() => {
  const found = menus.value.find((item) => route.path.startsWith(item.path))
  return found?.index || '/'
})

const handleSelect = (index) => {
  router.push(index)
}

const handleLogout = () => {
  auth.logout()
  router.replace({ name: 'login' })
}

const handleCourseChange = (value) => {
  courseStore.setActiveCourse(value)
  if (route.params.courseId) {
    router.push({ ...route, params: { ...route.params, courseId: value } })
  }
  // 课程切换时加载成员等基础数据
  courseStore.loadMembers(value).catch(() => {})
}

const loadInitial = async () => {
  try {
    await courseStore.loadCourses()
  } catch (err) {
    ElMessage.error('加载课程失败，请稍后重试')
  }
}

loadInitial()
</script>

<template>
  <el-container class="app-layout">
    <el-aside :width="collapsed ? '72px' : '240px'" class="sidebar">
      <div class="brand" @click="handleSelect('/')">
        <div class="logo">TA</div>
        <div v-if="!collapsed" class="brand-text">
          <p class="title">教师助手</p>
          <p class="subtitle">智慧教学</p>
        </div>
      </div>
      <el-menu
        :default-active="activeMenu"
        class="menu"
        :collapse="collapsed"
        :collapse-transition="false"
        @select="handleSelect"
      >
        <el-menu-item v-for="item in menus" :key="item.index" :index="item.index">
          <span>{{ item.title }}</span>
        </el-menu-item>
      </el-menu>
      <div class="collapse-toggle">
        <el-button text size="small" @click="collapsed = !collapsed">
          {{ collapsed ? '展开' : '收起' }}
        </el-button>
      </div>
    </el-aside>
    <el-container class="main">
      <el-header class="header">
        <div class="header-left">
          <el-select
            v-if="courseStore.courses.length"
            v-model="courseStore.activeCourseId"
            placeholder="选择课程"
            size="small"
            style="min-width: 200px"
            @change="handleCourseChange"
          >
            <el-option v-for="c in courseStore.courses" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
          <span v-else class="crumb">当前课程：{{ courseId }}</span>
        </div>
        <div class="header-right">
          <el-avatar size="small" :src="auth.user?.avatar_url">{{ auth.user?.name?.[0] || 'T' }}</el-avatar>
          <div class="user-info">
            <p class="name">{{ auth.user?.name || '教师' }}</p>
            <p class="role">{{ auth.user?.role || 'teacher' }}</p>
          </div>
          <el-button text size="small" @click="handleLogout">退出</el-button>
        </div>
      </el-header>
      <el-main class="content">
        <RouterView />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: linear-gradient(135deg, #f8f9ff 0%, #f4f7ff 50%, #ffffff 100%);
}

.sidebar {
  background: #0f172a;
  color: #e2e8f0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 16px;
  cursor: pointer;
}

.logo {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  background: linear-gradient(135deg, #5a6ff0, #7b8dff);
  display: grid;
  place-items: center;
  font-weight: 800;
  color: #f8fafc;
}

.brand-text .title {
  font-size: 16px;
  font-weight: 700;
  margin: 0;
}

.brand-text .subtitle {
  font-size: 12px;
  margin: 0;
  color: #94a3b8;
}

.menu {
  border-right: none;
  background: transparent;
  flex: 1;
}

.menu :deep(.el-menu-item) {
  color: #cbd5e1;
  border-radius: 8px;
  margin: 4px 8px;
}

.menu :deep(.el-menu-item.is-active) {
  background: rgba(255, 255, 255, 0.08);
  color: #fff;
}

.menu :deep(.el-menu-item:hover) {
  background: rgba(255, 255, 255, 0.05);
}

.collapse-toggle {
  padding: 12px;
  text-align: center;
}

.main {
  display: flex;
  flex-direction: column;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 20px;
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(8px);
  border-bottom: 1px solid #e5e7eb;
}

.header-left .crumb {
  font-weight: 600;
  color: #111827;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #111827;
}

.user-info {
  line-height: 1.2;
}

.name {
  margin: 0;
  font-weight: 700;
}

.role {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}

.content {
  padding: 20px 24px 32px;
}

@media (max-width: 960px) {
  .sidebar {
    position: fixed;
    z-index: 10;
    height: 100vh;
    transform: translateX(0);
  }
  .main {
    margin-left: 72px;
  }
}
</style>
