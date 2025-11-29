<script setup>
import { ElMessage } from 'element-plus'
import { reactive, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../../stores/auth'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()
const formRef = ref()

const form = reactive({
  email: '',
  password: '',
})

const rules = {
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

const handleLogin = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate()
  if (!valid) return
  try {
    await auth.login(form)
    const redirect = route.query.redirect || '/'
    router.replace(redirect)
  } catch (err) {
    const message = err.response?.data?.message || '登录失败，请检查账号密码'
    ElMessage.error(message)
  }
}
</script>

<template>
  <div class="login-page">
    <div class="panel">
      <div class="welcome">
        <p class="eyebrow">TEACHER ASSISTANT</p>
        <h1>智慧教学管理</h1>
        <p class="desc">
          统一管理资料、考勤、成绩分析与课堂互动，接入 AI 助手，释放教师生产力。
        </p>
      </div>
      <el-card shadow="hover" class="form-card">
        <h3>登录教师智能助手</h3>
        <el-form :model="form" :rules="rules" label-position="top" ref="formRef" @keyup.enter="handleLogin">
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="name@example.com" autocomplete="email" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" placeholder="请输入密码" type="password" show-password />
        </el-form-item>
        <el-button type="primary" class="submit" :loading="auth.loading" @click="handleLogin">
          登录
        </el-button>
        <el-button text class="link" @click="router.push({ name: 'register' })">还没有账号？去注册</el-button>
      </el-form>
    </el-card>
  </div>
</div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: grid;
  place-items: center;
  background: radial-gradient(circle at 15% 20%, #f9f5ff 0, #eef2ff 40%, #fefefe 100%);
  padding: 32px;
}

.panel {
  width: min(100%, 960px);
  background: rgba(255, 255, 255, 0.7);
  border-radius: 24px;
  padding: 32px;
  box-shadow: 0 20px 60px rgba(79, 114, 205, 0.15);
  display: grid;
  grid-template-columns: 1.2fr 1fr;
  gap: 24px;
}

.welcome {
  padding: 12px 12px 12px 0;
}

.eyebrow {
  letter-spacing: 0.12em;
  color: #64748b;
  font-weight: 700;
  margin-bottom: 10px;
}

h1 {
  margin: 0 0 12px;
  font-size: 32px;
  color: #0f172a;
}

.desc {
  color: #475569;
  line-height: 1.6;
}

.form-card {
  border: 1px solid #e5e7eb;
  border-radius: 16px;
}

.form-card h3 {
  margin: 0 0 16px;
  color: #0f172a;
}

.submit {
  width: 100%;
  margin-top: 8px;
}

.link {
  width: 100%;
}

@media (max-width: 960px) {
  .panel {
    grid-template-columns: 1fr;
    padding: 24px;
  }
}
</style>
