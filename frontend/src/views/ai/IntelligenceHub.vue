<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { classifyMaterial, gradePredict, recognizeAttendance, qaAsk } from '../../api/modules/ai'

const loading = ref(false)
const qaQuestion = ref('')
const qaAnswer = ref('')
const riskList = ref([])
const classifyTags = ref([])
const attendanceResult = ref(null)

const runClassify = async () => {
  loading.value = true
  try {
    const { data } = await classifyMaterial({ title: '第5次作业课件' })
    classifyTags.value = data.suggested_tags || []
    ElMessage.success('已生成标签')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '分类失败')
  } finally {
    loading.value = false
  }
}

const runPredict = async () => {
  loading.value = true
  try {
    const { data } = await gradePredict({ course_id: 1 })
    riskList.value = data.results || []
    ElMessage.success('预测完成（mock）')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '预测失败')
  } finally {
    loading.value = false
  }
}

const runAttendance = async () => {
  loading.value = true
  try {
    const { data } = await recognizeAttendance({})
    attendanceResult.value = data
    ElMessage.success('识别完成（mock）')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '识别失败')
  } finally {
    loading.value = false
  }
}

const runQa = async () => {
  if (!qaQuestion.value) {
    ElMessage.warning('请输入问题')
    return
  }
  loading.value = true
  try {
    const { data } = await qaAsk({ question: qaQuestion.value })
    qaAnswer.value = data.answer
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '问答失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <div class="hero">
      <div>
        <p class="eyebrow">AI CENTER</p>
        <h2>智能提升教学效率</h2>
        <p class="sub">接入 NLP、CV、统计模型，让资料管理、学情预警和点名更智能。</p>
        <div class="hero-actions">
          <el-button type="primary">开启一键分析</el-button>
          <el-button text>查看最近报告</el-button>
        </div>
      </div>
      <div class="bubble">
        <p>今日自动分类 12 份资料</p>
        <p>更新成绩预测：3 名学生需关注</p>
      </div>
    </div>

    <div class="grid">
      <el-card shadow="hover" class="ai-card">
        <div class="dot" style="background:#4f46e5"></div>
        <h3>自动化资料归类</h3>
        <p class="desc">关键词抽取 + 文本分类，自动打标签并给出推荐分类。</p>
        <el-button plain size="small" type="primary" @click="runClassify" :loading="loading">立即运行</el-button>
        <div class="result" v-if="classifyTags.length">
          <p>推荐标签：<el-tag v-for="t in classifyTags" :key="t" size="small">{{ t }}</el-tag></p>
        </div>
      </el-card>

      <el-card shadow="hover" class="ai-card">
        <div class="dot" style="background:#0ea5e9"></div>
        <h3>学情预警与预测</h3>
        <p class="desc">线性回归/随机森林预测成绩，标记高风险学生并提醒导师。</p>
        <el-button plain size="small" type="primary" @click="runPredict" :loading="loading">生成报告</el-button>
        <div class="result" v-if="riskList.length">
          <p>高风险学生：</p>
          <ul>
            <li v-for="r in riskList" :key="r.student_id">{{ r.student_id }} · 预测 {{ r.predicted_score }}</li>
          </ul>
        </div>
      </el-card>

      <el-card shadow="hover" class="ai-card">
        <div class="dot" style="background:#22c55e"></div>
        <h3>智能点到</h3>
        <p class="desc">上传课堂照片，OpenCV 人脸识别生成签到结果，支持人工校正。</p>
        <el-button plain size="small" type="primary" @click="runAttendance" :loading="loading">上传照片</el-button>
        <div class="result" v-if="attendanceResult">
          <p>识别率：{{ attendanceResult.accuracy * 100 }}% ({{ attendanceResult.recognized }}/{{ attendanceResult.total }})</p>
        </div>
      </el-card>

      <el-card shadow="hover" class="ai-card">
        <div class="dot" style="background:#f97316"></div>
        <h3>智能问答助手</h3>
        <p class="desc">基于课程资料构建 FAQ 检索，快速回答作业/考试常见问题。</p>
        <el-input v-model="qaQuestion" placeholder="输入问题" size="small" style="margin-bottom: 8px" />
        <el-button plain size="small" type="primary" @click="runQa" :loading="loading">提问</el-button>
        <div class="result" v-if="qaAnswer">
          <p>回答：{{ qaAnswer }}</p>
        </div>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.hero {
  background: linear-gradient(120deg, #eef2ff, #e0f2fe);
  border: 1px solid #d9e2ff;
  border-radius: 16px;
  padding: 20px;
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 16px;
  align-items: center;
}

.eyebrow {
  letter-spacing: 0.12em;
  color: #6366f1;
  font-weight: 800;
  margin-bottom: 6px;
}

.sub {
  margin: 0 0 10px;
  color: #334155;
}

.hero-actions {
  display: flex;
  gap: 12px;
}

.bubble {
  background: #0f172a;
  color: #f8fafc;
  padding: 14px 16px;
  border-radius: 12px;
  line-height: 1.5;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.15);
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 14px;
}

.ai-card {
  position: relative;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  position: absolute;
  right: 16px;
  top: 16px;
}

h3 {
  margin: 0 0 8px;
}

.desc {
  margin: 0 0 10px;
  color: #64748b;
}

.result {
  margin-top: 10px;
  color: #0f172a;
}
</style>
