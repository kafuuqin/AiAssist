<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { uploadFile } from '../../api/modules/uploads'
import { useAuthStore } from '../../stores/auth'
import api from '../../api/client'
import { classifyMaterial } from '../../api/modules/ai'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const dialogVisible = ref(false)
const searchKey = ref('')
const selectedTag = ref('')
const form = reactive({
  title: '',
  description: '',
  file_type: 'PDF',
  tags: [],
  file: null,
})
const tagOptions = computed(() => {
  const set = new Set()
  courseStore.materials.forEach((m) => (m.tags || []).forEach((t) => set.add(t)))
  return Array.from(set)
})

const isManager = computed(() => {
  const course = courseStore.currentCourse
  if (!auth.user) return false
  if (auth.user.role === 'admin') return true
  if (course && course.owner_id === auth.user.id) return true
  return auth.user.role === 'teacher'
})

const handleAutoClassify = async () => {
  if (!courseStore.activeCourseId) {
    ElMessage.warning('请选择课程')
    return
  }
  if (!courseStore.materials.length) {
    ElMessage.info('暂无资料可分类')
    return
  }
  try {
    loading.value = true
    const results = []
    for (const m of courseStore.materials) {
      const res = await classifyMaterial({ material_id: m.id, course_id: courseStore.activeCourseId })
      results.push({ id: m.id, tags: res.data?.tags || [] })
    }
    await load()
    ElMessage.success(`分类完成，共处理 ${results.length} 条`)
  } catch (err) {
    const msg = err.response?.data?.message || '分类失败'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}

const load = async (page = 1) => {
  if (!courseStore.activeCourseId) return
  loading.value = true
  try {
    await courseStore.loadMaterials(courseStore.activeCourseId, {
      page,
      q: searchKey.value || undefined,
      tags: selectedTag.value || undefined,
    })
  } catch (err) {
    ElMessage.error('加载资料失败')
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!form.title) {
    ElMessage.warning('请输入标题')
    return
  }
  if (!form.file) {
    ElMessage.warning('请选择文件')
    return
  }
  try {
    const fd = new FormData()
    fd.append('file', form.file)
    const uploadRes = await uploadFile(fd)
    await courseStore.addMaterial({
      title: form.title,
      description: form.description,
      file_type: form.file_type,
      tags: form.tags,
      path: uploadRes.data?.url,
      size: form.file.size,
    })
    ElMessage.success('上传成功')
    dialogVisible.value = false
    form.title = ''
    form.description = ''
    form.tags = []
    form.file = null
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '上传失败')
  }
}

const handlePreview = (path) => {
  downloadOrOpen(path, true)
}

const handleDownload = (path) => {
  downloadOrOpen(path, false)
}

const downloadOrOpen = async (path, inline = false) => {
  if (!path) {
    ElMessage.warning('暂无文件路径')
    return
  }
  try {
    const endpoint = path.startsWith('/api/') ? path.replace('/api/', '') : path.replace(/^\//, '')
    const { data } = await api.get(endpoint, { responseType: 'blob' })
    const blob = new Blob([data])
    const url = window.URL.createObjectURL(blob)
    if (inline) {
      window.open(url, '_blank')
    } else {
      const link = document.createElement('a')
      link.href = url
      link.download = endpoint.split('/').pop() || 'download'
      link.click()
    }
    window.URL.revokeObjectURL(url)
  } catch (err) {
    const msg = err.response?.data?.message || '文件获取失败，请检查权限'
    ElMessage.error(msg)
  }
}

onMounted(load)
watch(
  () => courseStore.activeCourseId,
  () => load(1)
)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <p class="eyebrow">资料中心</p>
        <h2>课程资料归档与搜索</h2>
        <p class="sub">上传/下载、在线预览、标签管理与自动分类。</p>
      </div>
      <div class="actions" v-if="isManager">
        <el-button type="primary" plain @click="dialogVisible = true">上传资料</el-button>
        <el-button type="success" plain @click="handleAutoClassify">AI 自动分类</el-button>
      </div>
    </div>

    <div class="filter">
      <el-input
        v-model="searchKey"
        placeholder="搜索标题/描述"
        prefix-icon="Search"
        clearable
        @clear="() => load(1)"
        @keyup.enter="() => load(1)"
      >
        <template #append>
          <el-button @click="() => load(1)">搜索</el-button>
        </template>
      </el-input>
      <el-segmented
        :options="[{ label: '全部', value: '' }, ...tagOptions.map((t) => ({ label: t, value: t }))]"
        size="large"
        :model-value="selectedTag"
        @change="(val) => { selectedTag.value = val; load(1) }"
      />
    </div>

    <el-empty v-if="!courseStore.materials.length && !loading" description="暂无资料" />
    <div v-else class="grid">
      <el-skeleton v-if="loading" animated :rows="4" />
      <el-card
        v-else
        v-for="item in courseStore.materials"
        :key="item.id"
        shadow="hover"
        class="material-card"
      >
        <div class="file-type">{{ item.file_type || '文件' }}</div>
        <h4>{{ item.title }}</h4>
        <div class="tags">
          <el-tag v-for="tag in item.tags || []" :key="tag" size="small" type="info">{{ tag }}</el-tag>
        </div>
        <p class="meta">上传者 {{ item.uploader_id }} · {{ item.created_at?.slice(0, 10) }}</p>
        <div class="card-actions">
          <el-button size="small" text @click="handlePreview(item.path)">预览</el-button>
          <el-button size="small" text type="primary" @click="handleDownload(item.path)">下载</el-button>
          <el-button size="small" text type="success">重分类</el-button>
        </div>
      </el-card>
    </div>

    <div class="pager" v-if="courseStore.materialPagination.total > courseStore.materialPagination.page_size">
      <el-pagination
        layout="prev, pager, next"
        :total="courseStore.materialPagination.total"
        :page-size="courseStore.materialPagination.page_size"
        :current-page="courseStore.materialPagination.page"
        @current-change="(p) => load(p)"
      />
    </div>

    <el-dialog v-model="dialogVisible" title="上传资料（示例接口）" width="480px">
      <el-form label-position="top">
        <el-form-item label="标题">
          <el-input v-model="form.title" placeholder="请输入资料标题" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="2" />
        </el-form-item>
        <el-form-item label="文件">
          <el-upload
            drag
            :auto-upload="false"
            :limit="1"
            accept=".pdf,.ppt,.pptx,.doc,.docx,.xls,.xlsx"
            :on-change="(file) => (form.file = file.raw)"
          >
            <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
            <div class="el-upload__text">拖拽或点击上传</div>
          </el-upload>
        </el-form-item>
        <el-form-item label="文件类型">
          <el-select v-model="form.file_type" style="width: 100%">
            <el-option label="PDF" value="PDF" />
            <el-option label="PPT" value="PPT" />
            <el-option label="DOCX" value="DOCX" />
            <el-option label="XLSX" value="XLSX" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <el-select v-model="form.tags" multiple placeholder="输入或选择标签" allow-create filterable>
            <el-option v-for="tag in form.tags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">提交</el-button>
      </template>
    </el-dialog>
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
  color: #64748b;
  margin: 0;
}

.actions {
  display: flex;
  gap: 10px;
}

.filter {
  display: grid;
  grid-template-columns: 2fr auto;
  gap: 12px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 14px;
}

.material-card {
  position: relative;
}

.file-type {
  position: absolute;
  right: 14px;
  top: 14px;
  background: #eef2ff;
  color: #4338ca;
  padding: 4px 8px;
  border-radius: 8px;
  font-weight: 700;
}

h4 {
  margin: 0 0 6px;
}

.tags {
  display: flex;
  gap: 6px;
  margin-bottom: 10px;
}

.meta {
  margin: 0 0 10px;
  color: #94a3b8;
}

.card-actions {
  display: flex;
  gap: 8px;
}

.pager {
  margin-top: 12px;
  display: flex;
  justify-content: flex-end;
}
</style>
