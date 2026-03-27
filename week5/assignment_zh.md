# 第 5 周 - 使用 Warp 进行 Agentic Development

将 `week5/` 中的应用作为你的练习场。本周与之前的作业类似，但重点放在 Warp 的 agentic development 环境和多智能体工作流上。

## 了解 Warp
- Warp Agentic Development Environment: [warp.dev](https://www.warp.dev/)
- [Warp University](https://www.warp.dev/university?slug=university)

## 探索起始应用
一个最小化的全栈起始应用。
- 使用 SQLite（SQLAlchemy）的 FastAPI 后端
- 静态前端（不需要 Node 工具链）
- 最小测试集（pytest）
- Pre-commit（black + ruff）
- 用于练习 agent 驱动工作流的任务

请使用这个应用作为练习场，实验你构建的 Warp 自动化能力。

### 结构

```text
backend/                # FastAPI 应用
frontend/               # 由 FastAPI 提供服务的静态 UI
data/                   # SQLite 数据库和种子数据
docs/                   # 用于 agent 驱动工作流的任务文档
```

### 快速开始

1. 激活你的 conda 环境。

```bash
conda activate cs146s
```

2. （可选）安装 pre-commit hooks

```bash
pre-commit install
```

3. 运行应用（在 `week5/` 目录下）

```bash
make run
```

4. 打开 `http://localhost:8000` 查看前端，打开 `http://localhost:8000/docs` 查看 API 文档。

5. 先体验一下这个起始应用，熟悉它当前的功能和行为。

### 测试
运行测试（在 `week5/` 目录下）

```bash
make test
```

### 格式化 / Lint

```bash
make format
make lint
```

## 第一部分：构建你的自动化（至少选择 2 个）
从 `week5/docs/TASKS.md` 中选择任务实现。你的实现必须以下面两种方式使用 Warp（详细要求见下文）：

- A) 使用 Warp Drive 功能，例如保存的 prompts、rules 或 MCP servers。
- B) 在 Warp 中结合多智能体工作流。

请将修改集中在 `week5/` 内的后端、前端、业务逻辑或测试上。
对于每个你选择的任务，请注明其难度等级。

### A) Warp Drive 保存的 prompts、rules、MCP servers（必做：至少一个）
创建一个或多个适用于本仓库、可共享的 Warp Drive prompt、rule 或 MCP server 集成。示例：
- 带覆盖率和 flaky 测试重跑能力的测试运行器
- 文档同步：根据 `/openapi.json` 生成或更新 `docs/API.md`，并列出路由差异
- 重构工具：重命名某个模块、更新导入、运行 lint 和测试
- 发布助手：提升版本号、运行检查、准备 changelog 片段
- 集成 Git MCP server，让 Warp 可以自主与 Git 交互（创建分支、提交、PR 说明等）

>提示：保持工作流聚焦；支持传参；保证幂等；尽量优先使用无界面、非交互式步骤。

### B) Warp 中的多智能体工作流（必做：至少一个）
运行一个多智能体会话，让不同 Warp 标签页中的独立 agent 并发处理不同任务。
- 在不同 Warp 标签页中，用并发 agent 分别完成 `TASKS.md` 中多个相互独立的任务。挑战：你最多可以同时让多少个 agent 一起工作？

>提示：[git worktree](https://git-scm.com/docs/git-worktree) 可能会有帮助，它可以避免多个 agent 彼此覆盖修改。

## 第二部分：将你的自动化真正用起来
现在你已经构建了 2 个或以上自动化，让我们把它们用起来。在 `writeup.md` 的 *"How you used the automation (what pain point it resolves or accelerates)"* 部分中，描述你如何利用每个自动化来改进某个工作流。

## 约束与范围
严格在 `week5/` 内工作（后端、前端、逻辑、测试）。除非某个自动化确实需要修改其他周的内容，并且你记录清楚原因，否则不要改动其他周。

## 交付物
1. 两个或以上 Warp 自动化，可以包括：
   - Warp Drive 工作流 / rules（分享链接和 / 或导出的定义）以及任何辅助脚本
   - 任何用于协调多个 agent 的补充 prompts / playbooks

2. 在 `week5/` 下提交一份 `writeup.md`，其中包括：
   - 每个自动化的设计，包括目标、输入 / 输出、步骤
   - 变更前 vs 变更后（即手动工作流 vs 自动化工作流）
   - 每个已完成任务使用的自主级别（用了哪些代码权限、为什么、你如何监督）
   - （如适用）多智能体说明：角色、协调策略，以及并发带来的收益 / 风险 / 失败点
   - 你如何使用这些自动化（它解决或加速了什么痛点）

## 提交说明
1. 确保你已经将所有修改推送到远程仓库，以便评分。
2. **确保你已将 brentju 和 febielin 都添加为你作业仓库的协作者。**
3. 通过 Gradescope 提交。
