# 第 8 周 - 多技术栈 AI 加速 Web 应用构建

## Demo Day 确认
请前往这个[表单](https://forms.gle/J3R3PSRqnFAJxhjG8)查看有关课程 demo day 的详细信息。

## 作业概览
用 3 种不同的技术栈构建同一个具备相同功能的 Web 应用。其中至少一个版本必须使用 [`bolt.new`](https://bolt.new/) 这个 AI 应用生成平台创建。至少一个版本的前端或后端必须使用非 JavaScript 语言（例如 Django、Ruby on Rails）。

你可以复用前几周的应用（“developer control center”），也可以自行创建一个新应用，只要它满足[最小功能范围](#minimum-functional-scope)。应用需要具备端到端可用性（前端 + 后端 + 持久化，若该技术栈需要），并展示一个连贯的功能集。

## 最小功能范围
- 用户可以对一个主要资源执行创建、读取、更新和删除操作（例如 notes、tasks、posts）
- 在适合该技术栈的情况下，使用持久化存储（数据库或文件）
- 基本的数据校验和错误处理
- 简单但可用的 UI，能够覆盖主要流程
- 清晰说明如何在本地运行每个版本（如果你部署了，也请提供部署链接）

## 技术栈要求
构建 3 个相同应用的独立版本，每个版本都必须采用不同的技术栈。示例：
- MERN（MongoDB、Express、React、Node.js）
- MEVN（MongoDB、Express、Vue.js、Node.js）
- Django + React（或 Vue）
- Flask + Vanilla JS（或 React）
- Next.js + Node（或 NestJS）
- Ruby on Rails（全栈）

请注意，至少有一个版本的前端或后端必须使用非 JavaScript 语言（例如 Python / Django、Ruby / Rails）。

至少有一个版本必须使用 AI 应用生成平台 **[`bolt.new`](https://bolt.new/)** 构建；不过你也可以在其他版本中探索别的应用生成平台（例如 Lovable、Figma Make）。

## 了解 Bolt
Bolt 是一个 AI 辅助开发平台，可以根据自然语言提示生成网站、Web 应用和移动应用。用户只需用纯文本描述自己的想法，Bolt 就能在几分钟内产出一个可运行的原型，范围可以从落地页、电商网站到 CRM 和移动工具。更多信息见[这里](https://support.bolt.new/building/intro-bolt)。

### 领取你的 Bolt 积分：
1. 找到我们通过邮件发送给你的唯一 Bolt 优惠码。
2. 前往 [bolt.new](https://bolt.new/) 并创建账号。
3. 在 Personal Settings > Subscriptions & Tokens 中，找到 Upgrade to Pro 模块并点击蓝色的 “Upgrade” 按钮。
4. 选择 “Add promotion code”，将你唯一的 promotion code 粘贴到对应输入框中。
5. 你将获得 3 个月免费的 Bolt Pro。激活试用需要绑定信用卡。**如果你不打算继续订阅，请务必在 3 个月结束前取消，以避免自动扣费。**

## 使用 AI 应用生成器的提示
- Bolt 这类应用生成器最适合现代全栈技术；如果你没有特别指定框架，通常也会默认生成这类技术栈。
- 建议从一个干净的 prompt 开始，描述你的应用概念、实体、路由和 UI 流程。
- 在 prompt 中清晰描述数据模型和它们之间的关系。
- 通过迭代优化 prompts，逐步完善数据模型、CRUD 接口、认证（如果使用）以及前端组件。
- 将每个版本隔离开，以避免依赖冲突。
- 导出或同步生成的代码，并将其作为独立项目文件夹提交到仓库中。

## 交付物
1. `week8/` 目录下的 **三个**项目文件夹（每个版本一个），每个都包括：
   - 源代码
   - `README.md`，包含前置条件、安装 / 配置说明、运行方式和环境变量配置
   - 关于生成后偏差、已知问题以及任何手动修复的说明
2. 完成 `writeup.md`：
   - 应用概念
   - 3 份应用描述（每个版本一份）

## 评分细则（100 分）
- 应用概念满足最小功能范围（10 分）
- 三种不同技术栈（10 分）
- 至少一个版本使用 Bolt（10 分）
- 至少一个版本使用非 JS 语言（10 分）
- 应用的三个版本（每个 **20 分**）：
   - 在 `week8/` 中以文件夹形式提供源代码（5 分）
   - `README.md`：前置条件、安装 / 配置说明、运行方式和环境变量配置（5 分）
   - 应用功能完整可用（5 分）
   - 在 `writeup.md` 中提供完整的版本说明（5 分）
