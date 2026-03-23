# 第 4 周 — 现实中的自主编码智能体（IRL）

> ***建议在开始之前先通读整份文档。***

本周你的任务是：在本仓库的上下文中，使用下列 **Claude Code** 功能的任意组合，构建至少 **2 个自动化**：

- 自定义斜杠命令（提交到 `.claude/commands/*.md`）
- 用于仓库或上下文指导的 `CLAUDE.md` 文件
- Claude SubAgents（分工协作的角色专用智能体）
- 集成到 Claude Code 的 MCP 服务器

你的自动化应当能实质性地改进开发者工作流——例如简化测试、文档、重构或数据相关任务。然后，你将使用你创建的自动化来扩展位于 `week4/` 的起始应用。

## 了解 Claude Code
为了更深入理解 Claude Code 并探索可用的自动化方案，请阅读以下两个资源：

1. **Claude Code 最佳实践：** [anthropic.com/engineering/claude-code-best-practices](https://www.anthropic.com/engineering/claude-code-best-practices)
2. **SubAgents 概览：** [docs.anthropic.com/en/docs/claude-code/sub-agents](https://docs.anthropic.com/en/docs/claude-code/sub-agents)

## 探索起始应用
一个极简的全栈起始应用，目标是作为 **“开发者的指挥中心”**。
- FastAPI 后端 + SQLite（SQLAlchemy）
- 静态前端（无需 Node 工具链）
- 极简测试（pytest）
- Pre-commit（black + ruff）
- 用于练习智能体驱动工作流的任务

把这个应用当作你实验所构建 Claude 自动化的游乐场。

### 结构

```
backend/                # FastAPI 应用
frontend/               # 由 FastAPI 提供服务的静态 UI
data/                   # SQLite 数据库 + 种子数据
docs/                   # 用于智能体驱动工作流的 TASKS
```

### 快速开始

1) 激活你的 conda 环境。

```bash
conda activate cs146s
```

2)（可选）安装 pre-commit hooks

```bash
pre-commit install
```

3) 运行应用（从 `week4/` 目录）

```bash
make run
```

4) 打开 `http://localhost:8000` 查看前端，打开 `http://localhost:8000/docs` 查看 API 文档。

5) 体验起始应用，了解其当前特性与功能。

### 测试
运行测试（从 `week4/` 目录）

```bash
make test
```

### 格式化/静态检查

```bash
make format
make lint
```

## 第一部分：构建你的自动化（选择 2 个或更多）
现在你已经熟悉了起始应用，下一步是构建自动化来增强或扩展它。下面给出若干自动化选项供你选择，你也可以跨类别混搭。

在构建自动化的同时，把你的改动记录到 `writeup.md` 文件中。先把 *“How you used the automation to enhance the starter application”* 这一节留空——你将在作业第二部分回到这里填写。

### A) Claude 自定义斜杠命令
斜杠命令适用于重复工作流：你可以在 `.claude/commands/` 内创建 Markdown 文件来复用这些工作流。Claude 会通过 `/` 将它们暴露出来。

- 示例 1：带覆盖率的测试运行器
  - 名称：`tests.md`
  - 意图：运行 `pytest -q backend/tests --maxfail=1 -x`，如果通过，再运行 coverage。
  - 输入：可选 marker 或路径。
  - 输出：总结失败原因并建议下一步。
- 示例 2：文档同步
  - 名称：`docs-sync.md`
  - 意图：读取 `/openapi.json`，更新 `docs/API.md`，并列出路由变更。
  - 输出：类似 diff 的总结和 TODO。
- 示例 3：重构脚手架
  - 名称：`refactor-module.md`
  - 意图：重命名一个模块（例如 `services/extract.py` → `services/parser.py`），更新 import，并运行 lint/tests。
  - 输出：修改文件清单与验证步骤清单。

>*提示：让命令保持聚焦，使用 `$ARGUMENTS`，并尽量偏好幂等步骤。考虑对安全工具进行 allowlist，并使用 headless 模式以便重复执行。*

### B) `CLAUDE.md` 指导文件
当你开始一次对话时，`CLAUDE.md` 会被自动读取，你可以在其中提供仓库特定的指令、上下文或指导，从而影响 Claude 的行为。请在仓库根目录创建一个 `CLAUDE.md`（也可以在 `week4/` 子文件夹中额外创建）来指导 Claude 的行为。

- 示例 1：代码导航与入口
  - 包括：如何运行应用、路由文件位置（`backend/app/routers`）、测试位置、数据库如何注入种子数据。
- 示例 2：风格与安全护栏
  - 包括：工具链期望（black/ruff）、可安全执行的命令、应避免的命令，以及 lint/test 的门禁要求。
- 示例 3：工作流片段
  - 包括：“当被要求新增一个 endpoint 时，先写一个失败的测试，再实现代码，再跑 pre-commit。”

> *提示：把 `CLAUDE.md` 当作一个 prompt 来迭代优化，保持简洁且可执行，并记录你希望 Claude 使用的自定义工具/脚本。*

### C) SubAgents（角色专用）
SubAgents 是为特定任务配置的专用 AI 助手，它们拥有各自的系统提示、工具与上下文。请设计两个或更多协作的智能体，每个负责同一工作流中的不同步骤。

- 示例 1：TestAgent + CodeAgent
  - 流程：TestAgent 为改动编写/更新测试 → CodeAgent 实现代码以通过测试 → TestAgent 验证。
- 示例 2：DocsAgent + CodeAgent
  - 流程：CodeAgent 新增一个 API 路由 → DocsAgent 更新 `API.md` 和 `TASKS.md`，并对照 `/openapi.json` 检查是否漂移。
- 示例 3：DBAgent + RefactorAgent
  - 流程：DBAgent 提出 schema 变更（调整 `data/seed.sql`）→ RefactorAgent 更新 models/schemas/routers 并修复 lint。

>*提示：使用清单/草稿本，角色间切换时重置上下文（`/clear`），并行运行相互独立的智能体以提高效率。*

## 第二部分：让你的自动化真正派上用场
当你已经构建了 2+ 个自动化之后，就来把它们用起来吧！在 `writeup.md` 的 *“How you used the automation to enhance the starter application”* 小节中，描述你如何利用每个自动化来改进或扩展应用功能。

例如：如果你实现了自定义斜杠命令 `/generate-test-cases`，请说明你如何用它来与起始应用交互并进行测试。

## 交付物
1) 两个或更多自动化，形式可以包括：
   - `.claude/commands/*.md` 中的斜杠命令
   - `CLAUDE.md` 文件
   - SubAgent 的提示/配置（清晰记录，必要时包含文件/脚本）

2) 位于 `week4/` 的一份写作报告 `writeup.md`，其中包括：
  - 设计灵感（例如引用最佳实践和/或 sub-agents 文档）
  - 每个自动化的设计（目标、输入/输出、步骤）
  - 如何运行（精确命令）、预期输出，以及回滚/安全说明
  - 前后对比（即手工流程 vs 自动化流程）
  - 你如何使用自动化来增强起始应用

## 提交说明
1. 确保你已经把所有改动推送到远端仓库以便评分。
2. **确保你已将 brentju 和 febielin 添加为你作业仓库的协作者。**
2. 通过 Gradescope 提交。

