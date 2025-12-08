<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElDialog } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import GestureLock from '../../components/GestureLock.vue'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const creating = ref(false)
const title = ref('')
const detailVisible = ref(false)
const detailLoading = ref(false)
const qrCode = ref('')
const passcode = ref('')
const gestureDialogVisible = ref(false)
const teacherGesture = ref('')
const selectedMode = ref('qrcode') // 默认二维码模式

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

  if (selectedMode.value === 'gesture' && !teacherGesture.value) {
    ElMessage.warning('请先绘制手势图案')
    return
  }

  creating.value = true
  try {
    const data = {
      title: title.value,
      mode: selectedMode.value
    }

    if (selectedMode.value === 'gesture') {
      data.gesture_pattern = teacherGesture.value
    }

    await courseStore.addAttendance(data)
    ElMessage.success('创建成功')
    title.value = ''
    teacherGesture.value = ''
    selectedMode.value = 'qrcode'
    gestureDialogVisible.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '创建失败')
  } finally {
    creating.value = false
  }
}

const openGestureDialog = () => {
  if (!title.value) {
    ElMessage.warning('请输入签到标题')
    return
  }
  gestureDialogVisible.value = true
  teacherGesture.value = ''
}

const handleGestureComplete = (pattern) => {
  teacherGesture.value = pattern
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
        <p class="sub">支持二维码、手势、拍照点名，实时查看到课率并导出报表。</p>
      </div>
      <div class="actions" v-if="isManager">
        <el-input v-model="title" placeholder="请输入签到标题" style="width: 220px" />
        <el-select v-model="selectedMode" placeholder="选择签到模式" style="width: 120px">
          <el-option label="二维码" value="qrcode" />
          <el-option label="手势" value="gesture" />
        </el-select>
        <el-button
          v-if="selectedMode === 'gesture'"
          type="primary"
          @click="openGestureDialog"
        >
          绘制手势
        </el-button>
        <el-button
          type="primary"
          :loading="creating"
          @click="handleCreate"
        >
          发布签到
        </el-button>
      </div>
    </div>

    <el-card shadow="hover">
      <div class="session-list">
        <div v-for="item in courseStore.attendance" :key="item.id" class="session-card">
          <div>
            <p class="title">{{ item.title }}</p>
            <p class="meta">
              模式：{{ item.mode === 'gesture' ? '手势签到' : '二维码签到' }} ·
              开始：{{ item.start_at?.slice(11, 16) || item.start_at?.slice(0, 10) }}
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

    <!-- 手势绘制对话框 -->
    <el-dialog
      v-model="gestureDialogVisible"
      title="绘制手势图案"
      width="500px"
      :close-on-click-modal="false"
    >
      <div class="gesture-dialog">
        <p class="prompt-text">请绘制手势图案，学生需要按照此图案进行签到：</p>
        <p class="hint-text">连接至少4个点，图案不能重复</p>

        <div class="gesture-container">
          <GestureLock @complete="handleGestureComplete" />
        </div>

        <div v-if="teacherGesture" class="gesture-result">
          <p>已绘制图案：</p>
          <p class="pattern">{{ teacherGesture }}</p>
        </div>
      </div>

      <template #footer>
        <el-button @click="gestureDialogVisible = false">取消</el-button>
        <el-button
          type="primary"
          :disabled="!teacherGesture"
          @click="gestureDialogVisible = false"
        >
          确认
        </el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="detailVisible" size="40%" title="考勤详情">
      <div v-if="detailLoading">加载中...</div>
      <div v-else>
        <div class="detail-head">
          <div>
            <p class="title">{{ courseStore.attendanceDetail.session?.title }}</p>
            <p class="meta">
              模式：{{ courseStore.attendanceDetail.session?.mode === 'gesture' ? '手势签到' : '二维码签到' }} ·
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
  align-items: center;
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

.gesture-dialog {
  padding: 20px 0;
}

.prompt-text {
  margin: 0 0 8px;
  font-weight: 600;
  color: #0f172a;
}

.hint-text {
  margin: 0 0 20px;
  color: #64748b;
  font-size: 14px;
}

.gesture-container {
  display: flex;
  justify-content: center;
  margin: 24px 0;
}

.gesture-result {
  margin-top: 16px;
  padding: 12px;
  background: #f1f5f9;
  border-radius: 8px;
}

.pattern {
  font-family: monospace;
  font-size: 16px;
  color: #6366f1;
  font-weight: 600;
}

@media (max-width: 720px) {
  .session-card {
    grid-template-columns: 1fr;
  }
  .ops {
    justify-content: flex-start;
  }
  .actions {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
}
</style>
