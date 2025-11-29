<script setup>
import { onMounted, ref, watch, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'

const courseStore = useCourseStore()
const loading = ref(false)
const pollingTimer = ref(null)
const creating = ref(false)
const pollForm = ref({
  question: '',
  options: [''],
})

const messages = [
  { id: 1, user: '学生 A', content: '老师能分享实验数据集吗？', time: '09:22' },
  { id: 2, user: '学生 B', content: '课堂投票很好用！', time: '09:30' },
]

const load = async () => {
  if (!courseStore.activeCourseId) return
  loading.value = true
  try {
    await courseStore.loadPolls()
  } catch (err) {
    ElMessage.error('加载互动失败')
  } finally {
    loading.value = false
  }
}

const handleAddOption = () => {
  pollForm.value.options.push('')
}

const handleCreatePoll = async () => {
  if (!pollForm.value.question || pollForm.value.options.filter((o) => o).length < 2) {
    ElMessage.warning('请输入问题并至少 2 个选项')
    return
  }
  creating.value = true
  try {
    const options = pollForm.value.options.filter((o) => o)
    await courseStore.addPoll({ question: pollForm.value.question, options })
    ElMessage.success('创建成功')
    pollForm.value = { question: '', options: [''] }
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '创建失败')
  } finally {
    creating.value = false
  }
}

onMounted(load)
watch(
  () => courseStore.activeCourseId,
  () => load()
)

watch(
  () => courseStore.polls,
  () => {
    if (pollingTimer.value) return
    pollingTimer.value = setInterval(() => {
      load()
    }, 5000)
  },
  { immediate: true }
)

onUnmounted(() => {
  if (pollingTimer.value) clearInterval(pollingTimer.value)
})
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <p class="eyebrow">课堂互动</p>
        <h2>实时投票 · 问答 · 弹幕</h2>
        <p class="sub">Socket 实时互动，课堂氛围与反馈一目了然。</p>
      </div>
      <el-popover placement="bottom-end" width="320">
        <template #reference>
          <el-button type="primary">创建投票</el-button>
        </template>
        <div class="popover">
          <el-input v-model="pollForm.question" placeholder="请输入问题" />
          <div class="opts">
            <el-input
              v-for="(opt, idx) in pollForm.options"
              :key="idx"
              v-model="pollForm.options[idx]"
              :placeholder="`选项 ${idx + 1}`"
              style="margin-top: 6px"
            />
          </div>
          <div class="popover-actions">
            <el-button text size="small" @click="handleAddOption">+ 添加选项</el-button>
            <el-button size="small" type="primary" :loading="creating" @click="handleCreatePoll">创建</el-button>
          </div>
        </div>
      </el-popover>
    </div>

    <div class="grid">
      <el-card shadow="hover">
        <div class="card-head">
          <h3>投票区</h3>
          <el-button text size="small">查看历史</el-button>
        </div>
        <div v-for="poll in courseStore.polls" :key="poll.id" class="poll">
          <p class="question">{{ poll.question }}</p>
          <div class="options">
            <div v-for="(opt, idx) in poll.options" :key="opt" class="option">
              <span>{{ opt }}</span>
              <el-progress
                :percentage="Math.round(((poll.votes?.[idx] || 0) / Math.max(poll.votes?.reduce((a, b) => a + b, 0) || 1, 1)) * 100)"
              />
            </div>
          </div>
        </div>
        <el-empty v-if="!courseStore.polls.length && !loading" description="暂无投票" />
      </el-card>

      <el-card shadow="hover">
        <div class="card-head">
          <h3>课堂问答</h3>
          <el-button text size="small">新建问题</el-button>
        </div>
        <div class="qa-list">
          <div v-for="item in messages" :key="item.id" class="qa-item">
            <p class="meta">{{ item.user }} · {{ item.time }}</p>
            <p class="content">{{ item.content }}</p>
            <el-button text size="small" type="primary">回复</el-button>
          </div>
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

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 14px;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.poll {
  display: grid;
  gap: 10px;
}

.question {
  margin: 0;
  font-weight: 700;
  color: #0f172a;
}

.options {
  display: grid;
  gap: 8px;
}

.option {
  background: #f8fafc;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
}

.qa-list {
  display: grid;
  gap: 10px;
}

.qa-item {
  padding: 10px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.meta {
  margin: 0 0 4px;
  color: #94a3b8;
}

.content {
  margin: 0 0 6px;
  color: #0f172a;
}

.popover {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.opts {
  display: grid;
  gap: 6px;
}

.popover-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
