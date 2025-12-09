import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import api, { updateAuthToken } from '@/services/api'

// 公共页面
const Login = () => import('@/views/Login.vue')
const Register = () => import('@/views/Register.vue')

// 需要认证的页面
const Dashboard = () => import('@/views/Dashboard.vue')
const Materials = () => import('@/views/Materials.vue')
const Attendance = () => import('@/views/Attendance.vue')
const Grades = () => import('@/views/Grades.vue')
const Classroom = () => import('@/views/Classroom.vue')
const Profile = () => import('@/views/Profile.vue')
const AI = () => import('@/views/AI.vue')

const routes = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    component: Login,
    meta: { requiresAuth: false }
  },
  {
    path: '/register',
    component: Register,
    meta: { requiresAuth: false }
  },
  {
    path: '/dashboard',
    component: Dashboard,
    meta: { requiresAuth: true }
  },
  {
    path: '/materials',
    component: Materials,
    meta: { requiresAuth: true }
  },
  {
    path: '/attendance',
    component: Attendance,
    meta: { requiresAuth: true }
  },
  {
    path: '/grades',
    component: Grades,
    meta: { requiresAuth: true }
  },
  {
    path: '/classroom',
    component: Classroom,
    meta: { requiresAuth: true }
  },
  {
    path: '/profile',
    component: Profile,
    meta: { requiresAuth: true }
  },
  {
    path: '/courses',
    component: () => import('@/views/Courses.vue'),
    meta: { requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/ai',
    component: AI,
    meta: { requiresAuth: true },
    children: [
      {
        path: 'prediction',
        name: 'GradePrediction',
        component: () => import('@/views/AI.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'qa',
        name: 'AIQA',
        component: () => import('@/views/AI.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  console.log('路由守卫:', { to: to.path, from: from.path, isAuthenticated: authStore.isAuthenticated })
  
  // 检查路由是否需要认证
  if (to.meta.requiresAuth !== false) {
    // 需要认证的路由
    if (authStore.isAuthenticated) {
      // 检查是否有基于角色的访问限制
      if (to.meta.role && authStore.user.role !== to.meta.role) {
        // 用户角色不符合要求，重定向到仪表盘
        next('/dashboard')
        return
      }
      
      console.log('允许访问受保护路由')
      next()
    } else {
      // 检查本地存储中是否有token
      const token = localStorage.getItem('token')
      if (token) {
        // 有token但store中没有，尝试设置
        authStore.token = token
        // 验证token有效性
        try {
          const response = await api.get('/auth/profile')
          authStore.user = response.data
          // 同步用户信息到localStorage
          localStorage.setItem('user', JSON.stringify(response.data))
          // 使用专用函数更新认证令牌
          updateAuthToken(token)
          // 更新store中的用户信息
          authStore.user = response.data
          // 等待一小段时间确保token设置完成
          await new Promise(resolve => setTimeout(resolve, 50))
          
          // 再次检查是否有基于角色的访问限制
          if (to.meta.role && authStore.user.role !== to.meta.role) {
            // 用户角色不符合要求，重定向到仪表盘
            next('/dashboard')
            return
          }
          
          console.log('Token有效，允许访问受保护路由')
          next()
        } catch (error) {
          // Token无效，清除并重定向到登录页
          console.log('Token无效，清除认证信息并重定向到登录页')
          authStore.logout()
          next('/login')
        }
      } else {
        // 未认证，重定向到登录页
        console.log('未认证，重定向到登录页')
        next('/login')
      }
    }
  } else {
    // 不需要认证的路由 (如登录页)
    if (to.path === '/login' && authStore.isAuthenticated) {
      // 已认证用户访问登录页时重定向到仪表盘
      console.log('已认证用户访问登录页，重定向到仪表盘')
      next('/dashboard')
    } else {
      next()
    }
  }
})

export default router