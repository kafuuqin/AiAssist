# 后端（Flask）快速说明

## 环境
- Python 3.10+
- 依赖：`pip install -r requirements.txt`
- 环境变量：复制 `.env.example` 为 `.env` 并修改 `DATABASE_URL`/`JWT_SECRET_KEY`。

## 开发运行
```bash
export FLASK_APP=wsgi.py
export FLASK_ENV=development
flask run --port 5000
```

## 数据库
- 首次初始化
```bash
flask db init   # 仅首次
flask db migrate -m "init"
flask db upgrade
```

- 常用模型：`User/Course/Enrollment/Material/AttendanceSession/AttendanceRecord/Assignment/Grade/Poll/PollVote`

## 健康检查
- `GET /health` -> `{"status": "ok"}`
- 认证：`POST /api/auth/register`、`POST /api/auth/login`
- 课程与资源：`/api/courses` 下提供课程/资料/考勤/成绩/投票等基础接口。
  - 课程：`GET/POST /api/courses`
  - 资料：`GET/POST /api/courses/<id>/materials`（分页：`page/page_size`），上传目录 `UPLOAD_DIR`
  - 上传：`POST /api/uploads`（表单 file 字段），访问 `GET /api/uploads/<filename>`
  - 考勤：`GET/POST /api/courses/<id>/attendance`；签到记录 `POST /api/courses/<id>/attendance/<session_id>/record`
  - 成绩：`GET /api/courses/<id>/grades`；统计 `GET /grades/stats`；作业 `GET/POST /assignments`；单条成绩录入 `POST /assignments/<assign_id>/grades`
  - 投票：`GET/POST /api/courses/<id>/polls`；投票 `POST /polls/<poll_id>/vote`
  - 成员：`GET/POST /api/courses/<id>/members`
  - 用户：`GET /api/users`（搜索）

> 当前接口为基础版，文件存储、权限细粒度校验、分页/过滤、异常处理与 AI 相关能力将后续补充。
