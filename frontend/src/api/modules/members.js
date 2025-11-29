import api from '../client'

export function fetchMembers(courseId) {
  return api.get(`/courses/${courseId}/members`)
}

export function addMember(courseId, payload) {
  return api.post(`/courses/${courseId}/members`, payload)
}

export function searchUsers(params) {
  return api.get('/users', { params })
}

export function updateMember(courseId, memberId, payload) {
  return api.patch(`/courses/${courseId}/members/${memberId}`, payload)
}

export function deleteMember(courseId, memberId) {
  return api.delete(`/courses/${courseId}/members/${memberId}`)
}
