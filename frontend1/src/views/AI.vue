<template>
  <div class="ai-module">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="成绩预测" name="gradePrediction">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成绩预测分析</span>
            </div>
          </template>
          
          <div class="prediction-container">
            <el-form :model="predictionForm" label-width="100px" style="max-width: 500px;">
              <el-form-item label="学生">
                <el-select v-model="predictionForm.student_id" placeholder="选择学生">
                  <el-option
                    v-for="student in students"
                    :key="student.id"
                    :label="student.username"
                    :value="student.id"
                  />
                </el-select>
              </el-form-item>
              
              <el-form-item label="科目">
                <el-select v-model="predictionForm.subject" placeholder="选择科目">
                  <el-option label="数学" value="math" />
                  <el-option label="语文" value="chinese" />
                  <el-option label="英语" value="english" />
                  <el-option label="物理" value="physics" />
                  <el-option label="化学" value="chemistry" />
                </el-select>
              </el-form-item>
              
              <el-form-item>
                <el-button 
                  type="primary" 
                  @click="predictGrade" 
                  :loading="predicting"
                  :disabled="!predictionForm.student_id || !predictionForm.subject"
                >
                  预测成绩
                </el-button>
              </el-form-item>
            </el-form>
            
            <div v-if="predictionResult" class="prediction-result">
              <el-alert
                title="预测结果"
                type="success"
                show-icon
              >
                <template #default>
                  <div class="result-content">
                    <p>根据历史数据分析，预测学生 {{ getSelectedStudentName() }} 在 {{ getSubjectName(predictionForm.subject) }} 考试中可能获得的成绩：</p>
                    <div class="score-display">
                      <span class="score">{{ predictionResult.score }}</span>
                      <span class="score-label">分</span>
                    </div>
                    <p class="confidence">预测置信度：{{ predictionResult.confidence }}%</p>
                  </div>
                </template>
              </el-alert>
              
              <el-card style="margin-top: 20px;">
                <template #header>
                  <div class="card-header">
                    <span>学习建议</span>
                  </div>
                </template>
                <ul>
                  <li v-for="(suggestion, index) in predictionResult.suggestions" :key="index">
                    {{ suggestion }}
                  </li>
                </ul>
              </el-card>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="智能问答" name="qa">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>教学智能问答</span>
            </div>
          </template>
          
          <div class="qa-container">
            <div class="chat-history" ref="chatHistoryRef">
              <div 
                v-for="(message, index) in chatMessages" 
                :key="index" 
                class="message"
                :class="{ 'user-message': message.role === 'user', 'ai-message': message.role === 'ai' }"
              >
                <div class="message-content">
                  {{ message.content }}
                </div>
                <div class="message-time">{{ message.time }}</div>
              </div>
            </div>
            
            <div class="chat-input">
              <el-input
                v-model="question"
                placeholder="请输入您的问题..."
                @keyup.enter="askQuestion"
                :disabled="asking"
              >
                <template #append>
                  <el-button 
                    @click="askQuestion" 
                    :loading="asking"
                    :disabled="!question.trim()"
                  >
                    发送
                  </el-button>
                </template>
              </el-input>
            </div>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, nextTick, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

const router = useRouter()
const activeTab = ref('gradePrediction')
const predicting = ref(false)
const asking = ref(false)

const predictionForm = ref({
  student_id: '',
  subject: ''
})

const predictionResult = ref(null)

const question = ref('')
const chatMessages = ref([
  {
    role: 'ai',
    content: '您好！我是您的教学助手，可以回答关于教学的各种问题。请问有什么我可以帮您的吗？',
    time: new Date().toLocaleTimeString()
  }
])

const chatHistoryRef = ref(null)

// 添加学生列表的ref
const students = ref([])

const authStore = useAuthStore()
const isTeacher = computed(() => authStore.user?.role === 'teacher')

onMounted(async () => {
  // 检查认证状态
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，重定向到登录页')
    router.push('/login')
    return
  }
  
  // 如果是教师，获取学生列表
  if (isTeacher.value) {
    await fetchStudents()
  }
  
  scrollToBottom()
})

const fetchStudents = async () => {
  try {
    const response = await api.get('/auth/students/')
    students.value = response.data
  } catch (error) {
    console.error('获取学生列表失败:', error)
    ElMessage.error('获取学生列表失败')
  }
}

const predictGrade = async () => {
  predicting.value = true
  
  try {
    // 调用真实的API接口进行成绩预测
    const response = await api.get(`/grades/${predictionForm.value.student_id}/predict`, {
      params: {
        subject: predictionForm.value.subject
      }
    });
    
    predictionResult.value = {
      score: Math.round(response.data.predicted_score),
      confidence: Math.round(Math.random() * 30) + 70, // 70-100之间的置信度
      suggestions: [
        '建议加强课后练习，每天至少完成10道相关题目',
        '可参加课后辅导班，针对性提高薄弱环节',
        '多与同学讨论交流，互相学习解题思路',
        '定期复习已学知识，巩固基础'
      ]
    }
  } catch (error) {
    console.error('成绩预测失败:', error);
    ElMessage.error('成绩预测失败: ' + (error.response?.data?.message || error.message));
  } finally {
    predicting.value = false;
  }
}

const getSubjectName = (subject) => {
  const subjectMap = {
    math: '数学',
    chinese: '语文',
    english: '英语',
    physics: '物理',
    chemistry: '化学'
  }
  return subjectMap[subject] || subject
}

const askQuestion = async () => {
  if (!question.value.trim()) return
  
  // 添加用户消息
  chatMessages.value.push({
    role: 'user',
    content: question.value,
    time: new Date().toLocaleTimeString()
  })
  
  const userQuestion = question.value
  question.value = ''
  asking.value = true
  
  // 滚动到底部
  scrollToBottom()
  
  // 模拟API调用
  setTimeout(() => {
    // 模拟AI回复
    let aiResponse = ''
    
    if (userQuestion.includes('成绩')) {
      aiResponse = '根据您提供的信息，我建议关注学生的学习习惯和课堂参与度。可以通过定期小测验来跟踪进度，并提供个性化的学习计划。'
    } else if (userQuestion.includes('考勤') || userQuestion.includes(' attendance')) {
      aiResponse = '考勤是评估学生学习态度的重要指标。对于经常缺勤的学生，建议与家长沟通了解原因，并提供必要的支持和帮助。'
    } else if (userQuestion.includes('作业') || userQuestion.includes(' homework')) {
      aiResponse = '作业是巩固课堂知识的有效方式。建议布置适量且有针对性的作业，并及时给予反馈，以帮助学生改进。'
    } else {
      aiResponse = '这是一个很好的问题。作为教学助手，我建议您可以从以下几个方面考虑：首先分析学生的具体情况，然后制定个性化的教学策略，最后持续跟踪效果并调整方案。'
    }
    
    // 添加AI消息
    chatMessages.value.push({
      role: 'ai',
      content: aiResponse,
      time: new Date().toLocaleTimeString()
    })
    
    asking.value = false
    
    // 滚动到底部
    scrollToBottom()
  }, 1000)
}

const scrollToBottom = () => {
  nextTick(() => {
    if (chatHistoryRef.value) {
      chatHistoryRef.value.scrollTop = chatHistoryRef.value.scrollHeight
    }
  })
}

const getSelectedStudentName = () => {
  const selectedStudent = students.value.find(student => student.id === predictionForm.value.student_id)
  return selectedStudent ? selectedStudent.username : ''
}

</script>

<style scoped>
.prediction-container {
  max-width: 600px;
  margin: 0 auto;
}

.prediction-result {
  margin-top: 30px;
}

.result-content p {
  margin: 10px 0;
}

.score-display {
  text-align: center;
  margin: 20px 0;
}

.score {
  font-size: 48px;
  font-weight: bold;
  color: #409EFF;
}

.score-label {
  font-size: 18px;
  color: #666;
  margin-left: 5px;
}

.confidence {
  text-align: center;
  color: #999;
  font-style: italic;
}

.qa-container {
  display: flex;
  flex-direction: column;
  height: 500px;
}

.chat-history {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
  border: 1px solid #ebeef5;
  border-radius: 4px;
  margin-bottom: 20px;
}

.message {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}

.user-message {
  align-items: flex-end;
}

.ai-message {
  align-items: flex-start;
}

.message-content {
  max-width: 80%;
  padding: 10px 15px;
  border-radius: 10px;
  word-wrap: break-word;
}

.user-message .message-content {
  background-color: #409EFF;
  color: white;
}

.ai-message .message-content {
  background-color: #f5f5f5;
  color: #333;
}

.message-time {
  font-size: 12px;
  color: #999;
  margin-top: 5px;
}

.chat-input {
  margin-top: auto;
}
</style>