<template>
  <div class="login-container">
    <div class="login-box">
      <h2>教师智能助手</h2>
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        label-width="0px"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="请输入用户名" 
            prefix-icon="User"
            clearable
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="请输入密码" 
            prefix-icon="Lock"
            show-password
          />
        </el-form-item>
        
        <el-form-item>
          <el-button 
            type="primary" 
            native-type="submit" 
            :loading="loading" 
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>
        
        <div class="footer">
          <span>还没有账号？</span>
          <el-button type="text" @click="$router.push('/register')">立即注册</el-button>
        </div>
      </el-form>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/store/auth'
import { ElMessage } from 'element-plus'
import api from '@/services/api'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于6位', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        console.log('准备登录，发送的数据:', loginForm)
        const result = await authStore.login(loginForm)
        console.log('登录结果:', result)
        if (result.success) {
          ElMessage.success('登录成功')
          // 确保API头部已正确设置
          console.log('登录成功后的Authorization头部:', api.defaults.headers.common['Authorization'])
          // 等待一段时间确保token设置完成
          await new Promise(resolve => setTimeout(resolve, 200))
          router.push('/dashboard')
        } else {
          // 根据不同的错误类型显示不同的消息
          if (result.error.includes('网络')) {
            ElMessage.error('网络连接失败，请检查网络设置')
          } else if (result.error.includes('401') || result.error.includes('认证')) {
            ElMessage.error('用户名或密码错误')
          } else {
            ElMessage.error(result.error)
          }
        }
      } catch (error) {
        console.error('登录过程中发生未预期的错误:', error)
        ElMessage.error('登录过程中发生错误，请稍后再试')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
  background-color: #f0f2f5;
}

.login-box {
  width: 400px;
  padding: 40px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-box h2 {
  text-align: center;
  margin-bottom: 30px;
  color: #333;
}

.footer {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-top: 20px;
}
</style>