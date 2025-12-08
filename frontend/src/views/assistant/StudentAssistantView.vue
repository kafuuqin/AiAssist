<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import { MagicStick, QuestionFilled } from '@element-plus/icons-vue'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)

const handleAskQuestion = () => {
  ElMessage.info('学习助手功能开发中...')
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>学习助手</h2>
        <p class="sub">智能问答和学习指导</p>
      </div>
    </div>

    <div class="assistant-content">
      <el-card shadow="hover" class="feature-card">
        <div class="feature-icon">
          <el-icon :size="48" color="#6366f1"><MagicStick /></el-icon>
        </div>
        <h3>智能问答</h3>
        <p class="feature-desc">向AI助手提问课程相关问题，获取个性化解答和学习建议</p>
        <el-button type="primary" :icon="QuestionFilled" @click="handleAskQuestion">
          开始提问
        </el-button>
      </el-card>

      <el-card shadow="hover" class="feature-card">
        <div class="feature-icon">
          <el-icon :size="48" color="#22c55e"><MagicStick /></el-icon>
        </div>
        <h3>学习规划</h3>
        <p class="feature-desc">根据你的学习进度和成绩，制定个性化的学习计划</p>
        <el-button type="success" :icon="MagicStick" @click="handleAskQuestion">
          查看规划
        </el-button>
      </el-card>

      <el-card shadow="hover" class="feature-card">
        <div class="feature-icon">
          <el-icon :size="48" color="#f59e0b"><MagicStick /></el-icon>
        </div>
        <h3>错题分析</h3>
        <p class="feature-desc">分析错题模式，提供针对性的知识点复习建议</p>
        <el-button type="warning" :icon="MagicStick" @click="handleAskQuestion">
          分析错题
        </el-button>
      </el-card>
    </div>
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

.assistant-content {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
}

.feature-card {
  text-align: center;
  padding: 32px 24px;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  margin-bottom: 16px;
}

.feature-card h3 {
  margin: 0 0 12px;
  color: #0f172a;
  font-size: 18px;
}

.feature-desc {
  margin: 0 0 20px;
  color: #64748b;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .assistant-content {
    grid-template-columns: 1fr;
  }
}
</style>