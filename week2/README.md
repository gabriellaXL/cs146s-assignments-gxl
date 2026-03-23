# Week 2：行动项提取器（Action Item Extractor）

这是一个基于 **FastAPI + SQLite** 的后端应用，目标是将自由格式会议纪要/笔记中的待办事项（Action Items）自动提取出来。

当前项目支持两种提取模式：

- **规则启发式提取**：`POST /action-items/extract`
- **LLM 提取（Ollama）**：`POST /action-items/extract-llm`

项目还提供了一个简洁前端页面（`week2/frontend/index.html`），可直接在浏览器里输入文本、触发提取、勾选完成状态、查看已保存笔记。

---

## 1. 功能概览

### 核心能力

- 输入任意文本笔记，抽取待办项
- 可选将原始文本保存为 note（`save_note: true`）
- 抽取后将 action items 持久化到 SQLite
- 支持勾选/取消完成状态
- 支持列出所有 notes 和 action items

### 两种提取策略

- **Heuristic（规则）**：速度快、无模型依赖，适合结构化较明显文本（如 bullet、TODO 前缀）
- **LLM（Ollama）**：对自然语言场景更友好，可识别隐式任务语义；当模型不可用时会回退到 heuristic

---

## 2. 项目结构

```text
week2/
  app/
    main.py                  # FastAPI 入口、生命周期、全局异常处理、路由挂载
    config.py                # 应用配置（标题、前端目录等）
    schemas.py               # Pydantic 请求/响应模型（API 合同）
    db.py                    # SQLite 连接、建表、CRUD、数据库异常封装
    routers/
      notes.py               # /notes 相关端点
      action_items.py        # /action-items 相关端点（含 LLM 提取端点）
    services/
      extract.py             # 规则提取 + LLM 提取逻辑
  frontend/
    index.html               # 前端页面（Extract / Extract LLM / List Notes）
  tests/
    test_extract.py          # 提取逻辑单元测试（含 mock LLM）
```

---

## 3. 环境准备

以下命令默认在仓库根目录执行（即 `modern-software-dev-assignments-master/`）。

### 3.1 安装依赖

```bash
poetry install
```

### 3.2 （可选）激活课程 conda 环境

如果你按课程要求使用 conda：

```bash
conda activate cs146s
```

### 3.3 （仅 LLM 提取需要）准备 Ollama 模型

先安装 Ollama，再拉起模型（示例）：

```bash
ollama run llama3.1:8b
```

> 若不使用 LLM 提取，仅使用 `/action-items/extract`，则不强依赖 Ollama。

---

## 4. 启动项目

```bash
poetry run uvicorn week2.app.main:app --reload
```

启动后访问：

- 前端页面：<http://127.0.0.1:8000/>
- OpenAPI 文档（Swagger）：<http://127.0.0.1:8000/docs>

---

## 5. API 说明

所有接口返回 JSON。

## 5.1 Notes 接口

### `POST /notes`

创建一条 note。

请求体：

```json
{
  "content": "Prepare sprint demo agenda"
}
```

响应示例：

```json
{
  "id": 1,
  "content": "Prepare sprint demo agenda",
  "created_at": "2026-03-21 12:34:56"
}
```

### `GET /notes`

按时间倒序（id 倒序）返回所有 notes。

### `GET /notes/{note_id}`

按 ID 获取单条 note；不存在时返回 404。

---

## 5.2 Action Items 接口

### `POST /action-items/extract`

使用启发式规则提取 action items。

请求体：

```json
{
  "text": "TODO: update README\n- [ ] write tests",
  "save_note": true
}
```

响应示例：

```json
{
  "note_id": 7,
  "items": [
    { "id": 31, "text": "update README" },
    { "id": 32, "text": "write tests" }
  ]
}
```

### `POST /action-items/extract-llm`

使用 LLM（Ollama）提取 action items。请求体与响应结构和 `/action-items/extract` 相同。

> 当前服务实现中，若 LLM 调用失败，会自动回退到 heuristic 提取，保证接口可用性。

### `GET /action-items`

返回 action items 列表，支持可选过滤参数：

- `note_id`：只查看某条 note 对应的 action items

### `POST /action-items/{action_item_id}/done`

更新某条 action item 的完成状态。

请求体：

```json
{
  "done": true
}
```

若 `action_item_id` 不存在，返回 404。

---

## 6. 前端页面使用说明

打开首页后可见：

- `Extract`：调用 `/action-items/extract`
- `Extract LLM`：调用 `/action-items/extract-llm`
- `List Notes`：调用 `/notes` 显示历史笔记
- Action Items 区域：显示提取结果，并可勾选状态（会触发 `/action-items/{id}/done`）

---

## 7. 测试

运行 Week 2 全部测试：

```bash
pytest week2/tests
```

仅运行提取逻辑测试：

```bash
pytest week2/tests/test_extract.py
```

当前测试重点覆盖：

- heuristic 的基础提取行为
- LLM 提取的空输入、列表输入、关键词前缀输入
- LLM 异常时回退到 heuristic 的行为

---

## 8. 数据与持久化

- 数据库文件：`week2/data/app.db`
- 应用启动时会自动建表（`notes`、`action_items`）
- `action_items.note_id` 外键指向 `notes.id`

---

## 9. 常见问题（FAQ）

### Q1：`/action-items/extract-llm` 报错或效果不稳定？

- 确认本地 Ollama 正在运行
- 确认模型已拉取（如 `llama3.1:8b`）
- 可先使用 `/action-items/extract` 验证基础流程

### Q2：为什么接口能返回但没看到数据？

- 确认请求体字段是否符合 schema（如 `text`、`content` 不可为空）
- 检查数据库文件是否在 `week2/data/app.db`
- 用 `GET /notes`、`GET /action-items` 验证持久化结果

### Q3：如何查看完整接口定义？

访问 Swagger 文档：<http://127.0.0.1:8000/docs>
