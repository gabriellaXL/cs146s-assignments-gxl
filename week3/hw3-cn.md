# 第 3 周——构建一个自定义 MCP Server

设计并实现一个 Model Context Protocol（MCP）服务器，用它来封装一个真实的外部 API。你可以选择：
- **本地运行**（STDIO 传输），并与某个 MCP 客户端集成（例如 Claude Desktop）。
- 或者**远程运行**（HTTP 传输），然后从一个模型 Agent 或客户端调用它。这个更难，但可以拿额外加分。

如果你能加入与 MCP Authorization 规范对齐的认证机制（API Key 或 OAuth2），会有额外加分。

## 学习目标
- 理解 MCP 的核心能力：tools、resources、prompts。
- 用带类型的参数实现 tool 定义，并做好健壮的错误处理。
- 遵循日志与传输的最佳实践（STDIO server 不要把日志写到 stdout）。
- （可选）为 HTTP 传输实现授权/认证流程。

## 要求
1. 选择一个外部 API，并记录你将使用哪些 endpoint。示例：天气、GitHub issues、Notion 页面、电影/电视剧数据库、日历、任务管理、金融/加密货币、旅行、体育数据。
2. 暴露至少两个 MCP tools。
3. 实现基础的鲁棒性：
   - 对 HTTP 失败、超时、空结果进行优雅报错。
   - 尊重 API 的 rate limit（例如：简单退避 backoff 或给用户提示/警告）。
4. 打包与文档：
   - 提供清晰的安装/运行说明、环境变量说明、运行命令。
   - 提供一个示例调用流程（用户在客户端里需要输入什么/点什么才能触发这些 tools）。
5. 选择一种部署模式：
   - 本地：STDIO server，可在你的机器上运行，并能被 Claude Desktop 或 Cursor 等 AI IDE 发现。
   - 远程：HTTP server，通过网络可访问，能被支持 MCP 的客户端或 agent runtime 调用。如果你真的部署并能从外网访问，可获得额外加分。
6. （可选）加分项：认证
   - 通过环境变量与客户端配置支持 API key；或
   - 为 HTTP 传输实现 OAuth2 风格的 bearer token：验证 token audience，并且永远不要把 token 透传给上游 API。

## 交付内容
- `week3/` 目录下的源代码（建议：`week3/server/`，并提供清晰入口文件，如 `main.py` 或 `app.py`）。
- `week3/README.md`，需要包含：
  - 先决条件、环境配置、运行说明（本地与/或远程）。
  - 如何配置 MCP 客户端（例如：本地模式下的 Claude Desktop 配置示例），或如何配置远程模式的 agent runtime。
  - Tool 参考文档：名称、参数、示例输入/输出、预期行为。

## 评分标准（总分 90）
- 功能（35）：实现 2+ tools、正确集成 API、输出有意义。
- 可靠性（20）：输入校验、错误处理、日志、rate-limit 意识。
- 开发者体验（20）：清晰的安装/运行文档、本地运行容易；合理的目录结构。
- 代码质量（15）：可读性强、命名清晰、复杂度低、适当的类型标注。
- 额外加分（10）：
  - +5 远程 HTTP MCP server，并且能被 agent/client（例如 OpenAI/Claude SDK）调用。
  - +5 认证实现正确（API key 或 OAuth2 + audience 验证）。

## 有用参考
- MCP Server Quickstart：[modelcontextprotocol.io/quickstart/server](https://modelcontextprotocol.io/quickstart/server)  
  *注意：不允许直接提交这个示例的原封不动版本。*
- MCP Authorization（HTTP）：[modelcontextprotocol.io/specification/2025-06-18/basic/authorization](https://modelcontextprotocol.io/specification/2025-06-18/basic/authorization)
- Cloudflare（Agents）上的远程 MCP：[developers.cloudflare.com/agents/guides/remote-mcp-server/](https://developers.cloudflare.com/agents/guides/remote-mcp-server/)  
  建议在部署前使用 modelcontextprotocol inspector 工具先在本地调试你的 server。
- https://vercel.com/docs/mcp/deploy-mcp-servers-to-vercel  
  如果你选择做远程 MCP 部署，Vercel 有免费套餐，是一个不错的选项。

