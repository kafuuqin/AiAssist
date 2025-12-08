<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '@/stores/course.js'
import { useAuthStore } from '@/stores/auth.js'
import SmartAttendanceDialog from '@/components/SmartAttendanceDialog.vue'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const creating = ref(false)
const title = ref('')
const detailVisible = ref(false)
const detailLoading = ref(false)
const qrCode = ref('')
const passcode = ref('')

const smartVisible = ref(false)
const smartSessionId = ref(null)

const load = async () => {
  if (!courseStore.activeCourseId) return
  loading.value = true
  try {
    await courseStore.loadAttendance()
  } catch (err) {
    ElMessage.error('加载考勤失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!title.value) {
    ElMessage.warning('请输入签到标题')
    return
  }
  creating.value = true
  try {
    await courseStore.addAttendance({ title: title.value })
    ElMessage.success('创建成功')
    title.value = ''
    await load()
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '创建失败')
  } finally {
    creating.value = false
  }
}

const openDetail = async (sessionId) => {
  detailVisible.value = true
  detailLoading.value = true
  try {
    await courseStore.loadAttendanceDetail(sessionId)
    qrCode.value = `签到-${sessionId}-${Date.now()}`
    passcode.value = Math.random().toString(36).slice(2, 8)
  } catch (err) {
    ElMessage.error('加载详情失败')
  } finally {
    detailLoading.value = false
  }
}

// 打开智能点到
const openSmartAttendance = () => {
  const openSessions = (courseStore.attendance || []).filter(
      (s) => s.status === 'open'
  )
  if (!openSessions.length) {
    ElMessage.warning('请先发布一个“进行中”的签到任务')
    return
  }
  smartSessionId.value = openSessions[0].id
  smartVisible.value = true
}

// 智能点到完成回调
const handleSmartFinished = async (payload) => {
  smartVisible.value = false
  await load()
  if (payload && payload.sessionId) {
    await openDetail(payload.sessionId)
  }
}

const handleExport = async (sessionId) => {
  if (!sessionId) return
  try {
    const data = await courseStore.loadAttendanceDetail(sessionId)
    const rows = (data.records || []).map(
        (r) => `${r.student_id},${r.status},${r.created_at || ''},${r.evidence || ''}`
    )
    const csv = ['student_id,status,created_at,evidence', ...rows].join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `attendance_${sessionId}.csv`
    link.click()
    window.URL.revokeObjectURL(url)
  } catch (err) {
    ElMessage.error('导出失败')
  }
}

const isManager = computed(() => {
  const course = courseStore.currentCourse
  if (!auth.user) return false
  if (auth.user.role === 'admin') return true
  if (course && course.owner_id === auth.user.id) return true
  return auth.user.role === 'teacher'
})

onMounted(load)
watch(
    () => courseStore.activeCourseId,
    () => load()
)
</script>



<template>
  <div class="page">
    <div class="page-head">
      <div>
        <p class="eyebrow">课堂考勤</p>
        <h2>签到任务与实时到课</h2>
        <p class="sub">支持二维码、口令、拍照点名，实时查看到课率并导出报表。</p>
      </div>
      <div class="actions" v-if="isManager">
        <el-input v-model="title" placeholder="请输入签到标题" style="width: 220px" />
        <el-button type="primary" :loading="creating" @click="handleCreate">发布签到</el-button>
        <el-button type="success" plain @click="openSmartAttendance">智能点到</el-button>
      </div>
    </div>

    <el-card shadow="hover">
      <div class="session-list">
        <div v-for="item in courseStore.attendance" :key="item.id" class="session-card">
          <div>
            <p class="title">{{ item.title }}</p>
            <p class="meta">
              模式：{{ item.mode }} · 开始：{{ item.start_at?.slice(11, 16) || item.start_at?.slice(0, 10) }}
            </p>
            <el-tag :type="item.status === 'open' ? 'success' : 'info'">{{ item.status }}</el-tag>
          </div>
          <div class="ops">
            <el-button text size="small" @click="openDetail(item.id)">查看详情</el-button>
            <el-button text size="small" type="primary" @click="handleExport(item.id)">导出</el-button>
          </div>
        </div>
        <el-empty v-if="!courseStore.attendance.length && !loading" description="暂无考勤记录" />
      </div>
    </el-card>

    <el-drawer v-model="detailVisible" size="40%" title="考勤详情">
      <div v-if="detailLoading">加载中...</div>
      <div v-else>
        <div class="detail-head">
          <div>
            <p class="title">{{ courseStore.attendanceDetail.session?.title }}</p>
            <p class="meta">
              模式：{{ courseStore.attendanceDetail.session?.mode }} ·
              {{ courseStore.attendanceDetail.session?.start_at?.slice(0, 19) }}
            </p>
          </div>
          <div class="tokens">
            <el-tag type="success">二维码：{{ qrCode }}</el-tag>
            <el-tag type="info">口令：{{ passcode }}</el-tag>
          </div>
        </div>
        <el-table :data="courseStore.attendanceDetail.records" size="small" style="margin-top: 12px">
          <el-table-column prop="student_id" label="学生ID" width="120" />
          <el-table-column prop="status" label="状态" width="100" />
          <el-table-column prop="created_at" label="签到时间" />
          <el-table-column prop="evidence" label="凭证" />
        </el-table>
      </div>
    </el-drawer>
    <SmartAttendanceDialog
        v-model:visible="smartVisible"
        :session-id="smartSessionId"
        :course-id="courseStore.activeCourseId"
        @finished="handleSmartFinished"
    />

  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.page-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.eyebrow {
  letter-spacing: 0.1em;
  color: #94a3b8;
  font-weight: 700;
  margin-bottom: 6px;
}

.sub {
  margin: 0;
  color: #64748b;
}

.actions {
  display: flex;
  gap: 10px;
}

.session-list {
  display: grid;
  gap: 12px;
}

.session-card {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 12px;
  padding: 12px 4px;
  border-bottom: 1px solid #f1f5f9;
}

.session-card:last-child {
  border-bottom: none;
}

.title {
  margin: 0 0 6px;
  font-weight: 700;
  color: #0f172a;
}

.meta {
  margin: 0 0 8px;
  color: #94a3b8;
}

.ops {
  display: flex;
  align-items: center;
  gap: 8px;
}

@media (max-width: 720px) {
  .session-card {
    grid-template-columns: 1fr;
  }
  .ops {
    justify-content: flex-start;
  }
}
</style>
