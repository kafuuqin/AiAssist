import api from '../client'

export function uploadFile(formData) {
  const token = localStorage.getItem('ta_access_token')
  return api.post('/uploads', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
  })
}
