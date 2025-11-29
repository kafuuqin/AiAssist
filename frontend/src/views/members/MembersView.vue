<script setup>
import { onMounted, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { useCourseStore } from '../../stores/course'
import { useAuthStore } from '../../stores/auth'

const courseStore = useCourseStore()
const auth = useAuthStore()
const loading = ref(false)
const adding = ref(false)
const selectedUser = ref(null)
const role = ref('student')
const userOptions = ref([])
const isOwner = ref(false)
const roleOptions = [
  { label: '拥有者', value: 'owner' },
  { label: '教师', value: 'teacher' },
  { label: '助教', value: 'assistant' },
  { label: '学生', value: 'student' },
]

const load = async () => {
  if (!courseStore.activeCourseId) return
  loading.value = true
  try {
    await courseStore.loadMembers()
  const course = courseStore.currentCourse
  isOwner.value = course && auth.user && course.owner_id === auth.user.id
  // admin 视为拥有者权限
  if (auth.user?.role === 'admin') {
    isOwner.value = true
  }
  } catch (err) {
    ElMessage.error('加载成员失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = async () => {
  if (!isOwner.value) {
    ElMessage.warning('只有课程拥有者可以添加成员')
    return
  }
  if (!selectedUser.value) {
    ElMessage.warning('请选择用户')
    return
  }
  adding.value = true
  try {
    await courseStore.addCourseMember({ user_id: selectedUser.value.id, role_in_course: role.value })
    ElMessage.success('添加成功')
    selectedUser.value = null
    role.value = 'student'
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '添加失败')
  } finally {
    adding.value = false
  }
}

const handleSearchUser = async (query) => {
  const items = await courseStore.searchUsers(query)
  userOptions.value = items || []
}

const handleRoleChange = async (member) => {
  if (!isOwner.value) {
    ElMessage.warning('只有拥有者可修改角色')
    return
  }
  try {
    await courseStore.updateCourseMember(member.id, { role_in_course: member.role_in_course })
    ElMessage.success('角色已更新')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '更新失败')
  }
}

const handleRemove = async (member) => {
  if (!isOwner.value) {
    ElMessage.warning('只有拥有者可移除成员')
    return
  }
  try {
    await courseStore.removeCourseMember(member.id)
    ElMessage.success('已移除')
  } catch (err) {
    ElMessage.error(err.response?.data?.message || '移除失败')
  }
}

onMounted(load)
watch(
  () => courseStore.activeCourseId,
  () => load()
)
</script>

<template>
  <div class="page">
    <div class="page-head">
      <div>
        <p class="eyebrow">课程成员</p>
        <h2>成员列表与权限</h2>
        <p class="sub">仅课程拥有者可添加成员（示例）。当前后端通过 user_id 添加。</p>
      </div>
      <div class="actions">
        <el-select
          v-model="selectedUser"
          filterable
          remote
          reserve-keyword
          placeholder="搜索姓名/邮箱"
          :remote-method="handleSearchUser"
          :loading="adding"
          style="width: 220px"
        >
          <el-option
            v-for="item in userOptions"
            :key="item.id"
            :label="`${item.name || ''} (${item.email})`"
            :value="item"
          />
        </el-select>
        <el-select v-model="role" placeholder="角色" style="width: 140px">
          <el-option v-for="opt in roleOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-button type="primary" :loading="adding" @click="handleAdd">添加成员</el-button>
      </div>
    </div>

    <el-table :data="courseStore.members" size="small" border v-loading="loading">
      <el-table-column prop="user.name" label="姓名">
        <template #default="{ row }">
          {{ row.user?.name || row.user_id }}
        </template>
      </el-table-column>
      <el-table-column prop="user.email" label="邮箱" />
      <el-table-column prop="role_in_course" label="角色" width="160">
        <template #default="{ row }">
          <el-select
            v-model="row.role_in_course"
            size="small"
            :disabled="!isOwner"
            style="width: 140px"
            @change="() => handleRoleChange(row)"
          >
            <el-option v-for="opt in roleOptions" :key="opt.value" :label="opt.label" :value="opt.value" />
          </el-select>
        </template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="120" />
      <el-table-column label="操作" width="120">
        <template #default="{ row }">
          <el-button text size="small" type="danger" :disabled="!isOwner" @click="() => handleRemove(row)">
            移除
          </el-button>
        </template>
      </el-table-column>
    </el-table>
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
  margin: 0;
  color: #64748b;
}

.actions {
  display: flex;
  gap: 10px;
}
</style>
