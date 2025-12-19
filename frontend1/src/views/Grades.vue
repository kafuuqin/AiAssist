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
              <el-select 
                v-model="analysisForm.subject" 
                placeholder="选择科目" 
                @change="fetchAnalysisData"
                style="width: 200px;"
              >
                <el-option
                  v-for="subject in subjects"
                  :key="subject"
                  :label="subject"
                  :value="subject"
                />
              </el-select>
            </div>
          </template>
          
          <el-row :gutter="20">
            <el-col :span="12">
              <div ref="chartContainer" style="width: 100%; height: 400px;"></div>
            </el-col>
            <el-col :span="12">
              <div ref="pieChartContainer" style="width: 100%; height: 400px;"></div>
            </el-col>
          </el-row>
          
          <div class="analysis-stats">
            <el-row :gutter="20">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.average !== null ? analysisData.average.toFixed(1) : 'N/A' }}</div>
                      <div class="stat-label">平均分</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.highest !== null ? analysisData.highest : 'N/A' }}</div>
                      <div class="stat-label">最高分</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.lowest !== null ? analysisData.lowest : 'N/A' }}</div>
                      <div class="stat-label">最低分</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.median !== null ? analysisData.median : 'N/A' }}</div>
                      <div class="stat-label">中位数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
            </el-row>
            
            <el-row :gutter="20" style="margin-top: 20px;">
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.count !== null ? analysisData.count : 'N/A' }}</div>
                      <div class="stat-label">总人数</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.passRate !== null ? analysisData.passRate.toFixed(1) : 'N/A' }}</div>
                      <div class="stat-label">及格率(%)</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.std !== null ? analysisData.std.toFixed(2) : 'N/A' }}</div>
                      <div class="stat-label">标准差</div>
                    </div>
                  </div>
                </el-card>
              </el-col>
              
              <el-col :span="6">
                <el-card class="stat-card">
                  <div class="stat-content">
                    <div class="stat-info">
                      <div class="stat-number">{{ analysisData.variance !== null ? analysisData.variance.toFixed(2) : 'N/A' }}</div>
                      <div class="stat-label">方差</div>
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
import { ref, onMounted, watch, getCurrentInstance, computed, nextTick } from 'vue'
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
const analysisForm = ref({
  subject: ''
})

const subjects = ref([])
const analysisData = ref({
  average: null,
  highest: null,
  lowest: null,
  median: null,
  count: null,
  passRate: null,
  std: null,
  variance: null
})

const router = useRouter()
const chartContainer = ref()
const pieChartContainer = ref()
let chart = null
let pieChart = null

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
  
  // 获取科目列表
  await fetchSubjects()
  
  // 使用 nextTick 确保 DOM 更新后再初始化图表
  await nextTick()
  initChart()
})

watch(activeTab, async (newTab) => {
  if (newTab === 'analysis') {
    // 等待DOM更新后再更新图表
    await nextTick();
    initChart(); // 重新初始化图表而不是仅仅更新
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
      student_name: students.value.find(s => s.id === item.student_id)?.username || '未知学生'
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

const fetchSubjects = async () => {
  try {
    const response = await api.get('/grades/')
    const allGrades = response.data
    subjects.value = [...new Set(allGrades.map(g => g.subject))]
    
    // 默认选择第一个科目
    if (subjects.value.length > 0 && !analysisForm.value.subject) {
      analysisForm.value.subject = subjects.value[0]
      // 等待DOM更新后再获取分析数据
      await nextTick()
      await fetchAnalysisData()
    }
  } catch (error) {
    console.error('获取科目列表失败:', error)
    ElMessage.error('获取科目列表失败')
  }
}

const fetchAnalysisData = async () => {
  if (!analysisForm.value.subject) {
    return;
  }
  
  try {
    const response = await api.get(`/grades/${analysisForm.value.subject}/statistics`);
    const stats = response.data;
    
    // 计算额外统计数据
    const passCount = grades.value.filter(g => 
      g.subject === analysisForm.value.subject && g.score >= 60).length;
    const totalCount = grades.value.filter(g => 
      g.subject === analysisForm.value.subject).length;
    
    analysisData.value = {
      average: stats.average,
      highest: stats.max,
      lowest: stats.min,
      median: stats.median,
      count: stats.count,
      passRate: totalCount > 0 ? (passCount / totalCount) * 100 : 0,
      std: stats.std,
      variance: stats.std ? stats.std * stats.std : null
    };
    
    // 更新图表
    await nextTick();
    updateChart();
  } catch (error) {
    console.error('获取分析数据失败:', error);
    ElMessage.error('获取分析数据失败');
  }
};

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
  // 确保DOM元素存在再初始化图表
  if (chartContainer.value) {
    // 如果已有图表实例，先销毁
    if (chart) {
      chart.dispose();
    }
    // 创建新的柱状图实例
    chart = echarts.init(chartContainer.value);
  }
  
  // 确保DOM元素存在再初始化饼图
  if (pieChartContainer.value) {
    // 如果已有饼图实例，先销毁
    if (pieChart) {
      pieChart.dispose();
    }
    // 创建新的饼图实例
    pieChart = echarts.init(pieChartContainer.value);
  }
  
  // 等待一小段时间确保图表初始化完成
  setTimeout(() => {
    updateChart();
  }, 100);
}

const updateChart = () => {
  if ((!chart && !pieChart) || !analysisForm.value.subject) return
  
  // 更新柱状图
  if (chart) {
    // 计算成绩分布
    const subjectGrades = grades.value.filter(g => g.subject === analysisForm.value.subject)
    const distribution = [0, 0, 0, 0, 0] // [60以下, 60-70, 70-80, 80-90, 90以上]
    
    subjectGrades.forEach(g => {
      if (g.score < 60) distribution[0]++
      else if (g.score < 70) distribution[1]++
      else if (g.score < 80) distribution[2]++
      else if (g.score < 90) distribution[3]++
      else distribution[4]++
    })
    
    const barOption = {
      title: {
        text: `${analysisForm.value.subject}成绩分布柱状图`,
        left: 'center'
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow'
        }
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: ['60分以下', '60-69分', '70-79分', '80-89分', '90分以上'],
        axisTick: {
          alignWithLabel: true
        }
      },
      yAxis: {
        type: 'value',
        name: '人数'
      },
      series: [{
        type: 'bar',
        barWidth: '60%',
        data: distribution,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#2378f7' },
              { offset: 0.7, color: '#2378f7' },
              { offset: 1, color: '#83bff6' }
            ])
          }
        }
      }]
    }
    
    chart.setOption(barOption, true)
  }
  
  // 更新饼图
  if (pieChart) {
    // 计算成绩段人数
    const subjectGrades = grades.value.filter(g => g.subject === analysisForm.value.subject)
    const distribution = [0, 0, 0, 0, 0] // [60以下, 60-70, 70-80, 80-90, 90以上]
    
    subjectGrades.forEach(g => {
      if (g.score < 60) distribution[0]++
      else if (g.score < 70) distribution[1]++
      else if (g.score < 80) distribution[2]++
      else if (g.score < 90) distribution[3]++
      else distribution[4]++
    })
    
    const pieOption = {
      title: {
        text: `${analysisForm.value.subject}成绩分布饼图`,
        left: 'center'
      },
      tooltip: {
        trigger: 'item'
      },
      legend: {
        orient: 'vertical',
        left: 'left'
      },
      series: [
        {
          type: 'pie',
          radius: '50%',
          data: [
            { value: distribution[0], name: '60分以下' },
            { value: distribution[1], name: '60-69分' },
            { value: distribution[2], name: '70-79分' },
            { value: distribution[3], name: '80-89分' },
            { value: distribution[4], name: '90分以上' }
          ],
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          }
        }
      ]
    };
    
    pieChart.setOption(pieOption, true)
  }
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