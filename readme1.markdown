一、当前阶段已完成的功能（开发成果总结）
认证与用户/课程管理
✅ 注册/登录/刷新/当前用户；课程列表/创建；课程成员增删改查，角色支持 owner/teacher/assistant/student，admin 放行。
🧩 后端：backend/app/api/auth.py、backend/app/api/courses.py（courses/members）、backend/app/authz.py（角色与成员校验）、backend/app/models/user.py、backend/app/models/course.py、backend/app/models/enrollment.py。
🎨 前端：frontend/src/stores/auth.js、frontend/src/router/index.js（守卫）、frontend/src/views/auth/LoginView.vue、RegisterView.vue、frontend/src/views/members/MembersView.vue。
⚠️ 限制：系统级角色仅 basic/teacher/student/admin，课程内权限简单；成员邀请/加入流程未做。
资料中心（Materials）
✅ 列表/搜索/分页/标签过滤；上传后创建资料；预览/下载带 JWT 与课程成员鉴权；AI 自动分类（jieba TF-IDF 关键词写回 tags）。
🧩 后端：backend/app/api/courses.py（materials）、backend/app/api/uploads.py（上传/下载校验）、backend/app/api/ai.py（materials/classify）、backend/app/models/material.py。
🎨 前端：frontend/src/views/materials/MaterialsView.vue、frontend/src/api/modules/uploads.js、frontend/src/api/modules/ai.js、frontend/src/stores/course.js。
⚠️ 限制：仅关键词提取，无全文内容提取；下载鉴权基于 Material 关联；预览为直接打开链接。
考勤（Attendance）
✅ 创建考勤（owner/teacher/admin）、列表、详情、添加记录；导出当前场次 CSV；权限基于课程成员。
🧩 后端：backend/app/api/courses.py（attendance）、backend/app/models/attendance.py。
🎨 前端：frontend/src/views/attendance/AttendanceView.vue、frontend/src/stores/course.js。
⚠️ 限制：无实时/二维码/口令校验逻辑（占位），导出为前端生成 CSV。
成绩管理与统计（Grades）
✅ 作业创建；成绩录入；导出 CSV（含说明行）；模板下载（带示例与说明）；统计用 pandas 计算均值/方差/分布；成绩导入 CSV/XLSX，pandas 严格校验（必填列、范围、重复），事务性 upsert；AI 预测按钮调用 mock。
🧩 后端：backend/app/api/courses.py（grades/assignments/template/export/stats）、backend/app/api/imports.py（导入校验）、backend/app/utils/exporter.py、backend/app/models/grade.py。
🎨 前端：frontend/src/views/grades/GradesView.vue、frontend/src/api/modules/courses.js、frontend/src/api/modules/uploads.js、frontend/src/api/modules/ai.js、frontend/src/stores/course.js。
⚠️ 限制：预测为 mock；导入未校验学生存在；模板说明简单；前端导出/导入 UI 简单。
课堂互动（投票）
✅ 投票创建、列表、投票，票数汇总展示。
🧩 后端：backend/app/api/courses.py（polls）、backend/app/models/interaction.py。
🎨 前端：frontend/src/views/interaction/InteractionView.vue、frontend/src/stores/course.js、frontend/src/api/modules/courses.js。
⚠️ 限制：无实时 Socket 推送，前端轮询。
上传/下载
✅ 上传 JWT 校验、扩展名/MIME/大小校验、危险扩展黑名单；下载需 JWT 且课程成员才能访问对应资料文件。
🧩 后端：backend/app/api/uploads.py、backend/app/config.py。
🎨 前端：frontend/src/api/modules/uploads.js（显式加 Authorization）、frontend/src/views/materials/MaterialsView.vue（blob 下载与错误提示）。
⚠️ 限制：未做病毒扫描/内容安全；下载基于 Material 关联判定。
AI 功能
✅ 资料自动分类（jieba 关键词）；成绩预测 mock；考勤识别/QA mock。
🧩 后端：backend/app/api/ai.py。
🎨 前端：frontend/src/views/materials/MaterialsView.vue、frontend/src/views/grades/GradesView.vue、frontend/src/views/ai/IntelligenceHub.vue。
⚠️ 限制：预测/识别/QA 为占位；未做异步/模型持久化。
权限、角色体系
✅ 支持全局 admin/teacher/student；课程内 role_in_course（owner/teacher/assistant/student），写操作接口限制 owner/teacher/ta/admin；成员管理仅 owner/admin。
🧩 后端：backend/app/authz.py、backend/app/api/courses.py（allow_roles/as_owner）、backend/app/models/enrollment.py。
🎨 前端：frontend/src/router/index.js（学生拒绝访问成员管理）、frontend/src/layouts/AppLayout.vue（菜单显示）、各视图按钮按角色/owner 控制。
⚠️ 限制：更细粒度的操作权限未全覆盖；邀请/审批流程缺失。
二、当前功能的测试方法（如何手工验证）
前置准备
环境：后端运行（DATABASE_URL 配 MySQL，执行 flask db upgrade），前端运行；可选执行种子脚本 python backend/scripts/seed_demo_data.py 生成 demo 数据。
登录账号：教师/owner 或 admin 以便执行管理操作；学生账号验证权限受限。
认证与用户/课程管理
前端：/register 注册（预期自动登录跳转 Dashboard）；/login 登录；左上课程下拉可切换已有课程；成员管理菜单仅 owner/admin 可见。
API：POST /api/auth/register|login，GET /api/courses（需 Bearer），GET/POST/PATCH/DELETE /api/courses/{id}/members（非 owner/admin 403）。
预期：登录成功返回 token；非成员访问课程资源 403。
资料中心
前置：已选课程、具备资料或上传一个文件后创建资料。
前端：进入“资料中心”，搜索框输入关键词回车，列表过滤；点击标签 segmented 过滤；点击“上传资料”选择合法文件，提交后出现新资料；点击“AI 自动分类”处理当前课程资料并刷新标签；预览/下载正常，非成员或未登录下载失败提示。
API：POST /api/uploads（需 Authorization，返回 url）；POST /api/courses/{cid}/materials 创建；GET /api/ai/materials/classify with material_id/course_id 返回 tags 并写回 DB。
考勤
前置：课程 owner/teacher/admin。
前端：进入“课堂考勤”，点击“发布签到”创建；列表点击“查看详情”显示记录；“导出”下载 CSV；学生账号应无法看到创建按钮。
API：POST /api/courses/{cid}/attendance 创建（非 owner/teacher/ta/admin 403）；GET /api/courses/{cid}/attendance/{sid} 详情。
成绩管理与统计
前置：课程 owner/teacher/admin；存在作业或先“新建作业”。
前端：进入“成绩分析”，查看列表与统计卡片/图表；“导出”下载含说明的 CSV；“模板下载”获取带示例的模板；“录入成绩”选择作业+学生提交成功；“导入成绩”上传 CSV/XLSX，成功提示并刷新，错误文件应提示包含行号的错误信息；“生成预测”提示 mock 结果。
API：GET /api/courses/{cid}/grades(export=csv)、GET /api/courses/{cid}/grades/template、POST /api/courses/{cid}/grades/import (需 assignment_id, file_path, Bearer)，错误返回 {message, errors:[{line, message}]}；GET /api/courses/{cid}/grades/stats 返回 avg/max/min/std/distribution。
课堂互动
前端：进入“课堂互动”，创建投票（至少两选项），提交后列表显示；点投票按钮，票数更新（轮询）。
API：POST /api/courses/{cid}/polls 创建；POST /api/courses/{cid}/polls/{pid}/vote 投票。
上传/下载
前端：资料中心上传合法类型/大小文件成功；上传危险扩展（exe/js 等）提示失败；下载需已登录课程成员。
API：POST /api/uploads（multipart, Bearer）；GET /api/uploads/{filename} 需成员，否则 401/403/404。
AI 模块
资料分类：POST /api/ai/materials/classify（material_id/course_id 或 title/description+course_id）返回 tags 并写回；验证 DB Material.tags 更新。
其他 AI：/ai/grades/predict、/ai/attendance/recognize、/ai/qa/ask 为 mock，只需验证接口可用和返回结构。
权限/角色
使用学生账号：菜单无成员管理；创建资料/考勤/作业/投票应被前端隐藏或后端返回 403；下载非所属课程文件 403。
使用 admin：应可访问所有课程资源并执行写操作。
三、待开发/未完成的功能与技术债
功能层面 TODO
权限细化：更精细的操作级权限、成员邀请/加入流程；前后端同步更新。涉及 backend/app/authz.py、相关 api 路由、前端守卫和 UI。
上传/下载安全深化：病毒/内容安全扫描，临时授权链接，文件访问审计。涉及 backend/app/api/uploads.py、config.py。
成绩导入增强：校验学生存在、批量错误汇总下载、支持回滚/预览模式。涉及 backend/app/api/imports.py、models/grade.py。
AI 实际模型：真实成绩预测、FAQ 检索、考勤识别，异步任务/模型持久化。涉及 backend/app/api/ai.py、潜在任务队列。
实时功能：考勤二维码/口令校验、SocketIO 推送考勤/投票更新，前端订阅。涉及 backend/app/models/attendance.py、interaction.py、前端 Interaction/Attendance。
资料预览与搜索：全文索引、PDF/图片预览、标签管理 UI。涉及 Material 模块及前端 Materials。
工程层面 TODO
自动化测试：后端 pytest 覆盖 auth/permissions/uploads/imports，前端 vitest/组件测试。backend/tests/、frontend/tests/。
CI/CD：GitHub Actions 运行 lint/test、可选构建镜像。.github/workflows/.
日志/监控：统一日志格式、错误追踪、健康指标。backend/app 初始化与配置。
部署优化：Docker 镜像体积优化、生产反向代理、环境模板完善。Dockerfile、docker-compose.yml、docs/docker-deploy.md。
文档补完：API 文档（OpenAPI/Postman）、运行手册、开发约定。docs/、README.md.
依赖关系提示：实时功能依赖 SocketIO 集成；AI 真实模型依赖数据清洗与存储；权限细化需前后端联动；测试/CI 依赖用例落地。