<template>
  <div class="grades">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="成绩录入" name="input" v-if="isTeacher">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成绩录入</span>
              <el-button type="primary" @click="showBatchImport = true">
                <el-icon><Upload /></el-icon>
                批量导入
              </el-button>
            </div>
          </template>
          
          <el-form :model="gradeForm" label-width="80px" style="max-width: 500px;">
            <el-form-item label="学生">
              <el-select v-model="gradeForm.student_id" placeholder="选择学生">
                <el-option
                  v-for="student in students"
                  :key="student.id"
                  :label="student.name"
                  :value="student.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="科目">
              <el-input v-model="gradeForm.subject" placeholder="输入科目名称" />
            </el-form-item>
            
            <el-form-item label="成绩">
              <el-input-number 
                v-model="gradeForm.score" 
                :min="0" 
                :max="100" 
                controls-position="right"
              />
            </el-form-item>
            
            <el-form-item label="考试类型">
              <el-select v-model="gradeForm.exam_type" placeholder="选择考试类型">
                <el-option label="平时测验" value="quiz" />
                <el-option label="期中考试" value="midterm" />
                <el-option label="期末考试" value="final" />
                <el-option label="作业" value="homework" />
              </el-select>
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="submitGrade" :loading="submitting">
                提交成绩
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-tab-pane>
      
      <!-- 批量导入对话框 -->
      <el-dialog v-model="showBatchImport" title="批量导入成绩" width="500px">
        <el-form :model="batchImportForm" label-width="80px">
          <el-form-item label="Excel文件">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :on-change="handleFileChange"
              :limit="1"
              accept=".xlsx,.xls,.csv"
            >
              <el-button slot="trigger" type="primary">选取文件</el-button>
              <template #tip>
                <div class="el-upload__tip">
                  请上传Excel文件(.xlsx/.xls)或CSV文件(.csv)
                </div>
              </template>
            </el-upload>
          </el-form-item>
        </el-form>
        <template #footer>
          <span class="dialog-footer">
            <el-button @click="showBatchImport = false">取消</el-button>
            <el-button type="primary" @click="submitBatchImport" :loading="batchImportLoading">
              导入
            </el-button>
          </span>
        </template>
      </el-dialog>
      
      <el-tab-pane label="成绩查询" name="query">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成绩查询</span>
              <el-button v-if="isTeacher" type="primary" @click="exportGrades" :disabled="grades.length === 0">
                <el-icon><Download /></el-icon>
                导出成绩
              </el-button>
            </div>
          </template>
          
          <el-form :inline="true" :model="queryForm" class="query-form">
            <el-form-item label="学生">
              <el-select v-model="queryForm.student_id" placeholder="选择学生">
                <el-option
                  v-for="student in students"
                  :key="student.id"
                  :label="student.name"
                  :value="student.id"
                />
              </el-select>
            </el-form-item>
            
            <el-form-item label="科目">
              <el-input v-model="queryForm.subject" placeholder="输入科目名称" />
            </el-form-item>
            
            <el-form-item>
              <el-button type="primary" @click="fetchGrades">查询</el-button>
            </el-form-item>
          </el-form>
          
          <el-table :data="grades" style="width: 100%" v-loading="loading">
            <el-table-column prop="student_name" label="学生姓名" />
            <el-table-column prop="subject" label="科目" />
            <el-table-column prop="score" label="成绩" />
            <el-table-column prop="exam_type" label="考试类型" />
            <el-table-column prop="created_at" label="录入时间" />
            <el-table-column label="操作" width="150" v-if="isTeacher">
              <template #default="scope">
                <el-button size="small" @click="editGrade(scope.row)">编辑</el-button>
                <el-button size="small" type="danger" @click="deleteGrade(scope.row)">删除</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
      
      <el-tab-pane label="成绩分析" name="analysis">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>成绩分析</span>
            </div>
          </template>
          
          <div ref="chartContainer" style="height: 400px;"></div>
          
          <div class="analysis-stats">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysis.average }}</div>
                      <div class="stat-label">平均分</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysis.highest }}</div>
                      <div class="stat-label">最高分</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysis.lowest }}</div>
                      <div class="stat-label">最低分</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysis.passRate }}%</div>
                      <div class="stat-label">及格率</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
          </div>
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted, watch, getCurrentInstance, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import * as echarts from 'echarts'
import api from '@/services/api'

// 获取全局属性
const { proxy } = getCurrentInstance()
const XLSX = proxy.$xlsx

const activeTab = ref('input')
const loading = ref(false)
const submitting = ref(false)
const showBatchImport = ref(false)
const batchImportLoading = ref(false)
const uploadRef = ref()

const gradeForm = ref({
  student_id: '',
  subject: '',
  score: null,
  exam_type: ''
})

const batchImportForm = ref({
  file: null
})

const queryForm = ref({
  student_id: '',
  subject: ''
})

const students = ref([])
const grades = ref([])
const analysis = ref({
  average: 85.5,
  highest: 98,
  lowest: 62,
  passRate: 92.5
})

const router = useRouter()
const chartContainer = ref()
let chart = null

const authStore = useAuthStore()
const isTeacher = computed(() => authStore.user?.role === 'teacher')

onMounted(async () => {
  // 检查认证状态
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，重定向到登录页')
    router.push('/login')
    return
  }
  
  // 获取学生列表（仅教师需要）
  if (isTeacher.value) {
    await fetchStudents()
  }
  
  // 获取成绩列表
  await fetchGrades()
  
  initChart()
})

watch(activeTab, (newTab) => {
  if (newTab === 'analysis') {
    updateChart()
  }
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

const submitGrade = async () => {
  if (!gradeForm.value.student_id || !gradeForm.value.subject || 
      gradeForm.value.score === null || !gradeForm.value.exam_type) {
    ElMessage.warning('请填写完整信息')
    return
  }
  
  submitting.value = true
  try {
    await api.post('/grades/', gradeForm.value)
    ElMessage.success('成绩录入成功')
    resetGradeForm()
    // 重新获取成绩列表
    await fetchGrades()
  } catch (error) {
    let errorMessage = '成绩录入失败'
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
    submitting.value = false
  }
}

const resetGradeForm = () => {
  gradeForm.value = {
    student_id: '',
    subject: '',
    score: null,
    exam_type: ''
  }
}

const handleFileChange = (file) => {
  batchImportForm.value.file = file.raw
}

const submitBatchImport = async () => {
  if (!batchImportForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  
  batchImportLoading.value = true
  try {
    // 读取文件内容
    const file = batchImportForm.value.file
    const filename = file.name
    const ext = filename.slice(filename.lastIndexOf('.')).toLowerCase()
    
    let data = []
    if (ext === '.xlsx' || ext === '.xls') {
      // 读取Excel文件
      const workbook = await readFileAsWorkbook(file)
      const firstSheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheetName]
      data = XLSX.utils.sheet_to_json(worksheet)
    } else if (ext === '.csv') {
      // 读取CSV文件
      const text = await file.text()
      const workbook = XLSX.read(text, { type: 'string' })
      const firstSheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheetName]
      data = XLSX.utils.sheet_to_json(worksheet)
    } else {
      throw new Error('不支持的文件格式')
    }
    
    // 转换列名（支持中英文）
    const columnMapping = {
      '学生ID': 'student_id',
      '科目': 'subject',
      '成绩': 'score',
      '考试类型': 'exam_type'
    }
    
    const convertedData = data.map(row => {
      const newRow = {}
      for (const [key, value] of Object.entries(row)) {
        const newKey = columnMapping[key] || key
        newRow[newKey] = value
      }
      // 设置默认考试类型
      if (!newRow.exam_type) {
        newRow.exam_type = ''
      }
      return newRow
    })
    
    // 逐条插入数据
    let successCount = 0
    let failCount = 0
    const errors = []
    
    for (const row of convertedData) {
      try {
        // 验证必填字段
        if (!row.student_id || !row.subject || row.score === undefined) {
          throw new Error(`缺少必要字段: ${JSON.stringify(row)}`)
        }
        
        // 发送到后端
        await api.post('/grades/', row)
        successCount++
      } catch (error) {
        failCount++
        errors.push({
          row: row,
          error: error.response?.data?.message || error.message
        })
      }
    }
    
    // 显示结果
    if (failCount === 0) {
      ElMessage.success(`成功导入 ${successCount} 条记录`)
    } else {
      ElMessage.warning(`成功导入 ${successCount} 条记录，失败 ${failCount} 条`) 
      console.error('导入失败的记录:', errors)
    }
    
    showBatchImport.value = false
    resetBatchImportForm()
    // 重新获取成绩列表
    await fetchGrades()
  } catch (error) {
    console.error('批量导入失败:', error)
    let errorMessage = '批量导入失败: ' + (error.message || error.toString())
    if (error.name === 'SyntaxError') {
      errorMessage = '文件格式错误，请检查文件内容'
    }
    ElMessage.error(errorMessage)
  } finally {
    batchImportLoading.value = false
  }
}

// 读取文件为Workbook对象
const readFileAsWorkbook = (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = XLSX.read(data, { type: 'array' })
        resolve(workbook)
      } catch (error) {
        reject(error)
      }
    }
    reader.onerror = (error) => reject(error)
    reader.readAsArrayBuffer(file)
  })
}

const resetBatchImportForm = () => {
  batchImportForm.value = {
    file: null
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

const fetchGrades = async () => {
  loading.value = true
  try {
    const response = await api.get('/grades/', {
      params: queryForm.value
    })
    grades.value = response.data.map(item => ({
      ...item,
      student_name: students.value.find(s => s.id === item.student_id)?.name || '未知学生'
    }))
  } catch (error) {
    let errorMessage = '查询成绩失败'
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

const editGrade = (grade) => {
  // 在实际应用中，这里会打开编辑对话框
  ElMessage.info(`编辑成绩: ${grade.subject}`)
}

const deleteGrade = async (grade) => {
  try {
    await ElMessageBox.confirm('确定要删除这个成绩记录吗？', '提示', {
      type: 'warning'
    })
    
    await api.delete(`/grades/${grade.id}`)
    ElMessage.success('删除成功')
    fetchGrades()
  } catch (error) {
    if (error !== 'cancel') {
      let errorMessage = '删除失败'
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
    }
  }
}

const initChart = () => {
  if (chartContainer.value) {
    chart = echarts.init(chartContainer.value)
    updateChart()
  }
}

const updateChart = () => {
  if (!chart) return
  
  const option = {
    title: {
      text: '成绩分布图'
    },
    tooltip: {},
    xAxis: {
      type: 'category',
      data: ['60以下', '60-70', '70-80', '80-90', '90以上']
    },
    yAxis: {
      type: 'value'
    },
    series: [{
      type: 'bar',
      data: [2, 5, 12, 18, 8],
      itemStyle: {
        color: '#409EFF'
      }
    }]
  }
  
  chart.setOption(option)
}

const exportGrades = async () => {
  try {
    // 创建表头映射，使导出的文件与导入格式一致
    const worksheetData = grades.value.map(item => ({
      'student_id': item.student_id,
      'subject': item.subject,
      'score': item.score,
      'exam_type': item.exam_type
    }));
    
    // 创建工作表
    const ws = XLSX.utils.json_to_sheet(worksheetData);
    
    // 创建工作簿
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, '成绩表');
    
    // 导出文件
    XLSX.writeFile(wb, '学生成绩.xlsx');
    
    ElMessage.success('成绩导出成功');
  } catch (error) {
    console.error('导出失败:', error);
    ElMessage.error('成绩导出失败');
  }
};



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

.analysis-stats {
  margin-top: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  height: 100%;
}

.stat-info {
  flex: 1;
  text-align: center;
}

.stat-number {
  font-size: 24px;
  font-weight: bold;
  margin-bottom: 5px;
}

.stat-label {
  color: #999;
}
</style>