# 教师智能助手（前后端分离）

基于 Vue 3（Vite）+ Flask + MySQL 的教学辅助系统，覆盖课程/成员、资料管理、考勤、成绩、课堂互动与基础 AI 能力（关键词抽取、mock 预测/问答/点名等）。

## 仓库结构
- `backend/`：Flask API（SQLAlchemy 模型、迁移、JWT 鉴权、统一响应、上传、演示脚本）
- `frontend/`：Vue 3 + Vite SPA（Pinia、Element Plus、ECharts）
- `docs/`：设计与接口草案（`architecture.md`）、容器化说明（`docker-deploy.md`）
- `docker-compose.yml`：frontend + backend + db 一键编排
- `instance/`：本地上传目录（应用启动时自动创建；容器中挂载卷）

## 运行方案概览
- 方案 A：本地开发运行（CMD，未依赖 Docker）
- 方案 B：Docker 一键部署

---

## 方案 A：本地开发运行（CMD）

### 前置要求
- Python 3.10+
- Node.js 20+
- MySQL 8 已安装并启动（示例账号 `root/pass`，库名 `teacher_assistant`）
- 端口：后端 5000、前端 5173

### 步骤 1：准备代码与依赖
```cmd
:: 可选：创建虚拟环境（建议在仓库根目录）
python -m venv .venv
.venv\Scripts\activate

:: 安装后端依赖
pip install -r backend\requirements.txt

:: 安装前端依赖
cd frontend
npm install
cd ..
```

### 步骤 2：准备数据库
```cmd
:: 创建数据库（需要有权限的账号）
mysql -uroot -p -e "CREATE DATABASE IF NOT EXISTS teacher_assistant DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 步骤 3：配置后端环境
```cmd
:: 复制示例环境文件
copy backend\.env.example backend\.env

:: 必要变量（如修改端口/密码请同步调整）
set FLASK_APP=wsgi.py
set FLASK_ENV=development
set FLASK_SKIP_DOTENV=1
set DATABASE_URL=mysql+pymysql://root:pass@127.0.0.1:3306/teacher_assistant
set JWT_SECRET_KEY=dev-secret
set CORS_ORIGINS=http://localhost:5173
set UPLOAD_DIR=.\instance\uploads
```

### 步骤 4：迁移并启动后端
```cmd
cd backend
python -m flask --app wsgi db upgrade
python -m flask --app wsgi run --host=0.0.0.0 --port=5000
```
健康检查：`http://localhost:5000/health`。

### 步骤 5：配置并启动前端
```cmd
cd frontend
echo VITE_API_BASE=http://localhost:5000/api > .env
npm run dev -- --host --port 5173 --strictPort
```
访问：`http://localhost:5173/`。

### 步骤 6：可选 - 导入演示数据
```cmd
set FLASK_SKIP_DOTENV=1
set DATABASE_URL=mysql+pymysql://root:pass@127.0.0.1:3306/teacher_assistant
python backend\scripts\seed_demo_data.py
```
示例账号：`alice.teacher@example.com / Passw0rd!`。

### 本地验证清单
- 注册/登录、创建课程、上传资料、发起考勤与投票
- `GET http://localhost:5000/health` 返回 `{"status":"ok"}`
- 资料上传下载、考勤记录、成绩导入导出、课程成员权限均可正常操作

---

## 方案 B：Docker 一键部署

### 前置要求
- Docker 与 docker compose v2+
- 端口：DB 3307（宿主映射）、后端 5000、前端 8080

### 步骤 1：根目录 `.env`
```env
MYSQL_ROOT_PASSWORD=pass
MYSQL_DATABASE=teacher_assistant
DB_PORT=3307

DATABASE_URL=mysql+pymysql://root:${MYSQL_ROOT_PASSWORD}@db:3306/${MYSQL_DATABASE}
JWT_SECRET_KEY=change-me
CORS_ORIGINS=http://localhost:8080,http://localhost:5173
MAX_UPLOAD_MB=20
ALLOWED_UPLOAD_EXTS=pdf,ppt,pptx,doc,docx,xls,xlsx,csv,png,jpg,jpeg
BACKEND_PORT=5000

VITE_API_BASE=http://localhost:5000/api
FRONTEND_PORT=8080
```

### 步骤 2：一键启动
```cmd
docker compose up -d --build
```
- MySQL 映射宿主 `3307`，数据卷：`db_data`
- 后端启动时自动执行 `flask db upgrade`
- 上传目录卷：`backend_uploads`

查看状态/日志：
```cmd
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### 步骤 3：可选 - 导入演示数据
```cmd
docker compose run --rm backend python scripts/seed_demo_data.py
```

### 步骤 4：访问
- 前端：`http://localhost:8080`
- 后端：`http://localhost:5000/api`
- 健康检查：`http://localhost:5000/health`
- MySQL：宿主 `localhost:3307`（root/pass）

### 维护
```cmd
docker compose restart backend frontend
docker compose down
docker compose down -v   :: 删除数据卷（会清空数据库与上传文件）
```

---

## 其他资料
- 设计与模块草案：`docs/architecture.md`
- Docker 说明：`docs/docker-deploy.md`
- 后端接口与模型概览：`backend/README.md`
