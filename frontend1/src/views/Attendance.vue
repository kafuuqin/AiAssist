<template>
  <div class="attendance">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="考勤任务" name="tasks" v-if="isTeacher">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>考勤任务列表</span>
              <el-button type="primary" @click="showCreateTaskDialog = true">
                <el-icon><Plus /></el-icon>
                创建考勤任务
              </el-button>
            </div>
          </template>
          
          <el-table :data="attendanceTasks" style="width: 100%" v-loading="loading">
            <el-table-column prop="id" label="任务ID" />
            <el-table-column prop="class_name" label="班级" />
            <el-table-column prop="subject" label="科目" />
            <el-table-column prop="start_time" label="开始时间" />
            <el-table-column prop="end_time" label="结束时间" />
            <el-table-column label="状态">
              <template #default="scope">
                <el-tag :type="scope.row.status === 'active' ? 'success' : 'info'">
                  {{ scope.row.status === 'active' ? '进行中' : '已结束' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="primary" 
                  :disabled="scope.row.status !== 'active'"
                  @click="startAttendance(scope.row)"
                >
                  开始考勤
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="考勤记录" name="records">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ isTeacher ? '考勤记录' : '我的考勤' }}</span>
            </div>
          </template>
          
          <el-table :data="attendanceRecords" style="width: 100%" v-loading="loading">
            <el-table-column prop="student_name" label="学生姓名" />
            <el-table-column prop="class_name" label="班级" />
            <el-table-column prop="subject" label="科目" />
            <el-table-column prop="date" label="日期" />
            <el-table-column prop="status" label="状态">
              <template #default="scope">
                <el-tag :type="getStatusType(scope.row.status)">
                  {{ getStatusText(scope.row.status) }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 创建考勤任务对话框 -->
    <el-dialog v-model="showCreateTaskDialog" title="创建考勤任务" width="500px">
      <el-form :model="taskForm" label-width="80px">
        <el-form-item label="班级">
          <el-input v-model="taskForm.class_name" />
        </el-form-item>
        <el-form-item label="科目">
          <el-input v-model="taskForm.subject" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="taskForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="taskForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showCreateTaskDialog = false">取消</el-button>
          <el-button type="primary" @click="createAttendanceTask" :loading="creating">
            创建
          </el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

const router = useRouter()
const activeTab = ref('tasks')
const loading = ref(false)
const creating = ref(false)
const showCreateTaskDialog = ref(false)

const attendanceTasks = ref([])
const attendanceRecords = ref([])

const taskForm = ref({
  class_name: '',
  subject: '',
  start_time: '',
  end_time: ''
})

const authStore = useAuthStore()
const isTeacher = computed(() => authStore.user?.role === 'teacher')

onMounted(() => {
  // 检查认证状态
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，重定向到登录页')
    router.push('/login')
    return
  }
  
  if (isTeacher.value) {
    fetchAttendanceTasks()
  }
  fetchAttendanceRecords()
})

const fetchAttendanceTasks = async () => {
  loading.value = true
  try {
    const response = await api.get('/attendance/tasks/')
    attendanceTasks.value = response.data.map(task => ({
      ...task,
      status: new Date() > new Date(task.start_time) && new Date() < new Date(task.end_time) 
        ? 'active' : 'inactive'
    }))
  } catch (error) {
    let errorMessage = '获取考勤任务失败'
    if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录'
      // 清除认证信息并重定向到登录页
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器错误，请稍后再试'
    } else if (!error.response) {
      errorMessage = '网络连接失败，请检查网络'
    }
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const fetchAttendanceRecords = async () => {
  loading.value = true
  try {
    const response = await api.get('/attendance/')
    attendanceRecords.value = response.data
  } catch (error) {
    let errorMessage = '获取考勤记录失败'
    if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录'
      // 清除认证信息并重定向到登录页
      const authStore = useAuthStore()
      authStore.logout()
      router.push('/login')
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器错误，请稍后再试'
    } else if (!error.response) {
      errorMessage = '网络连接失败，请检查网络'
    }
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const createAttendanceTask = async () => {
  creating.value = true
  try {
    await api.post('/attendance/tasks', {
      ...taskForm.value,
      start_time: taskForm.value.start_time.toISOString(),
      end_time: taskForm.value.end_time.toISOString()
    })
    
    ElMessage.success('创建成功')
    showCreateTaskDialog.value = false
    resetTaskForm()
    fetchAttendanceTasks()
  } catch (error) {
    ElMessage.error('创建失败')
  } finally {
    creating.value = false
  }
}

const resetTaskForm = () => {
  taskForm.value = {
    class_name: '',
    subject: '',
    start_time: '',
    end_time: ''
  }
}

const startAttendance = (task) => {
  // 在实际应用中，这里会跳转到考勤页面
  ElMessage.info(`开始考勤任务: ${task.subject}`)
}

const getStatusType = (status) => {
  switch (status) {
    case 'present': return 'success'
    case 'absent': return 'danger'
    case 'late': return 'warning'
    default: return 'info'
  }
}

const getStatusText = (status) => {
  switch (status) {
    case 'present': return '出勤'
    case 'absent': return '缺勤'
    case 'late': return '迟到'
    default: return '未知'
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  text-align: right;
}
</style>