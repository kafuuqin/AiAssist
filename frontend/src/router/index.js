import { createRouter, createWebHistory } from 'vue-router'
import AppLayout from '../layouts/AppLayout.vue'
import LoginView from '../views/auth/LoginView.vue'
import RegisterView from '../views/auth/RegisterView.vue'
import DashboardHome from '../views/dashboard/DashboardHome.vue'
import MaterialsView from '../views/materials/MaterialsView.vue'
import AttendanceView from '../views/attendance/AttendanceView.vue'
import GradesView from '../views/grades/GradesView.vue'
import InteractionView from '../views/interaction/InteractionView.vue'
import IntelligenceHub from '../views/ai/IntelligenceHub.vue'
import MembersView from '../views/members/MembersView.vue'
import { useAuthStore } from '../stores/auth'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { public: true, title: '登录 - 教师智能助手' },
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { public: true, title: '注册 - 教师智能助手' },
    },
    {
      path: '/',
      component: AppLayout,
      meta: { requiresAuth: true },
      children: [
        { path: '', name: 'dashboard', component: DashboardHome, meta: { title: '总览' } },
        {
          path: 'courses/:courseId/materials',
          name: 'materials',
          component: MaterialsView,
          meta: { title: '资料中心' },
        },
        {
          path: 'courses/:courseId/attendance',
          name: 'attendance',
          component: AttendanceView,
          meta: { title: '课堂考勤' },
        },
        {
          path: 'courses/:courseId/members',
          name: 'members',
          component: MembersView,
          meta: { title: '课程成员' },
        },
        {
          path: 'courses/:courseId/grades',
          name: 'grades',
          component: GradesView,
          meta: { title: '成绩分析' },
        },
        {
          path: 'courses/:courseId/interaction',
          name: 'interaction',
          component: InteractionView,
          meta: { title: '课堂互动' },
        },
        { path: 'ai', name: 'ai-hub', component: IntelligenceHub, meta: { title: '智能中心' } },
      ],
    },
    { path: '/:pathMatch(.*)*', redirect: '/' },
  ],
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  const isPublic = to.meta?.public
  if (!isPublic && !auth.user && auth.accessToken?.value) {
    auth.fetchMe().catch(() => auth.logout())
  }
  if (!isPublic && !auth.isAuthenticated) {
    next({ name: 'login', query: { redirect: to.fullPath } })
    return
  }
  // 角色限制：学生不可访问成员管理
  if (to.name === 'members' && auth.user?.role === 'student') {
    next({ name: 'dashboard' })
    return
  }
  if (to.name === 'login' && auth.isAuthenticated) {
    next({ name: 'dashboard' })
    return
  }
  if (to.meta?.title) {
    document.title = `${to.meta.title} - 教师智能助手`
  }
  next()
})

export default router
