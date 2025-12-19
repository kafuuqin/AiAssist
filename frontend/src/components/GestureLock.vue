<script setup>
import { ref, onMounted, onUnmounted } from 'vue'

const emit = defineEmits(['complete'])

const canvasRef = ref(null)
const points = ref([])
const isDrawing = ref(false)
const selectedPoints = ref([])

const pointPositions = [
  { x: 50, y: 50 }, { x: 150, y: 50 }, { x: 250, y: 50 },
  { x: 50, y: 150 }, { x: 150, y: 150 }, { x: 250, y: 150 },
  { x: 50, y: 250 }, { x: 150, y: 250 }, { x: 250, y: 250 }
]

const initCanvas = () => {
  const canvas = canvasRef.value
  const ctx = canvas.getContext('2d')
  
  // 设置canvas尺寸
  canvas.width = 300
  canvas.height = 300
  
  // 绘制初始点
  drawPoints(ctx)
}

const drawPoints = (ctx) => {
  ctx.clearRect(0, 0, 300, 300)
  
  // 绘制点
  pointPositions.forEach((pos, index) => {
    ctx.beginPath()
    ctx.arc(pos.x, pos.y, 15, 0, Math.PI * 2)
    ctx.fillStyle = selectedPoints.value.includes(index) ? '#6366f1' : '#cbd5e1'
    ctx.fill()
    
    // 绘制数字
    ctx.fillStyle = 'white'
    ctx.font = '12px Arial'
    ctx.textAlign = 'center'
    ctx.textBaseline = 'middle'
    ctx.fillText(index + 1, pos.x, pos.y)
  })
  
  // 绘制连线
  if (selectedPoints.value.length > 1) {
    ctx.strokeStyle = '#6366f1'
    ctx.lineWidth = 3
    ctx.beginPath()
    
    selectedPoints.value.forEach((pointIndex, idx) => {
      const point = pointPositions[pointIndex]
      if (idx === 0) {
        ctx.moveTo(point.x, point.y)
      } else {
        ctx.lineTo(point.x, point.y)
      }
    })
    
    // 绘制到当前鼠标位置
    if (points.value.length > 0 && isDrawing.value) {
      const lastPoint = pointPositions[selectedPoints.value[selectedPoints.value.length - 1]]
      ctx.lineTo(points.value[points.value.length - 1].x, points.value[points.value.length - 1].y)
    }
    
    ctx.stroke()
  }
}

const getPointAtPosition = (x, y) => {
  for (let i = 0; i < pointPositions.length; i++) {
    const point = pointPositions[i]
    const distance = Math.sqrt(Math.pow(x - point.x, 2) + Math.pow(y - point.y, 2))
    if (distance <= 20) {
      return i
    }
  }
  return -1
}

const handleMouseDown = (event) => {
  const rect = canvasRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  const pointIndex = getPointAtPosition(x, y)
  if (pointIndex !== -1) {
    isDrawing.value = true
    selectedPoints.value = [pointIndex]
    points.value = [{ x, y }]
    drawPoints(canvasRef.value.getContext('2d'))
  }
}

const handleMouseMove = (event) => {
  if (!isDrawing.value) return
  
  const rect = canvasRef.value.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  
  points.value.push({ x, y })
  
  const pointIndex = getPointAtPosition(x, y)
  if (pointIndex !== -1 && !selectedPoints.value.includes(pointIndex)) {
    selectedPoints.value.push(pointIndex)
  }
  
  drawPoints(canvasRef.value.getContext('2d'))
}

const handleMouseUp = () => {
  if (!isDrawing.value) return
  
  isDrawing.value = false
  
  // 验证手势
  if (selectedPoints.value.length >= 4) {
    const pattern = selectedPoints.value.map(idx => idx + 1).join('')
    emit('complete', pattern)
  } else {
    // 重置
    selectedPoints.value = []
    points.value = []
    drawPoints(canvasRef.value.getContext('2d'))
  }
}

const handleTouchStart = (event) => {
  event.preventDefault()
  const touch = event.touches[0]
  handleMouseDown({
    clientX: touch.clientX,
    clientY: touch.clientY
  })
}

const handleTouchMove = (event) => {
  event.preventDefault()
  const touch = event.touches[0]
  handleMouseMove({
    clientX: touch.clientX,
    clientY: touch.clientY
  })
}

const handleTouchEnd = (event) => {
  event.preventDefault()
  handleMouseUp()
}

onMounted(() => {
  initCanvas()
  
  // 添加事件监听器
  const canvas = canvasRef.value
  canvas.addEventListener('mousedown', handleMouseDown)
  canvas.addEventListener('mousemove', handleMouseMove)
  canvas.addEventListener('mouseup', handleMouseUp)
  canvas.addEventListener('touchstart', handleTouchStart)
  canvas.addEventListener('touchmove', handleTouchMove)
  canvas.addEventListener('touchend', handleTouchEnd)
})

onUnmounted(() => {
  // 移除事件监听器
  const canvas = canvasRef.value
  if (canvas) {
    canvas.removeEventListener('mousedown', handleMouseDown)
    canvas.removeEventListener('mousemove', handleMouseMove)
    canvas.removeEventListener('mouseup', handleMouseUp)
    canvas.removeEventListener('touchstart', handleTouchStart)
    canvas.removeEventListener('touchmove', handleTouchMove)
    canvas.removeEventListener('touchend', handleTouchEnd)
  }
})
</script>

<template>
  <div class="gesture-lock">
    <canvas 
      ref="canvasRef" 
      class="gesture-canvas"
      @mousedown="handleMouseDown"
      @mousemove="handleMouseMove"
      @mouseup="handleMouseUp"
      @touchstart="handleTouchStart"
      @touchmove="handleTouchMove"
      @touchend="handleTouchEnd"
    ></canvas>
  </div>
</template>

<style scoped>
.gesture-lock {
  display: flex;
  justify-content: center;
}

.gesture-canvas {
  border: 2px solid #e2e8f0;
  border-radius: 12px;
  background: white;
  cursor: pointer;
  touch-action: none;
}

.gesture-canvas:active {
  border-color: #6366f1;
}
</style>