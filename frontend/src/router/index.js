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
import StudentLayout from "@/layouts/StudentLayout.vue";
import StudentDashboard from "@/views/dashboard/StudentDashboard.vue";
import StudentMaterialsView from "@/views/materials/StudentMaterialsView.vue";
import StudentAttendanceView from "@/views/attendance/StudentAttendanceView.vue";
import StudentGradesView from "@/views/grades/StudentGradesView.vue";
import StudentInteractionView from "@/views/interaction/StudentInteractionView.vue";

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
    // 学生端路由
    {
      path: '/student',
      component: StudentLayout,
      meta: { requiresAuth: true },
      children: [
        {
          path: 'dashboard',
          name: 'student-dashboard',
          component: StudentDashboard,
          meta: { title: '学习总览', roles: ['student'] }
        },
        {
          path: 'materials',
          name: 'student-materials',
          component: StudentMaterialsView,
          meta: { title: '课程资料', roles: ['student'] }
        },
        {
          path: 'attendance',
          name: 'student-attendance',
          component: StudentAttendanceView,
          meta: { title: '课堂签到', roles: ['student'] }
        },
        {
          path: 'grades',
          name: 'student-grades',
          component: StudentGradesView,
          meta: { title: '我的成绩', roles: ['student'] }
        },
        {
          path: 'interaction',
          name: 'student-interaction',
          component: StudentInteractionView,
          meta: { title: '课堂互动', roles: ['student'] }
        },
        {
          path: 'assistant',
          name: 'student-assistant',
          component: StudentDashboard,
          meta: { title: '学习助手', roles: ['student'] }
        },
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

  // 角色权限控制
  if (auth.user) {
    const userRole = auth.user.role
    const routeRoles = to.meta?.roles

    // 学生只能访问学生端路由
    if (userRole === 'student' && !to.path.startsWith('/student')) {
      next('/student/dashboard')
      return
    }

    // 教师/管理员不能访问学生端路由
    if ((userRole === 'teacher' || userRole === 'admin') && to.path.startsWith('/student')) {
      next('/')
      return
    }

    // 检查路由角色限制
    if (routeRoles && !routeRoles.includes(userRole)) {
      next('/')
      return
    }

    // 学生不可访问成员管理
    if (to.name === 'members' && userRole === 'student') {
      next({ name: 'dashboard' })
      return
    }
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
