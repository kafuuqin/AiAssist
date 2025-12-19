import { defineStore } from 'pinia'
import api, { updateAuthToken } from '@/services/api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem('token') || null,
    user: JSON.parse(localStorage.getItem('user') || 'null') || null
  }),

  getters: {
    isAuthenticated: (state) => {
      // 检查store中的token和用户信息
      const hasTokenInStore = !!state.token
      const hasUserInStore = !!state.user
      // 检查localStorage中的token
      const hasTokenInStorage = !!localStorage.getItem('token')
      // 如果store中没有但localStorage中有，则同步到store
      if (!hasTokenInStore && hasTokenInStorage) {
        state.token = localStorage.getItem('token')
        return true
      }
      const result = hasTokenInStore && hasUserInStore
      console.log('检查认证状态:', { hasTokenInStore, hasUserInStore, hasTokenInStorage, result, token: state.token })
      return result
    },
    currentUser: (state) => state.user
  },

  actions: {
    async login(credentials) {
      try {
        console.log('尝试登录，发送的凭证:', credentials)
        const response = await api.post('/auth/login', credentials)
        console.log('登录响应完整数据:', response)
        
        // 检查响应数据结构
        const { access_token, user } = response.data
        console.log('登录响应数据:', { access_token, user })
        
        // 验证必要字段是否存在且为字符串
        if (!access_token || typeof access_token !== 'string' || !user) {
          console.error('Token不是有效字符串:', { access_token, type: typeof access_token });
          throw new Error('登录响应缺少有效token')
        }
        
        // 额外验证token是否为有效的JWT格式（至少包含两个点）
        if (access_token.split('.').length < 3) {
          console.error('Token不是有效的JWT格式:', access_token);
          throw new Error('Token格式无效')
        }
        
        this.token = access_token
        this.user = user
        
        // 验证token是否为有效字符串
        if (typeof access_token !== 'string') {
          throw new Error('Token不是有效字符串')
        }
        
        // 保存到本地存储
        localStorage.setItem('token', access_token)
        localStorage.setItem('user', JSON.stringify(user))
        
        // 使用专用函数更新认证令牌
        updateAuthToken(access_token)
        
        // 验证Token是否被正确设置
        console.log('API默认头部Authorization:', api.defaults.headers.common['Authorization'])
        
        // 确保实时更新localStorage中的token
        if (typeof window !== 'undefined') {
          localStorage.setItem('token', access_token);
        }
        
        // 更新store中的token
        this.token = access_token
        
        // 再次验证token是否正确设置
        const storedToken = localStorage.getItem('token');
        console.log('LocalStorage中的Token:', storedToken);
        
        // 等待一小段时间确保token设置完成
        await new Promise(resolve => setTimeout(resolve, 100))
        
        // 添加更多调试信息
        console.log('当前用户对象:', user)
        console.log('当前Token长度:', access_token.length)
        
        console.log('登录成功，token已设置')
        return { success: true, user }
      } catch (error) {
        console.error('登录失败:', error)
        // 确保在失败时清除任何可能存在的无效Token
        this.logout()
        
        // 增强错误处理
        let errorMessage = '登录失败'
        if (error.response) {
          // 服务器返回了错误状态码
          console.error('服务器错误状态:', error.response.status)
          console.error('服务器错误数据:', error.response.data)
          errorMessage = error.response.data?.message || `登录失败 (${error.response.status})`
        } else if (error.request) {
          // 请求已发出但没有收到响应
          console.error('网络请求无响应:', error.request)
          errorMessage = '网络连接失败，请检查网络设置'
        } else if (error.message) {
          // 其他错误
          console.error('请求错误:', error.message)
          errorMessage = error.message
        } else {
          console.error('未知错误:', error)
          errorMessage = '登录过程中发生未知错误'
        }
        
        return { success: false, error: errorMessage }
      }
    },

    async register(userData) {
      try {
        const response = await api.post('/auth/register', userData)
        return { success: true, message: response.data.message }
      } catch (error) {
        return { success: false, error: error.response?.data?.message || '注册失败' }
      }
    },

    logout() {
      this.token = null
      this.user = null
      
      // 清除本地存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      
      // 清除API默认头部
      delete api.defaults.headers.common['Authorization']
      
      // 为了确保彻底清除，我们也直接从api实例中删除
      if (api.defaults.headers.common && api.defaults.headers.common['Authorization']) {
        delete api.defaults.headers.common['Authorization']
      }
      
      // 重定向到登录页
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
    },

    async fetchProfile() {
      try {
        const response = await api.get('/auth/profile')
        this.user = response.data
        
        // 更新本地存储
        localStorage.setItem('user', JSON.stringify(response.data))
        
        return { success: true, user: response.data }
      } catch (error) {
        return { success: false, error: error.response?.data?.message || '获取用户信息失败' }
      }
    }
  }
})