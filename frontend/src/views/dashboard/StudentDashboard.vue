<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import { ElMessage } from 'element-plus'
import { ArrowRight } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { fetchStudentDashboard } from '../../api/modules/student'

const router = useRouter()
const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const dashboardData = ref({})

const myCourses = computed(() => courseStore.courses || [])

const stats = computed(() => {
  const data = dashboardData.value
  return [
    { title: '我的课程', value: myCourses.value.length, color: '#6366f1' },
    { title: '平均成绩', value: data.avg_score || '--', color: '#22c55e' },
    { title: '待完成作业', value: data.pending_assignments || 0, color: '#f59e0b' },
    { title: '出勤率', value: data.attendance_rate ? `${data.attendance_rate}%` : '--', color: '#10b981' },
  ]
})

const recentActivities = computed(() => {
  const activities = dashboardData.value.recent_activities || []
  return activities.map(activity => ({
    time: dayjs(activity.created_at).format('HH:mm'),
    title: activity.title,
    type: activity.type
  }))
})

const loadData = async () => {
  loading.value = true
  try {
    // 确保课程数据已加载
    if (courseStore.courses.length === 0) {
      await courseStore.loadStudentCourses()
    }
    
    if (courseStore.activeCourseId) {
      const response = await fetchStudentDashboard(courseStore.activeCourseId)
      dashboardData.value = response.data
      await courseStore.loadGrades()
    }
  } catch (err) {
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleCourseClick = (courseId) => {
  courseStore.setActiveCourse(courseId)
  router.push(`/student/materials`)
}

onMounted(loadData)
</script>

<template>
  <div class="dashboard-container">
    <div class="dashboard-header">
      <h1>学生仪表板</h1>
      <p>欢迎回来，{{ auth.user?.name || '学生' }}！</p>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <div 
        v-for="stat in stats" 
        :key="stat.title"
        class="stat-card"
        :style="{ borderLeftColor: stat.color }"
      >
        <div class="stat-content">
          <div class="stat-value">{{ stat.value }}</div>
          <div class="stat-title">{{ stat.title }}</div>
        </div>
      </div>
    </div>

    <!-- 我的课程 -->
    <div class="section">
      <div class="section-header">
        <h2>我的课程</h2>
        <el-button type="primary" link :icon="ArrowRight">查看全部</el-button>
      </div>
      <div class="courses-grid">
        <div 
          v-for="course in myCourses" 
          :key="course.id"
          class="course-card"
          @click="handleCourseClick(course.id)"
        >
          <div class="course-info">
            <h3>{{ course.name }}</h3>
            <p>{{ course.teacher_name }}</p>
            <span class="course-code">{{ course.code }}</span>
          </div>
          <div class="course-stats">
            <div class="stat">
              <span class="label">作业</span>
              <span class="value">{{ course.assignment_count || 0 }}</span>
            </div>
            <div class="stat">
              <span class="label">成绩</span>
              <span class="value">{{ course.avg_score || '--' }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 最近活动 -->
    <div class="section">
      <div class="section-header">
        <h2>最近活动</h2>
      </div>
      <div class="activities-list">
        <div 
          v-for="activity in recentActivities" 
          :key="activity.title + activity.time"
          class="activity-item"
        >
          <div class="activity-time">{{ activity.time }}</div>
          <div class="activity-content">
            <div class="activity-title">{{ activity.title }}</div>
            <div class="activity-type">{{ activity.type }}</div>
          </div>
        </div>
        <div v-if="recentActivities.length === 0" class="no-activities">
          暂无活动记录
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-container {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.dashboard-header {
  margin-bottom: 30px;
}

.dashboard-header h1 {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.dashboard-header p {
  color: #6b7280;
  font-size: 16px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  border-left: 4px solid;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #1f2937;
  margin-bottom: 8px;
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 30px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.section-header h2 {
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
}

.courses-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.course-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  cursor: pointer;
  transition: all 0.2s;
}

.course-card:hover {
  border-color: #6366f1;
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.1);
}

.course-info h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.course-info p {
  color: #6b7280;
  margin-bottom: 8px;
}

.course-code {
  background: #f3f4f6;
  color: #374151;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.course-stats {
  display: flex;
  gap: 20px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f3f4f6;
}

.stat {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.stat .label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat .value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.activities-list {
  space-y: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f3f4f6;
}

.activity-item:last-child {
  border-bottom: none;
}

.activity-time {
  background: #f3f4f6;
  color: #374151;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-right: 16px;
  min-width: 60px;
  text-align: center;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 4px;
}

.activity-type {
  font-size: 12px;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.no-activities {
  text-align: center;
  color: #6b7280;
  padding: 40px;
  font-style: italic;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: 1fr;
  }
  
  .courses-grid {
    grid-template-columns: 1fr;
  }
  
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>