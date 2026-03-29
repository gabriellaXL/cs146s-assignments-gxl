# 版本 3：Django 笔记管理器

本项目是第 8 周多栈作业的 Django 实现版本。它提供了一个稳定的服务端渲染笔记管理器，具备完整的 CRUD 功能、SQLite 持久化存储、输入校验，以及基础的自动化测试。

## 技术栈

- Python 3.10+
- Django
- SQLite

## 功能特性

- 创建、列表、查看、更新和删除笔记
- 基于 SQLite 的持久化存储
- 使用 Django 模板进行服务端渲染的 HTML 页面
- 表单校验及面向用户的错误提示
- 时间戳与笔记状态追踪
- 针对核心流程的基础 Django 测试覆盖

## 项目结构

```text
week8/version3-django/
├── config/                 Django 项目配置及根路由
├── notes/                  笔记应用（含模型、表单、视图和测试）
├── templates/              共用模板及应用模板
├── manage.py
└── README.md
```

## 环境配置

1. 在仓库根目录安装依赖：

```powershell
poetry install
```

2. 进入 Django 项目目录：

```powershell
cd week8/version3-django
```

3. 应用数据库迁移：

```powershell
poetry run python manage.py migrate
```

4. 启动开发服务器：

```powershell
poetry run python manage.py runserver
```

5. 打开浏览器访问 `http://127.0.0.1:8000/notes/`

## 测试

运行 Django 测试套件：

```powershell
cd week8/version3-django
poetry run python manage.py test
```

## 持久化存储

本项目使用 SQLite。开发数据库文件存储在：

`week8/version3-django/db.sqlite3`

## 补充说明

- 本版本有意使用 Django 模板而非独立的前端框架，以保持应用侧完全无 JavaScript 的技术栈。
- 应用聚焦于核心的 `Note` 资源，以保持与第 8 周其他两个实现版本在范围上的对齐。
