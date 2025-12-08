import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { 
  sendMessage as apiSendMessage, 
  uploadDocument as apiUploadDocument, 
  initializeChatSystem as apiInitializeSystem,
  getChatHistory as apiGetHistory,
  clearChatHistory as apiClearHistory,
  batchQuery as apiBatchQuery
} from '../api/modules/chat.js'
import { ElMessage } from "element-plus"

export const useChatStore = defineStore('chat', () => {
    // 状态
    const messages = ref([])
    const isTyping = ref(false)
    const systemStatus = ref('ready')
    const currentDocument = ref(null)
    const history = ref([])
    const settings = ref({
        maxHistory: 10,
        retrievalThreshold: 0.5,
        verboseMode: false
    })

    // 计算属性
    const totalMessages = computed(() => messages.value.length)
    const hasHistory = computed(() => history.value.length > 0)

    // 方法
    const addMessage = (role, content, metadata = {}) => {
        const message = {
            id: Date.now(),
            role, // 'user' 或 'assistant'
            content,
            timestamp: new Date().toLocaleTimeString(),
            metadata
        }

        messages.value.push(message)

        // 如果超过最大历史记录，移除最早的消息
        if (messages.value.length > settings.value.maxHistory * 2) {
            messages.value = messages.value.slice(-settings.value.maxHistory * 2)
        }
    }

    const sendMessage = async (content) => {
        // 添加用户消息
        addMessage('user', content)
        isTyping.value = true

        try {
            // 发送到后端API
            const response = await apiSendMessage({ message: content })

            // 添加助手回复
            addMessage('assistant', response.data.answer, {
                retrieval_used: response.data.retrieval_used || false,
                sources: response.data.sources || []
            })

            // 更新系统状态
            systemStatus.value = 'ready'

        } catch (error) {
            console.error('发送消息失败:', error)
            addMessage('assistant', '抱歉，处理您的请求时出现错误。请稍后再试。', {
                error: true
            })
        } finally {
            isTyping.value = false
        }
    }

    const clearMessages = () => {
        messages.value = []
    }

    const uploadDocument = async (file) => {
        const formData = new FormData()
        formData.append('file', file)

        try {
            systemStatus.value = 'uploading'
            const response = await apiUploadDocument(formData)
            currentDocument.value = response.document
            systemStatus.value = 'ready'
            return response
        } catch (error) {
            systemStatus.value = 'error'
            throw error
        }
    }

    const initializeSystem = async (config) => {
        try {
            systemStatus.value = 'initializing'
            const response = await apiInitializeSystem(config)
            systemStatus.value = 'ready'
            return response
        } catch (error) {
            systemStatus.value = 'error'
            throw error
        }
    }

    const fetchHistory = async () => {
        try {
            const response = await apiGetHistory()
            history.value = response.history
        } catch (error) {
            console.error('获取历史记录失败:', error)
        }
    }

    const clearHistory = async () => {
        try {
            // 1. 先调用API清空后端历史
            await apiClearHistory()

            // 2. 然后清空前端本地消息
            clearMessages()

            // 3. 清空历史记录列表
            history.value = []

            ElMessage.success('对话历史已清空')
        } catch (error) {
            console.error('清空历史记录失败:', error)
            ElMessage.error('清空历史失败')
        }
    }

    // 批量查询
    const batchQuery = async (queries) => {
        try {
            const response = await apiBatchQuery({ queries })
            return response
        } catch (error) {
            console.error('批量查询失败:', error)
            throw error
        }
    }

    return {
        // 状态
        messages,
        isTyping,
        systemStatus,
        currentDocument,
        history,
        settings,

        // 计算属性
        totalMessages,
        hasHistory,

        // 方法
        addMessage,
        sendMessage,
        clearMessages,
        uploadDocument,
        initializeSystem,
        fetchHistory,
        clearHistory,
        batchQuery
    }
})