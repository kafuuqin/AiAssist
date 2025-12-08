<script setup>
import { ref } from 'vue'
import { ElMessageBox, ElMessage } from 'element-plus'
import { ArrowDown } from '@element-plus/icons-vue'
import ChatWindow from '../../components/ChatWindows.vue'
import { useChatStore } from '@/stores/chat.js'

const chatStore = useChatStore()
const settingsVisible = ref(false)

const handleCommand = (command) => {
  switch (command) {
    case 'clear':
      chatStore.clearMessages()
      ElMessage.success('对话已清空')
      break
    case 'settings':
      settingsVisible.value = true
      break
    case 'help':
      window.open('/docs', '_blank')
      break
    case 'about':
      ElMessageBox.alert(
        'RAG智能对话系统 v1.0\n\n' +
        '功能特点：\n' +
        '• 智能区分文档查询与普通对话\n' +
        '• 支持多轮对话记忆\n' +
        '• 文档检索与语义理解\n' +
        '• 友好的交互界面',
        '关于系统',
        {
          confirmButtonText: '确定'
        }
      )
      break
  }
}
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>智能对话</h2>
        <p class="sub">与AI助手进行智能问答，支持文档检索与多轮对话</p>
      </div>
      <div class="header-actions">
        <el-dropdown @command="handleCommand">
          <el-button type="primary">
            更多操作<el-icon class="el-icon--right"><arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="clear">清空对话</el-dropdown-item>
              <el-dropdown-item command="settings">系统设置</el-dropdown-item>
              <el-dropdown-item command="help">帮助文档</el-dropdown-item>
              <el-dropdown-item command="about" divided>关于系统</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>

    <!-- 聊天区域 -->
    <div class="chat-area">
      <ChatWindow />
    </div>

  </div>
</template>

<style scoped>
.page {
  display: flex;
  flex-direction: column;
  gap: 18px;
  height: 100%;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0;
  margin-bottom: 0;
}

.page-header h2 {
  margin: 0 0 6px;
  color: #0f172a;
  font-size: 24px;
  font-weight: 600;
}

.sub {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chat-area {
  flex: 1;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.footer {
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  font-size: 12px;
  border-top: 1px solid #e2e8f0;
  margin-top: auto;
}

@media (max-width: 768px) {
  .page-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>