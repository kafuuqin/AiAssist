import api from '../client'

export function classifyMaterial(payload) {
  return api.post('/ai/materials/classify', payload)
}

export function gradePredict(payload) {
  return api.post('/ai/grades/predict', payload)
}

export function recognizeAttendance(payload) {
  return api.post('/ai/attendance/recognize', payload)
}

export function qaAsk(payload) {
  return api.post('/ai/qa/ask', payload)
}
