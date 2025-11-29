# Docker 一键部署指南

## 前置要求
- 已安装 Docker 与 docker compose（v2+）
- 仓库路径：`/path/to/AiAssist`

## 准备环境变量
- 后端示例：`backend/.env.docker.example`
- 前端示例：`frontend/.env.docker.example`

若需要覆盖默认值，可在仓库根目录创建 `.env`（被 docker compose 读取），示例：
```env
DATABASE_URL=mysql+pymysql://root:pass@db:3306/teacher_assistant
JWT_SECRET_KEY=change-me
CORS_ORIGINS=http://localhost:8080
VITE_API_BASE=http://localhost:5000/api
DB_PORT=3307
BACKEND_PORT=5000
FRONTEND_PORT=8080
```

## 一键启动（本地演示）
```bash
docker compose up -d --build
```
- 后端会在启动时自动执行 `flask db upgrade`
- 首次启动后，可选运行 demo 种子（容器内）：  
  `docker compose run --rm backend python scripts/seed_demo_data.py`

## 访问
- 前端：<http://localhost:8080>
- 后端 API：<http://localhost:5000/api>
- MySQL：宿主机 <http://localhost:3307>（root/pass）

## 常见问题
- **本机 3306 被占用**：已默认将宿主端口映射为 3307；如仍冲突，修改 `.env` 中 `DB_PORT`。
- **容器启动失败**：查看日志  
  - 后端：`docker compose logs -f backend`  
  - 前端：`docker compose logs -f frontend`  
  - 数据库：`docker compose logs -f db`
- **迁移失败**：确认 `DATABASE_URL` 正确；可手动执行  
  `docker compose run --rm backend flask db upgrade`
