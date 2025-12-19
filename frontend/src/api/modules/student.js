import api from '../client'

// 学生仪表板数据
export function fetchStudentDashboard(courseId) {
  return api.get(`/courses/${courseId}/student/dashboard`)
}

// 学生资料列表
export function fetchStudentMaterials(courseId, params) {
  return api.get(`/courses/${courseId}/student/materials`, { params })
}

// 学生考勤记录
export function fetchStudentAttendance(courseId) {
  return api.get(`/courses/${courseId}/student/attendance`)
}

// 学生签到
export function apiStudentCheckIn(courseId, sessionId, payload) {
  return api.post(`/courses/${courseId}/student/attendance/${sessionId}/checkin`, payload)
}

// 学生成绩查询
export function fetchStudentGrades(courseId) {
  return api.get(`/courses/${courseId}/student/grades`)
}

// 学生作业列表
export function fetchStudentAssignments(courseId) {
  return api.get(`/courses/${courseId}/student/assignments`)
}

// 学生投票列表
export function fetchStudentPolls(courseId) {
  return api.get(`/courses/${courseId}/student/polls`)
}

// 学生投票
export function studentVote(courseId, pollId, payload) {
  return api.post(`/courses/${courseId}/student/polls/${pollId}/vote`, payload)
}

// 学生课堂互动数据
export function fetchStudentInteractions(courseId) {
  return api.get(`/courses/${courseId}/student/interactions`)
}

// 学生课程列表
export function fetchStudentCourses() {
  return api.get('/courses/student/courses')
}