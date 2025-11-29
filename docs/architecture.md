# 教师智能助手系统架构草案

## 目标
- 面向教师的资料管理、考勤、成绩分析、课堂互动的一站式平台，前后端分离。
- 前端：Vue 3 + Vite + Pinia + Vue Router + Element Plus，提供桌面与移动端友好的管理界面。
- 后端：Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-SocketIO，MySQL 持久化。
- AI 与数据分析：Pandas/NumPy 统计，scikit-learn 预测，jieba/TF-IDF 资料分类，OpenCV 图像识别。
- 部署：Docker Compose 统一编排（web、api、db、worker），Postman/OpenAPI 规范接口。

## 系统架构
- `frontend/`：Vite + Vue 3 单页应用，使用 REST + WebSocket 调用。
- `backend/`：Flask API 服务（可能拆分定时/模型任务为 Celery/RQ worker），提供 REST、SocketIO。
- `mysql`：主数据源；可预留 Redis（会话/缓存/队列）。
- 对象存储：本地磁盘占位，预留兼容 S3 的抽象。
- 日志/监控：标准 JSON 日志，接口耗时、任务耗时埋点（后续接入 Prometheus/Grafana）。

## 角色与权限
- 角色：管理员（系统配置、课程管理）、教师（课程/资料/考勤/成绩管理）、学生（查看个人信息、签到、课堂互动）。
- 权限模型：基于角色的路由与接口守卫，JWT 认证，细粒度到课程维度的授权校验（课程成员才能访问相关资源）。

## 数据模型（草案）
- 用户/身份
  - `User(id, name, email, password_hash, role, avatar_url, created_at, updated_at)`
  - `Course(id, name, code, term, description, owner_id)`
  - `Enrollment(id, course_id, user_id, role_in_course[teacher|student], status)`
- 资料中心
  - `Material(id, course_id, title, description, path, file_type, size, tags, uploader_id, created_at)`
  - `MaterialTag(id, course_id, name)`；`material_tag_map(material_id, tag_id)`
  - `MaterialAnalysis(id, material_id, keywords, category, model_version, status, created_at)`
- 考勤
  - `AttendanceSession(id, course_id, title, mode[qrcode|manual|photo], start_at, end_at, status)`
  - `AttendanceRecord(id, session_id, student_id, status[present|late|absent], evidence, recognized_face_id, created_at)`
- 成绩
  - `Assignment(id, course_id, title, type, weight, full_score, due_at)`
  - `Grade(id, assignment_id, student_id, score, comment, graded_at)`
  - `GradeImportJob(id, course_id, template_path, status, total, success, fail, fail_reason)`
- 课堂互动
  - `Poll(id, course_id, question, options(json), is_active, created_at)`
  - `PollVote(id, poll_id, user_id, option_index, created_at)`
  - `QaThread(id, course_id, title, content, author_id, status, created_at)`
  - `QaMessage(id, thread_id, author_id, content, created_at)`
- AI/预测
  - `PerformanceForecast(id, course_id, model, version, trained_at, metrics, created_by)`
  - `ForecastResult(id, forecast_id, student_id, predicted_score, risk_level)`

## API 模块（REST 草案）
- 认证：`POST /api/auth/login`, `POST /api/auth/register`, `POST /api/auth/refresh`.
- 用户/课程：用户信息，课程 CRUD，选课/退课，课程成员列表。
- 资料中心：上传/下载/预览（预留 PDF/图片在线预览），课程标签管理，搜索（标题/标签/关键词）。
- 考勤：创建考勤任务，生成二维码 token，学生签到（二维码/手动/拍照），教师查看结果与导出。
- 成绩：录入（单条/Excel 导入），统计指标（均值/最高/最低/标准差），成绩分布/趋势接口。
- 课堂互动：实时投票、提问、弹幕（SocketIO 频道 per course），历史记录查询。
- 智能：
  - 资料分类：上传触发异步关键词提取/分类，返回建议标签。
  - 成绩预测：基于历史成绩训练线性回归/随机森林，返回高风险学生列表。
  - 智能问答：基于课程资料索引的 FAQ 检索（初期基于 TF-IDF/关键词召回）。
  - 智能点到：上传课堂照片 -> OpenCV 人脸检测/比对 -> 返回识别结果与置信度（先提供 mock 管道和接口）。

## 前端信息架构
- 布局：登录/注册独立页；主框架含侧边导航（课程、资料、考勤、成绩、互动、智能分析）、顶部状态栏（课程切换、用户菜单、通知）。
- 路由分组：`/auth`, `/dashboard`, `/courses/:id/materials`, `/courses/:id/attendance`, `/courses/:id/grades`, `/courses/:id/interaction`, `/ai`.
- 状态：Pinia store 拆分 `auth`, `course`, `materials`, `attendance`, `grades`, `interaction`, `ai`.
- 组件：通用表格、上传组件、图表区（ECharts 或 Element Plus/Chart.js 兼容）、二维码展示、文件预览抽屉。
- API 客户端：Axios 封装，拦截器处理 JWT、401 重定向、错误提示；WebSocket 客户端封装课堂互动与实时考勤。

## 开发与部署
- 代码结构（预期）
  - `frontend/`：现有 Vue 项目迁移并扩展。
  - `backend/`：Flask 应用，`app/` 包含 `api`, `models`, `services`, `tasks`, `auth`.
  - `docker-compose.yml`：`frontend`, `backend`, `db`, `redis`（可选）服务。
- 配置管理：`.env` + `.env.example`，区分 dev/prod。
- 测试：后端 pytest + coverage；前端 vitest 基础；API 用 Postman/OpenAPI 导出。

## 里程碑（与执行计划对应）
1) 完成架构文档、数据模型与接口草案（当前）。
2) 搭建后端骨架：配置、数据库模型、认证与基础 CRUD。
3) 搭建前端骨架：布局、路由、Pinia、UI 主题、API 基础。
4) 完成资料/考勤/成绩/互动核心流程。
5) 接入智能能力与容器化部署。

