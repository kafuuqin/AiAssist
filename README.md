# 教师智能助手

基于前后端分离的"教师智能助手"应用系统，使用 Flask + Vue.js 构建。

## 功能特性

### 基础模块
1. 用户认证与权限管理：多角色登录、注册、权限控制
2. 资料中心：支持文件上传/下载、在线预览、按课程/标签分类、全文搜索
3. 课堂考勤：教师创建考勤任务，学生扫码或手动确认
4. 成绩管理：
   - 成绩录入：单条录入、Excel模板批量导入
   - 统计分析：自动计算平均分、最高/最低分、标准差，生成可视化图表
5. 课堂互动：实现实时投票、提问、弹幕等功能

### 智能模块
1. 自动化资料归类：结合NLP技术，对上传的文档资料进行关键词提取或文本分类
2. 学情预警与预测：基于历史成绩数据，使用线性回归等机器学习模型预测成绩趋势
3. 智能问答助手：基于课程资料库构建问答机器人
4. 智能点到：支持教师上传课堂照片，通过人脸识别自动生成考勤结果
5. 智能座位表：根据教室布局照片及点到结果生成可视化座位表

## 技术栈

### 后端
- Flask (Python Web框架)
- Flask-SQLAlchemy (ORM)
- Flask-JWT-Extended (JWT认证)
- MySQL (数据库)
- NumPy, Pandas (数据分析)
- Scikit-learn (机器学习)
- OpenCV (图像处理)

### 前端
- Vue 3 + Composition API
- Pinia (状态管理)
- Vue Router (路由)
- Element Plus (UI组件库)

## 安装与运行

1. 克隆项目
```bash
git clone <项目地址>
```

2. 创建虚拟环境并激活
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置数据库
在 `config.py` 中修改数据库连接信息

5. 初始化数据库
```bash
python init_db.py
```

6. 运行后端服务
```bash
python app.py
```

## API 文档

API 文档使用 Swagger 生成，启动服务后访问 `/docs` 查看详细接口说明。

## 开发计划

- [x] 项目结构搭建
- [x] 数据库模型设计
- [x] 用户认证系统
- [x] 资料管理模块
- [x] 考勤管理模块
- [x] 成绩管理模块
- [x] 智能功能模块
- [ ] 前端界面开发
- [ ] 系统测试与优化
- [ ] 部署上线