import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import {
  fetchMyCourses,
  fetchMaterials,
  fetchAttendance,
  fetchAttendanceDetail,
  fetchGrades,
  fetchGradeStats,
  fetchPolls,
  createMaterial,
  createAttendance,
  createPoll,
  fetchAssignments,
  createAssignment,
  createGrade,
  importGrades,
} from '../api/modules/courses'
import {
    fetchStudentDashboard,
    fetchStudentMaterials,
    fetchStudentAttendance,
    fetchStudentGrades,
    fetchStudentAssignments,
    fetchStudentPolls,
    studentVote,
    fetchStudentInteractions,
    fetchStudentCourses, apiStudentCheckIn, // 确保这行导入存在
} from '../api/modules/student'
import { fetchMembers, addMember, updateMember, deleteMember } from '../api/modules/members'
import debounce from 'lodash.debounce'

export const useCourseStore = defineStore('course', () => {
  const courses = ref([])
  const activeCourseId = ref('')
  const materials = ref([])
  const materialPagination = ref({ page: 1, page_size: 10, total: 0 })
  const attendance = ref([])
  const attendanceDetail = ref({ session: null, records: [] })
  const grades = ref([])
  const gradeStats = ref({})
  const polls = ref([])
  const assignments = ref([])
  const members = ref([])
  const memberSearch = ref({ items: [], total: 0 })

  // 学生端数据
  const studentDashboard = ref({})
  const studentMaterials = ref([])
  const studentAttendance = ref([])
  const studentGrades = ref([])
  const studentAssignments = ref([])
  const studentPolls = ref([])

  const currentCourse = computed(() => courses.value.find((c) => String(c.id) === String(activeCourseId.value)))

  async function loadCourses() {
    const { data } = await fetchMyCourses()
    courses.value = data
    if (!activeCourseId.value && data?.length) {
      activeCourseId.value = data[0].id
    }
    return data
  }

  // 添加学生端课程加载方法
  async function loadStudentCourses() {
    const { data } = await fetchStudentCourses()
    courses.value = data
    if (!activeCourseId.value && data?.length) {
      activeCourseId.value = data[0].id
    }
    return data
  }

  // 修改后的loadCourses方法，根据用户角色调用不同的API
  async function loadCoursesByRole(userRole) {
    if (userRole === 'student') {
      return await loadStudentCourses()
    } else {
      return await loadCourses()
    }
  }

  async function loadMaterials(courseId = activeCourseId.value, params = {}) {
    if (!courseId) return []
    const page = params.page || materialPagination.value.page
    const pageSize = params.page_size || materialPagination.value.page_size
    const { data } = await fetchMaterials(courseId, {
      page,
      page_size: pageSize,
      q: params.q,
      tags: params.tags,
    })
    materials.value = data.items || data
    materialPagination.value = {
      page: data.page || page,
      page_size: data.page_size || pageSize,
      total: data.total || (data.items ? data.items.length : data.length),
    }
    return data.items || data
  }

  async function loadAttendance(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchAttendance(courseId)
    attendance.value = data
    return data
  }

  async function loadAttendanceDetail(sessionId, courseId = activeCourseId.value) {
    if (!courseId || !sessionId) return null
    const { data } = await fetchAttendanceDetail(courseId, sessionId)
    attendanceDetail.value = data
    return data
  }

  async function loadGrades(courseId = activeCourseId.value) {
    if (!courseId) return []
    const [listRes, statsRes] = await Promise.all([fetchGrades(courseId), fetchGradeStats(courseId)])
    grades.value = listRes.data
    gradeStats.value = statsRes.data
    return listRes.data
  }

  async function loadAssignments(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchAssignments(courseId)
    assignments.value = data
    return data
  }

  async function loadMembers(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchMembers(courseId)
    members.value = data
    return data
  }

  const searchUsers = debounce(async (q) => {
    if (!q) {
      memberSearch.value = { items: [], total: 0 }
      return []
    }
    const { data } = await import('../api/modules/members').then((m) => m.searchUsers({ q, page_size: 10 }))
    memberSearch.value = data
    return data.items
  }, 300)

  async function loadPolls(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchPolls(courseId)
    polls.value = data
    return data
  }

  // 学生端数据加载方法
  async function loadStudentDashboard(courseId = activeCourseId.value) {
    if (!courseId) return {}
    const { data } = await fetchStudentDashboard(courseId)
    studentDashboard.value = data
    return data
  }

  async function loadStudentMaterials(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchStudentMaterials(courseId)
    studentMaterials.value = data
    return data
  }

  async function loadStudentAttendance(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchStudentAttendance(courseId)
    studentAttendance.value = data
    return data
  }

  async function loadStudentGrades(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchStudentGrades(courseId)
    studentGrades.value = data
    return data
  }

  async function loadStudentAssignments(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchStudentAssignments(courseId)
    studentAssignments.value = data
    return data
  }

  async function loadStudentPolls(courseId = activeCourseId.value) {
    if (!courseId) return []
    const { data } = await fetchStudentPolls(courseId)
    studentPolls.value = data
    return data
  }

  // 学生端操作方法
  async function studentCheckIn(sessionId, payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    const { data } = await apiStudentCheckIn(courseId, sessionId, payload)
    // 重新加载考勤数据
    await loadStudentAttendance(courseId)
    return data
  }

  async function studentVote(pollId, option, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    const { data } = await apiStudentVote(courseId, pollId, { option })
    // 重新加载投票数据
    await loadStudentPolls(courseId)
    return data
  }

  function setActiveCourse(id) {
    activeCourseId.value = id
  }

  async function addMaterial(payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await createMaterial(courseId, payload)
    return loadMaterials(courseId)
  }

  async function addAttendance(payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await createAttendance(courseId, payload)
    return loadAttendance(courseId)
  }

  async function addPoll(payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await createPoll(courseId, payload)
    return loadPolls(courseId)
  }

  async function addAssignment(payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await createAssignment(courseId, payload)
    return loadAssignments(courseId)
  }

  async function addGrade(assignmentId, payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await createGrade(courseId, assignmentId, payload)
    return loadGrades(courseId)
  }

  async function importGradeFile(payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await importGrades(courseId, payload)
    return loadGrades(courseId)
  }

  async function addCourseMember(payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await addMember(courseId, payload)
    return loadMembers(courseId)
  }

  async function updateCourseMember(memberId, payload, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await updateMember(courseId, memberId, payload)
    return loadMembers(courseId)
  }

  async function removeCourseMember(memberId, courseId = activeCourseId.value) {
    if (!courseId) throw new Error('未选择课程')
    await deleteMember(courseId, memberId)
    return loadMembers(courseId)
  }

  return {
    courses,
    activeCourseId,
    materials,
    materialPagination,
    attendance,
    attendanceDetail,
    grades,
    gradeStats,
    polls,
    assignments,
    members,
    memberSearch,
    // 学生端数据
    studentDashboard,
    studentMaterials,
    studentAttendance,
    studentGrades,
    studentAssignments,
    studentPolls,
    currentCourse,
    loadCourses,
    loadMaterials,
    loadAttendance,
    loadAttendanceDetail,
    loadGrades,
    loadPolls,
    loadAssignments,
    loadMembers,
    searchUsers,
    loadStudentCourses,
    // 学生端方法
    loadStudentDashboard,
    loadStudentMaterials,
    loadStudentAttendance,
    loadStudentGrades,
    loadStudentAssignments,
    loadStudentPolls,
    studentCheckIn,
    studentVote,
    setActiveCourse,
    addMaterial,
    addAttendance,
    addPoll,
    addAssignment,
    addGrade,
    importGradeFile,
    addCourseMember,
    updateCourseMember,
    removeCourseMember,
  }
})
