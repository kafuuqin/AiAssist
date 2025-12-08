<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import GestureLock from '../../components/GestureLock.vue'
import { Calendar, Check, Clock, Close } from '@element-plus/icons-vue'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const checkingIn = ref(false)
const checkInDialogVisible = ref(false)
const currentSession = ref(null)
const studentGesture = ref('')
const gestureError = ref('')

const loadAttendance = async () => {
  if (!courseStore.activeCourseId) return
  loading.value = true
  try {
    await courseStore.loadStudentAttendance()
  } catch (err) {
    console.error('加载考勤失败:', err)
    ElMessage.error('加载考勤失败')
  } finally {
    loading.value = false
  }
}

const openSessions = computed(() => {
  return courseStore.studentAttendance.filter(item => 
    item.session?.status === 'open'
  )
})

const closedSessions = computed(() => {
  return courseStore.studentAttendance.filter(item => 
    item.session?.status === 'closed'
  )
})

const getAttendanceStatus = (attendanceItem) => {
  if (attendanceItem.record) { // 直接检查record字段是否有内容
    return { text: '已签到', type: 'success', icon: Check }
  }
  if (attendanceItem.session?.status === 'closed') {
    return { text: '已结束', type: 'info', icon: Close }
  }
  return { text: '未签到', type: 'warning', icon: Clock }
}

const openCheckIn = async (session) => {
  currentSession.value = session
  studentGesture.value = ''
  gestureError.value = ''
  checkInDialogVisible.value = true
}

const handleGestureComplete = (pattern) => {
  studentGesture.value = pattern
  gestureError.value = ''
  
  // 验证手势图案
  if (currentSession.value?.mode === 'gesture' && currentSession.value?.gesture_pattern) {
    if (pattern !== currentSession.value.gesture_pattern) {
      gestureError.value = '手势图案不匹配，请重新绘制'
    } else {
      gestureError.value = ''
    }
  }
}

// 移除updateAttendanceStatus函数，因为现在直接使用record字段判断
// 签到成功后，重新加载数据即可自动更新状态

const submitCheckIn = async () => {
  if (!studentGesture.value) {
    ElMessage.warning('请绘制手势图案')
    return
  }

  if (!currentSession.value) {
    ElMessage.error('签到会话不存在')
    return
  }

  // 如果是手势模式，验证手势图案
  if (currentSession.value.mode === 'gesture') {
    if (!currentSession.value.gesture_pattern) {
      ElMessage.error('该签到会话未设置手势图案')
      return
    }
    
    if (studentGesture.value !== currentSession.value.gesture_pattern) {
      ElMessage.error('手势图案不匹配，请重新绘制')
      return
    }
  }

  checkingIn.value = true
  try {
    await courseStore.studentCheckIn(currentSession.value.id, {
      evidence: studentGesture.value
    })
    ElMessage.success('签到成功')
    checkInDialogVisible.value = false
    
    // 重新加载数据确保状态同步（record字段会自动更新）
    await loadAttendance()
  } catch (err) {
    console.error('签到失败:', err)
    ElMessage.error('签到失败')
  } finally {
    checkingIn.value = false
  }
}

onMounted(() => {
  loadAttendance()
})
watch(() => courseStore.activeCourseId, loadAttendance)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>课堂签到</h2>
        <p class="sub">参与课堂签到，记录学习出勤</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else class="attendance-content">
      <!-- 进行中的签到 -->
      <div v-if="openSessions.length > 0" class="section">
        <h3 class="section-title">
          <el-icon><Clock /></el-icon>
          进行中的签到
        </h3>
        <div class="sessions-grid">
          <el-card 
            v-for="item in openSessions" 
            :key="item.session.id" 
            shadow="hover" 
            class="session-card"
          >
            <div class="session-header">
              <h4>{{ item.session.title }}</h4>
              <el-tag type="success" size="small">进行中</el-tag>
            </div>
            
            <div class="session-info">
              <div class="info-item">
                <span class="label">签到方式：</span>
                <span class="value">{{ item.session.mode === 'gesture' ? '手势签到' : '二维码签到' }}</span>
              </div>
              <div class="info-item">
                <span class="label">开始时间：</span>
                <span class="value">{{ new Date(item.session.start_at).toLocaleString() }}</span>
              </div>
            </div>

            <div class="session-actions">
              <el-button 
                v-if="!item.record"
                type="primary" 
                size="small"
                @click="openCheckIn(item.session)"
              >
                立即签到
              </el-button>
              <el-tag v-else type="success" size="small">已签到</el-tag>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 已结束的签到 -->
      <div v-if="closedSessions.length > 0" class="section">
        <h3 class="section-title">
          <el-icon><Calendar /></el-icon>
          历史签到记录
        </h3>
        <div class="sessions-grid">
          <el-card 
            v-for="item in closedSessions" 
            :key="item.session.id" 
            shadow="hover" 
            class="session-card"
          >
            <div class="session-header">
              <h4>{{ item.session.title }}</h4>
              <el-tag :type="getAttendanceStatus(item).type" size="small">
                {{ getAttendanceStatus(item).text }}
              </el-tag>
            </div>
            
            <div class="session-info">
              <div class="info-item">
                <span class="label">签到时间：</span>
                <span class="value">{{ new Date(item.session.start_at).toLocaleString() }}</span>
              </div>
              <div v-if="item.record" class="info-item">
                <span class="label">签到状态：</span>
                <span class="value">{{ item.record.status === 'present' ? '正常' : '异常' }}</span>
              </div>
            </div>

            <div class="session-meta">
              <span class="meta-text">签到方式：{{ item.session.mode === 'gesture' ? '手势签到' : '二维码签到' }}</span>
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="courseStore.studentAttendance.length === 0" class="empty">
        <el-empty description="暂无签到记录" />
      </div>
    </div>

    <!-- 签到对话框 -->
    <el-dialog 
      v-model="checkInDialogVisible" 
      :title="currentSession?.mode === 'gesture' ? '手势签到' : '课堂签到'" 
      width="500px"
      :close-on-click-modal="false"
    >
      <div v-if="currentSession" class="checkin-dialog">
        <div class="session-info">
          <h4>{{ currentSession.title }}</h4>
          <p class="session-desc">
            {{ currentSession.mode === 'gesture' ? '请按照教师设置的手势图案进行签到' : '请按照要求完成签到' }}
          </p>
        </div>

        <div v-if="currentSession.mode === 'gesture'" class="gesture-section">
          <p class="prompt-text">请绘制手势图案进行签到：</p>
          <p class="hint-text">连接至少4个点，图案不能重复</p>
          
          <div class="gesture-container">
            <GestureLock @complete="handleGestureComplete" />
          </div>

          <div v-if="gestureError" class="gesture-error">
            <el-alert :title="gestureError" type="error" show-icon :closable="false" />
          </div>

          <div v-if="studentGesture" class="gesture-result">
            <p>已绘制图案：</p>
            <p class="pattern">{{ studentGesture }}</p>
          </div>
        </div>

        <div v-else class="qrcode-section">
          <p class="prompt-text">请扫描二维码完成签到：</p>
          <div class="qrcode-container">
            <!-- 这里可以添加二维码显示组件 -->
            <div class="qrcode-placeholder">
              <el-icon size="48"><Check /></el-icon>
              <p>二维码签到功能</p>
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="checkInDialogVisible = false">取消</el-button>
        <el-button 
          v-if="currentSession?.mode === 'gesture'"
          type="primary" 
          :loading="checkingIn"
          :disabled="!studentGesture"
          @click="submitCheckIn"
        >
          确认签到
        </el-button>
        <el-button 
          v-else
          type="primary" 
          :loading="checkingIn"
          @click="submitCheckIn"
        >
          确认签到
        </el-button>
      </template>
    </el-dialog>
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

.section {
  margin-bottom: 32px;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 16px;
  color: #0f172a;
  font-size: 18px;
}

.sessions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.session-card {
  transition: all 0.2s;
}

.session-card:hover {
  transform: translateY(-2px);
}

.session-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 12px;
}

.session-header h4 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
}

.session-info {
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.label {
  color: #64748b;
  font-size: 14px;
}

.value {
  color: #0f172a;
  font-weight: 500;
}

.session-actions {
  display: flex;
  justify-content: flex-end;
}

.session-meta {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #f1f5f9;
}

.meta-text {
  font-size: 12px;
  color: #94a3b8;
}

.checkin-dialog .session-info {
  margin-bottom: 20px;
}

.checkin-dialog h4 {
  margin: 0 0 8px;
  color: #0f172a;
}

.session-desc {
  margin: 0;
  color: #64748b;
}

.gesture-section {
  margin-top: 20px;
}

.prompt-text {
  margin: 0 0 8px;
  font-weight: 600;
  color: #0f172a;
}

.hint-text {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.gesture-container {
  display: flex;
  justify-content: center;
  margin: 24px 0;
}

.gesture-error {
  margin: 16px 0;
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

.qrcode-section {
  margin-top: 20px;
}

.qrcode-container {
  display: flex;
  justify-content: center;
  margin: 24px 0;
}

.qrcode-placeholder {
  text-align: center;
  padding: 40px;
  background: #f8fafc;
  border-radius: 8px;
  color: #64748b;
}

.loading {
  padding: 40px 0;
}

.empty {
  padding: 60px 0;
}

@media (max-width: 768px) {
  .sessions-grid {
    grid-template-columns: 1fr;
  }
}
</style>