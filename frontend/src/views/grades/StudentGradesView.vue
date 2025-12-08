<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import { fetchStudentGrades } from '../../api/modules/student'
import { TrendCharts, DocumentChecked } from '@element-plus/icons-vue'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const grades = ref([])

const myGrades = computed(() => {
  return grades.value.filter(grade => String(grade.student_id) === String(auth.user?.id))
})

const averageScore = computed(() => {
  if (myGrades.value.length === 0) return 0
  const total = myGrades.value.reduce((sum, grade) => sum + (grade.score || 0), 0)
  return (total / myGrades.value.length).toFixed(1)
})

const highestScore = computed(() => {
  if (myGrades.value.length === 0) return 0
  return Math.max(...myGrades.value.map(grade => grade.score || 0))
})

const loadGrades = async () => {
  if (!courseStore.activeCourseId) return
  
  loading.value = true
  try {
    const response = await fetchStudentGrades(courseStore.activeCourseId)
    grades.value = response.data.grades || []  // 修复：正确提取grades数组
  } catch (err) {
    ElMessage.error('加载成绩失败')
  } finally {
    loading.value = false
  }
}

onMounted(loadGrades)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>我的成绩</h2>
        <p class="sub">查看课程成绩和统计信息</p>
      </div>
    </div>

    <div class="stats-grid">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <el-icon :size="32" color="#6366f1"><TrendCharts /></el-icon>
          <div>
            <p class="stat-label">平均成绩</p>
            <p class="stat-value">{{ averageScore }}</p>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <el-icon :size="32" color="#22c55e"><DocumentChecked /></el-icon>
          <div>
            <p class="stat-label">最高成绩</p>
            <p class="stat-value">{{ highestScore }}</p>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <el-icon :size="32" color="#f59e0b"><DocumentChecked /></el-icon>
          <div>
            <p class="stat-label">已批改作业</p>
            <p class="stat-value">{{ myGrades.length }}</p>
          </div>
        </div>
      </el-card>
    </div>

    <el-card shadow="hover">
      <template #header>
        <div class="card-header">
          <h3>成绩明细</h3>
        </div>
      </template>

      <div v-if="loading" class="loading">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="myGrades.length === 0" class="empty">
        <el-empty description="暂无成绩记录" />
      </div>

      <div v-else class="grades-table">
        <el-table :data="myGrades" style="width: 100%">
          <el-table-column prop="assignment_title" label="作业名称" min-width="200" />
          <el-table-column prop="score" label="成绩" width="100">
            <template #default="{ row }">
              <span :class="['score', { 'high-score': row.score >= 90, 'low-score': row.score < 60 }]">
                {{ row.score }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="full_score" label="满分" width="80" />
          <el-table-column prop="comment" label="评语" min-width="200" show-overflow-tooltip />
          <el-table-column prop="graded_at" label="批改时间" width="120" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.page-header h2 {
  margin: 0 0 8px;
  color: #0f172a;
}

.sub {
  margin: 0;
  color: #64748b;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  transition: all 0.2s;
}

.stat-card:hover {
  transform: translateY(-2px);
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-label {
  margin: 0 0 4px;
  font-size: 14px;
  color: #64748b;
}

.stat-value {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #0f172a;
}

.card-header h3 {
  margin: 0;
  color: #0f172a;
}

.grades-table {
  margin-top: 16px;
}

.score {
  font-weight: 600;
  padding: 4px 8px;
  border-radius: 4px;
}

.high-score {
  background: #dcfce7;
  color: #166534;
}

.low-score {
  background: #fee2e2;
  color: #dc2626;
}

.loading {
  padding: 40px 0;
}

.empty {
  padding: 60px 0;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>