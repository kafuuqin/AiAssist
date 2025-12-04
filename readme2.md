1. 项目简介与整体目标
教师智能助手：面向教师（主）与学生（从），支持资料管理、考勤、成绩录入与分析、课堂互动，并提供基础 AI 辅助（资料分类/预测等占位）。
已具备：注册/登录、课程与成员管理、资料上传/搜索/标签、考勤创建与记录、成绩录入/导入/导出/统计、投票互动、文件上传下载鉴权、AI 资料分类（jieba 关键词）、其余 AI mock。
用户流程：注册/登录 → 选择课程 → 管理资料/考勤/成绩/互动 → 可选调用 AI → 查看列表/导出报表。
2. 技术栈与架构概览
前后端分离：Flask 后端 + Vue 3 SPA 前端 + MySQL。
后端：Flask 3、Flask-SQLAlchemy、Flask-JWT-Extended、Flask-Migrate、Flask-Cors、pandas、jieba；CSV 导出；JWT 鉴权；课程成员校验 ensure_course_member。
前端：Vue 3（Composition API）、Vite、Vue Router、Pinia、Element Plus、axios、ECharts。
容器：docker-compose 提供 backend / frontend / db（MySQL 8）。
3. 目录结构说明
backend/app/api/：各蓝图
auth.py 认证；courses.py 课程/资料/考勤/成绩/投票/成员；uploads.py 上传/下载；imports.py 成绩导入；ai.py AI 接口；users.py 用户搜索。
backend/app/models/：user.py 用户；course.py 课程；enrollment.py 课程成员；material.py 资料；attendance.py 考勤/记录；grade.py 作业/成绩；interaction.py 投票/投票记录。
backend/app/utils/：responses.py 统一 ok/error；exporter.py 成绩导出/模板。
backend/requirements.txt：后端依赖。
frontend/src/views/：页面（Login/Register/Dashboard/Materials/Attendance/Grades/Interaction/AI Hub/Members）。
frontend/src/stores/：Pinia stores（auth、course）。
frontend/src/api/：client.js axios 实例；modules/ 分模块封装请求。
frontend/src/layouts/AppLayout.vue：主框架与菜单。
docker-compose.yml：backend/frontend/db 服务。
backend/scripts/seed_demo_data.py：演示数据脚本。
docs/docker-deploy.md、README.md：运行/部署说明。
4. 环境要求与依赖安装
4.1 基础环境
Python 3.10+，Node.js 20+，MySQL 8（默认端口宿主 3307→容器 3306），Docker & docker compose v2+（推荐）。
4.2 后端依赖
可选虚拟环境：python3 -m venv .venv && source .venv/bin/activate。
安装：pip install -r backend/requirements.txt（已含 pandas、jieba 等）。
4.3 前端依赖
cd frontend && npm install。
常用脚本：npm run dev（开发）、npm run build（构建）。
5. 数据库与迁移准备
配置 DATABASE_URL（示例：mysql+pymysql://root:pass@127.0.0.1:3307/teacher_assistant），可放在环境变量或 .env。
迁移：cd backend && FLASK_APP=wsgi.py FLASK_SKIP_DOTENV=1 DATABASE_URL=... python -m flask db upgrade。
演示数据：python backend/scripts/seed_demo_data.py（需已配置 DATABASE_URL）；生成示例用户/课程/资料/考勤/成绩/投票及示例文件。
6. 项目的启动方式
6.1 本地开发启动
后端：
环境变量：FLASK_APP=wsgi.py, FLASK_ENV=development, FLASK_SKIP_DOTENV=1, DATABASE_URL=..., JWT_SECRET_KEY=..., CORS_ORIGINS=http://localhost (line 5173), UPLOAD_DIR=./instance/uploads.
启动：cd backend && python -m flask run --host=0.0.0.0 --port=5000.
前端：
环境变量：VITE_API_BASE=http://localhost:5000/api（写入 frontend/.env）。
启动：cd frontend && npm run dev -- --host --port 5173 --strictPort.
6.2 Docker / docker-compose 一键启动
.env（根目录，可参考 backend/.env.docker.example、frontend/.env.docker.example）示例变量：
DATABASE_URL=mysql+pymysql://root:pass@db:3306/teacher_assistant
JWT_SECRET_KEY=change-me
VITE_API_BASE=http://localhost:5000/api
DB_PORT=3307, BACKEND_PORT=5000, FRONTEND_PORT=8080
启动：docker compose up -d --build（包含 db/backend/frontend；后端入口自动 flask db upgrade）。
访问：前端 http://localhost:8080，后端 API http://localhost:5000/api，MySQL 127.0.0.1 (line 3307)（root/pass 默认）。
手动迁移/种子（如需）：docker compose run --rm backend flask db upgrade；docker compose run --rm backend python scripts/seed_demo_data.py。
7. 已有功能的快速试玩/验证指南
Demo 账号（种子数据生成后）：教师 alice.teacher@example.com / Passw0rd!，学生 charlie.student@example.com 等。
登录前端 → 课程下拉选择示例课程：
资料中心：查看列表/标签，点“AI 自动分类”刷新标签；上传合法文件并创建资料；预览/下载需登录。
考勤：发布签到（教师/owner），查看详情/导出 CSV。
成绩：新建作业、录入成绩、导出 CSV、模板下载、导入 CSV/XLSX（错误会提示行号），查看统计图表，点击“生成预测”（mock）。
互动：创建投票并投票，列表票数更新。
成员：仅 owner/admin 可见并编辑角色。
AI Hub：调用 mock 接口（预测/识别/QA）验证返回结构即可。
上传/下载鉴权：未登录或非课程成员访问 /api/uploads/<file> 应被拒绝。
8. 开发规范与约定
8.1 后端
蓝图划分：auth/courses/uploads/imports/ai/users；新增业务按模块划分蓝图。
模型/字段命名：snake_case；关系在 models 目录。
路由/响应：RESTful 风格，统一返回 utils/responses.ok/error（{"data": ...} 或 {"message": ...}）。导出返回 CSV Response。
权限：JWT via Authorization Bearer；课程内用 ensure_course_member(course_id, as_owner/allow_roles)；admin 全局放行。
8.2 前端
结构：views（页面）、layouts（框架）、stores（Pinia 全局状态）、api/modules（封装 axios 调用）、router（守卫）。
API 调用：使用 api/client.js，支持 JWT 自动注入；上传等场景可显式传 Authorization。
UI：Element Plus 组件（表格/弹窗/表单），ECharts 用于成绩图表。
角色控制：菜单与按钮按 auth.user.role 和课程 owner 判断（学生隐藏管理操作）。
8.3 Git/分支（建议）
分支命名：feature/xxx、fix/xxx、chore/xxx。
提交信息前缀：feat:/fix:/chore:/docs: 等。
9. 测试与质量保障
现状：暂无自动化测试；依赖手工自测路径（见上）。
规划：后端 pytest（auth/permissions/uploads/imports/grades），前端 vitest/组件测试；CI（GitHub Actions）跑 lint/test。
本地至少验证：关键页面操作（资料上传/下载、考勤创建、成绩导入导出、投票、权限限制）和主要 API（auth/courses/uploads/imports/ai）。
10. 后续开发方向与 TODO
高优先：权限细化与邀请流程（authz + 前端守卫）、上传安全深化（病毒/临时链接）、真实 AI（预测/FAQ/识别）、实时考勤/投票（SocketIO、二维码/口令）。
中优先：成绩导入校验学生存在/预览模式、资料全文搜索与预览、导出/统计优化（更多分布指标）。
低优先：自动化测试/CI、日志监控、文档（OpenAPI/Postman）、部署优化（反代、镜像瘦身）。
涉及模块：backend/app/authz.py、api/courses.py、api/imports.py、api/ai.py、uploads.py、frontend 对应 views/stores/api、docker-compose.yml、docs/。