# 教师智能助手（前后端分离）

基于 Vue 3（Vite）+ Flask + MySQL 的教师智能助手系统，涵盖资料管理、考勤管理、成绩分析、课堂互动与智能能力（资料自动分类、成绩预测、智能问答、智能点到）。

## 当前状态
- 架构与数据模型草案：`docs/architecture.md`
- 前端：现有 Vite + Vue 3 模板，后续将扩展为完整管理端。
- 后端：待搭建 Flask/REST API 服务。

## 技术栈
- 前端：Vue 3 + Vite + Pinia + Vue Router + Element Plus
- 后端：Flask + Flask-SQLAlchemy + Flask-JWT-Extended + Flask-SocketIO
- 数据与智能：MySQL、Pandas/NumPy、scikit-learn、jieba、OpenCV
- 工具与部署：npm、pip、Docker Compose、Postman/OpenAPI

## 目录规划（预期）
- `frontend/`：Vue 单页应用（将从当前根目录迁移/扩展）
- `backend/`：Flask API、模型、服务、任务
- `docs/`：设计与接口文档

## 开发里程碑
1. 完成架构与模型设计（已完成草案）
2. 搭建后端骨架与认证（进行中：课程/资料/考勤/成绩/互动 API 基础完成）
3. 搭建前端骨架（布局/路由/状态）并接入基础 API（进行中）
4. 实现资料、考勤、成绩、互动核心流程（进行中）
5. 接入智能能力与容器化部署（待开始）

> 详细设计与接口草案见 `docs/architecture.md`。后续会补充运行与部署说明。
