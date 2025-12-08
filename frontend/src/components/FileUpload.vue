<template>
  <div class="file-upload">
    <el-upload
        class="upload-demo"
        drag
        multiple
        :show-file-list="true"
        :before-upload="beforeUpload"
        :on-success="handleSuccess"
        :on-error="handleError"
        :action="uploadUrl"
        :headers="headers"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 txt, pdf, doc, docx, md 格式，单个文件不超过 10MB
        </div>
      </template>
    </el-upload>

    <!-- 上传进度 -->
    <div v-if="uploading" class="upload-progress">
      <el-progress
          :percentage="uploadPercentage"
          :status="uploadStatus"
      />
      <el-text type="info" size="small">{{ uploadMessage }}</el-text>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useChatStore } from '../stores/chat'
import { ElMessage } from 'element-plus'

const chatStore = useChatStore()

const uploading = ref(false)
const uploadPercentage = ref(0)
const uploadMessage = ref('')
const uploadStatus = ref('')

const uploadUrl = computed(() => '/api/upload')
const headers = computed(() => ({
  'Authorization': `Bearer ${localStorage.getItem('token') || ''}`
}))

const beforeUpload = (file) => {
  const allowedTypes = [
    'text/plain',
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/markdown'
  ]

  const maxSize = 10 * 1024 * 1024 // 10MB

  // 检查文件类型
  if (!allowedTypes.some(type => file.type.includes(type.replace('application/', '')))) {
    ElMessage.error('不支持的文件格式')
    return false
  }

  // 检查文件大小
  if (file.size > maxSize) {
    ElMessage.error('文件大小不能超过10MB')
    return false
  }

  uploading.value = true
  uploadPercentage.value = 0
  uploadMessage.value = '开始上传...'
  uploadStatus.value = ''

  // 模拟上传进度
  const interval = setInterval(() => {
    if (uploadPercentage.value < 90) {
      uploadPercentage.value += 10
    }
  }, 500)

  // 清除定时器
  setTimeout(() => clearInterval(interval), 5000)

  return true
}

const handleSuccess = (response) => {
  uploadPercentage.value = 100
  uploadMessage.value = '上传成功'
  uploadStatus.value = 'success'

  // 更新当前文档
  chatStore.currentDocument = {
    name: response.filename,
    size: response.size,
    uploadedAt: new Date().toISOString()
  }

  ElMessage.success('文档上传成功')

  // 重置上传状态
  setTimeout(() => {
    uploading.value = false
    uploadPercentage.value = 0
    uploadMessage.value = ''
  }, 2000)
}

const handleError = (error) => {
  uploadMessage.value = '上传失败'
  uploadStatus.value = 'exception'

  ElMessage.error(`上传失败: ${error.message}`)

  setTimeout(() => {
    uploading.value = false
    uploadPercentage.value = 0
    uploadMessage.value = ''
  }, 2000)
}
</script>

<style scoped>
.file-upload {
  padding: 20px;
}

.upload-demo {
  margin-bottom: 20px;
}

.upload-progress {
  margin-top: 20px;
  text-align: center;
}

.el-upload__tip {
  font-size: 12px;
  color: #909399;
  margin-top: 10px;
}

:deep(.el-upload-dragger) {
  padding: 40px 20px;
}

:deep(.el-upload__text) {
  margin-top: 20px;
}
</style>