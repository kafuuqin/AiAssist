<script setup>
import { onMounted, ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'
import { fetchStudentMaterials } from '../../api/modules/student'
import { Download, Document, VideoPlay, Picture } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import api from "@/api/client.js";

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const materials = ref([])

const fileTypeIcon = computed(() => {
  return (type) => {
    const iconMap = {
      'pdf': Document,
      'doc': Document,
      'docx': Document,
      'ppt': Document,
      'pptx': Document,
      'video': VideoPlay,
      'image': Picture,
      'default': Document
    }
    return iconMap[type] || iconMap.default
  }
})

const fileTypeColor = computed(() => {
  return (type) => {
    const colorMap = {
      'pdf': '#f56565',
      'doc': '#4299e1',
      'docx': '#4299e1',
      'ppt': '#ed8936',
      'pptx': '#ed8936',
      'video': '#9f7aea',
      'image': '#48bb78',
      'default': '#a0aec0'
    }
    return colorMap[type] || colorMap.default
  }
})

// 文件大小格式化
const formatFileSize = (bytes) => {
  if (!bytes) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

// 日期格式化
const formatDate = (dateString) => {
  if (!dateString) return ''
  return dayjs(dateString).format('YYYY-MM-DD HH:mm')
}

const loadMaterials = async () => {
  if (!courseStore.activeCourseId) return
  
  loading.value = true
  try {
    const response = await fetchStudentMaterials(courseStore.activeCourseId)
    materials.value = response.data.items || response.data
  } catch (err) {
    ElMessage.error('加载资料失败')
  } finally {
    loading.value = false
  }
}

const downloadMaterial = async (material) => {
  try {
    // 使用配置了JWT拦截器的api客户端，而不是原生fetch
    let downloadUrl = material.path;
    if (!downloadUrl.startsWith('/api/')) {
      downloadUrl = `/api/uploads/${downloadUrl}`;
    }
    
    // 使用api客户端，它会自动处理JWT令牌
    const response = await api.get(downloadUrl, { 
      responseType: 'blob' 
    });
    
    if (response.status === 200) {
      const blob = response.data;
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = material.title || '资料下载';
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      ElMessage.success('下载成功');
    } else {
      ElMessage.error('下载失败');
    }
  } catch (err) {
    ElMessage.error('下载失败：' + (err.response?.data?.message || '网络错误'));
  }
}

onMounted(loadMaterials)
</script>

<template>
  <div class="page">
    <div class="page-header">
      <div>
        <h2>课程资料</h2>
        <p class="sub">查看和下载课程相关学习资料</p>
      </div>
    </div>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="materials.length === 0" class="empty">
      <el-empty description="暂无资料" />
    </div>

    <div v-else class="materials-grid">
      <el-card 
        v-for="material in materials" 
        :key="material.id" 
        shadow="hover" 
        class="material-card"
      >
        <div class="material-header">
          <el-icon :size="24" :color="fileTypeColor(material.file_type)">
            <component :is="fileTypeIcon(material.file_type)" />
          </el-icon>
          <div class="material-info">
            <h3 class="material-title">{{ material.title }}</h3>
            <p class="material-meta">
              {{ material.file_type?.toUpperCase() }} · {{ formatFileSize(material.size) }} · {{ formatDate(material.created_at) }}
            </p>
          </div>
        </div>
        
        <p class="material-description">{{ material.description }}</p>
        
        <div class="material-tags" v-if="material.tags && material.tags.length">
          <el-tag 
            v-for="tag in material.tags" 
            :key="tag" 
            size="small" 
            type="info"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <div class="material-actions">
          <el-button 
            type="primary" 
            size="small" 
            :icon="Download"
            @click="downloadMaterial(material)"
          >
            下载
          </el-button>
        </div>
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

.materials-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 16px;
}

.material-card {
  transition: all 0.2s;
}

.material-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.material-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.material-info {
  flex: 1;
}

.material-title {
  margin: 0 0 4px;
  font-size: 16px;
  font-weight: 600;
  color: #0f172a;
}

.material-meta {
  margin: 0;
  font-size: 12px;
  color: #94a3b8;
}

.material-description {
  margin: 0 0 16px;
  font-size: 14px;
  color: #64748b;
  line-height: 1.5;
}

.material-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin-bottom: 16px;
}

.material-actions {
  display: flex;
  justify-content: flex-end;
}

.loading {
  padding: 40px 0;
}

.empty {
  padding: 60px 0;
}

@media (max-width: 768px) {
  .materials-grid {
    grid-template-columns: 1fr;
  }
}
</style>