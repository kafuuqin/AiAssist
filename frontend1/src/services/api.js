import axios from 'axios'

// 创建axios实例
const api = axios.create({
  baseURL: '/api', // 使用Vite代理
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 初始化时尝试设置token
const token = localStorage.getItem('token');
console.log('初始化时从localStorage获取的Token:', token);
if (token && typeof token === 'string') {
  api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  // 同时设置另一种方式
  api.defaults.headers['Authorization'] = `Bearer ${token}`;
  console.log('初始化时Token设置成功');
}

// 导出前确保token是最新的
export const updateAuthToken = (newToken) => {
  console.log('尝试更新认证token:', newToken);
  // 验证token是否为有效字符串
  if (newToken && typeof newToken === 'string') {
    api.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
    localStorage.setItem('token', newToken);
    // 同时更新axios实例的默认配置
    api.defaults.headers['Authorization'] = `Bearer ${newToken}`;
    // 确保立即生效
    if (typeof window !== 'undefined') {
      localStorage.setItem('token', newToken);
    }
    console.log('Token更新成功');
  } else {
    console.error('尝试设置无效的token:', { newToken, type: typeof newToken });
    delete api.defaults.headers.common['Authorization'];
    delete api.defaults.headers['Authorization'];
    localStorage.removeItem('token');
  }
};

// 获取当前token
export const getCurrentToken = () => {
  // 优先从localStorage获取
  const token = localStorage.getItem('token');
  if (token && typeof token === 'string') {
    return token;
  }
  
  // 其次从默认headers获取
  if (api.defaults.headers.common && api.defaults.headers.common['Authorization'] && typeof api.defaults.headers.common['Authorization'] === 'string') {
    return api.defaults.headers.common['Authorization'].replace('Bearer ', '');
  }
  
  if (api.defaults.headers && api.defaults.headers['Authorization'] && typeof api.defaults.headers['Authorization'] === 'string') {
    return api.defaults.headers['Authorization'].replace('Bearer ', '');
  }
  
  return null;
};

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 确保headers对象存在
    if (!config.headers) {
      config.headers = {};
    }
    
    // 从本地存储获取token
    const token = localStorage.getItem('token')
    console.log('从localStorage获取的Token:', token);
    
    if (token && typeof token === 'string') {
      config.headers['Authorization'] = `Bearer ${token}`
    } else if (api.defaults.headers.common && api.defaults.headers.common['Authorization'] && typeof api.defaults.headers.common['Authorization'] === 'string') {
      // 从默认headers中获取token
      config.headers['Authorization'] = api.defaults.headers.common['Authorization']
    } else if (api.defaults.headers && api.defaults.headers['Authorization'] && typeof api.defaults.headers['Authorization'] === 'string') {
      // 从默认headers中获取token (另一种方式)
      config.headers['Authorization'] = api.defaults.headers['Authorization']
    } else {
      // 确保移除可能存在的旧认证头
      delete config.headers['Authorization']
    }
    
    // 打印请求头以帮助调试
    console.log('请求头信息:', config.headers)
    console.log('发送请求:', config)
    return config
  },
  (error) => {
    console.error('请求错误:', error)
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    console.log('收到响应:', response)
    return response
  },
  (error) => {
    console.error('响应错误:', error)
    if (error.response?.status === 401) {
      // token过期或无效，清除本地存储并跳转到登录页
      console.log('Token无效或已过期，跳转到登录页')
      // 清除认证存储
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 清除API默认头部
      delete api.defaults.headers.common['Authorization']
      // 只在当前不在登录页时才跳转
      if (typeof window !== 'undefined' && window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
    } else if (error.response?.status >= 500) {
      // 服务器错误
      console.error('服务器内部错误:', error.response?.data?.message || error.message)
    } else if (!error.response) {
      // 网络错误
      console.error('网络连接错误:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api