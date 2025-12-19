<template>
  <div class="courses">
    <el-tabs v-model="activeTab" v-if="isTeacher">
      <!-- 创建课程标签页 -->
      <el-tab-pane label="创建课程" name="create">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>创建新课程</span>
            </div>
          </template>
          
          <el-form :model="courseForm" label-width="80px" style="max-width: 500px;">
            <el-form-item label="课程名称">
              <el-input v-model="courseForm.name" placeholder="请输入课程名称" />
            </el-form-item>
            
            <el-form-item label="课程描述">
              <el-input 
                v-model="courseForm.description" 
                type="textarea" 
                placeholder="请输入课程描述"
              />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="createCourse" :loading="creating">
                创建课程
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 我的课程标签页 -->
      <el-tab-pane label="我的课程" name="myCourses">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>我的课程</span>
            </div>
          </template>
          
          <el-table :data="courses" style="width: 100%" v-loading="loading">
            <el-table-column prop="name" label="课程名称" />
            <el-table-column prop="description" label="课程描述" />
            <el-table-column prop="teacher_name" label="授课教师" />
            <el-table-column prop="created_at" label="创建时间" />
            <el-table-column label="操作" width="200">
              <template #default="scope">
                <el-button 
                  size="small" 
                  @click="viewCourseDetails(scope.row)"
                >
                  查看详情
                </el-button>
                <el-button 
                  v-if="isTeacher" 
                  size="small" 
                  type="primary" 
                  @click="manageStudents(scope.row)"
                >
                  管理学生
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>
    
    <!-- 管理学生对话框 -->
    <el-dialog v-model="showStudentManagement" :title="`管理课程: ${currentCourse.name}`" width="600px">
      <el-tabs v-model="studentTab">
        <!-- 学生列表标签页 -->
        <el-tab-pane label="学生列表" name="studentList">
          <el-table :data="courseStudents" style="width: 100%" v-loading="studentLoading">
            <el-table-column prop="student_name" label="学生姓名" />
            <el-table-column prop="enrolled_at" label="加入时间" />
            <el-table-column label="操作">
              <template #default="scope">
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="removeStudent(scope.row)"
                >
                  移除
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
        
        <!-- 添加学生标签页 -->
        <el-tab-pane label="添加学生" name="addStudent">
          <el-form :model="addStudentForm" label-width="80px">
            <el-form-item label="选择学生">
              <el-select 
                v-model="addStudentForm.student_id" 
                placeholder="请选择学生" 
                style="width: 100%"
              >
                <el-option
                  v-for="student in availableStudents"
                  :key="student.id"
                  :label="student.username"
                  :value="student.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button 
                type="primary" 
                @click="addStudent" 
                :loading="addingStudent"
              >
                添加学生
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

const activeTab = ref('create')
const studentTab = ref('studentList')
const loading = ref(false)
const studentLoading = ref(false)
const creating = ref(false)
const addingStudent = ref(false)
const showStudentManagement = ref(false)

const courseForm = ref({
  name: '',
  description: ''
})

const addStudentForm = ref({
  student_id: ''
})

const courses = ref([])
const courseStudents = ref([])
const availableStudents = ref([])
const currentCourse = ref({})
const isTeacher = ref(false)

const router = useRouter()

onMounted(async () => {
  // 检查认证状态
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    router.push('/login')
    return
  }
  
  // 获取用户角色
  const user = authStore.user
  isTeacher.value = user.role === 'teacher'
  
  // 如果不是教师，重定向到仪表盘
  if (!isTeacher.value) {
    router.push('/dashboard')
    return
  }
  
  // 获取课程列表
  await fetchCourses()
  
  // 获取可选学生列表
  await fetchAvailableStudents()
})

const createCourse = async () => {
  if (!courseForm.value.name) {
    ElMessage.warning('请输入课程名称')
    return
  }
  
  creating.value = true
  try {
    const response = await api.post('/courses/', courseForm.value)
    ElMessage.success(response.data.message)
    resetCourseForm()
    await fetchCourses()
  } catch (error) {
    handleError(error, '创建课程失败')
  } finally {
    creating.value = false
  }
}

const resetCourseForm = () => {
  courseForm.value = {
    name: '',
    description: ''
  }
}

const fetchCourses = async () => {
  loading.value = true
  try {
    const response = await api.get('/courses/')
    courses.value = response.data.map(course => ({
      ...course,
      created_at: new Date(course.created_at).toLocaleString()
    }))
  } catch (error) {
    handleError(error, '获取课程列表失败')
  } finally {
    loading.value = false
  }
}

const fetchAvailableStudents = async () => {
  try {
    const response = await api.get('/auth/students/')
    console.log('获取到的学生列表:', response.data)
    availableStudents.value = response.data
  } catch (error) {
    console.error('获取学生列表失败:', error)
    handleError(error, '获取学生列表失败')
  }
}

const fetchCourseStudents = async (courseId) => {
  studentLoading.value = true
  try {
    const response = await api.get(`/courses/${courseId}/students/`)
    console.log('获取课程学生列表:', response.data)
    courseStudents.value = response.data.map(student => ({
      ...student,
      enrolled_at: new Date(student.enrolled_at).toLocaleString()
    }))
  } catch (error) {
    console.error('获取课程学生列表失败:', error)
    handleError(error, '获取课程学生列表失败')
  } finally {
    studentLoading.value = false
  }
}

const viewCourseDetails = (course) => {
  ElMessage.info(`课程详情: ${course.name}`)
}

const manageStudents = async (course) => {
  currentCourse.value = course
  showStudentManagement.value = true
  await fetchCourseStudents(course.id)
}

const addStudent = async () => {
  if (!addStudentForm.value.student_id) {
    ElMessage.warning('请选择学生')
    return
  }
  
  addingStudent.value = true
  try {
    const payload = {
      student_id: addStudentForm.value.student_id
    }
    
    console.log('发送添加学生请求:', payload)
    const response = await api.post(`/courses/${currentCourse.value.id}/students/`, payload)
    console.log('添加学生响应:', response.data)
    ElMessage.success(response.data.message || '学生添加成功')
    resetAddStudentForm()
    await fetchCourseStudents(currentCourse.value.id)
  } catch (error) {
    console.error('添加学生失败:', error)
    handleError(error, '添加学生失败')
  } finally {
    addingStudent.value = false
  }
}

const removeStudent = async (student) => {
  try {
    await ElMessageBox.confirm(
      `确定要将学生 "${student.student_name}" 从课程中移除吗？`, 
      '确认移除', 
      {
        type: 'warning'
      }
    )
    
    await api.delete(`/courses/${currentCourse.value.id}/students/${student.student_id}/`)
    ElMessage.success('学生移除成功')
    await fetchCourseStudents(currentCourse.value.id)
  } catch (error) {
    if (error !== 'cancel') {
      handleError(error, '移除学生失败')
    }
  }
}

const resetAddStudentForm = () => {
  addStudentForm.value = {
    student_id: ''
  }
}

const handleError = (error, defaultMessage) => {
  let errorMessage = defaultMessage
  
  if (error.response?.status === 401) {
    errorMessage = '认证失败，请重新登录'
    const authStore = useAuthStore()
    authStore.logout()
    router.push('/login')
  } else if (error.response?.data?.message) {
    errorMessage = error.response.data.message
  } else if (error.response?.status >= 500) {
    errorMessage = '服务器错误，请稍后再试'
  } else if (!error.response) {
    errorMessage = '网络连接失败，请检查网络'
  }
  
  ElMessage.error(errorMessage)
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.query-form {
  margin-bottom: 20px;
}
</style>