<template>
  <div class="materials">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>资料中心</span>
          <el-button v-if="isTeacher" type="primary" @click="showUploadDialog = true">
            <el-icon><Plus /></el-icon>
            上传资料
          </el-button>
        </div>
      </template>
      
      <el-table :data="materials" style="width: 100%" v-loading="loading">
        <el-table-column prop="title" label="资料名称" />
        <el-table-column prop="description" label="描述" />
        <el-table-column prop="filename" label="文件名" />
        <el-table-column label="操作" width="280">
          <template #default="scope">
            <el-button size="small" @click="previewMaterial(scope.row)">
              预览
            </el-button>
            <el-button size="small" @click="downloadMaterial(scope.row)">
              下载
            </el-button>
            <el-button v-if="isTeacher" size="small" type="danger" @click="deleteMaterial(scope.row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- 上传资料对话框 -->
    <el-dialog v-model="showUploadDialog" title="上传资料" width="500px">
      <el-form :model="uploadForm" label-width="80px">
        <el-form-item label="标题">
          <el-input v-model="uploadForm.title" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="uploadForm.description" type="textarea" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload
            ref="uploadRef"
            :auto-upload="false"
            :on-change="handleFileChange"
            :limit="1"
          >
            <el-button slot="trigger" type="primary">选取文件</el-button>
          </el-upload>
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showUploadDialog = false">取消</el-button>
          <el-button type="primary" @click="uploadMaterial" :loading="uploadLoading">
            上传
          </el-button>
        </span>
      </template>
    </el-dialog>
    
    <!-- 预览对话框 -->
    <el-dialog 
      v-model="showPreviewDialog" 
      :title="'预览: ' + previewMaterialData.title" 
      width="80%"
      top="1vh"
      draggable
      resizable
    >
      <div class="preview-container">
        <!-- 图片预览 -->
        <div v-if="isImage(previewMaterialData.filename)" class="image-preview">
          <img :src="previewUrl" alt="预览图片" style="max-width: 100%; max-height: 95vh;" />
        </div>
        
        <!-- PDF预览 -->
        <div v-else-if="isPdf(previewMaterialData.filename)" class="pdf-preview">
          <iframe :src="previewUrl" width="100%" height="500vh" style="border: none;"></iframe>
        </div>
        
        <!-- 其他文件类型提示 -->
        <div v-else class="unsupported-preview">
          <p>此文件类型不支持在线预览。</p>
          <p>文件名: {{ previewMaterialData.filename }}</p>
          <el-button type="primary" @click="downloadMaterial(previewMaterialData)">下载文件</el-button>
        </div>
      </div>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="showPreviewDialog = false">关闭</el-button>
          <el-button type="primary" @click="downloadMaterial(previewMaterialData)">下载</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/store/auth'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()
const isTeacher = computed(() => authStore.user?.role === 'teacher')

const materials = ref([])
const loading = ref(false)
const showUploadDialog = ref(false)
const uploadLoading = ref(false)
const uploadRef = ref()

// 预览相关变量
const showPreviewDialog = ref(false)
const previewMaterialData = ref({})
const previewUrl = ref('')

const uploadForm = ref({
  title: '',
  description: '',
  file: null
})

onMounted(() => {
  fetchMaterials()
})

const fetchMaterials = async () => {
  // 检查认证状态
  const authStore = useAuthStore()
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，重定向到登录页')
    router.push('/login')
    return
  }
  
  loading.value = true
  try {
    const response = await api.get('/materials/')
    materials.value = response.data
  } catch (error) {
    let errorMessage = '获取资料列表失败'
    if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录'
      // 清除认证信息并重定向到登录页
      authStore.logout()
      router.push('/login')
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器错误，请稍后再试'
    } else if (!error.response) {
      errorMessage = '网络连接失败，请检查网络'
    }
    ElMessage.error(errorMessage)
  } finally {
    loading.value = false
  }
}

const handleFileChange = (file) => {
  uploadForm.value.file = file.raw
}

const uploadMaterial = async () => {
  if (!uploadForm.value.file) {
    ElMessage.warning('请选择文件')
    return
  }
  
  uploadLoading.value = true
  try {
    const formData = new FormData()
    formData.append('file', uploadForm.value.file)
    formData.append('title', uploadForm.value.title)
    formData.append('description', uploadForm.value.description)
    
    await api.post('/materials/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    
    ElMessage.success('上传成功')
    showUploadDialog.value = false
    resetUploadForm()
    fetchMaterials()
  } catch (error) {
    console.error('上传资料失败:', error)
    let errorMessage = '上传资料失败'
    if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录'
    } else if (error.response?.status === 413) {
      errorMessage = '文件太大，请选择较小的文件'
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器错误，请稍后再试'
    } else if (!error.response) {
      errorMessage = '网络连接失败，请检查网络'
    }
    ElMessage.error(errorMessage)
  } finally {
    uploadLoading.value = false
  }
}

const resetUploadForm = () => {
  uploadForm.value = {
    title: '',
    description: '',
    file: null
  }
  if (uploadRef.value) {
    uploadRef.value.clearFiles()
  }
}

// 判断是否为图片文件
const isImage = (filename) => {
  const imageExtensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp']
  const extension = filename.split('.').pop().toLowerCase()
  return imageExtensions.includes(extension)
}

// 判断是否为PDF文件
const isPdf = (filename) => {
  return filename.toLowerCase().endsWith('.pdf')
}

// 预览资料
const previewMaterial = async (material) => {
  try {
    previewMaterialData.value = material
    
    // 获取当前token
    const token = localStorage.getItem('token') || api.defaults.headers.common['Authorization']?.replace('Bearer ', '')
    
    // 构建带认证参数的预览URL
    const baseUrl = api.defaults.baseURL || '/api'
    previewUrl.value = `${baseUrl}/materials/${material.id}/?access_token=${token}&preview=true`
    
    showPreviewDialog.value = true
  } catch (error) {
    console.error('预览失败:', error)
    ElMessage.error('预览失败')
  }
}

const downloadMaterial = async (material) => {
  try {
    // 使用API客户端发送GET请求以触发下载
    const response = await api.get(`/materials/${material.id}/`, {
      responseType: 'blob' // 重要：指定响应类型为blob以处理文件下载
    });
    
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', material.filename);
    document.body.appendChild(link);
    link.click();
    
    // 清理
    document.body.removeChild(link);
    window.URL.revokeObjectURL(url);
    
    ElMessage.success(`开始下载文件: ${material.filename}`);
  } catch (error) {
    console.error('下载失败:', error);
    let errorMessage = '下载失败';
    
    if (error.response?.status === 404) {
      errorMessage = '文件不存在';
    } else if (error.response?.status === 401) {
      errorMessage = '认证失败，请重新登录';
      // 清除认证信息并重定向到登录页
      const authStore = useAuthStore();
      authStore.logout();
      router.push('/login');
    } else if (error.response?.status >= 500) {
      errorMessage = '服务器错误，请稍后再试';
    } else if (!error.response) {
      errorMessage = '网络连接失败，请检查网络';
    }
    
    ElMessage.error(errorMessage);
  }
}

const deleteMaterial = async (material) => {
  try {
    await ElMessageBox.confirm('确定要删除这个资料吗？', '提示', {
      type: 'warning'
    })
    
    await api.delete(`/materials/${material.id}/`)
    ElMessage.success('删除成功')
    fetchMaterials()
  } catch (error) {
    if (error !== 'cancel') {
      let errorMessage = '删除失败'
      if (error.response?.status === 401) {
        errorMessage = '认证失败，请重新登录'
        // 清除认证信息并重定向到登录页
        const authStore = useAuthStore()
        authStore.logout()
        router.push('/login')
      } else if (error.response?.status >= 500) {
        errorMessage = '服务器错误，请稍后再试'
      } else if (!error.response) {
        errorMessage = '网络连接失败，请检查网络'
      }
      ElMessage.error(errorMessage)
    }
  }
}
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.dialog-footer {
  text-align: right;
}

.preview-container {
  text-align: center;
}

.image-preview {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 300px;
}

.unsupported-preview {
  padding: 20px;
  text-align: center;
}
</style>
