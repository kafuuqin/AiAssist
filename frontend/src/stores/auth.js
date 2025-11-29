import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import api from '../api/client'

const TOKEN_KEY = 'ta_access_token'

export const useAuthStore = defineStore('auth', () => {
  const accessToken = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(null)
  const loading = ref(false)

  watch(
    accessToken,
    (val) => {
      if (val) {
        localStorage.setItem(TOKEN_KEY, val)
      } else {
        localStorage.removeItem(TOKEN_KEY)
      }
    },
    { immediate: true }
  )

  const isAuthenticated = computed(() => Boolean(accessToken.value))

  async function login(payload) {
    loading.value = true
    try {
      const { data } = await api.post('/auth/login', payload)
      accessToken.value = data.access_token
      user.value = data.user
      return data
    } finally {
      loading.value = false
    }
  }

  async function register(payload) {
    loading.value = true
    try {
      await api.post('/auth/register', payload)
      // 注册后直接登录
      return await login({ email: payload.email, password: payload.password })
    } finally {
      loading.value = false
    }
  }

  async function fetchMe() {
    if (!accessToken.value) return null
    const { data } = await api.get('/auth/me')
    user.value = data
    return data
  }

  function logout() {
    accessToken.value = ''
    user.value = null
  }

  return {
    accessToken,
    user,
    loading,
    isAuthenticated,
    login,
    register,
    logout,
    fetchMe,
  }
})
