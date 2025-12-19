<template>
  <div class="classroom">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="人脸识别" name="faceRecognition">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>人脸识别考勤</span>
            </div>
          </template>
          
          <div class="face-recognition-container">
            <div class="video-container">
              <video ref="videoRef" autoplay playsinline style="width: 100%; max-width: 600px;"></video>
              <canvas ref="canvasRef" style="display: none;"></canvas>
            </div>
            
            <div class="controls">
              <el-button type="primary" @click="startCamera" :loading="cameraLoading">
                {{ cameraStarted ? '重新开始' : '开始摄像头' }}
              </el-button>
              <el-button @click="captureImage" :disabled="!cameraStarted">
                拍照识别
              </el-button>
              <el-button @click="stopCamera" :disabled="!cameraStarted">
                停止摄像头
              </el-button>
            </div>
            
            <div class="result" v-if="recognitionResult">
              <el-alert
                :type="recognitionResult.success ? 'success' : 'error'"
                :title="recognitionResult.message"
                show-icon
              />
              
              <div v-if="recognitionResult.student" class="student-info">
                <el-descriptions title="识别结果" :column="1" border>
                  <el-descriptions-item label="学号">
                    {{ recognitionResult.student.id }}
                  </el-descriptions-item>
                  <el-descriptions-item label="姓名">
                    {{ recognitionResult.student.name }}
                  </el-descriptions-item>
                  <el-descriptions-item label="班级">
                    {{ recognitionResult.student.class }}
                  </el-descriptions-item>
                </el-descriptions>
                
                <el-button 
                  type="success" 
                  @click="markAttendance(recognitionResult.student)" 
                  style="margin-top: 20px;"
                >
                  确认考勤
                </el-button>
              </div>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="座位表生成" name="seatingChart">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>座位表生成</span>
            </div>
          </template>
          
          <div class="seating-chart-container">
            <el-form :model="seatingForm" label-width="100px" style="max-width: 500px;">
              <el-form-item label="班级">
                <el-input v-model="seatingForm.class_name" placeholder="输入班级名称" />
              </el-form-item>
              
              <el-form-item label="行数">
                <el-input-number v-model="seatingForm.rows" :min="1" :max="20" />
              </el-form-item>
              
              <el-form-item label="列数">
                <el-input-number v-model="seatingForm.columns" :min="1" :max="20" />
              </el-form-item>
              
              <el-form-item label="学生列表">
                <el-select 
                  v-model="seatingForm.students" 
                  multiple 
                  filterable 
                  allow-create 
                  default-first-option
                  placeholder="输入学生姓名，回车添加"
                  style="width: 100%"
                >
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button type="primary" @click="generateSeatingChart" :loading="generating">
                  生成座位表
                </el-button>
              </el-form-item>
            </el-form>
            
            <div v-if="seatingChart.length > 0" class="chart-display">
              <h3>{{ seatingForm.class_name }} 座位表</h3>
              <div class="seating-grid">
                <div 
                  v-for="(row, rowIndex) in seatingChart" 
                  :key="rowIndex" 
                  class="seating-row"
                >
                  <div 
                    v-for="(seat, colIndex) in row" 
                    :key="colIndex" 
                    class="seat"
                    :class="{ occupied: seat.student }"
                  >
                    <div class="seat-number">{{ seat.number }}</div>
                    <div class="student-name">{{ seat.student || '' }}</div>
                  </div>
                </div>
              </div>
              
              <el-button @click="exportSeatingChart" style="margin-top: 20px;">
                导出座位表
              </el-button>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'

const router = useRouter()
const activeTab = ref('faceRecognition')
const cameraStarted = ref(false)
const cameraLoading = ref(false)
const generating = ref(false)

const videoRef = ref(null)
const canvasRef = ref(null)

const recognitionResult = ref(null)

const seatingForm = ref({
  class_name: '一年级一班',
  rows: 5,
  columns: 6,
  students: ['张三', '李四', '王五', '赵六', '钱七', '孙八', '周九', '吴十']
})

const seatingChart = ref([])

const authStore = useAuthStore()
const isTeacher = computed(() => authStore.user?.role === 'teacher')

let stream = null

onMounted(() => {
  // 检查认证状态
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，重定向到登录页')
    router.push('/login')
    return
  }
  
  // 如果不是教师，重定向到仪表盘
  if (!isTeacher.value) {
    router.push('/dashboard')
    return
  }
  
  // 组件挂载时初始化
})

onUnmounted(() => {
  stopCamera()
})

const startCamera = async () => {
  cameraLoading.value = true
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: true })
    if (videoRef.value) {
      videoRef.value.srcObject = stream
      cameraStarted.value = true
    }
  } catch (error) {
    ElMessage.error('无法访问摄像头，请检查权限设置')
  } finally {
    cameraLoading.value = false
  }
}

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop())
    stream = null
  }
  cameraStarted.value = false
}

const captureImage = () => {
  if (!videoRef.value || !canvasRef.value) return
  
  const video = videoRef.value
  const canvas = canvasRef.value
  const context = canvas.getContext('2d')
  
  // 设置画布尺寸与视频相同
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  // 将视频帧绘制到画布上
  context.drawImage(video, 0, 0, canvas.width, canvas.height)
  
  // 在实际应用中，这里会将图片发送到后端进行人脸识别
  // 模拟识别结果
  simulateFaceRecognition()
}

const simulateFaceRecognition = () => {
  // 模拟人脸识别过程
  recognitionResult.value = {
    success: Math.random() > 0.3, // 70% 成功率
    message: Math.random() > 0.3 ? '识别成功' : '识别失败，请重新拍照',
    student: Math.random() > 0.3 ? {
      id: '2023001',
      name: '张三',
      class: '一年级一班'
    } : null
  }
}

const markAttendance = (student) => {
  // 在实际应用中，这里会调用API记录考勤
  ElMessage.success(`已为 ${student.name} 记录考勤`)
  recognitionResult.value = null
}

const generateSeatingChart = () => {
  generating.value = true
  
  // 模拟座位表生成过程
  setTimeout(() => {
    const { rows, columns, students } = seatingForm.value
    const chart = []
    
    let studentIndex = 0
    
    for (let i = 0; i < rows; i++) {
      const row = []
      for (let j = 0; j < columns; j++) {
        const seatNumber = String.fromCharCode(65 + i) + (j + 1)
        const student = studentIndex < students.length ? students[studentIndex] : ''
        
        row.push({
          number: seatNumber,
          student: student
        })
        
        studentIndex++
      }
      chart.push(row)
    }
    
    seatingChart.value = chart
    generating.value = false
    ElMessage.success('座位表生成成功')
  }, 1000)
}

const exportSeatingChart = () => {
  // 在实际应用中，这里会导出座位表为PDF或图片
  ElMessage.info('座位表导出功能将在实际应用中实现')
}
</script>

<style scoped>
.face-recognition-container {
  text-align: center;
}

.video-container {
  margin-bottom: 20px;
}

.controls {
  margin-bottom: 20px;
}

.result {
  max-width: 600px;
  margin: 0 auto;
}

.student-info {
  margin-top: 20px;
}

.seating-chart-container {
  max-width: 800px;
  margin: 0 auto;
}

.chart-display {
  margin-top: 30px;
  text-align: center;
}

.seating-grid {
  display: inline-block;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  overflow: hidden;
}

.seating-row {
  display: flex;
}

.seat {
  width: 80px;
  height: 80px;
  border: 1px solid #ebeef5;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  font-size: 12px;
}

.seat.occupied {
  background-color: #ecf5ff;
}

.seat-number {
  font-weight: bold;
  margin-bottom: 5px;
}

.student-name {
  text-align: center;
}
</style>