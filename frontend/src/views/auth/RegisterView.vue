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
  name: '',
  email: '',
  password: '',
  confirm: '',
})

const rules = {
  name: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  email: [{ required: true, message: '请输入邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
  confirm: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    {
      validator: (_, value, callback) => {
        if (value !== form.password) callback(new Error('两次输入不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

const handleRegister = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return
    try {
      ElMessage.info(form.name)
      await auth.register({ name: form.name, email: form.email, password: form.password })
      ElMessage.info(form.email)
      const redirect = route.query.redirect || '/'
      ElMessage.info(form.password)
      router.replace(redirect)
      ElMessage.info(form.name)
      ElMessage.success('注册成功，已自动登录')
    } catch (err) {
      const msg = err.response?.data?.message || '注册失败，请稍后重试'
      ElMessage.error(msg)
    }
  })
}
</script>

<template>
  <div class="auth-page">
    <div class="panel">
      <div class="welcome">
        <p class="eyebrow">CREATE ACCOUNT</p>
        <h1>注册教师智能助手</h1>
        <p class="desc">完善个人信息后，可立即登录并开始管理课程、资料与考勤。</p>
      </div>
      <el-card shadow="hover" class="form-card">
        <h3>创建新账号</h3>
        <el-form :model="form" :rules="rules" label-position="top" ref="formRef" @keyup.enter="handleRegister">
          <el-form-item label="姓名" prop="name">
            <el-input v-model="form.name" placeholder="请输入姓名" autocomplete="name" />
          </el-form-item>
          <el-form-item label="邮箱" prop="email">
            <el-input v-model="form.email" placeholder="name@example.com" autocomplete="email" />
          </el-form-item>
          <el-form-item label="密码" prop="password">
            <el-input v-model="form.password" type="password" show-password placeholder="至少 6 位" />
          </el-form-item>
          <el-form-item label="确认密码" prop="confirm">
            <el-input v-model="form.confirm" type="password" show-password placeholder="再次输入密码" />
          </el-form-item>
          <el-button type="primary" class="submit" :loading="auth.loading" @click="handleRegister">
            注册并登录
          </el-button>
          <el-button text class="link" @click="router.push({ name: 'login' })">已有账号？去登录</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
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
