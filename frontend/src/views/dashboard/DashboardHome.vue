<script setup>
import dayjs from 'dayjs'

const stats = [
  { title: '今日出勤', value: '92%', trend: '+3%', color: '#4ade80' },
  { title: '待批改作业', value: '12', trend: '-5', color: '#f59e0b' },
  { title: '互动消息', value: '38', trend: '+12', color: '#60a5fa' },
  { title: '风险预警', value: '5', trend: '+2', color: '#ef4444' },
]

const timeline = [
  { time: '09:00', title: '《线性代数》课程签到', detail: '签到口令与二维码发布' },
  { time: '10:40', title: '作业批改', detail: '第 4 章练习批改中' },
  { time: '13:30', title: '课堂互动', detail: '实时投票：下次讨论主题' },
  { time: '16:00', title: '成绩预测', detail: 'AI 更新预测报告，5 名学生需关注' },
]

const quickActions = [
  { label: '发布签到', icon: 'Postcard', desc: '二维码/口令签到' },
  { label: '批量导入成绩', icon: 'UploadFilled', desc: 'Excel 模板导入' },
  { label: '资料上传', icon: 'FolderAdd', desc: '自动分类与标签' },
  { label: '开启投票', icon: 'Notification', desc: '课堂实时互动' },
]
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <p class="eyebrow">今日 · {{ dayjs().format('MM月DD日 dddd') }}</p>
        <h2>教学总览</h2>
        <p class="sub">关注出勤、成绩、互动与风险预警，一站式掌控教学动态。</p>
      </div>
      <el-button type="primary" plain>查看全校课程</el-button>
    </div>

    <div class="grid stats">
      <el-card v-for="item in stats" :key="item.title" shadow="hover">
        <p class="stat-title">{{ item.title }}</p>
        <div class="stat-row">
          <span class="stat-value" :style="{ color: item.color }">{{ item.value }}</span>
          <span class="stat-trend">{{ item.trend }}</span>
        </div>
      </el-card>
    </div>

    <div class="grid two">
      <el-card shadow="hover" class="card">
        <div class="card-head">
          <h3>快捷操作</h3>
        </div>
        <div class="actions">
          <div v-for="action in quickActions" :key="action.label" class="action-item">
            <el-icon :size="20"><component :is="action.icon" /></el-icon>
            <div>
              <p class="label">{{ action.label }}</p>
              <p class="desc">{{ action.desc }}</p>
            </div>
            <el-button text size="small">前往</el-button>
          </div>
        </div>
      </el-card>

      <el-card shadow="hover" class="card">
        <div class="card-head">
          <h3>今日行程</h3>
          <el-tag type="info" effect="plain">提醒</el-tag>
        </div>
        <el-timeline>
          <el-timeline-item
            v-for="item in timeline"
            :key="item.time"
            :timestamp="item.time"
            placement="top"
          >
            <p class="label">{{ item.title }}</p>
            <p class="desc">{{ item.detail }}</p>
          </el-timeline-item>
        </el-timeline>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 18px;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.eyebrow {
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: #94a3b8;
  margin-bottom: 6px;
  font-weight: 700;
}

h2 {
  margin: 0 0 6px;
  color: #0f172a;
}

.sub {
  margin: 0;
  color: #475569;
}

.grid {
  display: grid;
  gap: 16px;
}

.stats {
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.two {
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
}

.stat-title {
  margin: 0 0 6px;
  color: #6b7280;
}

.stat-row {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stat-value {
  font-size: 26px;
  font-weight: 800;
}

.stat-trend {
  color: #6b7280;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.actions {
  display: grid;
  gap: 12px;
}

.action-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 12px;
  padding: 10px 12px;
  display: grid;
  grid-template-columns: auto 1fr auto;
  gap: 10px;
  align-items: center;
}

.label {
  margin: 0;
  color: #0f172a;
  font-weight: 700;
}

.desc {
  margin: 0;
  color: #6b7280;
}
</style>
