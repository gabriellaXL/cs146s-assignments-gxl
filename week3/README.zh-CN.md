# Week 3：Open-Meteo MCP Server

英文版： [README.md](C:/Users/gabri/Documents/cs146s/modern-software-dev-assignments-master/week3/README.md)

本目录包含一个按工程化标准组织的 MCP Server，用于完成 Week 3 作业。它封装了公开的 [Open-Meteo](https://open-meteo.com/) API，并通过 MCP 暴露天气查询能力；此外还额外提供了一个辅助 resource 和一个 prompt，用于提升客户端使用体验。

该实现采用作业要求中的 **本地 STDIO 部署模式**，目标不是“单文件演示跑通”，而是结构清晰、易维护、便于扩展的小型真实项目。

## 作业要求覆盖情况

本实现已经覆盖 Week 3 的核心要求：

- 使用真实外部 API：Open-Meteo 的 geocoding 和 forecast 接口。
- 提供两个 MCP tools：
  - `search_place`
  - `get_current_weather`
- 具备基础鲁棒性处理：
  - 非法输入
  - HTTP 传输错误
  - 超时
  - HTTP 429 限流
  - 上游 4xx / 5xx 错误
  - 空结果
  - 上游返回结构异常
- 提供清晰的安装与运行说明。
- 提供 Cursor 和 Claude Desktop 的 MCP 客户端配置示例。
- 提供示例调用流程和 tool 说明。
- 提供覆盖关键边界情况的最小测试集。

## 项目结构

```text
week3/
├── assignment.md
├── README.md
├── README.zh-CN.md
├── requirements.txt
├── server/
│   ├── app.py
│   ├── config.py
│   ├── errors.py
│   ├── formatters.py
│   ├── logging_utils.py
│   ├── main.py
│   ├── models.py
│   ├── openmeteo_client.py
│   ├── prompts.py
│   ├── resources.py
│   ├── service.py
│   ├── tools.py
│   └── validation.py
└── tests/
    ├── conftest.py
    ├── test_openmeteo_client.py
    ├── test_tools.py
    └── test_validation.py
```

## 上游 API

本服务使用以下 Open-Meteo 接口：

- Geocoding API：`GET https://geocoding-api.open-meteo.com/v1/search`
- Forecast API：`GET https://api.open-meteo.com/v1/forecast`

该服务 **不需要 API key**。

## 环境要求

- Python 3.10+
- 能访问 `geocoding-api.open-meteo.com` 和 `api.open-meteo.com`

## 安装

在仓库根目录执行：

```bash
pip install -r week3/requirements.txt
```

如果你的环境中还没有安装 `pytest`，也可以额外执行：

```bash
pip install pytest
```

## 运行 MCP Server

在仓库根目录执行：

```bash
python -m week3.server.main
```

这是一个 **STDIO MCP server**：

- MCP 协议消息从 stdin 读取、写入 stdout。
- 应用日志只写入 stderr。
- 不要在启动后手工往终端里输入内容。
- 正常使用方式是让 Cursor、Claude Desktop 等 MCP 客户端来启动并托管该进程。

## MCP 客户端配置

### Cursor

可在当前项目下创建 `.cursor/mcp.json`，或者使用全局配置 `%USERPROFILE%\\.cursor\\mcp.json`：

```json
{
  "mcpServers": {
    "openmeteo": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "week3.server.main"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

修改后请完全重启 Cursor。如果服务未显示，可查看 **MCP Logs** 排查问题。

重要提示：即使 `.cursor/mcp.json` 配置正确，也还需要到 **Cursor Settings > MCP** 中确认 `openmeteo` 这个 server 处于 **Enabled** 状态。仅有配置文件并不总是代表它已经在 UI 里启用。

### Claude Desktop

编辑 `%AppData%\\Claude\\claude_desktop_config.json`，加入：

```json
{
  "mcpServers": {
    "openmeteo": {
      "command": "python",
      "args": ["-m", "week3.server.main"],
      "cwd": "C:\\\\path\\\\to\\\\modern-software-dev-assignments-master"
    }
  }
}
```

请将 `cwd` 替换为你的仓库根目录绝对路径，然后重启 Claude Desktop。

## Tool 说明

### `search_place`

根据城市名或地点名解析出一个或多个候选地点。

参数：

- `name`（`str`，必填）：要查询的地点名称。
- `max_results`（`int`，可选，默认 `5`）：返回结果上限，取值范围 `1` 到 `10`。

示例输入：

```json
{
  "name": "Beijing",
  "max_results": 2
}
```

示例输出：

```text
1. Beijing (China, Beijing)
   Coordinates: 39.9042, 116.4074
```

预期行为：

- 拒绝空白地点名或过长地点名。
- 拒绝超出 `1..10` 范围的 `max_results`。
- 无匹配结果时返回清晰的 not found 提示。
- 上游服务失败时返回用户友好的错误消息。

### `get_current_weather`

根据经纬度查询当前天气。

参数：

- `latitude`（`float`，必填）：范围 `-90` 到 `90`。
- `longitude`（`float`，必填）：范围 `-180` 到 `180`。

示例输入：

```json
{
  "latitude": 39.9042,
  "longitude": 116.4074
}
```

示例输出：

```text
Observed at: 2026-03-27T15:00
Conditions: Mostly clear
Temperature: 18.4 C
Feels like: 17.9 C
Relative humidity: 32%
Wind: 11.2 km/h at 210 degrees
```

预期行为：

- 拒绝非法纬度或经度。
- 输出格式稳定，适合 LLM 消费。
- 区分输入校验失败、资源不存在、上游服务失败等不同错误类型。

## 额外 MCP 能力

虽然作业硬性要求只要求 tools，这个实现还额外提供了：

- Resource：`openmeteo://server-info`
  - 用于说明服务行为、上游接口和重试策略。
- Prompt：`plan_weather_lookup`
  - 用于引导客户端执行“先搜地点，再查天气”的两步调用流程。

这些只是轻量增强项，不替代作业要求中的 tools。

## 示例调用流程

在 Cursor 或 Claude Desktop 中，你可以这样使用：

1. 输入：`Find the current weather in Beijing.`
2. 客户端首先调用 `search_place`，传入 `name="Beijing"`。
3. 模型从返回结果中选出最合适的地点。
4. 客户端再调用 `get_current_weather`，传入对应经纬度。
5. 模型根据结果总结当前天气，并说明观测时间。

也可以直接明确提示模型：

```text
Use the search_place tool to find Beijing, then call get_current_weather with the returned coordinates.
```

## 鲁棒性与错误处理

该实现包括：

- 集中管理 URL、超时、重试次数、退避策略和 user-agent
- 在发起上游请求前做输入校验
- HTTP 超时处理
- 传输错误处理
- 针对 HTTP 429 的显式限流处理
- 针对上游 4xx / 5xx 的显式处理
- 非法 JSON 或异常返回结构检测
- 仅向 stderr 写日志，适合 STDIO MCP server

面向用户或模型的返回消息保持简洁。更详细的调试信息只写入开发者日志。

## 运行测试

在仓库根目录执行：

```bash
pytest week3/tests -q
```

测试覆盖了：

- 非法 tool 参数
- 空搜索结果
- 上游响应结构异常
- timeout 错误转换
- 429 限流处理
- 必要 tools 和 resource 的 MCP 注册

## 限制说明

- 当前提交实现的是 **本地 STDIO 模式**，不是 remote HTTP 模式。
- 未实现认证，因为 Open-Meteo 不要求 API key。
- 真实运行效果仍然依赖网络连通性和 Open-Meteo 服务可用性。

## 验证说明

在当前仓库环境中，可以通过自动化测试验证输入校验、格式化逻辑和基于 mock 的上游错误处理，而不需要真实外网访问。

但在最终提交前，仍建议你在有网络的机器上，用 Cursor、Claude Desktop 或 MCP Inspector 实际跑通一次完整流程：

`search_place -> get_current_weather`

这样能进一步确认真实接口调用、客户端配置和端到端体验都没有问题。
