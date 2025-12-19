<template>
  <div class="dashboard">
    <el-card class="welcome-card">
      <h2>欢迎使用教师智能助手</h2>
      <p>您好，{{ currentUser?.username }} ({{ roleMap[currentUser?.role] }})</p>
    </el-card>

    <el-row :gutter="20" class="stats-row">
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#409EFF"><Document /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.materials }}</div>
              <div class="stat-label">资料数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6" v-if="isTeacher">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#67C23A"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.students }}</div>
              <div class="stat-label">学生人数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#E6A23C"><Checked /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.attendance }}</div>
              <div class="stat-label">{{ isTeacher ? '今日考勤' : '我的考勤' }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon class="stat-icon" color="#F56C6C"><TrendCharts /></el-icon>
            <div class="stat-info">
              <div class="stat-number">{{ stats.grades }}</div>
              <div class="stat-label">{{ isTeacher ? '成绩记录' : '我的成绩' }}</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="charts-row">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成绩趋势</span>
            </div>
          </template>
          <div ref="chartContainer" style="height: 300px;"></div>
        </el-card>
      </el-col>
      
      <el-col :span="8">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>最新活动</span>
            </div>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(activity, index) in activities"
              :key="index"
              :timestamp="activity.timestamp"
              placement="top"
            >
              <el-card>
                <h4>{{ activity.title }}</h4>
                <p>{{ activity.content }}</p>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import * as echarts from 'echarts'

const authStore = useAuthStore()
const isTeacher = computed(() => authStore.user?.role === 'teacher')

const chartContainer = ref()
let chart = null

const currentUser = computed(() => authStore.currentUser)

const roleMap = {
  teacher: '教师',
  student: '学生',
  admin: '管理员'
}

const stats = ref({
  materials: 24,
  students: 42,
  attendance: 38,
  grades: 126
})

const activities = ref([
  {
    timestamp: '2023-05-15',
    title: '资料上传',
    content: '数学课件第一章已上传'
  },
  {
    timestamp: '2023-05-14',
    title: '成绩录入',
    content: '期中考试成绩已录入完毕'
  },
  {
    timestamp: '2023-05-13',
    title: '考勤统计',
    content: '本周考勤统计报告已生成'
  },
  {
    timestamp: '2023-05-12',
    title: '系统更新',
    content: '教师智能助手系统已更新至v1.2.0'
  }
])

onMounted(() => {
  initChart()
})

const initChart = () => {
  if (chartContainer.value) {
    chart = echarts.init(chartContainer.value)
    
    const option = {
      tooltip: {
        trigger: 'axis'
      },
      xAxis: {
        type: 'category',
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
      },
      yAxis: {
        type: 'value'
      },
      series: [
        {
          data: [82, 93, 88, 90, 95, 87, 92],
          type: 'line',
          smooth: true,
          itemStyle: {
            color: '#409EFF'
          }
        }
      ]
    }
    
    chart.setOption(option)
  }
}
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.welcome-card {
  margin-bottom: 20px;
}

.welcome-card h2 {
  margin-bottom: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  height: 120px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-icon {
  font-size: 40px;
  margin-right: 20px;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  color: #999;
}

.charts-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>