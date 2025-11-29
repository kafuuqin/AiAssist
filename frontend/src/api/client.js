import axios from 'axios'

const baseURL = import.meta.env.VITE_API_BASE || '/api'

const api = axios.create({
  baseURL,
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('ta_access_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (res) => {
    // 后端统一返回 {"data": actualPayload}，这里解包以便上层直接使用
    const payload = res.data
    if (payload && typeof payload === 'object' && 'data' in payload) {
      res.data = payload.data
    }
    return res
  },
  (error) => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('ta_access_token')
    }
    if (!error.response) {
      // 网络/代理错误，便于定位
      console.error('API network error', error)
    }
    return Promise.reject(error)
  }
)

export default api
