<template>
  <div class="profile-container">
    <el-card class="profile-card">
      <template #header>
        <div class="card-header">
          <span>个人资料</span>
        </div>
      </template>
      
      <el-form 
        ref="profileFormRef" 
        :model="profileForm" 
        :rules="rules" 
        label-width="100px"
        class="profile-form"
      >
        <el-form-item label="用户名" prop="username">
          <el-input v-model="profileForm.username" disabled />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="profileForm.email" />
        </el-form-item>
        
        <el-form-item label="姓名" prop="name">
          <el-input v-model="profileForm.name" />
        </el-form-item>
        
        <el-form-item label="角色" prop="role">
          <el-select v-model="profileForm.role" disabled>
            <el-option label="教师" value="teacher" />
            <el-option label="学生" value="student" />
          </el-select>
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="submitForm">保存更改</el-button>
          <el-button @click="resetForm">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <el-card class="password-card">
      <template #header>
        <div class="card-header">
          <span>修改密码</span>
        </div>
      </template>
      
      <el-form 
        ref="passwordFormRef" 
        :model="passwordForm" 
        :rules="passwordRules" 
        label-width="100px"
        class="password-form"
      >
        <el-form-item label="原密码" prop="oldPassword">
          <el-input v-model="passwordForm.oldPassword" type="password" show-password />
        </el-form-item>
        
        <el-form-item label="新密码" prop="newPassword">
          <el-input v-model="passwordForm.newPassword" type="password" show-password />
        </el-form-item>
        
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="passwordForm.confirmPassword" type="password" show-password />
        </el-form-item>
        
        <el-form-item>
          <el-button type="primary" @click="changePassword">修改密码</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/store/auth'

const router = useRouter()
const authStore = useAuthStore()

// 表单引用
const profileFormRef = ref()
const passwordFormRef = ref()

// 个人资料表单
const profileForm = reactive({
  username: '',
  email: '',
  name: '',
  role: ''
})

// 密码表单
const passwordForm = reactive({
  oldPassword: '',
  newPassword: '',
  confirmPassword: ''
})

// 个人资料表单验证规则
const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: ['blur', 'change'] }
  ],
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' }
  ]
}

// 密码表单验证规则
const passwordRules = {
  oldPassword: [
    { required: true, message: '请输入原密码', trigger: 'blur' }
  ],
  newPassword: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码长度至少6位', trigger: 'blur' }
  ],
  confirmPassword: [
    { required: true, message: '请确认新密码', trigger: 'blur' },
    { 
      validator: (rule, value, callback) => {
        if (value !== passwordForm.newPassword) {
          callback(new Error('两次输入的密码不一致'))
        } else {
          callback()
        }
      },
      trigger: 'blur'
    }
  ]
}

// 提交个人资料表单
const submitForm = async () => {
  if (!profileFormRef.value) return
  
  await profileFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 这里应该是调用API更新用户资料
        // 由于我们没有实际的后端API，这里只做演示
        ElMessage.success('个人资料更新成功')
      } catch (error) {
        ElMessage.error('更新失败: ' + error.message)
      }
    }
  })
}

// 修改密码
const changePassword = async () => {
  if (!passwordFormRef.value) return
  
  await passwordFormRef.value.validate(async (valid) => {
    if (valid) {
      try {
        // 这里应该是调用API修改密码
        // 由于我们没有实际的后端API，这里只做演示
        ElMessage.success('密码修改成功')
        
        // 重置密码表单
        passwordFormRef.value.resetFields()
      } catch (error) {
        ElMessage.error('密码修改失败: ' + error.message)
      }
    }
  })
}

// 重置个人资料表单
const resetForm = () => {
  profileFormRef.value?.resetFields()
}

// 加载用户资料
const loadUserProfile = () => {
  // 从store获取用户信息
  if (authStore.currentUser) {
    profileForm.username = authStore.currentUser.username || ''
    profileForm.email = authStore.currentUser.email || ''
    profileForm.name = authStore.currentUser.name || ''
    profileForm.role = authStore.currentUser.role || ''
  }
}

onMounted(() => {
  // 检查认证状态
  if (!authStore.isAuthenticated) {
    console.log('用户未认证，重定向到登录页')
    router.push('/login')
    return
  }
  
  loadUserProfile()
})
</script>

<style scoped>
.profile-container {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.profile-card,
.password-card {
  width: 100%;
  max-width: 600px;
}

.card-header {
  font-weight: bold;
  font-size: 18px;
}

.profile-form,
.password-form {
  margin-top: 20px;
}

.el-form-item {
  margin-bottom: 20px;
}
</style>