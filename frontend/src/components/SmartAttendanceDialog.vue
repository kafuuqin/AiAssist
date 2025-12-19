<script setup>
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import { useAuthStore } from '../stores/auth'
import { useCourseStore } from '../stores/course'

const props = defineProps({
  visible: {
    type: Boolean,
    default: false,
  },
  sessionId: {
    type: Number,
    default: null,
  },
  courseId: {
    type: Number,
    default: null,
  },
})

const emit = defineEmits(['update:visible', 'finished'])

const auth = useAuthStore()
const courseStore = useCourseStore()

const innerVisible = ref(false)

// 上传相关
const rawFile = ref(null)        // 当前选择的原始文件
const originalPreview = ref('')  // 原图预览（base64）
const recognizing = ref(false)

// 识别结果
const previewImage = ref('')     // 后端返回的画框图片（base64）
const recognizedList = ref([])   // 识别到的学生列表

const hasSession = computed(() => !!props.sessionId)

watch(
    () => props.visible,
    (v) => {
      innerVisible.value = v
      if (!v) {
        resetState()
      }
    }
)

watch(
    () => innerVisible.value,
    (v) => {
      if (!v) {
        emit('update:visible', false)
      }
    }
)

const resetState = () => {
  rawFile.value = null
  originalPreview.value = ''
  previewImage.value = ''
  recognizedList.value = []
}

/**
 * 处理文件选择（Element Plus el-upload 的 on-change 回调）
 */
const handleFileChange = (file) => {
  // file.raw 是真实的 File 对象
  rawFile.value = file.raw || file

  // 生成本地预览
  const reader = new FileReader()
  reader.onload = (e) => {
    originalPreview.value = e.target.result
  }
  reader.readAsDataURL(rawFile.value)
}

/**
 * 触发 el-upload 的手动选择（如果你想用原生 <input type="file"> 也可以）
 */
const uploadRef = ref(null)
/**
 * 调用后端 /faces/recognize 接口
 * 假设返回：
 * {
 *   success: true,
 *   data: {
 *     image_base64: 'data:image/jpeg;base64,...',
 *     faces: [
 *       {
 *         region: {...},
 *         best_match: {
 *           person_id: 123,
 *           distance: 0.23,
 *           is_recognized: true,
 *           extra: { name: '张三' }
 *         }
 *       }
 *     ]
 *   }
 * }
 */
const recognizeCurrentImage = async () => {
  if (!hasSession.value) {
    ElMessage.warning('请选择或创建一个签到任务')
    return
  }
  if (!rawFile.value) {
    ElMessage.warning('请先上传一张图片')
    return
  }

  recognizing.value = true
  try {
    const formData = new FormData()
    formData.append('file', rawFile.value, rawFile.value.name || 'image.jpg')

    const token = auth.token
    const resp = await axios.post('/faces/recognize', formData, {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    })

    const body = resp.data
    if (!body.success) {
      ElMessage.error(body.error || '识别失败')
      return
    }

    previewImage.value = body.data.image_base64
    recognizedList.value = (body.data.faces || []).map((f) => {
      const best = f.best_match || {}
      const extra = best.extra || {}
      return {
        region: f.region,
        student_id: best.person_id,
        name: extra.name || `学生${best.person_id}`,
        distance: best.distance,
        is_recognized: best.is_recognized,
      }
    })

    if (!recognizedList.value.length) {
      ElMessage.info('未识别到已录入的学生')
    } else {
      ElMessage.success(`识别到 ${recognizedList.value.length} 位学生`)
    }
  } catch (err) {
    console.error(err)
    ElMessage.error(err.response?.data?.error || '识别请求失败')
  } finally {
    recognizing.value = false
  }
}

/**
 * 完成签到：把识别出的学生列表提交到课程考勤接口
 * 你可以按自己后端的实际接口调整：
 *   例如 POST /courses/:course_id/attendance/:session_id/smart_checkin
 */
const submitSmartAttendance = async () => {
  if (!props.courseId || !props.sessionId) {
    ElMessage.warning('缺少课程或签到任务信息')
    return
  }
  if (!recognizedList.value.length) {
    ElMessage.warning('当前没有可提交的识别结果')
    return
  }

  try {
    // 这里假设你在 courseStore 里实现了 submitSmartAttendance
    await courseStore.submitSmartAttendance({
      courseId: props.courseId,
      sessionId: props.sessionId,
      records: recognizedList.value.map((r) => ({
        student_id: r.student_id,
        status: 'present',
        evidence: `face-${r.distance.toFixed(3)}`,
      })),
    })

    ElMessage.success('智能点到已提交')
    emit('finished', { sessionId: props.sessionId })
    innerVisible.value = false
    emit('update:visible', false)
  } catch (err) {
    console.error(err)
    ElMessage.error(err.response?.data?.message || '提交签到失败')
  }
}
</script>

<template>
  <el-dialog
      v-model="innerVisible"
      width="80%"
      :close-on-click-modal="false"
      title="智能点到（人脸识别）"
  >
    <div v-if="!hasSession" class="empty-hint">
      <el-empty description="请先在上方创建一个进行中的签到任务" />
    </div>

    <div v-else class="smart-layout">
      <!-- 左侧：上传 + 原图 / 识别图 -->
      <div class="left">
        <p class="block-title">上传识别图片</p>
        <el-upload
            ref="uploadRef"
            class="upload-block"
            :show-file-list="false"
            :auto-upload="false"
            accept="image/*"
            :on-change="handleFileChange"
        >
          <el-button type="primary">选择图片</el-button>
          <span style="margin-left: 8px; color: #64748b">
            支持 JPG / PNG
          </span>
        </el-upload>

        <p class="block-title" style="margin-top: 16px">原始图片预览</p>
        <div class="preview-box light">
          <img v-if="originalPreview" :src="originalPreview" class="preview-img" />
          <el-empty v-else description="请先选择图片" />
        </div>

        <div class="actions">
          <el-button
              type="success"
              :loading="recognizing"
              :disabled="!rawFile"
              @click="recognizeCurrentImage"
          >
            识别本次图片
          </el-button>
        </div>

        <p class="block-title" style="margin-top: 16px">识别结果画面</p>
        <div class="preview-box dark">
          <img v-if="previewImage" :src="previewImage" class="preview-img" />
          <el-empty v-else description="尚未识别" />
        </div>
      </div>

      <!-- 右侧：识别出的学生列表 -->
      <div class="right">
        <p class="block-title">识别出的学生</p>
        <el-table
            v-if="recognizedList.length"
            :data="recognizedList"
            size="small"
            height="360"
        >
          <el-table-column prop="student_id" label="学生ID" width="100" />
          <el-table-column prop="name" label="姓名" />
          <el-table-column prop="distance" label="距离" width="90">
            <template #default="{ row }">
              {{ row.distance.toFixed(3) }}
            </template>
          </el-table-column>
          <el-table-column label="结果" width="90">
            <template #default="{ row }">
              <el-tag :type="row.is_recognized ? 'success' : 'warning'">
                {{ row.is_recognized ? '匹配' : '未知' }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
        <el-empty
            v-else
            description="暂未识别到学生，请上传图片并点击“识别本次图片”"
        />

        <div class="footer-actions">
          <el-button @click="innerVisible = false">取消</el-button>
          <el-button type="primary" @click="submitSmartAttendance">
            完成签到
          </el-button>
        </div>
      </div>
    </div>
  </el-dialog>
</template>

<style scoped>
.smart-layout {
  display: grid;
  grid-template-columns: 2fr 1.5fr;
  gap: 16px;
}

.left,
.right {
  border-radius: 8px;
  padding: 8px;
  background-color: #f8fafc;
}

.block-title {
  font-weight: 600;
  margin-bottom: 8px;
  color: #0f172a;
}

.upload-block {
  margin-bottom: 8px;
}

.preview-box {
  border-radius: 8px;
  min-height: 160px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.preview-box.light {
  background: #e2e8f0;
}
.preview-box.dark {
  background: #0b1120;
}

.preview-img {
  max-width: 100%;
  max-height: 260px;
  border-radius: 8px;
}

.actions {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.footer-actions {
  margin-top: 16px;
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.empty-hint {
  padding: 24px 0;
}
@media (max-width: 960px) {
  .smart-layout {
    grid-template-columns: 1fr;
  }
}
</style>
