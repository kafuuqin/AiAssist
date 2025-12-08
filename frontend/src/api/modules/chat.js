import api from '../client'

export function sendMessage(payload) {
  return api.post('/chat', payload)
}

export function batchQuery(payload) {
  return api.post('/chat/batch', payload)
}

export function uploadDocument(formData) {
  const token = localStorage.getItem('ta_access_token')
  return api.post('/chat/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
}

export function getChatStatus() {
  return api.get('/chat/status')
}

export function clearChatHistory() {
  return api.post('/chat/clear')
}

export function getChatHistory() {
  return api.get('/chat/history')
}

export function initializeChatSystem(payload) {
  return api.post('/chat/initialize', payload)
}