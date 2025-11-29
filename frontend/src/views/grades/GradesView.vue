<script setup>
import { onMounted, computed, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart, { THEME_KEY } from 'vue-echarts'
import { provide } from 'vue'
import { uploadFile } from '../../api/modules/uploads'
import { exportGrades, downloadGradeTemplate } from '../../api/modules/courses'
import { gradePredict } from '../../api/modules/ai'
import { useAuthStore } from '../../stores/auth'

use([CanvasRenderer, BarChart, LineChart, GridComponent, TooltipComponent, LegendComponent])
provide(THEME_KEY, 'light')

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const createVisible = ref(false)
const gradeVisible = ref(false)
const importVisible = ref(false)
const importFile = ref(null)
const importFileList = ref([])
const uploadKey = ref(0)
const selectedAssignmentFilter = ref(null)
const assignmentForm = ref({
  title: '',
  type: '作业',
  full_score: 100,
  weight: 1,
})
const gradeForm = ref({
  assignment_id: null,
  student_id: '',
  score: '',
  comment: '',
})

const metrics = computed(() => [
  { label: '平均分', value: courseStore.gradeStats.avg ?? '--' },
  { label: '最高分', value: courseStore.gradeStats.max ?? '--' },
  { label: '最低分', value: courseStore.gradeStats.min ?? '--' },
  { label: '标准差', value: courseStore.gradeStats.std ? courseStore.gradeStats.std.toFixed(2) : '--' },
  { label: '人数', value: courseStore.gradeStats.count ?? 0 },
])

const isOwner = computed(() => {
  const course = courseStore.currentCourse
  return course && auth.user && course.owner_id === auth.user.id
})

const isManager = computed(() => {
  if (!auth.user) return false
  if (auth.user.role === 'admin') return true
  if (isOwner.value) return true
  return auth.user.role === 'teacher'
})

const barOption = computed(() => {
  const scores = courseStore.grades.map((g) => g.score || 0)
  const buckets = [0, 60, 70, 80, 90, 100]
  const labels = ['<60', '60-69', '70-79', '80-89', '90+']
  const counts = [0, 0, 0, 0, 0]
  scores.forEach((s) => {
    if (s < 60) counts[0]++
    else if (s < 70) counts[1]++
    else if (s < 80) counts[2]++
    else if (s < 90) counts[3]++
    else counts[4]++
  })
  return {
    tooltip: {},
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [{ type: 'bar', data: counts, itemStyle: { color: '#6366f1' } }],
  }
})

const lineOption = computed(() => {
  // 按作业 ID 聚合平均分
  const byAssignment = {}
  courseStore.grades.forEach((g) => {
    if (!byAssignment[g.assignment_id]) byAssignment[g.assignment_id] = []
    byAssignment[g.assignment_id].push(g.score)
  })
  const assignmentIds = Object.keys(byAssignment).sort((a, b) => Number(a) - Number(b))
  const labels = assignmentIds.map((id) => {
    const found = courseStore.assignments.find((a) => String(a.id) === String(id))
    return found ? found.title : `作业${id}`
  })
  const values = assignmentIds.map((id) => {
    const arr = byAssignment[id]
    return arr.reduce((a, b) => a + b, 0) / arr.length
  })
  return {
    tooltip: {},
    xAxis: { type: 'category', data: labels },
    yAxis: { type: 'value' },
    series: [{ type: 'line', data: values, smooth: true, itemStyle: { color: '#22c55e' } }],
  }
})

const load = async () => {
  if (!courseStore.activeCourseId) return
  loading.value = true
  try {
    await courseStore.loadGrades()
    await courseStore.loadAssignments()
    await courseStore.loadMembers()
  } catch (err) {
    ElMessage.error('加载成绩失败')
  } finally {
    loading.value = false
  }
}

onMounted(load)
watch(
  () => courseStore.activeCourseId,
  () => load()
)

const handleCreateAssignment = async () => {
  if (!assignmentForm.value.title) {
    ElMessage.warning('请输入作业标题')
    return
  }
  try {
    await courseStore.addAssignment(assignmentForm.value)
    ElMessage.success('创建成功')
    assignmentForm.value = { title: '', type: '作业', full_score: 100, weight: 1 }
    createVisible.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '创建失败')
  }
}

const handleCreateGrade = async () => {
  if (!gradeForm.value.assignment_id || !gradeForm.value.student_id) {
    ElMessage.warning('请选择作业并输入学生 ID')
    return
  }
  try {
    await courseStore.addGrade(gradeForm.value.assignment_id, {
      student_id: gradeForm.value.student_id,
      score: gradeForm.value.score,
      comment: gradeForm.value.comment,
    })
    ElMessage.success('录入成功')
    gradeForm.value = { assignment_id: null, student_id: '', score: '', comment: '' }
    gradeVisible.value = false
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '录入失败')
  }
}

const handleImport = async () => {
  if (!gradeForm.value.assignment_id) {
    ElMessage.warning('请选择作业')
    return
  }
  if (!importFile.value) {
    ElMessage.warning('请上传文件')
    return
  }
  try {
    const fd = new FormData()
    fd.append('file', importFile.value)
    const uploadRes = await uploadFile(fd)
    await courseStore.importGradeFile({
      assignment_id: gradeForm.value.assignment_id,
      file_path: uploadRes.data?.url,
    })
    ElMessage.success('导入成功')
    importVisible.value = false
    importFile.value = null
    importFileList.value = []
    // 重置上传控件
    uploadKey.value++
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '导入失败')
  }
}

const handleFileChange = (file, fileList) => {
  importFile.value = file.raw
  importFileList.value = fileList.slice(-1)
}

const handleFileRemove = () => {
  importFile.value = null
  importFileList.value = []
}

const handleFileExceed = (files, fileList) => {
  importFileList.value = fileList.slice(-1)
  importFile.value = importFileList.value[0]?.raw || null
  ElMessage.warning('一次仅上传一个文件，已保留最新文件')
}

const handleExport = () => {
  if (!courseStore.activeCourseId) return
  const params = selectedAssignmentFilter.value ? { assignment_id: selectedAssignmentFilter.value } : {}
  exportGrades(courseStore.activeCourseId, params)
    .then((res) => {
      const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `grades_course_${courseStore.activeCourseId}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
    })
    .catch(() => ElMessage.error('导出失败'))
}

const handleDownloadTemplate = () => {
  if (!courseStore.activeCourseId) return
  downloadGradeTemplate(courseStore.activeCourseId)
    .then((res) => {
      const blob = new Blob([res.data], { type: 'text/csv;charset=utf-8;' })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `grades_template_course_${courseStore.activeCourseId}.csv`
      link.click()
      window.URL.revokeObjectURL(url)
    })
    .catch(() => ElMessage.error('模板下载失败'))
}

const handlePredict = async () => {
  if (!courseStore.activeCourseId) return
  try {
    const { data } = await gradePredict({ course_id: courseStore.activeCourseId })
    const risks = (data.results || []).map((r) => `${r.student_id}: ${r.predicted_score}`).join('，')
    ElMessage.success(risks ? `预测结果：${risks}` : '预测完成')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '预测失败')
  }
}
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <p class="eyebrow">成绩分析</p>
        <h2>成绩录入 · 统计 · 预测</h2>
        <p class="sub">单条录入、Excel 导入、分布与趋势可视化，AI 预测高风险学生。</p>
      </div>
      <div class="actions">
        <el-button type="primary" plain @click="createVisible = true" :disabled="!isManager">新建作业</el-button>
        <el-button type="primary" @click="gradeVisible = true" :disabled="!isManager">录入成绩</el-button>
        <el-button type="primary" plain @click="importVisible = true" :disabled="!isManager">导入成绩</el-button>
        <el-button type="success" plain @click="handlePredict">生成预测</el-button>
      </div>
    </div>

    <div class="metrics">
      <el-card v-for="item in metrics" :key="item.label" shadow="never">
        <p class="label">{{ item.label }}</p>
        <p class="value">{{ item.value }}</p>
      </el-card>
    </div>

    <el-card shadow="hover">
      <template #header>
        <div class="card-head">
          <span>成绩列表</span>
      <div class="filter">
            <el-select v-model="selectedAssignmentFilter" placeholder="筛选作业" size="small" clearable>
              <el-option label="全部" :value="null" />
              <el-option v-for="a in courseStore.assignments" :key="a.id" :label="a.title" :value="a.id" />
            </el-select>
            <el-button size="small" text type="primary" @click="handleExport">导出</el-button>
            <el-button size="small" text @click="handleDownloadTemplate">模板下载</el-button>
          </div>
        </div>
      </template>
      <el-table :data="courseStore.grades" size="small" border v-loading="loading">
        <el-table-column prop="student_id" label="学生" width="120" />
        <el-table-column prop="assignment_id" label="作业ID" />
        <el-table-column prop="score" label="得分" width="90" />
        <el-table-column label="趋势" width="120">
          <template #default>
            <el-tag type="info" effect="plain">--</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="140">
          <template #default>
            <el-button text size="small">编辑</el-button>
            <el-button text size="small" type="primary">详情</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <div class="charts">
      <el-card shadow="hover">
        <h4>分数分布</h4>
        <v-chart :option="barOption" autoresize style="height: 280px" />
      </el-card>
      <el-card shadow="hover">
        <h4>成绩趋势</h4>
        <v-chart :option="lineOption" autoresize style="height: 280px" />
      </el-card>
    </div>

    <el-dialog v-model="createVisible" title="新建作业">
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="assignmentForm.title" placeholder="例如：第 4 次作业" />
        </el-form-item>
        <el-form-item label="类型">
          <el-input v-model="assignmentForm.type" placeholder="作业/考试/实验" />
        </el-form-item>
        <el-form-item label="满分">
          <el-input-number v-model="assignmentForm.full_score" :min="0" />
        </el-form-item>
        <el-form-item label="权重">
          <el-input-number v-model="assignmentForm.weight" :min="0" :step="0.1" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="createVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateAssignment">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="gradeVisible" title="录入成绩">
      <el-form label-position="top">
        <el-form-item label="选择作业">
          <el-select v-model="gradeForm.assignment_id" placeholder="请选择作业" style="width: 100%">
            <el-option v-for="a in courseStore.assignments" :key="a.id" :value="a.id" :label="a.title" />
          </el-select>
        </el-form-item>
        <el-form-item label="学生">
          <el-select v-model="gradeForm.student_id" placeholder="请选择学生" filterable style="width: 100%">
            <el-option
              v-for="m in courseStore.members"
              :key="m.user_id"
              :label="m.user?.name || m.user?.email || m.user_id"
              :value="m.user_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="得分">
          <el-input-number v-model="gradeForm.score" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="评语">
          <el-input v-model="gradeForm.comment" type="textarea" rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="gradeVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateGrade">提交</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="importVisible" title="导入成绩">
      <el-form label-position="top">
        <el-form-item label="选择作业">
          <el-select v-model="gradeForm.assignment_id" placeholder="请选择作业" style="width: 100%">
            <el-option v-for="a in courseStore.assignments" :key="a.id" :value="a.id" :label="a.title" />
          </el-select>
        </el-form-item>
        <el-form-item label="上传 Excel/CSV 模板">
          <el-upload
            :key="uploadKey"
            drag
            :auto-upload="false"
            :limit="1"
            accept=".xlsx,.xls,.csv"
            :on-change="handleFileChange"
            :on-remove="handleFileRemove"
            :on-exceed="handleFileExceed"
            :file-list="importFileList"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽或点击上传</div>
          </el-upload>
        </el-form-item>
        <el-alert
          title="请使用模板导入，必填列：student_id, assignment_id, score；支持 CSV/XLSX，错误会返回行号。"
          type="info"
          show-icon
        />
      </el-form>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" @click="handleImport">导入</el-button>
      </template>
    </el-dialog>
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

.metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
  gap: 12px;
}

.label {
  margin: 0 0 4px;
  color: #6b7280;
}

.value {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
  color: #111827;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.filter {
  display: flex;
  gap: 8px;
  align-items: center;
}
</style>
