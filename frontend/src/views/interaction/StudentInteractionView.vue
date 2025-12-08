<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import { fetchStudentPolls, studentVote } from '../../api/modules/student'
import { ChatDotRound, DataBoard } from '@element-plus/icons-vue'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const polls = ref([])
const selectedPoll = ref(null)
const voteDialogVisible = ref(false)
const selectedOption = ref('')

const activePolls = computed(() => {
  return polls.value.filter(poll => poll.status === 'active')
})

const completedPolls = computed(() => {
  return polls.value.filter(poll => poll.status === 'completed')
})

const loadPolls = async () => {
  if (!courseStore.activeCourseId) return
  
  loading.value = true
  try {
    const response = await fetchStudentPolls(courseStore.activeCourseId)
    polls.value = response.data
  } catch (err) {
    ElMessage.error('加载投票失败')
  } finally {
    loading.value = false
  }
}

const openVoteDialog = (poll) => {
  selectedPoll.value = poll
  selectedOption.value = ''
  voteDialogVisible.value = true
}

const submitVote = async () => {
  if (!selectedOption.value) {
    ElMessage.warning('请选择投票选项')
    return
  }

  try {
    await studentVote(courseStore.activeCourseId, selectedPoll.value.id, {
      option: selectedOption.value
    })
    ElMessage.success('投票成功')
    voteDialogVisible.value = false
    await loadPolls() // 重新加载数据
  } catch (err) {
    ElMessage.error('投票失败')
  }
}

const hasVoted = (poll) => {
  return poll.votes?.some(vote => String(vote.student_id) === String(auth.user?.id))
}

const getVotePercentage = (poll, option) => {
  const totalVotes = poll.votes?.length || 0
  if (totalVotes === 0) return 0
  const optionVotes = poll.votes?.filter(vote => vote.option === option).length || 0
  return ((optionVotes / totalVotes) * 100).toFixed(1)
}

onMounted(loadPolls)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>课堂互动</h2>
        <p class="sub">参与课堂投票和互动活动</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else class="interaction-content">
      <!-- 进行中的投票 -->
      <div v-if="activePolls.length > 0" class="section">
        <h3 class="section-title">
          <el-icon><ChatDotRound /></el-icon>
          进行中的投票
        </h3>
        <div class="polls-grid">
          <el-card 
            v-for="poll in activePolls" 
            :key="poll.id" 
            shadow="hover" 
            class="poll-card"
          >
            <div class="poll-header">
              <h4>{{ poll.title }}</h4>
              <el-tag type="success" size="small">进行中</el-tag>
            </div>
            <p class="poll-description">{{ poll.description }}</p>
            
            <div class="poll-options">
              <div 
                v-for="option in poll.options" 
                :key="option" 
                class="option-item"
              >
                <el-radio 
                  v-model="selectedOption" 
                  :label="option" 
                  :disabled="hasVoted(poll)"
                >
                  {{ option }}
                </el-radio>
              </div>
            </div>

            <div class="poll-actions">
              <el-button 
                v-if="!hasVoted(poll)"
                type="primary" 
                size="small"
                @click="openVoteDialog(poll)"
              >
                投票
              </el-button>
              <el-tag v-else type="info" size="small">已投票</el-tag>
            </div>
          </el-card>
        </div>
      </div>

      <!-- 已结束的投票 -->
      <div v-if="completedPolls.length > 0" class="section">
        <h3 class="section-title">
          <el-icon><DataBoard /></el-icon>
          投票结果
        </h3>
        <div class="polls-grid">
          <el-card 
            v-for="poll in completedPolls" 
            :key="poll.id" 
            shadow="hover" 
            class="poll-card"
          >
            <div class="poll-header">
              <h4>{{ poll.title }}</h4>
              <el-tag type="info" size="small">已结束</el-tag>
            </div>
            <p class="poll-description">{{ poll.description }}</p>
            
            <div class="poll-results">
              <div 
                v-for="option in poll.options" 
                :key="option" 
                class="result-item"
              >
                <div class="result-label">{{ option }}</div>
                <div class="result-bar">
                  <div 
                    class="result-fill" 
                    :style="{ width: getVotePercentage(poll, option) + '%' }"
                  ></div>
                </div>
                <div class="result-percentage">{{ getVotePercentage(poll, option) }}%</div>
              </div>
            </div>

            <div class="poll-meta">
              总投票数: {{ poll.votes?.length || 0 }}
            </div>
          </el-card>
        </div>
      </div>

      <div v-if="polls.length === 0" class="empty">
        <el-empty description="暂无投票活动" />
      </div>
    </div>

    <!-- 投票对话框 -->
    <el-dialog 
      v-model="voteDialogVisible" 
      title="投票" 
      width="400px"
    >
      <div v-if="selectedPoll" class="vote-dialog">
        <h4>{{ selectedPoll.title }}</h4>
        <p class="vote-description">{{ selectedPoll.description }}</p>
        
        <div class="vote-options">
          <el-radio-group v-model="selectedOption">
            <el-radio 
              v-for="option in selectedPoll.options" 
              :key="option" 
              :label="option"
              class="vote-option"
            >
              {{ option }}
            </el-radio>
          </el-radio-group>
        </div>
      </div>

      <template #footer>
        <el-button @click="voteDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitVote">确认投票</el-button>
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

.polls-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.poll-card {
  transition: all 0.2s;
}

.poll-card:hover {
  transform: translateY(-2px);
}

.poll-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 8px;
}

.poll-header h4 {
  margin: 0;
  color: #0f172a;
  font-size: 16px;
}

.poll-description {
  margin: 0 0 16px;
  color: #64748b;
  font-size: 14px;
}

.poll-options {
  margin-bottom: 16px;
}

.option-item {
  margin-bottom: 8px;
}

.poll-actions {
  display: flex;
  justify-content: flex-end;
}

.poll-results {
  margin-bottom: 16px;
}

.result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.result-label {
  width: 100px;
  font-size: 14px;
  color: #374151;
}

.result-bar {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.result-fill {
  height: 100%;
  background: #6366f1;
  border-radius: 4px;
  transition: width 0.3s;
}

.result-percentage {
  width: 50px;
  text-align: right;
  font-size: 14px;
  color: #6b7280;
}

.poll-meta {
  text-align: right;
  font-size: 12px;
  color: #9ca3af;
}

.vote-dialog h4 {
  margin: 0 0 8px;
  color: #0f172a;
}

.vote-description {
  margin: 0 0 16px;
  color: #64748b;
}

.vote-options {
  margin-bottom: 16px;
}

.vote-option {
  display: block;
  margin-bottom: 8px;
}

.loading {
  padding: 40px 0;
}

.empty {
  padding: 60px 0;
}

@media (max-width: 768px) {
  .polls-grid {
    grid-template-columns: 1fr;
  }
}
</style>