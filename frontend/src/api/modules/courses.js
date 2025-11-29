import api from '../client'

export function fetchMyCourses() {
  return api.get('/courses')
}

export function createCourse(payload) {
  return api.post('/courses', payload)
}

export function fetchMaterials(courseId, params) {
  return api.get(`/courses/${courseId}/materials`, { params })
}

export function createMaterial(courseId, payload) {
  return api.post(`/courses/${courseId}/materials`, payload)
}

export function fetchAttendance(courseId) {
  return api.get(`/courses/${courseId}/attendance`)
}

export function createAttendance(courseId, payload) {
  return api.post(`/courses/${courseId}/attendance`, payload)
}

export function fetchAttendanceDetail(courseId, sessionId) {
  return api.get(`/courses/${courseId}/attendance/${sessionId}`)
}

export function fetchGrades(courseId) {
  return api.get(`/courses/${courseId}/grades`)
}

export function exportGrades(courseId, params = {}) {
  return api.get(`/courses/${courseId}/grades`, {
    params: { ...params, export: 'csv' },
    responseType: 'blob',
  })
}

export function fetchGradeStats(courseId) {
  return api.get(`/courses/${courseId}/grades/stats`)
}

export function fetchAssignments(courseId) {
  return api.get(`/courses/${courseId}/assignments`)
}

export function createAssignment(courseId, payload) {
  return api.post(`/courses/${courseId}/assignments`, payload)
}

export function createGrade(courseId, assignmentId, payload) {
  return api.post(`/courses/${courseId}/assignments/${assignmentId}/grades`, payload)
}

export function importGrades(courseId, payload) {
  return api.post(`/courses/${courseId}/grades/import`, payload)
}

export function downloadGradeTemplate(courseId) {
  return api.get(`/courses/${courseId}/grades/template`, { responseType: 'blob' })
}

export function fetchPolls(courseId) {
  return api.get(`/courses/${courseId}/polls`)
}

export function createPoll(courseId, payload) {
  return api.post(`/courses/${courseId}/polls`, payload)
}

export function votePoll(courseId, pollId, payload) {
  return api.post(`/courses/${courseId}/polls/${pollId}/vote`, payload)
}
