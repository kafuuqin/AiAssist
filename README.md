# 教师智能助手（前后端分离）

基于 Vue 3（Vite）+ Flask + MySQL 的教师智能助手系统，涵盖资料管理、考勤管理、成绩分析、课堂互动与智能能力（资料自动分类、成绩预测、智能问答、智能点到）。

## 当前状态
- 架构与数据模型草案：`docs/architecture.md`
- 后端：Flask + SQLAlchemy + JWT，课程/资料/考勤/成绩/互动/AI mock API 完成，上传与统一响应、中间件、Dockerfile、docker-compose 基础完成。
- 前端：Vue 3 + Vite + Pinia + Element Plus，认证、课程切换、资料（上传/搜索/分页）、考勤详情、成绩（录入/导入/图表）、互动轮询、AI mock 调用。
- 权限：课程接口增加成员/拥有者校验，支持课程成员列表和添加；课程创建可附带成员；资料列表支持排序。

## 技术栈
- 前端：Vue 3 + Vite + Pinia + Vue Router + Element Plus + ECharts
- 后端：Flask + Flask-SQLAlchemy + Flask-JWT-Extended (+ 预留 SocketIO)
- 数据与智能：MySQL、Pandas/NumPy、scikit-learn、jieba、OpenCV（部分为后续接入，现有 mock）
- 工具与部署：npm、pip、Dockerfile、Docker Compose、Postman/OpenAPI

## 目录规划（预期）
- `frontend/`：Vue 单页应用（将从当前根目录迁移/扩展）
- `backend/`：Flask API、模型、服务、任务
- `docs/`：设计与接口文档

## 开发里程碑
1. 完成架构与模型设计（已完成草案）
2. 搭建后端骨架与认证（已基本完成：课程/资料/考勤/成绩/互动/AI mock/上传/统一响应）
3. 搭建前端骨架（已完成：布局/路由/状态/认证，接入基础 API）
4. 实现资料、考勤、成绩、互动核心流程（进行中：上传/搜索/分页、考勤详情、成绩导入/图表、互动轮询）
5. 接入智能能力与容器化部署（进行中：AI mock、Dockerfile/docker-compose；后续接入真实模型与任务队列）

> 详细设计与接口草案见 `docs/architecture.md`。后续会补充运行与部署说明。

## 本地开发快速启动

### 前置条件
- Python 3.10+
- Node.js 20+（建议用 nvm 管理）
- Docker（用于拉起 MySQL 8）
- 端口可用性：后端 `5000`，前端 `5173`，数据库宿主机映射 `3307`（本机 3306 被占用）

### 数据库（MySQL 8）启动
```bash
# 如已存在容器可跳过
docker run -d --name aiassist-db \
  -p 3307:3306 \
  -e MYSQL_ROOT_PASSWORD=pass \
  -e MYSQL_DATABASE=teacher_assistant \
  mysql:8.0
```
默认连接串：`mysql+pymysql://root:pass@127.0.0.1:3307/teacher_assistant`。

### 后端启动（Flask）
```bash
cd backend
# 可选：创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate   # Windows PowerShell: .venv\Scripts\Activate.ps1
# 安装依赖
pip install -r requirements.txt
# 准备环境变量（复制 .env.example 覆盖需要的值）
cp .env.example .env
# 或直接导出
export FLASK_APP=wsgi.py
export FLASK_ENV=development
export FLASK_SKIP_DOTENV=1
export DATABASE_URL=mysql+pymysql://root:pass@127.0.0.1:3307/teacher_assistant
export JWT_SECRET_KEY=dev-secret
export CORS_ORIGINS=http://localhost:5173
export UPLOAD_DIR=./instance/uploads
export MAX_UPLOAD_MB=20
export ALLOWED_UPLOAD_EXTS=pdf,ppt,pptx,doc,docx,xls,xlsx,png,jpg,jpeg

# 数据库迁移
flask db upgrade
# 启动服务
flask run --host=0.0.0.0 --port=5000
```
日志默认输出到控制台；可用 `FLASK_SKIP_DOTENV=1` 保证环境变量只由外部提供。

### 前端启动（Vite + Vue 3）
```bash
cd frontend
# 配置 API 地址（如有 .env.example 可复制；默认指向本地后端）
echo "VITE_API_BASE=http://localhost:5000/api" > .env
# 安装依赖
npm install
# 启动开发服务
npm run dev -- --host --port 5173 --strictPort
```
访问 `http://localhost:5173/`。

### 基础验证流程
1. 打开 `http://localhost:5173/register` 注册新用户，成功后应自动登录并进入主页。
2. 新建课程（左侧菜单），在资料/考勤/成绩/互动等页面执行创建、列表、投票等操作确认接口可用。
3. 访问 `http://localhost:5000/health` 返回 `{"status":"ok"}` 以检查后端存活。

### 常见问题
- **5000/5173 端口占用**：关闭占用进程或调整启动端口（前端 `--port`，后端 `--port`）。  
- **数据库连接失败**：确认容器已启动且使用宿主 `3307`，`DATABASE_URL` 主机为 `127.0.0.1`。  
- **PIP 提示外部管理环境**：优先使用虚拟环境；或在受控环境下使用 `pip install --user`。  
- **跨域**：确保 `CORS_ORIGINS` 包含前端访问域（默认 `http://localhost:5173`）。

## Docker 一键部署
详见 `docs/docker-deploy.md`，核心步骤：
1. 准备 `.env`（可参考 `backend/.env.docker.example`、`frontend/.env.docker.example`），必要时设置 `DATABASE_URL`、`JWT_SECRET_KEY`、`VITE_API_BASE` 等。
2. 一键启动：`docker compose up -d --build`（包含 db/backend/frontend）。后端启动时自动执行 `flask db upgrade`。
3. 访问：前端 `http://localhost:8080`，后端 API `http://localhost:5000/api`，MySQL `localhost:3307`（root/pass）。
4. 可选：`docker compose run --rm backend python scripts/seed_demo_data.py` 注入演示数据。
