<template>
  <div class="chat-window">
    <!-- 消息列表 -->
    <div ref="messagesContainer" class="messages-container">
      <div v-if="messages.length === 0" class="empty-state">
        <div class="empty-icon">
          <el-icon size="48" color="#909399"><ChatDotRound /></el-icon>
        </div>
        <div class="empty-text">开始与AI助手对话</div>
        <div class="empty-tip">输入问题或上传文档获取帮助</div>
      </div>

      <div v-for="message in messages" :key="message.id" class="message-wrapper">
        <!-- 用户消息 -->
        <div v-if="message.role === 'user'" class="message user-message">
          <div class="message-avatar">
            <el-avatar size="small" :style="{ backgroundColor: '#409EFF' }">
              你
            </el-avatar>
          </div>
          <div class="message-bubble">
            <div class="message-content">
              {{ message.content }}
            </div>
            <div class="message-footer">
              <span class="message-time">{{ message.timestamp }}</span>
            </div>
          </div>
        </div>

        <!-- 助手消息 -->
        <div v-else class="message assistant-message">
          <div class="message-avatar">
            <el-avatar size="small" :style="{ backgroundColor: '#67C23A' }">
              AI
            </el-avatar>
          </div>
          <div class="message-bubble">
            <div class="message-header">
              <span class="assistant-name">AI助手</span>
              <el-tag
                  v-if="message.metadata?.retrieval_used"
                  size="small"
                  type="success"
                  class="ml-2"
              >
                文档检索
              </el-tag>
            </div>
            <div class="message-content">
              {{ message.content }}
            </div>
            <div class="message-footer">
              <span class="message-time">{{ message.timestamp }}</span>
            </div>

            <!-- 来源信息 -->
            <div v-if="message.metadata?.sources?.length" class="sources-section">
              <el-collapse>
                <el-collapse-item title="参考来源" name="sources">
                  <div v-for="(source, index) in message.metadata.sources" :key="index" class="source-item">
                    <el-text type="info" size="small">
                      来源 {{ index + 1 }}: {{ source.substring(0, 150) }}...
                    </el-text>
                  </div>
                </el-collapse-item>
              </el-collapse>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 - 固定在底部 -->
    <div class="input-section-fixed">
      <div class="input-wrapper">
        <el-input
            v-model="inputMessage"
            type="textarea"
            :rows="3"
            placeholder="请输入您的问题..."
            :disabled="isTyping"
            @keydown.enter.exact.prevent="handleSend"
            class="message-input"
        />
        <div class="input-actions">
          <el-button-group>
            <el-button
                type="primary"
                :disabled="!inputMessage.trim() || isTyping"
                @click="handleSend"
                :loading="isTyping"
            >
              <el-icon class="mr-1"><Position /></el-icon>
              {{ isTyping ? '思考中...' : '发送' }}
            </el-button>
            <el-button
                @click="handleClear"
                :disabled="messages.length === 0"
            >
              <el-icon class="mr-1"><Delete /></el-icon>
              清空
            </el-button>
            <el-button
                @click="handleUpload"
            >
              <el-icon class="mr-1"><Upload /></el-icon>
              上传文档
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick, computed, onMounted, onUnmounted } from 'vue'
import { useChatStore } from '../stores/chat'
import { ElMessage } from 'element-plus'
import {Delete, Position, Upload, ChatDotRound} from "@element-plus/icons-vue";

const chatStore = useChatStore()
const messagesContainer = ref(null)
const inputMessage = ref('')

// 计算属性
const messages = computed(() => chatStore.messages)
const isTyping = computed(() => chatStore.isTyping)

// 滚动到底部
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

// 监听消息变化
watch(messages, () => {
  scrollToBottom()
}, { deep: true })

// 发送消息
const handleSend = async () => {
  if (!inputMessage.value.trim()) return

  const message = inputMessage.value.trim()
  inputMessage.value = ''

  try {
    await chatStore.sendMessage(message)
  } catch (error) {
    ElMessage.error('发送消息失败：' + error.message)
    // 恢复用户消息
    inputMessage.value = message
  }
}

// 清空消息
const handleClear = () => {
  chatStore.clearMessages()
  chatStore.clearHistory()
  ElMessage.success('消息已清空')
}

// 上传文档
const handleUpload = () => {
  // 这里可以触发文件上传对话框
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.txt,.pdf,.doc,.docx,.md'

  input.onchange = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    try {
      await chatStore.uploadDocument(file)
      ElMessage.success('文档上传成功')
    } catch (error) {
      ElMessage.error('文档上传失败：' + error.message)
    }
  }

  input.click()
}

// 处理键盘事件
const handleKeyDown = (e) => {
  // 支持 Ctrl+Enter 或 Cmd+Enter 发送
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    handleSend()
  }
}

// 组件挂载时添加键盘监听
onMounted(() => {
  window.addEventListener('keydown', handleKeyDown)
})

// 组件卸载时移除键盘监听
onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.chat-window {
  display: flex;
  flex-direction: column;
  height: 100vh; /* 使用视窗高度 */
  position: relative;
  background: linear-gradient(135deg, #f5f7fa 0%, #e4e7ed 100%);
}

/* 消息容器 - 可滚动区域 */
.messages-container {
  flex: 1;
  overflow-y: auto;
  padding: 20px 20px 140px; /* 底部padding防止被输入框遮挡 */
  position: relative;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 60%;
  color: #909399;
  text-align: center;
}

.empty-icon {
  margin-bottom: 16px;
  opacity: 0.6;
}

.empty-text {
  font-size: 18px;
  font-weight: 500;
  margin-bottom: 8px;
}

.empty-tip {
  font-size: 14px;
  opacity: 0.7;
}

.message-wrapper {
  padding: 12px 0;
  animation: fadeInUp 0.3s ease-out;
}

.message {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  max-width: 85%;
  margin: 0 auto;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  flex-shrink: 0;
}

.message-bubble {
  max-width: calc(100% - 52px);
  background: white;
  border-radius: 18px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  position: relative;
  transition: all 0.2s ease;
}

.user-message .message-bubble {
  background: linear-gradient(135deg, #409EFF, #66b1ff);
  color: white;
  border-bottom-right-radius: 4px;
}

.assistant-message .message-bubble {
  background: white;
  border: 1px solid #ebeef5;
  border-bottom-left-radius: 4px;
}

.message-bubble:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
  transform: translateY(-1px);
}

.message-header {
  display: flex;
  align-items: center;
  margin-bottom: 8px;
  font-size: 14px;
  font-weight: 500;
}

.assistant-name {
  color: #67C23A;
}

.message-content {
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
}

.user-message .message-content {
  color: white;
}

.assistant-message .message-content {
  color: #303133;
}

.message-footer {
  margin-top: 8px;
  display: flex;
  justify-content: flex-end;
}

.message-time {
  font-size: 12px;
  color: #909399;
  opacity: 0.7;
}

.user-message .message-time {
  color: rgba(255, 255, 255, 0.8);
}

.sources-section {
  margin-top: 12px;
  border-top: 1px solid #ebeef5;
  padding-top: 12px;
}

.source-item {
  margin-bottom: 6px;
  padding: 8px;
  background-color: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #67C23A;
}

/* 固定底部的输入框容器 */
.input-section-fixed {
  bottom: 0;
  left: 0;
  right: 0;
  background: white;
  border-top: 1px solid #e4e7ed;
  padding: 20px;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.1);
  z-index: 1000;
}

.input-wrapper {
  max-width: 1200px;
  margin: 0 auto;
  position: relative;
}

.message-input {
  border-radius: 12px;
}

.message-input :deep(.el-textarea__inner) {
  border-radius: 12px;
  border: 1px solid #e4e7ed;
  resize: none;
  transition: all 0.2s ease;
  font-size: 14px;
  line-height: 1.5;
}

.message-input :deep(.el-textarea__inner:focus) {
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.1);
}

.input-actions {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}

.ml-2 {
  margin-left: 8px;
}

.mr-1 {
  margin-right: 4px;
}

/* 滚动条样式 */
.messages-container::-webkit-scrollbar {
  width: 6px;
}

.messages-container::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 3px;
}

.messages-container::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 打字机效果 */
.typing-indicator {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.typing-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: #67C23A;
  animation: typing 1.4s infinite ease-in-out;
}

.typing-dot:nth-child(1) { animation-delay: -0.32s; }
.typing-dot:nth-child(2) { animation-delay: -0.16s; }

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0.8);
    opacity: 0.5;
  }
  40% {
    transform: scale(1);
    opacity: 1;
  }
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chat-window {
    height: 100vh;
  }

  .messages-container {
    padding: 16px 16px 160px; /* 移动端增加底部padding */
  }

  .message-wrapper {
    padding: 8px 0;
  }

  .message {
    max-width: 95%;
  }

  .message-bubble {
    padding: 12px;
  }

  .input-section-fixed {
    padding: 16px;
  }

  .message-input :deep(.el-textarea__inner) {
    font-size: 16px; /* 移动端增加字体大小 */
  }
}

/* 平板设备适配 */
@media (min-width: 769px) and (max-width: 1024px) {
  .input-wrapper {
    max-width: 90%;
  }
}

/* 大屏幕适配 */
@media (min-width: 1025px) {
  .input-wrapper {
    max-width: 1000px;
  }
}
</style>