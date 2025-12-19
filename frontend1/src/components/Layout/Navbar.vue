<template>
  <div class="navbar">
    <div class="navbar-left">
      <el-icon class="menu-toggle" @click="toggleSidebar">
        <Expand v-if="isCollapse" />
        <Fold v-else />
      </el-icon>
      <span class="page-title">{{ pageTitle }}</span>
    </div>
    
    <div class="navbar-right">
      <div class="user-info">
        <el-dropdown @command="handleUserCommand">
          <div class="user-avatar">
            <el-avatar :size="32" icon="UserFilled" />
            <span class="username">{{ currentUser?.username }}</span>
          </div>
          
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>
                个人中心
              </el-dropdown-item>
              <el-dropdown-item command="settings">
                <el-icon><Setting /></el-icon>
                设置
              </el-dropdown-item>
              <el-dropdown-item divided command="logout">
                <el-icon><SwitchButton /></el-icon>
                退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage, ElMessageBox } from 'element-plus'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const emit = defineEmits(['toggle-sidebar'])

const isCollapse = computed(() => {
  return false // 这里可以根据实际需要连接到侧边栏的折叠状态
})

const currentUser = computed(() => authStore.currentUser)

const pageTitle = computed(() => {
  // 根据路由动态设置页面标题
  const routeMap = {
    '/dashboard': '仪表盘',
    '/materials': '资料中心',
    '/attendance': '考勤管理',
    '/grades': '成绩管理',
    '/classroom': '课堂互动',
    '/ai/prediction': '成绩预测',
    '/ai/qa': '智能问答'
  }
  
  return routeMap[route.path] || '教师智能助手'
})

const toggleSidebar = () => {
  emit('toggle-sidebar')
}

const handleUserCommand = async (command) => {
  switch (command) {
    case 'profile':
      ElMessage.info('个人中心功能将在后续版本中实现')
      break
    case 'settings':
      ElMessage.info('设置功能将在后续版本中实现')
      break
    case 'logout':
      try {
        await ElMessageBox.confirm('确定要退出登录吗？', '提示', {
          type: 'warning'
        })
        
        authStore.logout()
        router.push('/login')
        ElMessage.success('已退出登录')
      } catch (error) {
        if (error !== 'cancel') {
          ElMessage.error('退出登录失败')
        }
      }
      break
  }
}
</script>

<style scoped>
.navbar {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
}

.navbar-left {
  display: flex;
  align-items: center;
}

.menu-toggle {
  font-size: 20px;
  cursor: pointer;
  margin-right: 20px;
}

.page-title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.navbar-right {
  display: flex;
  align-items: center;
}

.user-info {
  margin-left: 20px;
}

.user-avatar {
  display: flex;
  align-items: center;
  cursor: pointer;
}

.username {
  margin-left: 10px;
  font-size: 14px;
  color: #333;
}
</style>